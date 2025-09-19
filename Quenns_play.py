"""
Queens-like puzzle prototype using pygame.

Rules implemented:
- Each row, column, and colored region must contain exactly one crown (queen).
- No two crowns can be adjacent (including diagonals).
- Solver to count solutions and verify uniqueness.

Controls:
- Left click: cycle cell state (empty -> X -> queen -> empty).
- Right click: remove mark from a cell.
- C: Check current board; runs solver and reports whether the current board is the unique solution.
- U: Count number of solutions (may take longer on larger boards).
- S: Auto-solve (fill board with the unique solution if there is exactly one).
- R: Reset board (clear all crowns).
- H: Show a single hint (place one correct crown from the solution temporarily).
- Esc or close window: quit.
"""

import pygame
import sys
from collections import defaultdict
import time
import csv
from Quenns_generation import find_and_save_unique_maps

# ---------- Puzzle definition ----------
CELL_SIZE = 70
MARGIN = 50

WIDTH = 7
HEIGHT = 7

find_and_save_unique_maps(WIDTH, HEIGHT, attempts=5000, want=1)

"""Load puzzle grid back into nested list (like REGIONS)."""
with open('puzzle.csv', newline="") as f:
    reader = csv.reader(f)
    REGIONS = [[int(cell) for cell in row] for row in reader]

REGION_COLORS = [
    (255, 99, 71), (0, 191, 255), (50, 205, 50), (255, 215, 0),
    (255, 105, 180), (138, 43, 226), (255, 140, 0), (0, 255, 127),
    (70, 130, 180), (220, 20, 60), (0, 255, 255), (255, 0, 255),
    (0, 128, 128), (255, 0, 0), (0, 0, 255),
]

# ---------- Helper functions ----------
def in_bounds(x, y):
    return 0 <= x < WIDTH and 0 <= y < HEIGHT

def neighbors(x, y):
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            nx, ny = x + dx, y + dy
            if in_bounds(nx, ny):
                yield (nx, ny)

def initial_region_map(regions):
    rmap = defaultdict(list)
    for y in range(HEIGHT):
        for x in range(WIDTH):
            rmap[regions[y][x]].append((x, y))
    return dict(rmap)

REGION_MAP = initial_region_map(REGIONS)
REGION_IDS = list(REGION_MAP.keys())

def is_valid_partial(board):
    row_counts = defaultdict(int)
    col_counts = defaultdict(int)
    region_counts = defaultdict(int)
    for (x, y), state in board.items():
        if state != "Q":
            continue
        row_counts[y] += 1
        col_counts[x] += 1
        region_counts[REGIONS[y][x]] += 1
        for nx, ny in neighbors(x, y):
            if board.get((nx, ny)) == "Q":
                return False
    if any(v > 1 for v in row_counts.values()): return False
    if any(v > 1 for v in col_counts.values()): return False
    if any(v > 1 for v in region_counts.values()): return False
    return True

def solver_count_and_one_solution(limit=None):
    regions = REGION_IDS
    solutions = 0
    one_solution = None

    def backtrack(i, taken_rows, taken_cols, taken_regions, occupied):
        nonlocal solutions, one_solution
        if limit is not None and solutions >= limit:
            return
        if i == len(regions):
            solutions += 1
            occ = sorted(occupied, key=lambda x: x[0])
            if one_solution is None:
                one_solution = [occ.copy()]
            else:
                one_solution.append(occ.copy())
            return
        rid = regions[i]
        for (x, y) in REGION_MAP[rid]:
            if y in taken_rows or x in taken_cols:
                continue
            bad = False
            for nx, ny in neighbors(x, y):
                if (nx, ny) in occupied:
                    bad = True
                    break
            if bad: continue
            occupied.add((x, y))
            taken_rows.add(y); taken_cols.add(x); taken_regions.add(rid)
            backtrack(i+1, taken_rows, taken_cols, taken_regions, occupied)
            occupied.remove((x, y))
            taken_rows.remove(y); taken_cols.remove(x); taken_regions.remove(rid)
            if limit is not None and solutions >= limit:
                return

    backtrack(0, set(), set(), set(), set())
    return solutions, one_solution

def check_user_solution(user_board):
    row_counts = defaultdict(int)
    col_counts = defaultdict(int)
    region_counts = defaultdict(int)
    for (x, y), state in user_board.items():
        if state != "Q":
            continue
        row_counts[y] += 1
        col_counts[x] += 1
        region_counts[REGIONS[y][x]] += 1
        for nx, ny in neighbors(x, y):
            if user_board.get((nx, ny)) == "Q":
                return {'valid_complete': False, 'reason': 'adjacent_crowns'}
    for y in range(HEIGHT):
        if row_counts[y] != 1:
            return {'valid_complete': False, 'reason': f'row_{y}_count_{row_counts[y]}'}
    for x in range(WIDTH):
        if col_counts[x] != 1:
            return {'valid_complete': False, 'reason': f'col_{x}_count_{col_counts[x]}'}
    for rid in REGION_IDS:
        if region_counts[rid] != 1:
            return {'valid_complete': False, 'reason': f'region_{rid}_count_{region_counts[rid]}'}
    start = time.time()
    count, solution = solver_count_and_one_solution(limit=2)
    elapsed = time.time()-start
    return {'valid_complete': True, 'solutions_count': count, 'elapsed': elapsed,
            'one_solution': solution[0] if solution else None}

# ---------- Pygame UI ----------
pygame.init()

try:
    CROWN_FONT = pygame.font.Font("DejaVuSans.ttf", 48)  # supports ♛
except:
    CROWN_FONT = pygame.font.SysFont("arialunicode", 48)

FONT = pygame.font.SysFont(None, 36)
SMALL_FONT = pygame.font.SysFont(None, 22)
X_FONT = pygame.font.SysFont(None, 28, bold=True)

screen_w = WIDTH * CELL_SIZE + MARGIN*2
screen_h = HEIGHT * CELL_SIZE + MARGIN*2 + 60
screen = pygame.display.set_mode((screen_w, screen_h))
pygame.display.set_caption('Queens Puzzle Prototype')

clock = pygame.time.Clock()

# board state: dict {(x,y): "X" or "Q"}
board = {}

def draw_board(highlight_solution=None):
    screen.fill((230,230,230))
    for y in range(HEIGHT):
        for x in range(WIDTH):
            rid = REGIONS[y][x]
            color = REGION_COLORS[rid % len(REGION_COLORS)]
            rect = pygame.Rect(MARGIN + x*CELL_SIZE, MARGIN + y*CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, (120,120,120), rect, 1)
    for (x,y), state in board.items():
        cx = MARGIN + x*CELL_SIZE + CELL_SIZE//2
        cy = MARGIN + y*CELL_SIZE + CELL_SIZE//2
        if state == "Q":
            text = CROWN_FONT.render('\u265B', True, (10,10,10))
            tr = text.get_rect(center=(cx,cy))
            screen.blit(text, tr)
        elif state == "X":
            text = X_FONT.render("X", True, (10,10,10))
            tr = text.get_rect(center=(cx,cy))
            screen.blit(text, tr)
    if highlight_solution:
        for (x,y) in highlight_solution:
            if (x,y) in board: continue
            cx = MARGIN + x*CELL_SIZE + CELL_SIZE//2
            cy = MARGIN + y*CELL_SIZE + CELL_SIZE//2
            s = CROWN_FONT.render('\u265B', True, (80,80,80))
            s.set_alpha(110)
            tr = s.get_rect(center=(cx,cy))
            screen.blit(s, tr)
    info = SMALL_FONT.render(
        'Left click: cycle (empty→X→Q→empty)  |  Right click: clear  |  C: Check  U: Count  S: Solve  H: Hint  R: Reset',
        True, (20,20,20))
    screen.blit(info, (MARGIN, screen_h-45))
    pygame.display.flip()

def cell_at_pixel(px, py):
    if px < MARGIN or py < MARGIN: return None
    x = (px - MARGIN) // CELL_SIZE
    y = (py - MARGIN) // CELL_SIZE
    if in_bounds(x, y):
        return (x, y)
    return None

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
                    print('Not a complete valid solution:', res.get('reason'))
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
                    board = {(x,y): "Q" for (x,y) in sol[0]}
                    print(f'Board filled with solution. Found {cnt} solutions.')
                else:
                    print(f'Cannot auto-solve: found {cnt} solutions.')
            elif event.key == pygame.K_h:
                cnt, sol = solver_count_and_one_solution(limit=2)
                if cnt == 1 and sol is not None:
                    for c in sol[0]:
                        if c not in board:
                            board[c] = "Q"
                            hint_active = c
                            break
                    print('Placed one hint from solution.')
                else:
                    print('Hint unavailable: puzzle has no unique solution.')
        elif event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            cell = cell_at_pixel(*pos)
            if cell:
                if event.button == 1:  # left click cycle
                    current = board.get(cell)
                    if current is None:
                        board[cell] = "X"
                    elif current == "X":
                        temp = dict(board)
                        temp[cell] = "Q"
                        if is_valid_partial(temp):
                            board[cell] = "Q"
                            hint_active = None
                        else:
                            print('Invalid placement (adjacency or duplicates).')
                    elif current == "Q":
                        del board[cell]
                elif event.button == 3:  # right click clear
                    if cell in board:
                        del board[cell]
    draw_board(highlight_solution=None)

pygame.quit()
sys.exit()
