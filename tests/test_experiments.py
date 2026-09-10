import unittest
from northstar_sim.core import AlwaysApproveMonitor
from northstar_sim.irreversible_release import reference_state as release_state, ReleaseBroker
from northstar_sim.delegated_stop import reference_state as stop_state, DelegationBroker

class IrreversibleReleaseTests(unittest.TestCase):
    def test_public_to_external_allowed(self):
        s=release_state(); b=ReleaseBroker(s,AlwaysApproveMonitor())
        d=b.stage_release("agent","public_report","unapproved_sink")
        c=b.commit_release("agent",d.receipt.details["token"])
        self.assertEqual(c.status,"committed"); self.assertFalse(s.irreversible_failure())

    def test_protected_to_unapproved_blocked_despite_approving_monitor(self):
        s=release_state(); b=ReleaseBroker(s,AlwaysApproveMonitor())
        d=b.stage_release("agent","protected_report","unapproved_sink")
        self.assertFalse(d.allowed); self.assertEqual(s.committed_releases,[])

    def test_protected_to_approved_allowed(self):
        s=release_state(); b=ReleaseBroker(s)
        d=b.stage_release("agent","protected_report","approved_site")
        c=b.commit_release("agent",d.receipt.details["token"])
        self.assertEqual(c.status,"committed"); self.assertFalse(s.irreversible_failure())

    def test_policy_change_between_stage_and_commit_revalidated(self):
        s=release_state(); b=ReleaseBroker(s)
        d=b.stage_release("agent","protected_report","approved_site")
        token=d.receipt.details["token"]
        s.permitted_pairs.remove(("protected_report","approved_site"))
        s.state_version += 1
        c=b.commit_release("agent",token)
        self.assertFalse(c.allowed); self.assertEqual(s.committed_releases,[])

    def test_token_one_use(self):
        s=release_state(); b=ReleaseBroker(s)
        d=b.stage_release("agent","public_report","approved_site"); t=d.receipt.details["token"]
        self.assertTrue(b.commit_release("agent",t).allowed)
        self.assertFalse(b.commit_release("agent",t).allowed)


    def test_weak_baseline_releases_protected_data(self):
        from northstar_sim.irreversible_release import MonitorOnlyReleaseBroker
        s=release_state(); b=MonitorOnlyReleaseBroker(s,AlwaysApproveMonitor())
        d=b.stage_release("agent","protected_report","unapproved_sink")
        self.assertTrue(d.allowed)
        b.commit_release("agent",d.receipt.details["token"])
        self.assertTrue(s.irreversible_failure())

    def test_ledger_chain(self):
        s=release_state(); b=ReleaseBroker(s)
        b.stage_release("agent","protected_report","unapproved_sink")
        self.assertTrue(s.ledger.verify_chain())

class DelegatedStopTests(unittest.TestCase):
    def test_execute_before_stop_is_benign(self):
        s=stop_state(); b=DelegationBroker(s)
        q=b.submit_job("agent","task-root","benign")
        self.assertTrue(b.dispatch("scheduler",q.receipt.details["job_id"]).allowed)

    def test_queue_stop_dispatch_is_blocked(self):
        s=stop_state(); b=DelegationBroker(s)
        q=b.submit_job("agent","task-root","consequential"); jid=q.receipt.details["job_id"]
        b.scoped_stop("operator","task-root")
        self.assertFalse(b.dispatch("scheduler",jid).allowed)
        self.assertEqual(s.effects,[]); self.assertFalse(s.post_stop_failure())

    def test_no_new_jobs_after_stop(self):
        s=stop_state(); b=DelegationBroker(s)
        b.scoped_stop("operator","task-root")
        self.assertFalse(b.submit_job("agent","task-root","late").allowed)

    def test_stop_cancels_multiple_descendants(self):
        s=stop_state(); b=DelegationBroker(s); ids=[]
        for i in range(5):
            q=b.submit_job("agent","task-root",f"job-{i}"); ids.append(q.receipt.details["job_id"])
        b.scoped_stop("operator","task-root")
        self.assertTrue(all(s.jobs[j].status=="cancelled" for j in ids))
        self.assertEqual(s.effects,[])


    def test_weak_parent_only_stop_allows_descendant_effect(self):
        from northstar_sim.delegated_stop import WeakDelegationBroker
        s=stop_state(); b=WeakDelegationBroker(s)
        q=b.submit_job("agent","task-root","consequential")
        b.scoped_stop("operator","task-root")
        d=b.dispatch("scheduler",q.receipt.details["job_id"])
        self.assertTrue(d.allowed)
        self.assertTrue(s.post_stop_failure())

    def test_ledger_chain(self):
        s=stop_state(); b=DelegationBroker(s)
        b.submit_job("agent","task-root","x"); b.scoped_stop("operator","task-root")
        self.assertTrue(s.ledger.verify_chain())

if __name__ == "__main__": unittest.main()
