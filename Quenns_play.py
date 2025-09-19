"""
Queens-like puzzle prototype using pygame.

Rules implemented:
- Each row, column, and colored region must contain exactly one crown (queen).
- No two crowns can be adjacent (including diagonals).
- Solver to count solutions and verify uniqueness.

Controls:
- Left click: toggle crown on a cell (place if empty, remove if has crown).
- Right click: remove crown from a cell.
- C: Check current board; runs solver and reports whether the current board is the unique solution.
- U: Count number of solutions (may take longer on larger boards).</n- S: Auto-solve (fill board with the unique solution if there is exactly one).
- R: Reset board (clear all crowns).
- H: Show a single hint (place one correct crown from the solution temporarily).
- Esc or close window: quit.

Notes:
- A sample 7x7 puzzle (regions) is embedded. You can add or replace puzzles by changing the `REGIONS` matrix and `WIDTH`/`HEIGHT`.
- The solver enforces the rules exactly as described and will count all possible solutions using backtracking.

Dependencies:
- pygame

Run:
python3 queens_pygame_prototype.py

"""

import pygame
import sys
from collections import defaultdict
from copy import deepcopy
import time

# ---------- Puzzle definition (example) ----------
# GRID: width x height

CELL_SIZE = 70
MARGIN = 50

# Regions: an HEIGHT list of WIDTH integers representing region ids.
# This is a sample puzzle. Each region id groups cells that must contain exactly one crown.
# You can modify this to design other puzzles.
# REGIONS = [
#     [0,0,1,1,2,2,2],
#     [0,3,3,1,4,4,2],
#     [5,3,6,6,4,7,7],
#     [5,5,6,8,8,7,9],
#     [10,5,11,8,12,12,9],
#     [10,11,11,11,12,13,9],
#     [10,10,14,14,14,13,13],
# ]

REGIONS = [[0,1,2,3,4],
           [0,1,2,3,4],
            [0,1,2,3,4],
            [0,1,2,3,4],
            [0,1,2,3,4]]

REGIONS = [[0,1,2,2,2,3,3],
 [0,1,4,4,2,5,3],
 [0,1,4,2,2,5,5],
 [0,1,1,2,2,2,2],
 [0,1,6,2,2,2,2],
 [0,1,6,2,2,2,2],
 [0,0,0,0,0,0,0]]

WIDTH = len(REGIONS)
HEIGHT = len(REGIONS)
REGION_COLORS = [
    (255, 99, 71),    # Tomato red
    (0, 191, 255),    # Deep sky blue
    (50, 205, 50),    # Lime green
    (255, 215, 0),    # Gold
    (255, 105, 180),  # Hot pink
    (138, 43, 226),   # Blue violet
    (255, 140, 0),    # Dark orange
    (0, 255, 127),    # Spring green
    (70, 130, 180),   # Steel blue
    (220, 20, 60),    # Crimson
    (0, 255, 255),    # Cyan
    (255, 0, 255),    # Magenta
    (0, 128, 128),    # Teal
    (255, 0, 0),      # Pure red
    (0, 0, 255),      # Pure blue
]



# ---------- Helper functions & Solver ----------

def in_bounds(x,y):
    return 0 <= x < WIDTH and 0 <= y < HEIGHT


def neighbors(x,y):
    """Return list of neighbor coordinates including diagonals."""
    for dx in (-1,0,1):
        for dy in (-1,0,1):
            if dx==0 and dy==0: 
                continue
            nx, ny = x+dx, y+dy
            if in_bounds(nx,ny):
                yield (nx,ny)


def initial_region_map(regions):
    """Return mapping region_id -> list of coords."""
    rmap = defaultdict(list)
    for y in range(HEIGHT):
        for x in range(WIDTH):
            rmap[regions[y][x]].append((x,y))
    return dict(rmap)

REGION_MAP = initial_region_map(REGIONS)
REGION_IDS = list(REGION_MAP.keys())


def is_valid_partial(board):
    """Check partial board validity: no two crowns adjacent and no row/col has >1 crowns and no region >1 crowns."""
    # board is dict (x,y)->1 for crown
    row_counts = defaultdict(int)
    col_counts = defaultdict(int)
    region_counts = defaultdict(int)
    for (x,y) in board:
        row_counts[y] += 1
        col_counts[x] += 1
        region_counts[REGIONS[y][x]] += 1
        # adjacency
        for nx,ny in neighbors(x,y):
            if (nx,ny) in board:
                return False
    # >1 in row/col/region invalid
    for v in row_counts.values():
        if v > 1: return False
    for v in col_counts.values():
        if v > 1: return False
    for v in region_counts.values():
        if v > 1: return False
    return True


def solver_count_and_one_solution(limit=None):
    """Count solutions and return one solution if found. Uses backtracking.
    limit: if provided, stop search after finding 'limit' solutions (for speed)
    Returns (count, one_solution_dict_or_None)
    """
    # We'll assign exactly one crown per region, so iterate region by region.
    regions = REGION_IDS

    solutions = 0
    one_solution = None

    # Precompute cells grouped by row/col/region to speed checks
    cell_coords = [(x,y) for y in range(HEIGHT) for x in range(WIDTH)]

    # To speed up, we'll keep track of taken rows/cols/regions and occupied set
    def backtrack(i, taken_rows, taken_cols, taken_regions, occupied):
        nonlocal solutions, one_solution
        if limit is not None and solutions >= limit:
            return
        if i == len(regions):
            # All regions assigned one crown each -> solution found if rows/cols count equal number of regions?
            # We must also ensure number of crowns == HEIGHT (since one per row needed). But puzzle sizes may differ.
            solutions += 1
            # sort occupied for consistency
            occupied = sorted(occupied, key=lambda x: x[0])
            if one_solution is None:
                one_solution = [occupied.copy()]
            else:
                one_solution.append(occupied.copy())
            return
        rid = regions[i]
        cells = REGION_MAP[rid]
        for (x,y) in cells:
            # check row/col free
            if y in taken_rows or x in taken_cols:
                continue
            # check adjacency free
            bad = False
            for nx,ny in neighbors(x,y):
                if (nx,ny) in occupied:
                    bad = True
                    break
            if bad: continue
            # place
            occupied.add((x,y))
            taken_rows.add(y); taken_cols.add(x); taken_regions.add(rid)
            backtrack(i+1, taken_rows, taken_cols, taken_regions, occupied)
            # undo
            occupied.remove((x,y))
            taken_rows.remove(y); taken_cols.remove(x); taken_regions.remove(rid)
            if limit is not None and solutions >= limit:
                return

    backtrack(0, set(), set(), set(), set())
    return solutions, one_solution


def check_user_solution(user_board):
    """Check if user_board is a complete and correct solution.
    Returns dict with keys: 'valid_complete' (bool), 'unique' (bool/None if not checked), 'solutions_count' (int)
    """
    # Quick check: ensure each region has exactly one, each row exactly one, each col exactly one, adjacency ok
    # counts
    row_counts = defaultdict(int)
    col_counts = defaultdict(int)
    region_counts = defaultdict(int)
    for y in range(HEIGHT):
        for x in range(WIDTH):
            if (x,y) in user_board:
                row_counts[y]+=1
                col_counts[x]+=1
                region_counts[REGIONS[y][x]] +=1
                # adjacency
                for nx,ny in neighbors(x,y):
                    if (nx,ny) in user_board:
                        return {'valid_complete':False, 'reason':'adjacent_crowns'}
    # each row
    for y in range(HEIGHT):
        if row_counts[y] != 1:
            return {'valid_complete':False, 'reason':f'row_{y}_count_{row_counts[y]}'}
    for x in range(WIDTH):
        if col_counts[x] != 1:
            return {'valid_complete':False, 'reason':f'col_{x}_count_{col_counts[x]}'}
    for rid in REGION_IDS:
        if region_counts[rid] != 1:
            return {'valid_complete':False, 'reason':f'region_{rid}_count_{region_counts[rid]}'}
    # It's a complete valid placement, now check uniqueness by running solver_count
    start = time.time()
    count, solution = solver_count_and_one_solution(limit=2)
    elapsed = time.time()-start
    return {'valid_complete':True, 'solutions_count':count, 'elapsed':elapsed, 'one_solution': solution[0] if solution else None}

# ---------- Pygame UI ----------

pygame.init()
FONT = pygame.font.SysFont(None, 36)
SMALL_FONT = pygame.font.SysFont(None, 22)
CROWN_FONT = pygame.font.SysFont(None, 48)

screen_w = WIDTH * CELL_SIZE + MARGIN*2
screen_h = HEIGHT * CELL_SIZE + MARGIN*2 + 60
screen = pygame.display.set_mode((screen_w, screen_h))
pygame.display.set_caption('Queens Puzzle Prototype')

clock = pygame.time.Clock()

# board state: set of (x,y) with crowns
board = set()

def draw_board(highlight_solution=None):
    screen.fill((230,230,230))
    # draw regions grid background
    for y in range(HEIGHT):
        for x in range(WIDTH):
            rid = REGIONS[y][x]
            color = REGION_COLORS[rid % len(REGION_COLORS)]
            rect = pygame.Rect(MARGIN + x*CELL_SIZE, MARGIN + y*CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, (120,120,120), rect, 1)
    # draw crowns
    for (x,y) in board:
        cx = MARGIN + x*CELL_SIZE + CELL_SIZE//2
        cy = MARGIN + y*CELL_SIZE + CELL_SIZE//2
        text = CROWN_FONT.render('\u265B', True, (10,10,10))
        tr = text.get_rect(center=(cx,cy))
        screen.blit(text, tr)
    # if highlight_solution provided, draw faint crowns for solution
    if highlight_solution:
        for (x,y) in highlight_solution:
            if (x,y) in board: continue
            cx = MARGIN + x*CELL_SIZE + CELL_SIZE//2
            cy = MARGIN + y*CELL_SIZE + CELL_SIZE//2
            s = CROWN_FONT.render('\u265B', True, (80,80,80))
            s.set_alpha(110)
            tr = s.get_rect(center=(cx,cy))
            screen.blit(s, tr)
    # draw UI text
    info = SMALL_FONT.render('Left click: toggle crown  |  Right click: remove  |  C: Check  U: Count sols  S: Solve  H: Hint  R: Reset', True, (20,20,20))
    screen.blit(info, (MARGIN, screen_h-45))

    pygame.display.flip()


def cell_at_pixel(px,py):
    if px < MARGIN or py < MARGIN: return None
    x = (px - MARGIN) // CELL_SIZE
    y = (py - MARGIN) // CELL_SIZE
    if in_bounds(x,y):
        return (x,y)
    return None

# For hint functionality, obtain unique solution if exists
_cached_solution = None
_cached_solution_time = 0

running = True
hint_active = None

while running:
    clock.tick(30)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_r:
                board.clear()
                hint_active = None
            elif event.key == pygame.K_c:
                res = check_user_solution(board)
                if not res.get('valid_complete'):
                    reason = res.get('reason')
                    print('Not a complete valid solution:', reason)
                else:
                    cnt = res.get('solutions_count')
                    elapsed = res.get('elapsed')
                    if cnt == 1:
                        print(f'Correct! Unique solution verified (solver time {elapsed:.2f}s).')
                    else:
                        print(f'Valid placement but solver found {cnt} solutions (solver time {elapsed:.2f}s).')
            elif event.key == pygame.K_u:
                print('Counting solutions (may take time)...')
                t0 = time.time()
                cnt, sol = solver_count_and_one_solution(limit=None)
                t1 = time.time()
                print(f'Found {cnt} solutions in {t1-t0:.2f}s')
            elif event.key == pygame.K_s:
                print('Solving...')
                cnt, sol = solver_count_and_one_solution(limit=10)
                if cnt >= 1 and sol is not None:                    
                    board = set(sol[0])
                    print(sol)
                    print(f'Board filled with solution. found {cnt} solutions.')
                else:
                    print(f'Cannot auto-solve: found {cnt} solutions.')
            elif event.key == pygame.K_h:
                # reveal a single hint from the unique solution
                cnt, sol = solver_count_and_one_solution(limit=2)
                if cnt == 1 and sol is not None:
                    # pick a not-yet-placed crown cell
                    for c in sol[0]:
                        if c not in board:
                            board.add(c)
                            hint_active = c
                            break
                    print('Placed one hint from solution.')
                else:
                    print('Hint unavailable: puzzle has no unique solution (or none found).')
        elif event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            cell = cell_at_pixel(*pos)
            if cell:
                if event.button == 1:  # left click -> toggle
                    if cell in board:
                        board.remove(cell)
                    else:
                        # attempt to place but only if not causing immediate adjacency or >1 row/col/region
                        temp = set(board)
                        temp.add(cell)
                        if is_valid_partial(temp):
                            board.add(cell)
                            hint_active = None
                        else:
                            print('Invalid placement (adjacency or duplicates).')
                elif event.button == 3:  # right click -> remove
                    if cell in board:
                        board.remove(cell)
    # draw
    draw_board(highlight_solution=None)

pygame.quit()
sys.exit()
