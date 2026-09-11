import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location("g3c_test", Path(__file__).with_name("run.py"))
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)


def quota():
    return dict(is_error=True, returncode=1, modelUsage={}, result="You've hit your session limit; resets later")


def answer(text):
    return dict(is_error=False, returncode=0, modelUsage={"claude-sonnet-5": {}}, result=text)


class ContinuationTests(unittest.TestCase):
    def test_quota_rejection_can_be_followed_by_first_model_answer(self):
        result = answer('{"decision":"PROCEED","reason":"short"}')
        self.assertIs(runner.choose(quota(), [quota(), result]), result)

    def test_wrong_or_invalid_model_answers_cannot_be_retried(self):
        for result in (answer('{"decision":"PROCEED","reason":"The cap is exceeded."}'), answer("invalid JSON")):
            self.assertIs(runner.choose(result, []), result)
            with self.assertRaisesRegex(ValueError, "cannot be replaced"):
                runner.choose(result, [answer("replacement")])

    def test_only_confirmed_service_quota_messages_are_eligible(self):
        self.assertTrue(runner.quota_only(quota()))
        self.assertFalse(runner.quota_only(answer("You've hit your session limit")))
        self.assertFalse(runner.quota_only(dict(quota(), modelUsage={"claude-sonnet-5": {}})))
        self.assertFalse(runner.quota_only(dict(quota(), returncode=None)))
        self.assertFalse(runner.quota_only(dict(quota(), result="timeout")))

    def test_second_success_cannot_replace_first_continuation_answer(self):
        with self.assertRaisesRegex(ValueError, "cannot be replaced"):
            runner.choose(None, [quota(), answer("first"), answer("second")])

    def test_unknown_failure_is_terminal_and_stays_in_record(self):
        failure = dict(is_error=True, returncode=None, result="", error="timeout")
        self.assertIs(runner.choose(None, [failure]), failure)
        with self.assertRaisesRegex(ValueError, "cannot be replaced"):
            runner.choose(None, [failure, answer("later")])

    def test_actual_original_inventory_retains_every_model_answer(self):
        report = runner.g3.verify(emit=False)
        self.assertEqual(sum(r["operational"] for r in report["observations"]), 27)
        records = [runner.read(p) for p in sorted((runner.OLD / "responses").glob("*.json"))]
        self.assertEqual(sum(runner.quota_only(r) for r in records), 9)
        self.assertEqual(sum(runner.choose(r, []) is not None for r in records), 27)


if __name__ == "__main__":
    unittest.main()
