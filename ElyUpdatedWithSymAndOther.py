from functools import lru_cache

BITS = 6                # supports stack sizes 0..63 (enough for n<=63)
MASK = (1 << BITS) - 1

def pack_all_ones(n: int) -> int:
    s = 0
    for i in range(n):
        s |= 1 << (i * BITS)
    return s

def get_cell(state: int, i: int) -> int:
    return (state >> (i * BITS)) & MASK

def set_cell(state: int, i: int, val: int) -> int:
    shift = i * BITS
    state &= ~(MASK << shift)
    state |= (val & MASK) << shift
    return state

def reflect(state: int, n: int) -> int:
    r = 0
    for i in range(n):
        v = get_cell(state, i)
        r = set_cell(r, n - 1 - i, v)
    return r

def canon(state: int, n: int) -> int:
    r = reflect(state, n)
    return state if state <= r else r

def solve_upto(N: int):
    results = {}

    for n in range(1, N + 1):
        start = canon(pack_all_ones(n), n)

        @lru_cache(None)
        def winning(state: int) -> bool:
            state = canon(state, n)

            # Gather candidate moves with a heuristic score, but without building huge objects.
            # Score: larger resulting destination stack first (more constraining).
            candidates = []

            for i in range(n):
                k = get_cell(state, i)
                if k == 0:
                    continue

                # left
                j = i - k
                if j >= 0:
                    dest = get_cell(state, j)
                    if dest != 0:
                        candidates.append((-(dest + k), i, j, k))

                # right
                j = i + k
                if j < n:
                    dest = get_cell(state, j)
                    if dest != 0:
                        candidates.append((-(dest + k), i, j, k))

            # No moves => losing
            if not candidates:
                return False

            candidates.sort()

            for _, i, j, k in candidates:
                dest = get_cell(state, j)
                ns = state
                ns = set_cell(ns, i, 0)
                ns = set_cell(ns, j, dest + k)
                ns = canon(ns, n)
                if not winning(ns):
                    return True

            return False

        results[n] = 1 if winning(start) else 2
        print(n, results[n])

    return results

if __name__ == "__main__":
    solve_upto(20)
