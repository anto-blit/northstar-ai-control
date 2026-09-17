import unittest

from qmatch import qmatch


class TestQmatch(unittest.TestCase):
    def test_literal(self):
        self.assertTrue(qmatch("abc", "abc"))
        self.assertFalse(qmatch("abc", "abd"))

    def test_question(self):
        self.assertTrue(qmatch("a?c", "abc"))
        self.assertTrue(qmatch("???", "xyz"))

    def test_length_must_match(self):
        self.assertFalse(qmatch("ab", "abc"))
        self.assertFalse(qmatch("abc", "ab"))

    def test_empty(self):
        self.assertTrue(qmatch("", ""))
        self.assertFalse(qmatch("", "a"))


if __name__ == "__main__":
    unittest.main()
