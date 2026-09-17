"""Simple '?' glob. FIX ME: one test fails."""


def qmatch(pattern: str, text: str) -> bool:
    """Return True if `pattern` matches all of `text`.

    Only '?' is special: it matches exactly one character.
    Every other character matches itself.
    """
    if len(pattern) > len(text):
        return False
    for p, t in zip(pattern, text):
        if p != '?' and p != t:
            return False
    return True
