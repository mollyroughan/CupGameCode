from functools import lru_cache

def moves(state):
    n = len(state)
    for i, k in enumerate(state):
        if k == 0:
            continue
        for d in (-k, k):
            j = i + d
            if 0 <= j < n and state[j] > 0:
                new = list(state)
                new[i] = 0
                new[j] += k
                yield tuple(new)

@lru_cache(None)
def winning(state):
    return any(not winning(nxt) for nxt in moves(state))

def iter_strategy_paths(n, max_paths=None):
    """
    Generate all paths where the player who can force a win
    (P1 if start winning, otherwise P2) plays optimally.
    """
    start = (1,) * n

    strategy_player = 1 if winning(start) else 2

    yielded = 0

    def dfs(path, depth):
        nonlocal yielded
        if max_paths is not None and yielded >= max_paths:
            return

        s = path[-1]
        children = list(moves(s))

        if not children:
            yielded += 1
            yield list(path)
            return

        current_player = 1 if depth % 2 == 0 else 2

        if current_player == strategy_player:
            # Only follow winning moves
            children = [t for t in children if not winning(t)]

        for t in children:
            path.append(t)
            yield from dfs(path, depth + 1)
            path.pop()

            if max_paths is not None and yielded >= max_paths:
                return

    yield from dfs([start], 0)

def write_strategy_paths(n, max_paths=None):
    start = (1,) * n
    strategy_player = 1 if winning(start) else 2

    filename = f"winning_paths_n{n}_P{strategy_player}.txt"

    with open(filename, "w") as f:
        f.write(f"n = {n}\n")
        f.write(f"Winning player: Player {strategy_player}\n")
        f.write("=" * 40 + "\n\n")

        for idx, path in enumerate(iter_strategy_paths(n, max_paths=max_paths), start=1):
            f.write(f"Path {idx} ({len(path)-1} moves):\n")
            for state in path:
                f.write(f"  {state}\n")
            f.write("\n")

    print(f"Wrote paths for Player {strategy_player} to {filename}")

if __name__ == "__main__":
    n = 9
    write_strategy_paths(n, max_paths=None)  # set None if you're brave