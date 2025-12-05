import pygame
import sys
import random
import time  

# CONFIG
ROWS = 6
COLS = 7
DEPTH = 5

TILE = 100
WIDTH = COLS * TILE
HEIGHT = (ROWS + 1) * TILE

WHITE = (240, 240, 240)
BLACK = (0, 0, 0)
GREY = (80, 80, 80)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)

pygame.init()
font = pygame.font.SysFont("arial", 40)
small_font = pygame.font.SysFont("arial", 28)
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Connect Four - Minimax / BFS")

clock = pygame.time.Clock()

# GAME LOGIC
board = [['.' for _ in range(COLS)] for _ in range(ROWS)]

def reset_board():
    for r in range(ROWS):
        for c in range(COLS):
            board[r][c] = '.'

def cek(col):
    return 0 <= col < COLS and board[0][col] == '.'

def taruh(col, s):
    for r in range(ROWS-1, -1, -1):
        if board[r][col] == '.':
            board[r][col] = s
            return

def balik(col):
    for r in range(ROWS):
        if board[r][col] != '.':
            board[r][col] = '.'
            return

def menang(s):
    # Horizontal
    for r in range(ROWS):
        for c in range(COLS-3):
            if board[r][c]==s and board[r][c+1]==s and board[r][c+2]==s and board[r][c+3]==s:
                return True
    # Vertical
    for r in range(ROWS-3):
        for c in range(COLS):
            if board[r][c]==s and board[r+1][c]==s and board[r+2][c]==s and board[r+3][c]==s:
                return True
    # Diagonal /
    for r in range(3, ROWS):
        for c in range(COLS-3):
            if board[r][c]==s and board[r-1][c+1]==s and board[r-2][c+2]==s and board[r-3][c+3]==s:
                return True
    # Diagonal \
    for r in range(ROWS-3):
        for c in range(COLS-3):
            if board[r][c]==s and board[r+1][c+1]==s and board[r+2][c+2]==s and board[r+3][c+3]==s:
                return True
    return False

def penuh():
    return all(board[0][c] != '.' for c in range(COLS))

def hitung():
    if menang('O'): return 1000
    if menang('X'): return -1000
    return 0

# Minimax
def minimax(depth, maximize):
    score = hitung()
    if score == 1000 or score == -1000 or depth == 0 or penuh():
        return score

    if maximize:
        best = -9999
        for c in range(COLS):
            if cek(c):
                taruh(c, 'O')
                val = minimax(depth-1, False)
                balik(c)
                if val > best:
                    best = val
        return best
    else:
        best = 9999
        for c in range(COLS):
            if cek(c):
                taruh(c, 'X')
                val = minimax(depth-1, True)
                balik(c)
                if val < best:
                    best = val
        return best

def pilih_minimax():
    best = -9999
    best_col = None
    for c in range(COLS):
        if cek(c):
            taruh(c, 'O')
            val = minimax(DEPTH, False)
            balik(c)
            if val > best:
                best = val
                best_col = c
    if best_col is None:
        valid = [c for c in range(COLS) if cek(c)]
        return random.choice(valid) if valid else 0
    return best_col

# BFS
def pilih_bfs():
    for c in range(COLS):
        if cek(c):
            taruh(c, 'O')
            if menang('O'):
                balik(c)
                return c
            balik(c)

    for c in range(COLS):
        if cek(c):
            taruh(c, 'X')
            if menang('X'):
                balik(c)
                return c
            balik(c)

    valid = [c for c in range(COLS) if cek(c)]
    return random.choice(valid) if valid else 0

# UI
def draw_board():
    screen.fill(BLACK)
    for c in range(COLS):
        for r in range(ROWS):
            pygame.draw.rect(screen, WHITE, (c*TILE, (r+1)*TILE, TILE, TILE))
            pygame.draw.circle(screen, BLACK,
                (c*TILE + TILE//2, (r+1)*TILE + TILE//2), TILE//2 - 6)
    for r in range(ROWS):
        for c in range(COLS):
            if board[r][c] == 'X':
                pygame.draw.circle(screen, RED,
                    (c*TILE + TILE//2, (r+1)*TILE + TILE//2), TILE//2 - 8)
            elif board[r][c] == 'O':
                pygame.draw.circle(screen, YELLOW,
                    (c*TILE + TILE//2, (r+1)*TILE + TILE//2), TILE//2 - 8)

def draw_button(text, y):
    rect = pygame.Rect(WIDTH//2 - 150, y, 300, 60)
    pygame.draw.rect(screen, GREY, rect)
    label = font.render(text, True, WHITE)
    screen.blit(label, label.get_rect(center=rect.center))
    return rect

def draw_title(text, y):
    label = font.render(text, True, WHITE)
    screen.blit(label, label.get_rect(center=(WIDTH//2, y)))

def draw_game_over_overlay(result_text):
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))

    msg = font.render(result_text, True, WHITE)
    screen.blit(msg, (WIDTH//2 - msg.get_width()//2, 150))

    again_btn = draw_button("PLAY AGAIN", 300)
    menu_btn = draw_button("MAIN MENU", 400)
    return again_btn, menu_btn

# MAIN LOOP
def run():
    state = "MENU"
    turn_player = True
    game_over = False
    result_text = ""
    ai_mode = "minimax"

    reset_board()

    while True:
        clock.tick(60)

        if state == "MENU":
            screen.fill(BLACK)
            draw_title("CONNECT FOUR", 110)
            mm_btn = draw_button("PLAY (MINIMAX)", 220)
            bfs_btn = draw_button("PLAY (BFS EASY)", 300)
            exit_btn = draw_button("EXIT", 380)
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if mm_btn.collidepoint(event.pos):
                        reset_board()
                        turn_player = True
                        game_over = False
                        ai_mode = "minimax"
                        state = "PLAY"
                    elif bfs_btn.collidepoint(event.pos):
                        reset_board()
                        turn_player = True
                        game_over = False
                        ai_mode = "bfs"
                        state = "PLAY"
                    elif exit_btn.collidepoint(event.pos):
                        pygame.quit(); sys.exit()

        elif state == "PLAY":
            draw_board()
            if game_over:
                again_btn, menu_btn = draw_game_over_overlay(result_text)
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()

                if game_over:
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if again_btn.collidepoint(event.pos):
                            reset_board()
                            turn_player = True
                            game_over = False
                            result_text = ""
                        elif menu_btn.collidepoint(event.pos):
                            state = "MENU"
                    continue

                if turn_player and event.type == pygame.MOUSEBUTTONDOWN:
                    col = event.pos[0] // TILE
                    if cek(col):
                        taruh(col, 'X')
                        if menang('X'):
                            result_text = "PLAYER WIN!"
                            game_over = True
                        elif penuh():
                            result_text = "DRAW!"
                            game_over = True
                        else:
                            turn_player = False

            # AI TURN + penghitungan waktu
            if not turn_player and not game_over:

                print("AI thinking...")             
                start = time.time()                  # waktu mulai

                pygame.time.delay(200)
                if ai_mode == "minimax":
                    col = pilih_minimax()
                else:
                    col = pilih_bfs()

                dur = time.time() - start            # hitung durasi
                print(f"AI finished in {dur:.4f} seconds")   

                if not cek(col):
                    valid = [c for c in range(COLS) if cek(c)]
                    col = random.choice(valid) if valid else 0

                taruh(col, 'O')
                if menang('O'):
                    result_text = "AI WIN!"
                    game_over = True
                elif penuh():
                    result_text = "DRAW!"
                    game_over = True
                else:
                    turn_player = True

# START
if __name__ == "__main__":
    run()
