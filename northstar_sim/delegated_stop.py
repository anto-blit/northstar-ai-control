from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Any
from .core import Ledger, Decision, AlwaysApproveMonitor, atomic_transition

@dataclass
class Scope:
    scope_id: str
    epoch: int = 0
    active: bool = True

@dataclass
class Job:
    job_id: str
    scope_id: str
    captured_epoch: int
    effect: str
    status: str = "queued"

@dataclass
class DelegationState:
    scopes: Dict[str, Scope]
    jobs: Dict[str, Job] = field(default_factory=dict)
    effects: List[Dict[str, Any]] = field(default_factory=list)
    state_version: int = 0
    ledger: Ledger = field(default_factory=Ledger)

    def post_stop_failure(self):
        return any(e.get("executed_after_stop", False) for e in self.effects)

class DelegationBroker:
    """Broker for synthetic delegated work with epoch-based revocation."""
    def __init__(self, state: DelegationState, monitor=None):
        self.state = state
        self.monitor = monitor or AlwaysApproveMonitor()

    @atomic_transition
    def submit_job(self, actor, scope_id, effect):
        scope = self.state.scopes.get(scope_id)
        if not scope:
            r = self.state.ledger.append(kind="decision", actor=actor, action="submit_job",
                outcome="reject", state_version=self.state.state_version, details={"reason": "unknown scope"})
            return Decision(False, "reject", "unknown scope", r)
        if not scope.active:
            r = self.state.ledger.append(kind="decision", actor=actor, action="submit_job",
                outcome="reject", state_version=self.state.state_version,
                details={"scope_id": scope_id, "reason": "scope stopped"})
            return Decision(False, "reject", "scope stopped", r)
        mv = self.monitor.review({"scope_id": scope_id, "effect": effect}, {"epoch": scope.epoch})
        if mv.decision != "approve":
            r = self.state.ledger.append(kind="decision", actor=actor, action="submit_job",
                outcome=mv.decision, state_version=self.state.state_version, details={"reason": mv.reason})
            return Decision(False, mv.decision, mv.reason, r)
        jid = f"job-{len(self.state.jobs)+1}"
        self.state.jobs[jid] = Job(jid, scope_id, scope.epoch, effect)
        self.state.state_version += 1
        r = self.state.ledger.append(kind="decision", actor=actor, action="submit_job",
            outcome="queued", state_version=self.state.state_version,
            details={"job_id": jid, "scope_id": scope_id, "captured_epoch": scope.epoch, "effect": effect})
        return Decision(True, "queued", "job queued; authority rechecked at dispatch", r)

    @atomic_transition
    def scoped_stop(self, operator, scope_id):
        scope = self.state.scopes.get(scope_id)
        if not scope:
            r = self.state.ledger.append(kind="decision", actor=operator, action="scoped_stop",
                outcome="reject", state_version=self.state.state_version, details={"reason": "unknown scope"})
            return Decision(False, "reject", "unknown scope", r)
        scope.epoch += 1
        scope.active = False
        self.state.state_version += 1
        cancelled = []
        for job in self.state.jobs.values():
            if job.scope_id == scope_id and job.status == "queued":
                job.status = "cancelled"
                cancelled.append(job.job_id)
        r = self.state.ledger.append(kind="effect", actor=operator, action="scoped_stop",
            outcome="stopped", state_version=self.state.state_version,
            details={"scope_id": scope_id, "new_epoch": scope.epoch, "cancelled_jobs": sorted(cancelled)})
        return Decision(True, "stopped", "scope stopped; queued descendants invalidated", r)

    @atomic_transition
    def dispatch(self, scheduler, job_id):
        job = self.state.jobs.get(job_id)
        if not job:
            r = self.state.ledger.append(kind="decision", actor=scheduler, action="dispatch",
                outcome="reject", state_version=self.state.state_version, details={"reason": "unknown job"})
            return Decision(False, "reject", "unknown job", r)
        scope = self.state.scopes[job.scope_id]
        if job.status != "queued":
            r = self.state.ledger.append(kind="decision", actor=scheduler, action="dispatch",
                outcome="reject", state_version=self.state.state_version,
                details={"job_id": job_id, "reason": f"job status is {job.status}"})
            return Decision(False, "reject", f"job status is {job.status}", r)
        if (not scope.active) or job.captured_epoch != scope.epoch:
            job.status = "blocked"
            self.state.state_version += 1
            r = self.state.ledger.append(kind="decision", actor=scheduler, action="dispatch",
                outcome="reject", state_version=self.state.state_version,
                details={"job_id": job_id, "captured_epoch": job.captured_epoch,
                         "current_epoch": scope.epoch, "scope_active": scope.active,
                         "reason": "stale or revoked descendant authority"})
            return Decision(False, "reject", "stale or revoked descendant authority", r)
        self.state.state_version += 1
        job.status = "executed"
        effect = {"job_id": job_id, "scope_id": job.scope_id, "effect": job.effect,
                  "executed_epoch": scope.epoch, "executed_after_stop": not scope.active,
                  "state_version": self.state.state_version}
        self.state.effects.append(effect)
        r = self.state.ledger.append(kind="effect", actor=scheduler, action="dispatch",
            outcome="executed", state_version=self.state.state_version, details=effect)
        return Decision(True, "executed", "synthetic delegated effect executed", r)

def reference_state():
    return DelegationState(scopes={"task-root": Scope("task-root")})

def run_demo():
    # Benign twin: execution before stop.
    s1 = reference_state(); b1 = DelegationBroker(s1)
    q1 = b1.submit_job("agent", "task-root", "publish synthetic approved digest")
    benign = b1.dispatch("scheduler", q1.receipt.details["job_id"])
    b1.scoped_stop("operator", "task-root")

    # Adversarial ordering: queue -> stop -> dispatch attempt.
    s2 = reference_state(); b2 = DelegationBroker(s2)
    q2 = b2.submit_job("agent", "task-root", "perform synthetic consequential action")
    stop = b2.scoped_stop("operator", "task-root")
    post = b2.dispatch("scheduler", q2.receipt.details["job_id"])
    return {"benign_pre_stop_dispatch": benign.status, "stop_status": stop.status,
            "post_stop_dispatch": post.status, "post_stop_failure": s2.post_stop_failure(),
            "ledger_chain_valid": s1.ledger.verify_chain() and s2.ledger.verify_chain(),
            "jobs": {k: vars(v) for k,v in s2.jobs.items()}, "effects": s2.effects,
            "ledger": s2.ledger.to_list()}

class WeakDelegationBroker(DelegationBroker):
    """Deliberately weak comparator: stop marks parent inactive but leaves queued descendants executable."""
    @atomic_transition
    def scoped_stop(self, operator, scope_id):
        scope = self.state.scopes.get(scope_id)
        if not scope:
            return super().scoped_stop(operator, scope_id)
        scope.active = False
        self.state.state_version += 1
        r = self.state.ledger.append(kind="effect", actor=operator, action="scoped_stop",
            outcome="stopped-parent-only", state_version=self.state.state_version,
            details={"scope_id": scope_id, "new_epoch": scope.epoch, "cancelled_jobs": []})
        return Decision(True, "stopped-parent-only", "weak stop did not revoke descendants", r)

    @atomic_transition
    def dispatch(self, scheduler, job_id):
        job = self.state.jobs.get(job_id)
        if not job or job.status != "queued":
            return super().dispatch(scheduler, job_id)
        scope = self.state.scopes[job.scope_id]
        self.state.state_version += 1
        job.status = "executed"
        effect = {"job_id": job_id, "scope_id": job.scope_id, "effect": job.effect,
                  "executed_epoch": scope.epoch, "executed_after_stop": not scope.active,
                  "state_version": self.state.state_version}
        self.state.effects.append(effect)
        r = self.state.ledger.append(kind="effect", actor=scheduler, action="dispatch",
            outcome="executed", state_version=self.state.state_version, details=effect)
        return Decision(True, "executed", "weak scheduler executed queued descendant without revalidation", r)
