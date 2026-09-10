#!/usr/bin/env python3
"""CLI for freezing plans, producing team packets, and recording study runs."""
import argparse
import json
from pathlib import Path

from northstar_sim.study import (
    ARMS, CONTROLS, StudySession, arm_packet, digest, exact_keys, freeze,
    run_episode, summarize, verify_manifest,
)


def read_json(path):
    def unique_keys(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError(f"duplicate JSON key: {key}")
            result[key] = value
        return result
    return json.loads(Path(path).read_text(encoding="utf-8"), object_pairs_hook=unique_keys)


def write_new(path, value):
    # Refuse overwrites: each frozen manifest/result is a separate artifact.
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write("\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    frozen = sub.add_parser("freeze", help="validate and hash a feasibility plan and current code")
    frozen.add_argument("plan")
    frozen.add_argument("output")
    packet = sub.add_parser("packet", help="export only a team's development cases and guidance")
    packet.add_argument("manifest")
    packet.add_argument("arm", choices=ARMS)
    packet.add_argument("output")
    discover = sub.add_parser("discover", help="run a charged batch; resume preserves and replays prior attempts")
    discover.add_argument("manifest")
    discover.add_argument("submissions")
    discover.add_argument("output")
    discover.add_argument("--resume", help="previous discovery result; all attempts and costs are retained")
    replay = sub.add_parser("replay", help="paired fixed challenges of starting and repaired controls")
    replay.add_argument("manifest")
    replay.add_argument("challenges")
    replay.add_argument("output")
    args = parser.parse_args()
    if args.command == "freeze":
        result = freeze(read_json(args.plan))
    else:
        manifest = read_json(args.manifest)
        verify_manifest(manifest)
        if args.command == "packet":
            result = arm_packet(manifest, args.arm)
        elif args.command == "discover":
            session = StudySession(manifest)
            parent = None
            if args.resume:
                previous = read_json(args.resume)
                if previous["manifest_sha256"] != manifest["manifest_sha256"]:
                    raise ValueError("resume manifest mismatch")
                for attempt in previous["attempts"]:
                    session.submit(attempt["submission"])
                if any(session.export()[key] != previous[key] for key in ("usage", "attempts", "runs")):
                    raise ValueError("prior discovery results do not reproduce")
                parent = digest(previous)
            submissions = read_json(args.submissions)
            if not isinstance(submissions, list):
                raise ValueError("submissions must be a JSON list")
            feedback = [session.submit(submission) for submission in submissions]
            result = {**session.export(), "parent_result_sha256": parent, "new_feedback": feedback,
                      "report": summarize(session.runs, manifest["plan"]["utility_floor"])}
        else:
            challenges = read_json(args.challenges)
            if not isinstance(challenges, list):
                raise ValueError("challenges must be a JSON list")
            cases = {case["case_id"]: case for case in manifest["plan"]["cases"]}
            runs = []
            for challenge in challenges:
                exact_keys(challenge, ("case_id", "actions"), "challenge")
                if challenge["case_id"] not in cases:
                    raise ValueError("unknown challenge case")
                for control in CONTROLS:
                    runs.append(run_episode(cases[challenge["case_id"]], challenge["actions"], control))
            result = {"manifest_sha256": manifest["manifest_sha256"], "challenge_sha256": digest(challenges),
                      "evaluation_mode": "fixed_replay_no_adaptive_evaluator",
                      "runs": runs, "report": summarize(runs, manifest["plan"]["utility_floor"])}
    write_new(args.output, result)
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, KeyError, TypeError) as exc:
        raise SystemExit(f"Study input/run error: {exc}")
