"""
Queens-like puzzle prototype using pygame.
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

# Ask the user for the board size at runtime
while True:
    try:
        size = int(input("Enter the grid size (e.g., 7 for a 7x7 board): "))
        if size < 5 or size > 9:
            print("Please enter a number between 5 and 9.")
            continue
        break
    except ValueError:
        print("Please enter a valid integer.")

find_and_save_unique_maps(size, size, attempts=5000, want=1)

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
    return 0 <= x < size and 0 <= y < size

def neighbors(x, y):
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0: continue
            nx, ny = x + dx, y + dy
            if in_bounds(nx, ny): yield (nx, ny)

def initial_region_map(regions):
    from collections import defaultdict
    rmap = defaultdict(list)
    for y in range(size):
        for x in range(size):
            rmap[regions[y][x]].append((x, y))
    return dict(rmap)

REGION_MAP = initial_region_map(REGIONS)
REGION_IDS = list(REGION_MAP.keys())

def is_valid_partial(board):
    row_counts, col_counts, region_counts = defaultdict(int), defaultdict(int), defaultdict(int)
    for (x, y), state in board.items():
        if state != "Q": continue
        row_counts[y] += 1; col_counts[x] += 1; region_counts[REGIONS[y][x]] += 1
        for nx, ny in neighbors(x, y):
            if board.get((nx, ny)) == "Q":
                return False
    if any(v > 1 for v in row_counts.values()): return False
    if any(v > 1 for v in col_counts.values()): return False
    if any(v > 1 for v in region_counts.values()): return False
    return True

def solver_count_and_one_solution(limit=None):
    regions = REGION_IDS
    solutions, one_solution = 0, None

    def backtrack(i, taken_rows, taken_cols, taken_regions, occupied):
        nonlocal solutions, one_solution
        if limit is not None and solutions >= limit: return
        if i == len(regions):
            solutions += 1
            occ = sorted(occupied, key=lambda x: x[0])
            if one_solution is None: one_solution = [occ.copy()]
            else: one_solution.append(occ.copy())
            return
        rid = regions[i]
        for (x, y) in REGION_MAP[rid]:
            if y in taken_rows or x in taken_cols: continue
            if any((nx, ny) in occupied for nx, ny in neighbors(x, y)): continue
            occupied.add((x, y))
            taken_rows.add(y); taken_cols.add(x); taken_regions.add(rid)
            backtrack(i+1, taken_rows, taken_cols, taken_regions, occupied)
            occupied.remove((x, y))
            taken_rows.remove(y); taken_cols.remove(x); taken_regions.remove(rid)
            if limit is not None and solutions >= limit: return

    backtrack(0, set(), set(), set(), set())
    return solutions, one_solution

def check_user_solution(user_board):
    row_counts, col_counts, region_counts = defaultdict(int), defaultdict(int), defaultdict(int)
    for (x, y), state in user_board.items():
        if state != "Q": continue
        row_counts[y] += 1; col_counts[x] += 1; region_counts[REGIONS[y][x]] += 1
        for nx, ny in neighbors(x, y):
            if user_board.get((nx, ny)) == "Q":
                return {'valid_complete': False, 'reason': 'adjacent_crowns'}
    for y in range(size):
        if row_counts[y] != 1: return {'valid_complete': False, 'reason': f'row_{y}_count_{row_counts[y]}'}
    for x in range(size):
        if col_counts[x] != 1: return {'valid_complete': False, 'reason': f'col_{x}_count_{col_counts[x]}'}
    for rid in REGION_IDS:
        if region_counts[rid] != 1: return {'valid_complete': False, 'reason': f'region_{rid}_count_{region_counts[rid]}'}
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
BIG_FONT = pygame.font.SysFont(None, 72, bold=True)
SMALL_FONT = pygame.font.SysFont(None, 22)
X_FONT = pygame.font.SysFont(None, 28, bold=True)

screen_w = size * CELL_SIZE + MARGIN*2
screen_h = size * CELL_SIZE + MARGIN*2 + 60
screen = pygame.display.set_mode((screen_w, screen_h))
pygame.display.set_caption('Queens Puzzle Prototype')

clock = pygame.time.Clock()

board = {}   # {(x,y): "X" or "Q"}
game_won = False
win_time = 0

def draw_board(highlight_solution=None):
    screen.fill((230,230,230))
    for y in range(size):
        for x in range(size):
            rid = REGIONS[y][x]
            rect = pygame.Rect(MARGIN + x*CELL_SIZE, MARGIN + y*CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(screen, REGION_COLORS[rid % len(REGION_COLORS)], rect)
            pygame.draw.rect(screen, (120,120,120), rect, 1)
    for (x,y), state in board.items():
        cx, cy = MARGIN + x*CELL_SIZE + CELL_SIZE//2, MARGIN + y*CELL_SIZE + CELL_SIZE//2
        if state == "Q":
            text = CROWN_FONT.render('\u265B', True, (10,10,10))
            screen.blit(text, text.get_rect(center=(cx,cy)))
        elif state == "X":
            text = X_FONT.render("X", True, (10,10,10))
            screen.blit(text, text.get_rect(center=(cx,cy)))
    if highlight_solution:
        for (x,y) in highlight_solution:
            if (x,y) in board: continue
            cx, cy = MARGIN + x*CELL_SIZE + CELL_SIZE//2, MARGIN + y*CELL_SIZE + CELL_SIZE//2
            s = CROWN_FONT.render('\u265B', True, (80,80,80))
            s.set_alpha(110)
            screen.blit(s, s.get_rect(center=(cx,cy)))
    info = SMALL_FONT.render(
        'Left click: cycle (empty→X→Q→empty)  |  Right click: clear  |  C: Check  U: Count  S: Solve  H: Hint  R: Reset',
        True, (20,20,20))
    screen.blit(info, (MARGIN, screen_h-45))

    # At the bottom of the board, above controls
    timer_text = SMALL_FONT.render(f"Time: {int(elapsed_time)}s", True, (0,0,0))
    screen.blit(timer_text, (MARGIN, screen_h-25))

    # Modify the win overlay to show final time
    if game_won:
        overlay = BIG_FONT.render("YOU WIN!", True, (0,180,0))
        rect = overlay.get_rect(center=(screen_w//2, screen_h//2 - 30))
        screen.blit(overlay, rect)

        time_overlay = FONT.render(f"Time: {int(elapsed_time)}s", True, (0,180,0))
        rect2 = time_overlay.get_rect(center=(screen_w//2, screen_h//2 + 30))
        screen.blit(time_overlay, rect2)


    pygame.display.flip()

def cell_at_pixel(px, py):
    if px < MARGIN or py < MARGIN: return None
    x, y = (px - MARGIN) // CELL_SIZE, (py - MARGIN) // CELL_SIZE
    return (x, y) if in_bounds(x, y) else None

running, hint_active = True, None
left_held = False
right_held = False

start_time = time.time()
elapsed_time = 0


while running:
    clock.tick(30)
    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE: running = False
            elif event.key == pygame.K_r:
                board.clear(); hint_active = None; game_won = False
            elif event.key == pygame.K_c:
                res = check_user_solution(board)
                if not res.get('valid_complete'):
                    print('Not a complete valid solution:', res.get('reason'))
                else:
                    cnt = res.get('solutions_count')
                    if cnt == 1:
                        print("YOU WIN!")
                        game_won = True
                        win_time = time.time()
                    else:
                        print(f'Valid placement but solver found {cnt} solutions.')
            elif event.key == pygame.K_s:
                cnt, sol = solver_count_and_one_solution(limit=10)
                if cnt >= 1 and sol is not None:
                    board = {(x,y): "Q" for (x,y) in sol[0]}
                    print("Auto-solved!")
                else:
                    print("Cannot auto-solve.")
            elif event.key == pygame.K_h:
                cnt, sol = solver_count_and_one_solution(limit=2)
                if cnt == 1 and sol is not None:
                    for c in sol[0]:
                        if c not in board:
                            board[c] = "Q"; hint_active = c; break
                    print('Placed one hint.')
                else:
                    print('Hint unavailable.')
        
            elif event.key == pygame.K_n:
                

                print("Generating new board...")
                # 1. Generate new puzzle
                find_and_save_unique_maps(size, size, attempts=5000, want=1)
                # 2. Load new puzzle into REGIONS
                with open('puzzle.csv', newline="") as f:
                    reader = csv.reader(f)
                    REGIONS[:] = [[int(cell) for cell in row] for row in reader]
                # 3. Update REGION_MAP and REGION_IDS
                REGION_MAP = initial_region_map(REGIONS)
                REGION_IDS = list(REGION_MAP.keys())
                # 4. Clear current board
                board.clear()
                hint_active = None
                game_won = False
                # 5. Animate new board
                for y in range(size):
                    for x in range(size):
                        rect = pygame.Rect(MARGIN + x*CELL_SIZE, MARGIN + y*CELL_SIZE, CELL_SIZE, CELL_SIZE)
                        color = REGION_COLORS[REGIONS[y][x] % len(REGION_COLORS)]
                        pygame.draw.rect(screen, color, rect)
                        pygame.draw.rect(screen, (120,120,120), rect, 1)
                        pygame.display.flip()
                        pygame.time.delay(30)  # sequential cell animation
                print("New board ready!")
                start_time = time.time()  # reset timer
                elapsed_time = 0

        elif event.type == pygame.MOUSEBUTTONDOWN:
            cell = cell_at_pixel(*event.pos)
            if not cell: continue

            if event.button == 1:  # left click
                left_held = True
                current = board.get(cell)
                if current is None:
                    board[cell] = "X"
                elif current == "X":
                    temp = dict(board); temp[cell] = "Q"
                    if is_valid_partial(temp):
                        board[cell] = "Q"
                        hint_active = None
                        # Auto win check
                        res = check_user_solution(board)
                        if res.get('valid_complete') and res.get('solutions_count') == 1:
                            print("YOU WIN!")
                            game_won = True
                            win_time = time.time()
                    else:
                        print("Invalid placement.")
                elif current == "Q":
                    del board[cell]

            elif event.button == 3:  # right click
                right_held = True
                if board.get(cell) == "X":
                    del board[cell]

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1: left_held = False
            elif event.button == 3: right_held = False

        elif event.type == pygame.MOUSEMOTION:
            cell = cell_at_pixel(*event.pos)
            if not cell: continue

            if left_held:
                # drag only sets empty cells to X
                if cell not in board:
                    board[cell] = "X"

            elif right_held:
                # drag clears Xs only
                if board.get(cell) == "X":
                    del board[cell]



    # auto-clear win after 3s
    if game_won and time.time() - win_time > 3:
        game_won = False

    if not game_won:
        elapsed_time = time.time() - start_time

    draw_board(highlight_solution=None)

pygame.quit()
sys.exit()
