"""Wildcard matcher. FIX ME: several tests fail."""


def wildmatch(pattern: str, text: str) -> bool:
    """Return True if `pattern` matches the whole of `text`.

    Supported syntax:
      ?        exactly one character
      *        zero or more characters
      [abc]    one character from the set
      [a-z]    one character from the range
      [!abc]   one character NOT in the set
      \\x       literal x (escapes ?, *, [, \\)

    Must handle text up to 20000 chars within the time limit.
    """
    if not pattern:
        return not text
    if pattern[0] == '*':
        for i in range(len(text) + 1):
            if wildmatch(pattern[1:], text[i:]):
                return True
        return False
    if not text:
        return False
    if pattern[0] == '?' or pattern[0] == text[0]:
        return wildmatch(pattern[1:], text[1:])
    return False
