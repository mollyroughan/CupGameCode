from functools import lru_cache

def moves(state):
    n = len(state)
    for i, k in enumerate(state):
        if k == 0:
            continue
        for d in (-k, k):          # left or right by exactly k
            j = i + d
            if 0 <= j < n and state[j] > 0:   # must land on nonempty
                new = list(state)
                new[i] = 0
                new[j] += k
                yield tuple(new)

@lru_cache(None)
def winning(state):
    # True if player to move can force a win
    return any(not winning(nxt) for nxt in moves(state))

def first_wins(n):
    return winning((1,) * n)

if __name__ == "__main__":
    for n in range(1, 21):
        print(n, "First wins" if first_wins(n) else "Second wins")
