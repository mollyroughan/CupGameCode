from functools import lru_cache

def canon(state):
    # Treat state and any rotation as identical, pick smallest

    n = len(state)
    if n == 0:
        return state
    best = state
    s = state
    for shift in range(1, n):
        rot = s[shift:] + s[:shift]
        if rot < best:
            best = rot
    return best

def moves_cycle(state):
    # Generate all legal moves
    n = len(state)
    for i, k in enumerate(state):
        if k == 0:
            continue

        # If k is a multiple of n, moving k lands back on i (not a move)
        r = k % n
        if r == 0:
            continue

        # Move rightwards around the cycle by exactly k
        j = (i + r) % n

        if state[j] == 0:
            continue  # must land on nonempty

        new = list(state)
        new[i] = 0
        new[j] += k
        yield canon(tuple(new))  # normalize by rotation

@lru_cache(None)
def winning(state):

    # True iff the player to move has a winning strategy from this state.

    state = canon(state)
    return any(not winning(nxt) for nxt in moves_cycle(state))

def first_wins(n):
    return winning(canon((1,) * n))

if __name__ == "__main__":
    for n in range(29, 30):
        print(n, "First wins" if first_wins(n) else "Second wins")