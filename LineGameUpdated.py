# AI Generated

from functools import lru_cache

def solve_upto(N, bits=6):
    """
    Returns a list win[n] for n=0..N where win[n]=True iff first player wins
    from the all-ones start on n nodes.
    Uses bitpacked state, reflection canonicalization, and memoized DFS.
    """
    mask = (1 << bits) - 1

    def get_cell(state, i):
        return (state >> (i * bits)) & mask

    def set_cell(state, i, val):
        shift = i * bits
        state &= ~(mask << shift)
        state |= (val & mask) << shift
        return state

    def pack_all_ones(n):
        s = 0
        for i in range(n):
            s |= 1 << (i * bits)
        return s

    def reflect(state, n):
        # Reverse the cells
        r = 0
        for i in range(n):
            v = get_cell(state, i)
            r = set_cell(r, n - 1 - i, v)
        return r

    def canon(state, n):
        r = reflect(state, n)
        return state if state <= r else r

    # Precompute all states are length-specific, so cache per n by nesting
    win = [False] * (N + 1)

    for n in range(1, N + 1):
        start = canon(pack_all_ones(n), n)

        @lru_cache(None)
        def winning(state):
            # Generate moves without allocating lists/tuples
            for i in range(n):
                k = get_cell(state, i)
                if k == 0:
                    continue

                # Try left and right by exactly k
                j = i - k
                if j >= 0:
                    dest = get_cell(state, j)
                    if dest != 0:
                        new_state = state
                        new_state = set_cell(new_state, i, 0)
                        new_state = set_cell(new_state, j, dest + k)
                        if not winning(canon(new_state, n)):
                            return True

                j = i + k
                if j < n:
                    dest = get_cell(state, j)
                    if dest != 0:
                        new_state = state
                        new_state = set_cell(new_state, i, 0)
                        new_state = set_cell(new_state, j, dest + k)
                        if not winning(canon(new_state, n)):
                            return True

            return False  # no winning move => losing position

        win[n] = winning(start)

        # Optional: print progress
        # print(n, "W" if win[n] else "L", "cache:", winning.cache_info().currsize)

    return win

if __name__ == "__main__":
    N = 35
    win = solve_upto(N, bits=6)
    for n in range(1, N + 1):
        print(n, "First" if win[n] else "Second")



