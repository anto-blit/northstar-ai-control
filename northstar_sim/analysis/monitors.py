"""An imperfect monitor, so the monitor axis can be varied instead of stubbed.

Relative to a content predicate, ``core.AlwaysApproveMonitor`` has a 100%
false-negative rate and no false positives. It does not vary review quality.
Later revocation is a separate event: a legitimate approval before stop need
not have been a monitor error.

``ImperfectMonitor`` is a simulated detector over a declared ground-truth
predicate. It is not a learned model and carries no claim about the error rate
of any real monitor. Rates are inputs to a sensitivity analysis, not estimates.

Draws come from an explicitly seeded ``random.Random`` so a sweep is
reproducible and its seed is recorded alongside the result.
"""
import random

from ..core import MonitorVerdict


class ImperfectMonitor:
    """Approve/reject with declared error rates against ``should_reject``.

    ``should_reject(proposal, context)`` states what a perfect monitor would do.
    A false negative approves a proposal that should be rejected; a false
    positive rejects one that should be approved. Rates of 0.0 give a perfect
    monitor; ``false_negative_rate=1.0`` reproduces ``AlwaysApproveMonitor`` on
    the proposals the predicate flags.
    """

    def __init__(self, should_reject, false_negative_rate=0.0,
                 false_positive_rate=0.0, seed=0):
        for rate in (false_negative_rate, false_positive_rate):
            if type(rate) not in (int, float) or not 0.0 <= rate <= 1.0:
                raise ValueError("monitor error rates must lie in [0, 1]")
        self.should_reject = should_reject
        self.false_negative_rate = false_negative_rate
        self.false_positive_rate = false_positive_rate
        self.rng = random.Random(seed)
        self.reviews = 0

    def review(self, proposal, context):
        self.reviews += 1
        truth_rejects = bool(self.should_reject(proposal, context))
        draw = self.rng.random()
        if truth_rejects:
            if draw < self.false_negative_rate:
                return MonitorVerdict("approve", "monitor false negative")
            return MonitorVerdict("reject", "monitor rejected a prohibited proposal")
        if draw < self.false_positive_rate:
            return MonitorVerdict("reject", "monitor false positive")
        return MonitorVerdict("approve", "monitor approved a legitimate proposal")


def release_predicate(state):
    """Perfect release detector: protected artifact reaching an unapproved sink."""
    def should_reject(proposal, _context):
        artifact = state.artifacts.get(proposal["artifact_id"])
        destination = state.destinations.get(proposal["destination_id"])
        if artifact is None or destination is None:
            return True
        return (artifact.classification == "protected"
                and destination.scope == "external_unapproved")
    return should_reject


def delegation_predicate(forbidden_effects):
    """Perfect delegation detector: a job effect named as forbidden."""
    forbidden = frozenset(forbidden_effects)

    def should_reject(proposal, _context):
        return proposal["effect"] in forbidden
    return should_reject
