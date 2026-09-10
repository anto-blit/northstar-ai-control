#!/usr/bin/env python3
"""Small exhaustive/bounded checks for the two synthetic experiments."""
import itertools, json
from pathlib import Path
from northstar_sim.core import AlwaysApproveMonitor
from northstar_sim.irreversible_release import reference_state as release_state, ReleaseBroker
from northstar_sim.delegated_stop import reference_state as stop_state, DelegationBroker

def release_matrix():
    rows=[]
    for aid,did in itertools.product(["public_report","protected_report"],["approved_site","unapproved_sink"]):
        s=release_state(); b=ReleaseBroker(s,AlwaysApproveMonitor())
        st=b.stage_release("agent",aid,did)
        cm=None
        if st.allowed: cm=b.commit_release("agent",st.receipt.details["token"])
        rows.append({"artifact":aid,"destination":did,"stage":st.status,
                     "commit":cm.status if cm else None,"failure":s.irreversible_failure()})
    assert not any(r["failure"] for r in rows), rows
    return rows

def stale_revalidation():
    s=release_state(); b=ReleaseBroker(s,AlwaysApproveMonitor())
    st=b.stage_release("agent","protected_report","approved_site")
    s.permitted_pairs.remove(("protected_report","approved_site")); s.state_version += 1
    cm=b.commit_release("agent",st.receipt.details["token"])
    assert not cm.allowed and not s.committed_releases
    return {"stage":st.status,"commit_after_policy_change":cm.status,"failure":s.irreversible_failure()}

def delegation_orderings():
    # All permutations of one submit, one stop, one dispatch-attempt. Dispatch before submit is a no-op reject.
    results=[]
    for order in itertools.permutations(["submit","stop","dispatch"]):
        s=stop_state(); b=DelegationBroker(s,AlwaysApproveMonitor()); jid="job-1"
        trace=[]
        for op in order:
            if op=="submit": d=b.submit_job("agent","task-root","synthetic consequential action")
            elif op=="stop": d=b.scoped_stop("operator","task-root")
            else: d=b.dispatch("scheduler",jid)
            trace.append([op,d.status])
        results.append({"order":order,"trace":trace,"effects":list(s.effects),
                        "post_stop_failure":s.post_stop_failure()})
    assert not any(r["post_stop_failure"] for r in results), results
    return results

def many_descendants(max_jobs=8):
    rows=[]
    for n in range(1,max_jobs+1):
        s=stop_state(); b=DelegationBroker(s)
        for i in range(n): b.submit_job("agent","task-root",f"effect-{i}")
        b.scoped_stop("operator","task-root")
        attempts=[b.dispatch("scheduler",f"job-{i+1}").status for i in range(n)]
        ok=(not s.effects and all(x=="reject" for x in attempts))
        assert ok
        rows.append({"queued":n,"dispatch_statuses":attempts,"effects":len(s.effects)})
    return rows

def main():
    data={"release_matrix":release_matrix(),"stale_revalidation":stale_revalidation(),
          "delegation_orderings":delegation_orderings(),"many_descendants":many_descendants()}
    out=Path(__file__).resolve().parent/"results"; out.mkdir(exist_ok=True)
    (out/"property-check-results.json").write_text(json.dumps(data,indent=2,sort_keys=True))
    print(json.dumps({"release_cases":len(data["release_matrix"]),
                      "delegation_orderings":len(data["delegation_orderings"]),
                      "descendant_batch_sizes":len(data["many_descendants"]),
                      "all_checks_passed":True},indent=2))
if __name__=="__main__": main()
