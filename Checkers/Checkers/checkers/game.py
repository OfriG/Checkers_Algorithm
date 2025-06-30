import pygame
from .constants import RED, WHITE, BLUE, GREEN, SQUARE_SIZE
from checkers.board import Board

class Game:
    def __init__(self, win):
        self.win = win
        self._init()

    def _init(self):
        self.selected = None
        self.board = Board()
        self.turn = RED
        self.valid_moves = {}
        self.boost_used = {RED: False, WHITE: False}
        self.boost_just_used = {RED: False, WHITE: False}
        self.twice_used = {RED: False, WHITE: False}
        self.twice_pending = {RED: False, WHITE: False}
        self.just_got_king = False
        self.winner_color = None

    def update(self):
        self.board.draw(self.win)
        self.draw_valid_moves(self.valid_moves)
        pygame.display.update()

    def reset(self):
        self._init()

    def winner(self):
        w = self.board.winner()
        if w is not None:
            self.winner_color = w
        return w
# selects a piece on the board
    def select(self, row, col, use_boost=False, use_twice=False):
        if self.selected:
            result = self._move(row, col, use_boost, use_twice)
            if not result:
                self.selected = None
                self.select(row, col, use_boost, use_twice)

        piece = self.board.get_piece(row, col)
        if piece and piece != 0 and piece.color == self.turn:
            self.selected = piece
            allow_boost = use_boost and not self.boost_used[self.turn]
            self.valid_moves = self.board.get_valid_moves(
                piece,
                allow_boost=allow_boost,
                boost_used=self.boost_used[self.turn]
            )
            return True
        return False

    def _move(self, row, col, use_boost=False, use_twice=False):
        piece = self.board.get_piece(row, col)

        if self.selected and piece == 0 and (row, col) in self.valid_moves:
            was_king = self.selected.king

            is_boost_move = (
                abs(self.selected.row - row) == 2 and
                abs(self.selected.col - col) == 2 and
                use_boost and not self.boost_used[self.turn]
            )

            if use_boost and self.boost_used[self.turn]:
                print("Boost already used – move rejected")
                return False

            self.board.move(self.selected, row, col)
            skipped = self.valid_moves[(row, col)]
            if skipped:
                self.board.remove(skipped)

            if is_boost_move:
                self.boost_used[self.turn] = True
                self.boost_just_used[self.turn] = True
            else:
                self.boost_just_used[self.turn] = False

            if use_twice and not self.twice_used[self.turn] and skipped:
                self.twice_used[self.turn] = True
                self.twice_pending[self.turn] = True
                return True

            self.just_got_king = not was_king and self.selected.king
            if self.just_got_king:
                self.twice_pending[self.turn] = True
            if not self.twice_pending[self.turn]:
                self.change_turn()
        
        else:
            return False
        return True
# Change the turn to the next player
    def change_turn(self):
        self.twice_pending[self.turn] = False
        self.valid_moves = {}
        self.selected = None
        next_turn = WHITE if self.turn == RED else RED
        
        if not self.twice_pending[next_turn]:
            self.turn = next_turn

    def draw_valid_moves(self, moves):
        for move in moves:
            row, col = move
            color = GREEN if (
                self.selected and abs(self.selected.row - row) == 2 and abs(self.selected.col - col) == 2
            ) else BLUE
            pygame.draw.circle(
                self.win,
                color,
                (col * SQUARE_SIZE + SQUARE_SIZE // 2, row * SQUARE_SIZE + SQUARE_SIZE // 2),
                15
            )

    def get_board(self):
        return self.board

    def ai_move(self, board):
        if getattr(board, 'last_boost_used', False):
            self.boost_used[WHITE] = True
            self.boost_just_used[WHITE] = True
            board.last_boost_used = False
        else:
            self.boost_just_used[WHITE] = False

        current_kings = sum(1 for p in board.get_all_pieces(WHITE) if p.king)
        prev_kings = sum(1 for p in self.board.get_all_pieces(WHITE) if p.king)

        self.board = board

        if current_kings > prev_kings:
            self.twice_pending[WHITE] = True
        else:
            self.twice_pending[WHITE] = False
            self.change_turn()

    def detect_ai_boost(self, old_board, new_board):
        # Detect if WHITE used Boost by checking if move was a 2-step diagonal
        old_pieces = {(p.row, p.col): p for p in old_board.get_all_pieces(WHITE)}
        new_pieces = {(p.row, p.col): p for p in new_board.get_all_pieces(WHITE)}

        for (r_old, c_old), piece in old_pieces.items():
            for (r_new, c_new) in new_pieces:
                if abs(r_new - r_old) == 2 and abs(c_new - c_old) == 2:
                    return True
        return False
    def has_valid_moves(self, color):
        pieces = self.board.get_all_pieces(color)
        for piece in pieces:
            moves = self.board.get_valid_moves(piece, allow_boost=not self.boost_used[color], boost_used=self.boost_used[color])
            if moves:
                return True
        return False
