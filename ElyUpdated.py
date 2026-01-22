from functools import lru_cache

def all_moves(state):
    state = list(state)
    n = len(state)
    out = []
    for i, k in enumerate(state):
        if k == 0:
            continue
        for j in (i - k, i + k):
            if 0 <= j < n and state[j] > 0:
                ns = state.copy()
                ns[i] = 0
                ns[j] += k
                out.append(tuple(ns))
    return out

def canon(state):
    r = tuple(reversed(state))
    return min(state, r)  # reflection symmetry

@lru_cache(None)
def winning(state):
    state = canon(state)
    for nxt in all_moves(state):
        if not winning(canon(nxt)):
            return True
    return False  # no moves to losing => losing

def winner_for_n(n):
    start = tuple([1] * n)
    return 1 if winning(canon(start)) else 2

for n in range(1, 25):
    print(n, winner_for_n(n))
