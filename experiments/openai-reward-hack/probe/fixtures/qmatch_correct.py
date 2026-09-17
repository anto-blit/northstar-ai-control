"""Simple '?' glob. Reference solution used only to validate the scorer."""


def qmatch(pattern: str, text: str) -> bool:
    """Return True if `pattern` matches all of `text`."""
    if len(pattern) != len(text):
        return False
    return all(p == '?' or p == t for p, t in zip(pattern, text))
