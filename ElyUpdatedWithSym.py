```python
from functools import lru_cache

def canon(state):
    """Canonicalize by reflection symmetry (left-right flip)."""
    r = state[::-1]
    return state if state <= r else r

def all_moves(state):
    """Generate next states, already canonicalized (reflection)."""
    n = len(state)
    out = []
    for i, k in enumerate(state):
        if k == 0:
            continue
        for j in (i - k, i + k):
            if 0 <= j < n and state[j] > 0:
                ns = list(state)
                ns[i] = 0
                ns[j] += k
                out.append(canon(tuple(ns)))
    return out

@lru_cache(None)
def winning(state):
    """
    True iff the player to move has a winning move from 'state'.
    NOTE: 'state' is assumed canonicalized at entry (we canonicalize anyway).
    """
    state = canon(state)
    for nxt in all_moves(state):
        if not winning(nxt):
            return True
    return False  # no move to a losing state => losing state

def winner_for_n(n):
    start = canon((1,) * n)
    return 1 if winning(start) else 2

if __name__ == "__main__":
    for n in range(1, 25):
        print(n, winner_for_n(n))
```
