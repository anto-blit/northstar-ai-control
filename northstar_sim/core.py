from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any
from copy import deepcopy
from functools import wraps
import hashlib, json


def atomic_transition(method):
    """Publish a complete in-memory transition only after its ledger write succeeds.

    The runner must serialize calls. This is copy-on-write for this synthetic
    state, not a disk transaction or rollback of external effects. Exceptions
    propagate to the runner; neither partial state nor partial receipts publish.
    References to nested state objects are snapshots, not live handles.
    """
    @wraps(method)
    def wrapped(self, *args, **kwargs):
        original = self.state
        candidate = deepcopy(original)
        self.state = candidate
        try:
            result = method(self, *args, **kwargs)
        finally:
            self.state = original
        original.__dict__ = candidate.__dict__
        return result
    return wrapped

@dataclass(frozen=True)
class Receipt:
    seq: int
    kind: str
    actor: str
    action: str
    outcome: str
    state_version: int
    details: Dict[str, Any]
    prior_hash: str
    receipt_hash: str

def canonical_json(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True)

def _hash(payload: Dict[str, Any]) -> str:
    return hashlib.sha256(canonical_json(payload).encode()).hexdigest()

@dataclass
class Ledger:
    receipts: List[Receipt] = field(default_factory=list)
    @property
    def tip(self): return self.receipts[-1].receipt_hash if self.receipts else "GENESIS"
    def append(self, *, kind, actor, action, outcome, state_version, details):
        payload = {"seq": len(self.receipts)+1, "kind": kind, "actor": actor,
                   "action": action, "outcome": outcome, "state_version": state_version,
                   "details": deepcopy(details), "prior_hash": self.tip}
        r = Receipt(receipt_hash=_hash(payload), **payload)
        self.receipts.append(r)
        return r
    def verify_chain(self):
        prior = "GENESIS"
        for seq, r in enumerate(self.receipts, start=1):
            payload = {"seq": r.seq, "kind": r.kind, "actor": r.actor,
                       "action": r.action, "outcome": r.outcome,
                       "state_version": r.state_version, "details": r.details,
                       "prior_hash": prior}
            if r.seq != seq or r.prior_hash != prior or _hash(payload) != r.receipt_hash:
                return False
            prior = r.receipt_hash
        return True
    def to_list(self): return [asdict(r) for r in self.receipts]

@dataclass
class MonitorVerdict:
    decision: str
    reason: str

class AlwaysApproveMonitor:
    def review(self, proposal, context):
        return MonitorVerdict("approve", "forced-approve test monitor")

@dataclass
class Decision:
    allowed: bool
    status: str
    reason: str
    receipt: Optional[Receipt] = None
