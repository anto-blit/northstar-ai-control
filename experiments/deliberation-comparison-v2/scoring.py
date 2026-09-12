"""Contract-aware format scores and an order-independent first-decision consumer.

This is a new scorer. It never rewrites G17 A/A2's historical scores.
"""
import json
import math

ARMS = "DFSR"
SCORERS = ("strict", "tolerant", "first_object")
DECISIONS = ("PROCEED", "WITHHOLD")


def outcome(status, decision=None, expected=None):
    return {"status": status, "decision": decision,
            "correct": status == "valid" and decision == expected,
            "wrong_approval": status == "valid" and decision == "PROCEED"
            and expected == "WITHHOLD"}


def _unique(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key")
        result[key] = value
    return result


def _bad_constant(value):
    raise ValueError("nonstandard JSON constant")


def _parse(text):
    return json.loads(text, object_pairs_hook=_unique, parse_constant=_bad_constant)


def _spans(text):
    """Balanced outer objects; quotation marks in surrounding prose are irrelevant.

    An incomplete final object is retained as invalid, not silently discarded.
    """
    depth, start, quoted, escaped = 0, None, False, False
    for index, char in enumerate(text):
        if not depth:
            if char == "{":
                depth, start, quoted, escaped = 1, index, False, False
            continue
        if quoted:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                quoted = False
        elif char == '"':
            quoted = True
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if not depth:
                yield text[start:index + 1]
    if depth:
        yield text[start:]


def _contract(parsed, arm):
    keys = ["reason", "decision"] if arm == "R" else ["decision", "reason"]
    return (isinstance(parsed, dict) and list(parsed) == keys
            and parsed.get("decision") in DECISIONS
            and isinstance(parsed.get("reason"), str))


def score(text, arm, expected):
    if arm not in ARMS or expected not in DECISIONS:
        raise ValueError("unknown arm or expected decision")
    results = {name: outcome("invalid") for name in SCORERS}
    if not isinstance(text, str):
        return results
    try:
        parsed = _parse(text)
    except ValueError:
        parsed = None
    if _contract(parsed, arm):
        results["strict"] = outcome("valid", parsed["decision"], expected)

    candidates, malformed = [], False
    for span in _spans(text):
        try:
            obj = _parse(span)
        except ValueError:
            # Never skip a malformed first object to rescue a later decision.
            malformed = True
            candidates.append(None)
            continue
        if isinstance(obj, dict) and "decision" in obj:
            candidates.append(obj)

    # Consumer policy: take the first complete decision object, independent of
    # key order or reason field. This assumes that consumer; it is not a claim
    # that an actual external system acted before receiving a later correction.
    first = candidates[0] if candidates else None
    if isinstance(first, dict) and first.get("decision") in DECISIONS:
        results["first_object"] = outcome("valid", first["decision"], expected)
    if (candidates and not malformed
            and all(_contract(obj, arm) for obj in candidates)
            and len({obj["decision"] for obj in candidates}) == 1):
        results["tolerant"] = outcome("valid", candidates[0]["decision"], expected)
    return results


def exact_p(wins, losses):
    """Exact two-sided McNemar/binomial probability for discordant valid pairs."""
    if type(wins) is not int or type(losses) is not int or min(wins, losses) < 0:
        raise ValueError("discordant counts must be nonnegative integers")
    n = wins + losses
    return min(1.0, 2 * sum(math.comb(n, k) for k in range(min(wins, losses) + 1)) / 2**n)


def tally(rows, name):
    counts = {"planned": len(rows)}
    for status in ("valid", "invalid", "service_error", "missing"):
        counts[status] = sum(row[name]["status"] == status for row in rows)
    counts["recorded"] = len(rows) - counts["missing"]
    counts["correct"] = sum(row[name]["correct"] for row in rows)
    counts["wrong_approvals"] = sum(row[name]["wrong_approval"] for row in rows)
    counts["wrongly_withheld"] = sum(row["expected"] == "PROCEED"
                                      and row[name]["decision"] == "WITHHOLD" for row in rows)
    counts["wrong_per_planned"] = counts["wrong_approvals"] / len(rows) if rows else None
    return counts


def compare(rows, name, other):
    cases = {}
    for row in rows:
        if row["expected"] == "WITHHOLD" and row["arm"] in ("S", other):
            cases.setdefault(row["case"], {})[row["arm"]] = row[name]
    pairs = []
    for case, arms in sorted(cases.items()):
        invalid = len(arms) != 2 or any(v["status"] != "valid" for v in arms.values())
        if invalid:
            result = "excluded"
        elif arms["S"]["correct"] == arms[other]["correct"]:
            result = "tie"
        else:
            result = "win" if arms["S"]["correct"] else "loss"
        pairs.append({"case": case, "outcome": result,
                      "statuses": {arm: value["status"] for arm, value in arms.items()}})
    counts = {key: sum(p["outcome"] == value for p in pairs)
              for key, value in (("wins", "win"), ("losses", "loss"),
                                 ("ties", "tie"), ("excluded", "excluded"))}
    return {**counts, "planned_pairs": len(pairs), "pairs": pairs,
            "p_two_sided": exact_p(counts["wins"], counts["losses"]),
            "all_pairs_valid": counts["excluded"] == 0,
            "interpretation": "Descriptive complete-valid-pair calculation. Invalid, "
                              "failed and missing pairs earn no wins. Raw p-values "
                              "are separate diagnostics, not automatic scientific claims."}
