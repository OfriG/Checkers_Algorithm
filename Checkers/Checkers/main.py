import pygame
from checkers.constants import WIDTH, HEIGHT, SQUARE_SIZE, RED, WHITE
from checkers.game import Game
from minimax.algorithm import minimax
import tkinter as tk
from tkinter import messagebox

# initialize tkinter without opening a window
tk_root = tk.Tk()
tk_root.withdraw()

FPS = 60

pygame.init()
pygame.font.init()

WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Checkers')

BOOST_BTN = pygame.Rect(WIDTH - 140, HEIGHT - 50, 120, 40)

def get_row_col_from_mouse(pos):
    x, y = pos
    row = y // SQUARE_SIZE
    col = x // SQUARE_SIZE
    return row, col

def draw_winner(win, color):
    font = pygame.font.SysFont(None, 72)
    text = f"{'RED' if color == RED else 'WHITE'} WINS!"
    text_surface = font.render(text, True, (255, 255, 255))
    text_rect = text_surface.get_rect(center=(WIDTH/2, HEIGHT/2))
    win.blit(text_surface, text_rect)
    pygame.display.update()
    pygame.time.wait(3000)

def draw_message(win, message):
    font = pygame.font.SysFont(None, 36)
    text_surface = font.render(message, True, (255, 255, 255))
    text_rect = text_surface.get_rect(center=(WIDTH/2, HEIGHT - 70))
    pygame.draw.rect(win, (0, 0, 0), (0, HEIGHT - 90, WIDTH, 90))
    win.blit(text_surface, text_rect)

def draw_boost_button(win, game):
    if game.turn == RED and not game.boost_used[RED]:
        pygame.draw.rect(win, (70, 130, 180), BOOST_BTN)
        font = pygame.font.SysFont(None, 28)
        text = font.render("Use Boost", True, (255, 255, 255))
        text_rect = text.get_rect(center=BOOST_BTN.center)
        win.blit(text, text_rect)

def main():
    run = True
    clock = pygame.time.Clock()
    game = Game(WIN)
    boost_mode = False
    boost_button_visible = True
    ai_boost_alert_shown = False

    while run:
        clock.tick(FPS)

        if game.turn == WHITE:
            value, new_board = minimax(game.get_board(), 2, WHITE, game)
            if new_board:
                new_board.last_boost_used = game.detect_ai_boost(game.get_board(), new_board)
                game.ai_move(new_board)
            else:
                continue

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()

                if BOOST_BTN.collidepoint(pos) and boost_button_visible and not game.boost_used[RED] and game.turn == RED:
                    boost_mode = True
                    boost_button_visible = False
                    draw_message(WIN, "Boost mode activated!")

                else:
                    row, col = get_row_col_from_mouse(pos)
                    use_twice = event.button == 2 and not game.twice_used[RED]

                    if game.turn == RED:
                        game.select(row, col, boost_mode, use_twice)
                        boost_mode = False

        game.update()

        if game.turn == RED and not game.boost_used[RED] and boost_button_visible:
            draw_boost_button(WIN, game)

        # Game messages and popups
        if game.boost_just_used[RED]:
            draw_message(WIN, "Boost used!")

        elif game.boost_just_used[WHITE] and not ai_boost_alert_shown:
            messagebox.showinfo("AI Boost", "AI used Boost!")
            game.boost_just_used[WHITE] = False
            ai_boost_alert_shown = True

        if game.twice_pending[RED]:
            messagebox.showinfo("Twice Turn", "You get another turn (Twice)!")
            game.twice_pending[RED] = False

        elif game.twice_pending[WHITE]:
            messagebox.showinfo("Twice Turn", "AI gets another turn (Twice)!")
            game.twice_pending[WHITE] = False

            # AI does the next move immediately
            value, new_board = minimax(game.get_board(), 2, WHITE, game)
            if new_board:
                new_board.last_boost_used = game.detect_ai_boost(game.get_board(), new_board)
                game.ai_move(new_board)

        if game.just_got_king:
            if game.turn == RED:
                messagebox.showinfo("King crowned!", "You got a King! You get another turn (Twice)!")
            else:
                messagebox.showinfo("King crowned!", "AI got a King! It gets another turn (Twice)!")
                game.twice_pending[WHITE] = True
            game.just_got_king = False

        if game.turn == RED and not game.has_valid_moves(RED):
            draw_message(WIN, "No valid moves left. WHITE wins!")
            pygame.display.update()
            pygame.time.wait(2000)
            messagebox.showinfo("Game Over", "No valid moves for RED. WHITE wins!")
            run = False
        elif game.turn == WHITE and not game.has_valid_moves(WHITE):
            draw_message(WIN, "No valid moves left. RED wins!")
            pygame.display.update()
            pygame.time.wait(2000)
            messagebox.showinfo("Game Over", "No valid moves for WHITE. RED wins!")
            run = False

        winner = game.winner()
        if winner is not None:
            draw_winner(WIN, winner)
            messagebox.showinfo("Game Over", f"{'RED' if winner == RED else 'WHITE'} wins!")
            run = False

        pygame.display.update()

    pygame.quit()

main()
