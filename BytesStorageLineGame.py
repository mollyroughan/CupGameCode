from functools import lru_cache
from time import perf_counter


def canon(state):
    """
    Canonical representative under reflection symmetry for a path graph.

    Since the path graph looks the same from left-to-right and right-to-left,
    a state and its reverse have the same win/loss value.

    bytes objects compare lexicographically, so min(state, state[::-1])
    gives a consistent representative.
    """
    rev = state[::-1]
    return min(state, rev)


def moves(state):
    """
    Generate all legal moves for the path graph.

    state is stored as a bytes object.
    state[i] is the size of the stack at position i.
    A stack of size k at i may move exactly k spaces left or right,
    provided it lands on a nonempty stack.
    """
    n = len(state)

    for i, k in enumerate(state):
        if k == 0:
            continue

        for d in (-k, k):
            j = i + d

            if 0 <= j < n and state[j] > 0:
                new = bytearray(state)
                new[i] = 0
                new[j] += k
                yield canon(bytes(new))


def make_solver():
    """
    Creates a fresh cached solver.

    This makes it easy to clear all memory between different values of n.
    """

    @lru_cache(maxsize=None)
    def winning(state):
        """
        Returns True if the player to move can force a win from this state.
        """
        return any(not winning(nxt) for nxt in moves(state))

    return winning


def first_wins(n, show_stats=True):
    """
    Returns True if Player 1 wins from the starting state with n cups.

    Starting state:
        (1, 1, ..., 1)

    Stored as:
        bytes([1, 1, ..., 1])
    """
    winning = make_solver()

    start = canon(bytes([1] * n))

    t0 = perf_counter()
    result = winning(start)
    t1 = perf_counter()

    if show_stats:
        info = winning.cache_info()
        print(f"n = {n}")
        print("Result:", "First wins" if result else "Second wins")
        print(f"Time: {t1 - t0:.3f} seconds")
        print(f"States cached: {info.currsize}")
        print(f"Cache hits: {info.hits}")
        print(f"Cache misses: {info.misses}")
        print()

    return result


def state_to_tuple(state):
    """
    Converts a bytes state back into a tuple for readable printing.

    Example:
        bytes([1, 1, 0, 2]) -> (1, 1, 0, 2)
    """
    return tuple(state)


def winning_first_moves(n):
    """
    Returns all winning first moves for Player 1, if any.

    A first move is winning if it sends Player 2 to a losing state.
    """
    winning = make_solver()

    start = canon(bytes([1] * n))

    good_moves = []

    for nxt in moves(start):
        if not winning(nxt):
            good_moves.append(nxt)

    return good_moves


if __name__ == "__main__":
    n = 18
    first_wins(n, show_stats=True)

    # Optional: print winning first moves for a specific n.
    # Change this value if desired.
    # n = 17
    moves_for_n = winning_first_moves(n)

    print("=" * 60)
    print(f"Winning first moves for n = {n}: {len(moves_for_n)}")

    for state in moves_for_n:
        print(state_to_tuple(state))