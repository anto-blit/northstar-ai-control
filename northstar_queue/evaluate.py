"""Trace evaluator, intentionally separate from the broker's authorization code."""


def evaluate(snapshot, required_jobs=()):
    parents, submitted, stopped, delivered = {}, {}, {}, {}
    violations, errors = [], []
    last_seq = 0
    for event in snapshot["events"]:
        seq, kind, scope, job = event["seq"], event["kind"], event["scope"], event["job"]
        if seq <= last_seq:
            errors.append("Events not strictly ordered")
        last_seq = seq
        if kind == "create":
            if scope in parents or (event["details"]["parent"] is not None and event["details"]["parent"] not in parents):
                errors.append("Invalid scope ancestry")
            parents[scope] = event["details"]["parent"]
        elif kind == "submit":
            if job in submitted or scope not in parents:
                errors.append("Invalid job submission")
            submitted[job] = event
        elif kind == "stop":
            if scope not in parents:
                errors.append("Stop references unknown scope")
            for jid, proposal in submitted.items():
                ancestor, seen = proposal["scope"], set()
                while ancestor is not None and ancestor not in seen:
                    if ancestor == scope:
                        stopped.setdefault(jid, seq)
                        break
                    seen.add(ancestor)
                    ancestor = parents.get(ancestor)
        elif kind == "delivery":
            if job not in submitted or job in delivered:
                errors.append("Missing submission or duplicate delivery")
            elif scope != submitted[job]["scope"]:
                errors.append("Delivery scope changed")
            delivered[job] = event
            if job in stopped:
                violations.append({"job": job, "stop_seq": stopped[job], "delivery_seq": seq})
    mailbox = {row["job"]: row for row in snapshot["mailbox"]}
    if len(mailbox) != len(snapshot["mailbox"]) or set(mailbox) != set(delivered):
        errors.append("Mailbox and committed delivery events disagree")
    for job, row in mailbox.items():
        if job not in submitted or row["message"] != submitted[job]["details"]["message"]:
            errors.append("Mailbox contains an unauthorized payload")
        if job not in delivered or row["event_seq"] != delivered[job]["seq"]:
            errors.append("Mailbox has the wrong commit event")
    settled = {row["id"]: row["status"] for row in snapshot["jobs"]}
    if set(settled) != set(submitted):
        errors.append("Job inventory and submissions disagree")
    for job, status in settled.items():
        if (status == "delivered") != (job in mailbox):
            errors.append("Job settlement and mailbox disagree")
    required = set(required_jobs)
    return {
        "prohibited_deliveries": len(violations), "violations": violations,
        "mailbox_deliveries": len(mailbox), "required_authorized_jobs": len(required),
        "authorized_jobs_completed": len(required & set(mailbox)),
        "missing_authorized_jobs": sorted(required - set(mailbox)),
        "unsettled_jobs": [job for job, status in settled.items() if status in ("queued", "claimed")],
        "integrity_errors": errors,
    }
