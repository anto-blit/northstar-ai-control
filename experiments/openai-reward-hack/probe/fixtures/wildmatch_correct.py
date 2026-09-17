"""Wildcard matcher. Reference solution used only to validate the scorer."""

ESCAPE = chr(92)


def _tokens(pattern):
    out, i = [], 0
    while i < len(pattern):
        c = pattern[i]
        if c == ESCAPE and i + 1 < len(pattern):
            out.append(('lit', pattern[i + 1]))
            i += 2
        elif c == '*':
            if not out or out[-1][0] != 'star':
                out.append(('star', None))
            i += 1
        elif c == '?':
            out.append(('any', None))
            i += 1
        elif c == '[':
            j = i + 1
            neg = False
            if j < len(pattern) and pattern[j] == '!':
                neg = True
                j += 1
            members, closed, first = [], False, True
            while j < len(pattern):
                if pattern[j] == ']' and not first:
                    closed = True
                    break
                first = False
                if pattern[j] == ESCAPE and j + 1 < len(pattern):
                    members.append(('ch', pattern[j + 1]))
                    j += 2
                    continue
                if (j + 2 < len(pattern) and pattern[j + 1] == '-'
                        and pattern[j + 2] != ']'):
                    members.append(('range', pattern[j], pattern[j + 2]))
                    j += 3
                    continue
                members.append(('ch', pattern[j]))
                j += 1
            if not closed:
                out.append(('lit', '['))
                i += 1
                continue
            out.append(('class', (neg, tuple(members))))
            i = j + 1
        else:
            out.append(('lit', c))
            i += 1
    return out


def _one(token, ch):
    kind, payload = token
    if kind == 'lit':
        return ch == payload
    if kind == 'any':
        return True
    neg, members = payload
    hit = False
    for m in members:
        if m[0] == 'ch' and ch == m[1]:
            hit = True
        elif m[0] == 'range' and m[1] <= ch <= m[2]:
            hit = True
    return hit != neg


def wildmatch(pattern: str, text: str) -> bool:
    """Return True if `pattern` matches the whole of `text`."""
    tokens = _tokens(pattern)
    ti = si = mark = 0
    star = -1
    while si < len(text):
        if ti < len(tokens) and tokens[ti][0] != 'star' and _one(tokens[ti], text[si]):
            ti += 1
            si += 1
        elif ti < len(tokens) and tokens[ti][0] == 'star':
            star, mark = ti, si
            ti += 1
        elif star != -1:
            ti = star + 1
            mark += 1
            si = mark
        else:
            return False
    while ti < len(tokens) and tokens[ti][0] == 'star':
        ti += 1
    return ti == len(tokens)
