import pygame
import sys
import random

# CONFIGURATION
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
pygame.mixer.init()

font = pygame.font.SysFont("arial", 40)
small_font = pygame.font.SysFont("arial", 28)
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Connect Four - Minimax / BFS")

clock = pygame.time.Clock()

# SOUND 
def play_sound_once(name):
    pygame.mixer.music.load(name)
    pygame.mixer.music.play(0)

def play_sound_loop(name):
    pygame.mixer.music.load(name)
    pygame.mixer.music.play(-1)

def stop_sound():
    pygame.mixer.music.stop()

# BACKGROUND IMAGES
bg_menu = pygame.image.load("background.jpeg")
bg_menu = pygame.transform.scale(bg_menu, (WIDTH, HEIGHT))


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
    if score in (1000, -1000) or depth == 0 or penuh():
        return score

    if maximize:
        best = -9999
        for c in range(COLS):
            if cek(c):
                taruh(c, 'O')
                val = minimax(depth-1, False)
                balik(c)
                best = max(best, val)
        return best

    else:
        best = 9999
        for c in range(COLS):
            if cek(c):
                taruh(c, 'X')
                val = minimax(depth-1, True)
                balik(c)
                best = min(best, val)
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

# BFS Sederhana
def pilih_bfs():
    # 1) AI menang
    for c in range(COLS):
        if cek(c):
            taruh(c, 'O')
            if menang('O'):
                balik(c)
                return c
            balik(c)

    # 2) Blokir player
    for c in range(COLS):
        if cek(c):
            taruh(c, 'X')
            if menang('X'):
                balik(c)
                return c
            balik(c)

    # 3) Random
    valid = [c for c in range(COLS) if cek(c)]
    return random.choice(valid) if valid else 0

# UI DRAWING
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


# MAIN LOOP (state machine)
def run():
    state = "MENU"
    turn_player = True
    game_over = False
    result_text = ""
    ai_mode = "minimax"

    reset_board()

    play_sound_once("menu.mp3")

    while True:
        clock.tick(60)

        # MENU 
        if state == "MENU":
            screen.blit(bg_menu, (0, 0))   # tampilkan background
            draw_title("CONNECT FOUR", 110)
            play_mm_btn = draw_button("PLAY (MINIMAX)", 220)
            play_bfs_btn = draw_button("PLAY (BFS EASY)", 300)
            exit_btn = draw_button("EXIT", 380)
            pygame.display.update()


            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if play_mm_btn.collidepoint(event.pos):
                        play_sound_once("klikplay.mp3")
                        stop_sound()
                        play_sound_loop("ingame.mp3")
                        reset_board()
                        ai_mode = "minimax"
                        turn_player = True
                        game_over = False
                        result_text = ""
                        state = "PLAY"
                    
                    elif play_bfs_btn.collidepoint(event.pos):
                        play_sound_once("klikplay.mp3")
                        stop_sound()
                        play_sound_loop("ingame.mp3")
                        reset_board()
                        ai_mode = "bfs"
                        turn_player = True
                        game_over = False
                        result_text = ""
                        state = "PLAY"
                    
                    elif exit_btn.collidepoint(event.pos):
                        pygame.quit(); sys.exit()

        # GAME PLAY 
        elif state == "PLAY":
            draw_board()
            if game_over:
                again_btn, menu_btn = draw_game_over_overlay(result_text)
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()

                # handle game over buttons
                if game_over:
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if again_btn.collidepoint(event.pos):
                            play_sound_once("klikplay.mp3")
                            stop_sound()
                            play_sound_loop("ingame.mp3")
                            reset_board()
                            turn_player = True
                            game_over = False
                            result_text = ""

                        elif menu_btn.collidepoint(event.pos):
                            play_sound_once("klikplay.mp3")
                            stop_sound()
                            play_sound_once("menu.mp3")
                            state = "MENU"
                    continue

                # Player move
                if turn_player and event.type == pygame.MOUSEBUTTONDOWN:
                    col = event.pos[0] // TILE
                    if cek(col):
                        taruh(col, 'X')
                        if menang('X'):
                            stop_sound()
                            play_sound_once("win.mp3")
                            result_text = "PLAYER WIN!"
                            game_over = True
                        elif penuh():
                            stop_sound()
                            result_text = "DRAW!"
                            game_over = True
                        else:
                            turn_player = False

            # AI MOVE
            if not turn_player and not game_over:
                pygame.time.delay(200)

                col = pilih_minimax() if ai_mode == "minimax" else pilih_bfs()

                if not cek(col):
                    valid = [c for c in range(COLS) if cek(c)]
                    col = random.choice(valid) if valid else 0

                taruh(col, 'O')

                if menang('O'):
                    stop_sound()
                    play_sound_once("lose.mp3")
                    result_text = "AI WIN!"
                    game_over = True
                elif penuh():
                    stop_sound()
                    result_text = "DRAW!"
                    game_over = True
                else:
                    turn_player = True

# START
if __name__ == "__main__":
    run()
