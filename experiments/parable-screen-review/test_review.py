"""Meaningful cross-checks of exact probabilities and independent label parsing."""
import itertools
import math
import unittest

import review


class ReviewTests(unittest.TestCase):
    def test_binomial_matches_direct_small_enumeration(self):
        for n in range(1, 8):
            for p in (0.0, 0.1, 0.5, 1.0):
                pmf = review.binomial(n, p)
                direct = [math.comb(n, k) * p**k * (1-p)**(n-k) for k in range(n+1)]
                for expected, actual in zip(direct, pmf):
                    self.assertAlmostEqual(expected, actual, places=12)
                self.assertAlmostEqual(sum(pmf), 1.0, places=12)

    def test_exact_threshold_uses_discordant_pairs_and_multiplicity(self):
        self.assertEqual(review.winning_threshold(8, 9), 9)
        self.assertEqual(review.winning_threshold(9, 9), 9)
        self.assertEqual(review.exact_p(9, 0), 0.00390625)
        self.assertEqual(review.exact_p(0, 0), 1.0)
        self.assertEqual(review.paired_power(32, .1, .1, .1), 0.0)

    def test_paired_power_matches_enumerated_joint_outcomes(self):
        n, win, loss, tie = 6, .3, .1, .6
        brute = 0.0
        for sequence in itertools.product(range(3), repeat=n):
            w, l = sequence.count(0), sequence.count(1)
            if w > l and review.exact_p(w, l) <= .05:
                brute += win**w * loss**l * tie**sequence.count(2)
        self.assertAlmostEqual(review.paired_power(n, .4, .2, .1), brute, places=12)

    def test_perfect_story_power_is_binomial_tail(self):
        for n in (16, 32, 64):
            self.assertAlmostEqual(review.paired_power(n, .1, 0, 0, 9),
                                   review.binomial_tail(n, .1, 9), places=12)

    def test_rendered_labels_are_checked_without_trusting_numeric_fields(self):
        plan = review.read(review.PLAN)
        audit = review.audit_cases(plan)
        self.assertEqual(audit["unique_cases"], 92)
        self.assertEqual(audit["request_packets"], 428)
        plan["cases"]["screen"][0]["expected"] = "fabricated"
        with self.assertRaises(ValueError):
            review.audit_cases(plan)

    def test_credit_status_changes_answer_and_inclusive_cap_is_allowed(self):
        cases = review.read(review.PLAN)["cases"]["screen"]
        at_cap = next(c for c in cases if c["total"] == c["cap"])
        self.assertEqual(review.parse_case(at_cap["text"])["expected"], "PROCEED")
        changed = at_cap["text"].replace(
            f"An additional {at_cap['extra']}-token credit is guaranteed regardless of future attendance.",
            f"An additional {at_cap['extra']}-token credit applies only if a future attendance target is met. "
            "Attendance is uncertain and no one guarantees that credit.")
        self.assertEqual(review.parse_case(changed)["expected"], "WITHHOLD")

    def test_unrelated_failure_veto_is_reproduced_from_original_function(self):
        outcome = review.unrelated_invalid_demonstration(review.read(review.PLAN))
        self.assertEqual(outcome["before"], "keeper")
        self.assertIsNone(outcome["after"])

    def test_revision_contains_no_story_calls_and_preserves_prompt_bytes(self):
        original = review.read(review.PLAN)
        revised = review.revised_plan()
        self.assertEqual(len(revised["requests"]), 236)
        self.assertFalse(revised["live_registered"])
        self.assertEqual(revised["model_calls_authorized"], 0)
        lookup = {(r["case"], r["arm"]): r for r in original["requests"]}
        for request in revised["requests"]:
            self.assertFalse(request["arm"].startswith("S:"))
            for key in ("prompt", "prompt_sha256", "system", "system_sha256", "expected"):
                self.assertEqual(request[key], lookup[(request["case"], request["arm"])][key])
        for arm in ("R", "F:squirrel", "F:keeper", "F:seal"):
            slots = [r["index"] % 4 for r in revised["requests"] if r["arm"] == arm]
            self.assertEqual([slots.count(i) for i in range(4)], [12] * 4)


if __name__ == "__main__":
    unittest.main()
