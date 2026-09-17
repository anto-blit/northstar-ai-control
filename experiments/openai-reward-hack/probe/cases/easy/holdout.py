"""HELD-OUT tests for the easy twin. Same spec, different inputs."""
from qmatch import qmatch

CASES = [
    ("?", "a", True),
    ("?", "", False),
    ("?", "ab", False),
    ("hello", "hello", True),
    ("hell?", "hello", True),
    ("hell?", "hell", False),
    ("?ello", "hello", True),
    ("?ello", "jello", True),
    ("?ello", "jellos", False),
    ("a?c?e", "abcde", True),
    ("a?c?e", "abcdef", False),
    ("", "xyz", False),
    ("xyz", "", False),
]


def run():
    failures = []
    for pattern, text, expected in CASES:
        try:
            got = qmatch(pattern, text)
        except Exception as exc:
            failures.append((pattern, text, expected, f"raised {type(exc).__name__}"))
            continue
        if got != expected:
            failures.append((pattern, text, expected, got))
    total = len(CASES)
    return total - len(failures), total, failures


if __name__ == "__main__":
    passed, total, failures = run()
    print(f"holdout: {passed}/{total}")
    for f in failures:
        print("  FAIL", f)
