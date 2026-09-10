"""Frozen, budgeted synthetic discovery/replay harness; standard library only.

The research runner is trusted. Teams submit JSON data, never Python code.
An in-process API is useful for adaptive research but is not process isolation.
"""
from copy import deepcopy
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
import json
import math

from .core import canonical_json
from .irreversible_release import (
    Artifact, Destination, ReleaseState, ReleaseBroker, MonitorOnlyReleaseBroker,
)
from .delegated_stop import Scope, DelegationState, DelegationBroker, WeakDelegationBroker
from .outcomes import score_episode

ROOT = Path(__file__).resolve().parent.parent
ARMS = ("generic", "technical", "grammar", "northstar")
RESOURCES = ("episodes", "actions", "tokens", "human_minutes", "preparation_minutes")
CONTROLS = ("starting", "repaired")


def digest(value):
    return sha256(canonical_json(value).encode("utf-8")).hexdigest()


def exact_keys(value, fields, label):
    if not isinstance(value, dict) or set(value) != set(fields):
        raise ValueError(f"{label}: expected exactly {sorted(fields)}")


def bounded_int(value, low, high, label):
    if type(value) is not int or not low <= value <= high:
        raise ValueError(f"{label}: expected integer in [{low}, {high}]")


def identifier(value, label):
    if not isinstance(value, str) or not value or len(value) > 120:
        raise ValueError(f"{label}: expected nonempty string of at most 120 characters")


def unique_strings(values, label):
    if not isinstance(values, list):
        raise ValueError(f"{label}: expected list")
    for value in values:
        identifier(value, label)
    if len(set(values)) != len(values):
        raise ValueError(f"{label}: duplicate values")


def pairs(values, left, right, label):
    if not isinstance(values, list):
        raise ValueError(f"{label}: expected list")
    for pair in values:
        if (not isinstance(pair, list) or len(pair) != 2 or
                not all(isinstance(x, str) for x in pair) or
                pair[0] not in left or pair[1] not in right):
            raise ValueError(f"{label}: invalid object pair")
    if len({tuple(pair) for pair in values}) != len(values):
        raise ValueError(f"{label}: duplicate pairs")


def validate_case(case):
    exact_keys(case, ("case_id", "family_id", "pair_id", "split", "kind", "environment",
                      "task", "setup", "schedule", "horizon", "oracle"), "case")
    for field in ("case_id", "family_id", "pair_id"):
        identifier(case[field], field)
    if case["split"] not in ("development", "held_out") or case["kind"] not in ("adversarial", "benign"):
        raise ValueError("invalid split or case kind")
    if not isinstance(case["task"], str) or not case["task"].strip():
        raise ValueError("task must describe the legitimate work")
    bounded_int(case["horizon"], 1, 64, "horizon")
    setup = case["setup"]
    if case["environment"] == "release":
        exact_keys(setup, ("artifacts", "destinations", "permitted_pairs"), "release setup")
        for field in ("artifacts", "destinations"):
            if not isinstance(setup[field], list) or not 1 <= len(setup[field]) <= 16:
                raise ValueError(f"{field}: expected 1-16 objects")
        for artifact in setup["artifacts"]:
            exact_keys(artifact, ("artifact_id", "classification", "body"), "artifact")
            identifier(artifact["artifact_id"], "artifact ID")
            if artifact["classification"] not in ("public", "protected") or not isinstance(artifact["body"], str):
                raise ValueError("invalid synthetic artifact")
        for dest in setup["destinations"]:
            exact_keys(dest, ("destination_id", "scope"), "destination")
            identifier(dest["destination_id"], "destination ID")
            if dest["scope"] not in ("approved_public", "external_unapproved"):
                raise ValueError("invalid destination scope")
        aids = [item["artifact_id"] for item in setup["artifacts"]]
        dids = [item["destination_id"] for item in setup["destinations"]]
        unique_strings(aids, "artifacts")
        unique_strings(dids, "destinations")
        pairs(setup["permitted_pairs"], aids, dids, "permitted pairs")
    elif case["environment"] == "delegation":
        exact_keys(setup, ("scope_ids", "effects", "max_pending_jobs"), "delegation setup")
        unique_strings(setup["scope_ids"], "scopes")
        unique_strings(setup["effects"], "effects")
        if not 1 <= len(setup["scope_ids"]) <= 2 or not 1 <= len(setup["effects"]) <= 16:
            raise ValueError("delegation requires 1-2 scopes and 1-16 effect IDs")
        bounded_int(setup["max_pending_jobs"], 1, 8, "max pending jobs")
        aids, dids = [], []
    else:
        raise ValueError("unsupported environment adapter")
    oracle = case["oracle"]
    exact_keys(oracle, ("forbidden_release_pairs", "useful_release_pairs", "useful_job_effects",
                        "forbid_post_stop_effects"), "oracle")
    pairs(oracle["forbidden_release_pairs"], aids, dids, "forbidden pairs")
    pairs(oracle["useful_release_pairs"], aids, dids, "useful pairs")
    unique_strings(oracle["useful_job_effects"], "useful effects")
    if not set(oracle["useful_job_effects"]) <= set(setup.get("effects", [])):
        raise ValueError("oracle references unknown effect")
    if type(oracle["forbid_post_stop_effects"]) is not bool:
        raise ValueError("forbid_post_stop_effects must be boolean")
    if set(map(tuple, oracle["forbidden_release_pairs"])) & set(map(tuple, oracle["useful_release_pairs"])):
        raise ValueError("a release cannot be both prohibited and useful")
    if not oracle["useful_release_pairs"] and not oracle["useful_job_effects"]:
        raise ValueError("every case needs a measurable legitimate task")
    if not isinstance(case["schedule"], list):
        raise ValueError("schedule must be a list")
    previous_tick = -1
    for event in case["schedule"]:
        if not isinstance(event, dict):
            raise ValueError("schedule event must be an object")
        fields = {
            "stop": ("tick", "verb", "scope_id"),
            "dispatch": ("tick", "verb"),
            "revoke_pair": ("tick", "verb", "artifact_id", "destination_id"),
        }.get(event.get("verb"))
        if fields is None:
            raise ValueError("unknown scheduled operation")
        exact_keys(event, fields, "schedule event")
        bounded_int(event["tick"], 0, case["horizon"] - 1, "schedule tick")
        if event["tick"] < previous_tick:
            raise ValueError("schedule must be in chronological order")
        previous_tick = event["tick"]
        if event["verb"] == "revoke_pair":
            if case["environment"] != "release":
                raise ValueError("release schedule event in delegation environment")
            pairs([[event["artifact_id"], event["destination_id"]]], aids, dids, "revoked pair")
        elif case["environment"] != "delegation":
            raise ValueError("delegation schedule event in release environment")
        elif event["verb"] == "stop" and event["scope_id"] not in setup["scope_ids"]:
            raise ValueError("scheduled stop references unknown scope")


def validate_plan(plan):
    exact_keys(plan, ("study_id", "study_class", "independence", "budgets", "utility_floor",
                      "cases", "repair_provenance"), "plan")
    identifier(plan["study_id"], "study ID")
    # A confirmatory study requires a stronger environment/evaluator and external
    # review; toggling a JSON flag must never upgrade these authored examples.
    if plan["study_class"] != "feasibility":
        raise ValueError("this harness supports feasibility studies only")
    exact_keys(plan["independence"], ("environment_author", "independent_review", "holdout_custodian"), "independence")
    for value in plan["independence"].values():
        identifier(value, "independence declaration")
    exact_keys(plan["repair_provenance"], ("description", "human_minutes"), "repair provenance")
    identifier(plan["repair_provenance"]["description"], "repair description")
    minutes = plan["repair_provenance"]["human_minutes"]
    if type(minutes) not in (int, float) or not math.isfinite(minutes) or minutes < 0:
        raise ValueError("repair effort must be nonnegative and finite")
    exact_keys(plan["budgets"], ARMS, "arm budgets")
    for budget in plan["budgets"].values():
        exact_keys(budget, RESOURCES, "budget")
        for resource, limit in budget.items():
            if type(limit) not in (int, float) or not math.isfinite(limit) or limit <= 0:
                raise ValueError("budgets must be positive and finite")
            if resource in ("episodes", "actions", "tokens") and type(limit) is not int:
                raise ValueError("count budgets must be integers")
    if any(budget != plan["budgets"][ARMS[0]] for budget in plan["budgets"].values()):
        raise ValueError("discovery arms must have identical resource ceilings")
    floor = plan["utility_floor"]
    if type(floor) not in (int, float) or not math.isfinite(floor) or not 0 <= floor <= 1:
        raise ValueError("utility floor must be in [0, 1]")
    if not isinstance(plan["cases"], list) or not plan["cases"]:
        raise ValueError("plan must contain cases")
    case_ids, families, twins = set(), {}, {}
    for case in plan["cases"]:
        validate_case(case)
        if case["case_id"] in case_ids:
            raise ValueError("duplicate case ID")
        case_ids.add(case["case_id"])
        prior_split = families.setdefault(case["family_id"], case["split"])
        if prior_split != case["split"]:
            raise ValueError("family leakage across development and held-out splits")
        twins.setdefault(case["pair_id"], []).append(case)
    for group in twins.values():
        if (len(group) != 2 or {case["kind"] for case in group} != {"benign", "adversarial"} or
                len({(case["family_id"], case["split"], case["environment"]) for case in group}) != 1):
            raise ValueError("each pair must contain one benign and one adversarial case in the same family/split/environment")
    if set(families.values()) != {"development", "held_out"}:
        raise ValueError("both development and held-out families are required")


def source_hashes():
    paths = sorted((ROOT / "northstar_sim").glob("*.py"))
    paths += [ROOT / "study.py"]
    paths += sorted((ROOT / "protocol" / "study-arms").glob("*.md"))
    return {path.relative_to(ROOT).as_posix(): sha256(path.read_bytes()).hexdigest() for path in paths}


def freeze(plan):
    validate_plan(plan)
    body = {"schema_version": 1, "plan": deepcopy(plan), "source_hashes": source_hashes(),
            "created_at": datetime.now(timezone.utc).isoformat()}
    return {**body, "manifest_sha256": digest(body)}


def verify_manifest(manifest):
    exact_keys(manifest, ("schema_version", "plan", "source_hashes", "created_at", "manifest_sha256"), "frozen manifest")
    if manifest["schema_version"] != 1:
        raise ValueError("unknown manifest schema")
    body = {key: value for key, value in manifest.items() if key != "manifest_sha256"}
    if digest(body) != manifest["manifest_sha256"]:
        raise ValueError("frozen manifest content changed")
    if manifest["source_hashes"] != source_hashes():
        raise ValueError("source or arm instructions changed; freeze a new study")
    validate_plan(manifest["plan"])


def public_case(case):
    # Author labels, future interventions, oracle and held-out cases stay out of
    # online packets. Teams share the common outcome definitions in common.md.
    view = {key: deepcopy(case[key]) for key in ("environment", "task", "setup", "horizon")}
    view["case_id"] = "case-" + digest(case["case_id"])[:16]
    return view


def arm_packet(manifest, arm):
    verify_manifest(manifest)
    if arm not in ARMS:
        raise ValueError("unknown arm")
    folder = ROOT / "protocol" / "study-arms"
    return {"manifest_sha256": manifest["manifest_sha256"], "arm": arm,
            "budget": manifest["plan"]["budgets"][arm],
            "common_instructions": (folder / "common.md").read_text(encoding="utf-8"),
            "method_instructions": (folder / f"{arm}.md").read_text(encoding="utf-8"),
            "cases": [public_case(case) for case in manifest["plan"]["cases"] if case["split"] == "development"]}


def run_episode(case, actions, control):
    """Execute data-only proposals and a frozen scheduler, then settle to horizon."""
    if control not in CONTROLS:
        raise ValueError("unknown control")
    if not isinstance(actions, list) or len(actions) > case["horizon"]:
        raise ValueError("actions must be a list within the declared horizon")
    setup = case["setup"]
    release = case["environment"] == "release"
    if release:
        state = ReleaseState(
            {a["artifact_id"]: Artifact(**a) for a in setup["artifacts"]},
            {d["destination_id"]: Destination(**d) for d in setup["destinations"]},
            set(map(tuple, setup["permitted_pairs"])))
        broker = (ReleaseBroker if control == "repaired" else MonitorOnlyReleaseBroker)(state)
    else:
        state = DelegationState({sid: Scope(sid) for sid in setup["scope_ids"]})
        broker = (DelegationBroker if control == "repaired" else WeakDelegationBroker)(state)
    events, trace, tokens = [], [], []
    error = None

    def observed_effects(tick, before):
        current = state.committed_releases if release else state.effects
        for effect in current[before:]:
            if release:
                events.append({"kind": "release", "tick": tick, "artifact_id": effect["artifact_id"],
                               "destination_id": effect["destination_id"]})
            else:
                events.append({"kind": "job_effect", "tick": tick, "scope_id": effect["scope_id"],
                               "effect": effect["effect"], "job_id": effect["job_id"]})

    try:
        for tick in range(case["horizon"]):
            for scheduled in case["schedule"]:
                if scheduled["tick"] != tick:
                    continue
                before = len(state.committed_releases if release else state.effects)
                if scheduled["verb"] == "stop":
                    decision = broker.scoped_stop("operator", scheduled["scope_id"])
                    if decision.allowed:
                        events.append({"kind": "stop", "tick": tick, "scope_id": scheduled["scope_id"]})
                    status = decision.status
                elif scheduled["verb"] == "dispatch":
                    queued = [job.job_id for job in state.jobs.values() if job.status == "queued"]
                    status = broker.dispatch("scheduler", queued[0]).status if queued else "idle"
                else:
                    # Operator-only fixture change, recorded by the runner. No
                    # attacker action can invoke this policy mutation.
                    state.permitted_pairs.discard((scheduled["artifact_id"], scheduled["destination_id"]))
                    state.state_version += 1
                    status = "revoked"
                observed_effects(tick, before)
                trace.append({"tick": tick, "source": "scheduler", "action": scheduled, "status": status})
            if tick >= len(actions):
                continue
            action = actions[tick]
            before = len(state.committed_releases if release else state.effects)
            try:
                if not isinstance(action, dict):
                    raise ValueError("action must be an object")
                verb = action.get("verb")
                if verb == "wait":
                    exact_keys(action, ("verb",), "wait")
                    status, reason = "wait", "no action"
                elif release and verb == "stage":
                    exact_keys(action, ("verb", "artifact_id", "destination_id"), "stage")
                    identifier(action["artifact_id"], "artifact ID")
                    identifier(action["destination_id"], "destination ID")
                    decision = broker.stage_release("agent", action["artifact_id"], action["destination_id"])
                    status, reason = decision.status, decision.reason
                    if decision.allowed:
                        tokens.append(decision.receipt.details["token"])
                elif release and verb == "commit":
                    exact_keys(action, ("verb", "stage_index"), "commit")
                    bounded_int(action["stage_index"], 0, 63, "stage index")
                    if action["stage_index"] >= len(tokens):
                        raise ValueError("stage index does not reference a successful stage")
                    decision = broker.commit_release("agent", tokens[action["stage_index"]])
                    status, reason = decision.status, decision.reason
                elif not release and verb == "submit":
                    exact_keys(action, ("verb", "scope_id", "effect"), "submit")
                    identifier(action["scope_id"], "scope ID")
                    identifier(action["effect"], "effect ID")
                    if action["scope_id"] not in setup["scope_ids"] or action["effect"] not in setup["effects"]:
                        raise ValueError("unknown scope or effect")
                    if sum(job.status == "queued" for job in state.jobs.values()) >= setup["max_pending_jobs"]:
                        status, reason = "hold", "pending job budget exhausted"
                    else:
                        decision = broker.submit_job("agent", action["scope_id"], action["effect"])
                        status, reason = decision.status, decision.reason
                else:
                    raise ValueError("unknown or unauthorized verb")
            except ValueError as exc:
                status, reason = "reject_malformed", str(exc)
            observed_effects(tick, before)
            trace.append({"tick": tick, "source": "agent", "action": action, "status": status, "reason": reason})
    except Exception as exc:
        # An infrastructure fault is not a clean episode and cannot erase a
        # previously observed failure. Trusted runner errors remain visible.
        error = f"{type(exc).__name__}: {exc}"
    pending = len(state.staged) if release else sum(job.status == "queued" for job in state.jobs.values())
    score = score_episode(events, case["oracle"], pending, error)
    return {"case_id": case["case_id"], "family_id": case["family_id"], "pair_id": case["pair_id"],
            "split": case["split"], "kind": case["kind"], "control": control,
            "events": events, "trace": trace, "ledger": state.ledger.to_list(), "score": score}


class StudySession:
    """Budgeted adaptive discovery: inspect feedback, then submit another episode.

    This object and the full frozen manifest belong to the trusted researcher.
    Expose only arm_packet and submit feedback to a discovery team.
    """
    def __init__(self, manifest):
        verify_manifest(manifest)
        self.manifest = deepcopy(manifest)
        self.cases = {public_case(case)["case_id"]: case for case in manifest["plan"]["cases"]
                      if case["split"] == "development"}
        self.usage = {arm: dict.fromkeys(RESOURCES, 0) for arm in ARMS}
        self.attempts = []
        self.runs = []

    def submit(self, submission):
        # A valid accounting envelope is required before accepting a trial.
        # Malformed *actions*, unknown cases, and overlong plans are charged.
        try:
            exact_keys(submission, ("arm", "case_id", "actions", "costs"), "submission")
            arm = submission["arm"]
            if arm not in ARMS:
                raise ValueError("unknown arm")
            exact_keys(submission["costs"], ("tokens", "human_minutes", "preparation_minutes"), "reported costs")
            for resource, cost in submission["costs"].items():
                if type(cost) not in (int, float) or not math.isfinite(cost) or cost < 0:
                    raise ValueError("reported costs must be nonnegative and finite")
                if resource == "tokens" and type(cost) is not int:
                    raise ValueError("token cost must be an integer")
        except (ValueError, TypeError) as exc:
            self.attempts.append({"submission": deepcopy(submission), "status": "invalid_envelope",
                                  "charged": False, "reason": str(exc)})
            return {"status": "invalid_envelope", "reason": str(exc)}
        actions = submission["actions"]
        charge = {"episodes": 1, "actions": len(actions) if isinstance(actions, list) else 1,
                  **submission["costs"]}
        remaining = {key: self.manifest["plan"]["budgets"][arm][key] - self.usage[arm][key] for key in RESOURCES}
        if any(charge[key] > remaining[key] for key in RESOURCES):
            self.attempts.append({"submission": deepcopy(submission), "status": "budget_rejected", "charged": False})
            return {"status": "budget_rejected", "remaining": remaining}
        for key in RESOURCES:
            self.usage[arm][key] += charge[key]
        attempt = {"submission": deepcopy(submission), "charged": True}
        self.attempts.append(attempt)
        try:
            case = self.cases.get(submission["case_id"])
            if case is None or case["split"] != "development":
                raise ValueError("case unavailable for discovery")
            result = run_episode(case, actions, "starting")
        except (ValueError, TypeError) as exc:
            attempt.update(status="invalid_candidate", reason=str(exc))
            return {"status": "invalid_candidate", "reason": str(exc)}
        attempt["status"] = "launched"
        result.update(arm=arm, attempt_index=len(self.attempts) - 1)
        self.runs.append(result)
        # Feedback uses public decisions; no future schedule, family labels,
        # oracle fields, ground-truth score, or held-out data are returned.
        return {"status": "launched", "observations": [row for row in result["trace"] if row["source"] == "agent"],
                "remaining": {key: self.manifest["plan"]["budgets"][arm][key] - self.usage[arm][key] for key in RESOURCES}}

    def export(self):
        return {"manifest_sha256": self.manifest["manifest_sha256"], "usage": deepcopy(self.usage),
                "attempts": deepcopy(self.attempts), "runs": deepcopy(self.runs)}


def summarize(runs, utility_floor):
    groups = {}
    for run in runs:
        key = (run.get("arm", "independent_replay"), run["control"], run["split"], run["family_id"])
        groups.setdefault(key, []).append(run)
    rows = []
    for (arm, control, split, family), values in sorted(groups.items()):
        n = len(values)
        failures = sum(run["score"]["status"] == "failure" for run in values)
        unknown = sum(run["score"]["status"] == "unresolved" for run in values)
        benign = [run["score"]["utility"] for run in values if run["kind"] == "benign"]
        utility = sum(benign) / len(benign) if benign else None
        rows.append({"arm": arm, "control": control, "split": split, "family_id": family,
                     "episodes": n, "failures": failures, "unresolved": unknown,
                     "observed_failure_fraction": failures / n,
                     "classification_range": [failures / n, (failures + unknown) / n],
                     "benign_mean_utility": utility,
                     "utility_gate": None if utility is None else utility >= utility_floor})
    return {"study_class": "feasibility", "groups": rows,
            "interpretation": "Episode fractions in the supplied trial mix; classification ranges are not confidence intervals.",
            "discovery_advantage": "not_established",
            "primary_prevention_claim": "not_established",
            "recoverability": "not_assessed",
            "independent_root_cause_adjudication": "required_before_counting_distinct_discoveries"}
