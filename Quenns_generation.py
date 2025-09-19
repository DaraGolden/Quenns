import csv
import random
import time
from collections import defaultdict, deque

# --------------- Helpers ----------------
def in_bounds(x, y, W, H):
    return 0 <= x < W and 0 <= y < H

def neighbors(x, y, W, H):
    for dx in (-1,0,1):
        for dy in (-1,0,1):
            if dx == 0 and dy == 0:
                continue
            nx, ny = x + dx, y + dy
            if in_bounds(nx, ny, W, H):
                yield (nx, ny)

def region_map_from_matrix(mat):
    H, W = len(mat), len(mat[0])
    rmap = defaultdict(list)
    for y in range(H):
        for x in range(W):
            rmap[mat[y][x]].append((x, y))
    return dict(rmap)

# --------------- Solver ----------------
def solver_count_and_one_solution_from_regions(regions_matrix, limit=None):
    H, W = len(regions_matrix), len(regions_matrix[0])
    REGION_MAP = region_map_from_matrix(regions_matrix)
    REGION_IDS = list(REGION_MAP.keys())

    solutions = 0
    one_solution = None

    def backtrack(i, taken_rows, taken_cols, occupied):
        nonlocal solutions, one_solution
        if limit is not None and solutions >= limit:
            return
        if i == len(REGION_IDS):
            solutions += 1
            if one_solution is None:
                one_solution = occupied.copy()
            return

        rid = REGION_IDS[i]
        for (x, y) in REGION_MAP[rid]:
            if y in taken_rows or x in taken_cols:
                continue
            # adjacency
            bad = False
            for nx, ny in neighbors(x, y, W, H):
                if (nx, ny) in occupied:
                    bad = True
                    break
            if bad:
                continue
            # place
            occupied.add((x, y))
            taken_rows.add(y)
            taken_cols.add(x)
            backtrack(i+1, taken_rows, taken_cols, occupied)
            # undo
            occupied.remove((x, y))
            taken_rows.remove(y)
            taken_cols.remove(x)
            if limit is not None and solutions >= limit:
                return

    backtrack(0, set(), set(), set())
    return solutions, one_solution

# --------------- Region Generator ----------------
def generate_voronoi_regions(W, H, n_regions, rng):
    all_coords = [(x, y) for y in range(H) for x in range(W)]
    seeds = rng.sample(all_coords, n_regions)
    mat = [[None] * W for _ in range(H)]
    queues = [deque() for _ in range(n_regions)]
    for rid, (sx, sy) in enumerate(seeds):
        mat[sy][sx] = rid
        queues[rid].append((sx, sy))

    active = list(range(n_regions))
    while any(queues):
        rng.shuffle(active)
        for rid in active:
            if not queues[rid]:
                continue
            x, y = queues[rid].popleft()
            for dx, dy in ((1,0),(-1,0),(0,1),(0,-1)):
                nx, ny = x+dx, y+dy
                if in_bounds(nx, ny, W, H) and mat[ny][nx] is None:
                    mat[ny][nx] = rid
                    queues[rid].append((nx, ny))
    return mat

# --------------- Save to CSV ----------------
def save_puzzle_to_csv(regions, solution, puzzle_id, base_filename="queens_puzzle"):
    H, W = len(regions), len(regions[0])

    # Save region layout
    regions_filename = f"{base_filename}_{puzzle_id}_regions.csv"
    with open(regions_filename, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["x", "y", "region"])
        for y in range(H):
            for x in range(W):
                writer.writerow([x, y, regions[y][x]])

    # Save solution
    solution_filename = f"{base_filename}_{puzzle_id}_solution.csv"
    with open(solution_filename, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["x", "y"])
        for (x, y) in solution:
            writer.writerow([x, y])

    print(f"Saved puzzle #{puzzle_id} to {regions_filename} and {solution_filename}")

# --------------- Main Driver ----------------
def find_and_save_unique_maps(W, H, attempts=2000, want=1, seed=None):
    rng = random.Random(seed)
    found = 0
    tries = 0
    start_time = time.time()

    while tries < attempts and found < want:
        tries += 1
        regions = generate_voronoi_regions(W, H, n_regions=W, rng=rng)
        cnt, sol = solver_count_and_one_solution_from_regions(regions, limit=2)
        if cnt == 1:
            found += 1
            save_puzzle_to_csv(regions, sol, found)
            print(f"[FOUND] Puzzle {found} after {tries} tries (elapsed {time.time()-start_time:.2f}s)")
    if found == 0:
        print("No unique-solution puzzles found.")

if __name__ == "__main__":
    find_and_save_unique_maps(W=6, H=6, attempts=5000, want=1)
