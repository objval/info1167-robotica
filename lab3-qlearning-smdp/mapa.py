ROWS = 6
COLS = 7
MAP_STR = [
    ". S S S S . .",
    ". S . . S . .",
    "S S S X S S S",
    ". . S . S . .",
    ". . S S S . .",
    ". . . M . . .",
]

def parse_map():
    grid = []
    for row_str in MAP_STR:
        grid.append(row_str.split())
    return grid

GRID = parse_map()

def get_states():
    states = []
    for r in range(ROWS):
        for c in range(COLS):
            if GRID[r][c] in ("S", "M"):
                states.append((r, c))
    return states

def get_goal():
    for r in range(ROWS):
        for c in range(COLS):
            if GRID[r][c] == "M":
                return (r, c)
    return None

ACTIONS = ["Norte", "Sur", "Este", "Oeste"]
ACTION_DELTAS = {
    "Norte": (-1, 0),
    "Sur": (1, 0),
    "Este": (0, 1),
    "Oeste": (0, -1),
}
LATERAL_ACTIONS = {
    "Norte": ["Este", "Oeste"],
    "Sur": ["Este", "Oeste"],
    "Este": ["Norte", "Sur"],
    "Oeste": ["Norte", "Sur"],
}
import random as _rnd

def get_random_start():
    non_goal = [s for s in get_states() if s != get_goal()]
    return _rnd.choice(non_goal)

START = (0, 1)

def is_valid(r, c):
    if r < 0 or r >= ROWS or c < 0 or c >= COLS:
        return False
    return GRID[r][c] in ("S", "M")

def move(state, action):
    r, c = state
    dr, dc = ACTION_DELTAS[action]
    nr, nc = r + dr, c + dc
    if is_valid(nr, nc):
        return (nr, nc)
    return state

def get_neighbors(state):
    r, c = state
    neighbors = []
    for action in ACTIONS:
        nr, nc = move(state, action)
        if (nr, nc) != (r, c):
            neighbors.append((nr, nc))
    return neighbors

def print_grid():
    print("\nMapa del Robot:")
    print("  " + " ".join(str(c) for c in range(COLS)))
    for r in range(ROWS):
        print(f"{r} " + " ".join(GRID[r]))
    print()

if __name__ == "__main__":
    print_grid()
    states = get_states()
    goal = get_goal()
    print(f"Estados transitables: {len(states)}")
    print(f"Meta: {goal}")
    print(f"Inicio: {START}")
