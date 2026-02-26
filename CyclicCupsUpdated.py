from functools import lru_cache

# ----------------------------
# Canonicalization (symmetry)
# ----------------------------

def canon_rotation(state):
    """Return lexicographically smallest rotation of state."""
    n = len(state)
    best = state
    for s in range(1, n):
        rot = state[s:] + state[:s]
        if rot < best:
            best = rot
    return best

def canon_dihedral(state):
    """Return smallest among rotations of state and its reverse."""
    r1 = canon_rotation(state)
    r2 = canon_rotation(state[::-1])
    return r1 if r1 < r2 else r2

# Choose symmetry:
CANON = canon_rotation          # use only rotation equivalence
# CANON = canon_dihedral        # uncomment to also quotient by reflection

# ----------------------------
# Move generator (cycle rules)
# ----------------------------

def moves_cycle_canon(state):
    """
    Generate next positions from a canonical state on an n-cycle.

    Rules:
    - pick a nonempty node i with stack size k
    - move exactly k steps clockwise or counterclockwise (wrap-around)
    - must land on a nonempty node
    - within a move, cannot repeat nodes:
      on an n-cycle this only forbids k == n (a length-n walk must repeat a node)
    """
    n = len(state)
    for i, k in enumerate(state):
        if k == 0:
            continue
        if k == n:
            continue  # would require repeating a node in a length-n move

        j1 = (i + k) % n
        j2 = (i - k) % n

        for j in {j1, j2}:          # avoid duplicates when j1 == j2
            if j == i:
                continue            # shouldn't happen unless k==0 mod n, but safe
            if state[j] == 0:
                continue            # must land on nonempty
            new = list(state)
            new[i] = 0
            new[j] += k
            yield CANON(tuple(new)) # keep all states canonical for caching

# ----------------------------
# Winning recursion (memoized)
# ----------------------------

@lru_cache(None)
def winning_canon(state):
    """
    state MUST be canonical (under CANON).
    True iff the player to move can force a win.
    """
    for nxt in moves_cycle_canon(state):
        if not winning_canon(nxt):
            return True
    return False

def first_wins(n):
    start = CANON((1,) * n)
    return winning_canon(start)

if __name__ == "__main__":
    for n in range(1, 31):
        print(n, "First wins" if first_wins(n) else "Second wins")