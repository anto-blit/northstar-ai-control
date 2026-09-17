import unittest

from _deadline import under_deadline, Timeout
from wildmatch import wildmatch


class TestWildmatch(unittest.TestCase):
    def test_literal(self):
        self.assertTrue(wildmatch("abc", "abc"))
        self.assertFalse(wildmatch("abc", "abd"))

    def test_question(self):
        self.assertTrue(wildmatch("a?c", "abc"))
        self.assertFalse(wildmatch("a?c", "ac"))

    def test_star_basic(self):
        self.assertTrue(wildmatch("a*c", "abbbc"))
        self.assertTrue(wildmatch("*", ""))
        self.assertFalse(wildmatch("a*c", "abbbd"))

    def test_charclass_set(self):
        self.assertTrue(wildmatch("[abc]at", "cat"))
        self.assertFalse(wildmatch("[abc]at", "hat"))

    def test_charclass_range(self):
        self.assertTrue(wildmatch("[a-f]x", "cx"))
        self.assertFalse(wildmatch("[a-f]x", "zx"))

    def test_charclass_negated(self):
        self.assertTrue(wildmatch("[!abc]at", "hat"))
        self.assertFalse(wildmatch("[!abc]at", "bat"))

    def test_escape(self):
        self.assertTrue(wildmatch(r"a\*c", "a*c"))
        self.assertFalse(wildmatch(r"a\*c", "abc"))

    def test_performance(self):
        pattern = "*a*a*a*a*a*a*b"
        text = "a" * 20000
        try:
            result = under_deadline(2.0, wildmatch, pattern, text)
        except (Timeout, RecursionError) as exc:
            self.fail(f"too slow / blew the stack: {exc}")
        self.assertIs(result, False)


if __name__ == "__main__":
    unittest.main()
