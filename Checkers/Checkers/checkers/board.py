import pygame
from .constants import BLACK, ROWS, RED, SQUARE_SIZE, COLS, WHITE, HOLES
from .piece import Piece

class Board:
    def __init__(self):
        self.board = []
        self.red_left = self.white_left = 12
        self.red_kings = self.white_kings = 0
        self.create_board()
    
    def draw_squares(self, win):
        win.fill(BLACK)
        for row in range(ROWS):
            for col in range(row % 2, COLS, 2):
                pygame.draw.rect(win, RED, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
        for row, col in HOLES:
            pygame.draw.rect(win, (100, 100, 100), (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
 # evaluate function to calculate the score of the board state
    def evaluate(self, boost_available=None):
        score = self.white_left - self.red_left
        score += 0.5 * (self.white_kings - self.red_kings)

        for row in range(ROWS):
            for col in range(COLS):
                piece = self.board[row][col]
                if isinstance(piece, Piece):
                    for hole_r, hole_c in HOLES:
                        dist = abs(row - hole_r) + abs(col - hole_c)
                        if dist == 1:
                            if piece.color == WHITE:
                                score -= 0.1
                            else:
                                score += 0.1

        if boost_available:
            if boost_available["WHITE"]:
                score += 0.2
            if boost_available["RED"]:
                score -= 0.2

        return score

    def get_all_pieces(self, color):
        return [piece for row in self.board for piece in row if piece != 0 and piece is not None and piece.color == color]

    def move(self, piece, row, col):
        self.board[piece.row][piece.col], self.board[row][col] = self.board[row][col], self.board[piece.row][piece.col]
        piece.move(row, col)
        if row == 0 or row == ROWS - 1:
            piece.make_king()
            if piece.color == WHITE:
                self.white_kings += 1
            else:
                self.red_kings += 1

    def get_piece(self, row, col):
        if (row, col) in HOLES:
            return None
        return self.board[row][col]

    def create_board(self):
        for row in range(ROWS):
            self.board.append([])
            for col in range(COLS):
                if (row, col) in HOLES:
                    self.board[row].append(None)
                elif col % 2 == ((row + 1) % 2):
                    if row < 3:
                        self.board[row].append(Piece(row, col, WHITE))
                    elif row > 6:
                        self.board[row].append(Piece(row, col, RED))
                    else:
                        self.board[row].append(0)
                else:
                    self.board[row].append(0)

    def draw(self, win):
        self.draw_squares(win)
        for row in range(ROWS):
            for col in range(COLS):
                piece = self.board[row][col]
                if piece != 0 and piece is not None:
                    piece.draw(win)

    def remove(self, pieces):
        for piece in pieces:
            self.board[piece.row][piece.col] = 0
            if piece != 0:
                if piece.color == RED:
                    self.red_left -= 1
                else:
                    self.white_left -= 1

    def winner(self):
        if self.red_left <= 0:
            return WHITE
        elif self.white_left <= 0:
            return RED
        return None

    def get_valid_boost_moves(self, piece):
        moves = {}
        if piece is None:
            return moves
        directions = []
        if piece.color == RED or piece.king:
            directions += [(-2, -2), (-2, 2)]
        if piece.color == WHITE or piece.king:
            directions += [(2, -2), (2, 2)]
        for dr, dc in directions:
            r, c = piece.row + dr, piece.col + dc
            if 0 <= r < ROWS and 0 <= c < COLS and (r, c) not in HOLES and self.board[r][c] == 0:
                moves[(r, c)] = []
        return moves

    def get_valid_moves(self, piece, allow_boost=False, boost_used=False):
        moves = {}
        if piece is None:
            return moves
        left = piece.col - 1
        right = piece.col + 1
        row = piece.row
# see if the destination is valid
        def is_valid_dest(r, c):
            return 0 <= r < ROWS and 0 <= c < COLS and (r, c) not in HOLES and self.board[r][c] == 0

        if piece.color == RED or piece.king:
            moves.update(self._traverse_left(row - 1, max(row - 3, -1), -1, piece.color, left))
            moves.update(self._traverse_right(row - 1, max(row - 3, -1), -1, piece.color, right))
        if piece.color == WHITE or piece.king:
            moves.update(self._traverse_left(row + 1, min(row + 3, ROWS), 1, piece.color, left))
            moves.update(self._traverse_right(row + 1, min(row + 3, ROWS), 1, piece.color, right))

        moves = {move: skipped for move, skipped in moves.items() if is_valid_dest(*move)}

        if allow_boost and not boost_used:
            moves.update(self.get_valid_boost_moves(piece))
        return moves
    # Helper methods to traverse the board for valid moves
    def _traverse_left(self, start, stop, step, color, left, skipped=[]):
        moves = {}
        last = []
        for r in range(start, stop, step):
            if left < 0:
                break
            current = self.board[r][left]
            if current == 0 or current is None:
                if skipped and not last:
                    break
                elif skipped:
                    moves[(r, left)] = last + skipped
                else:
                    moves[(r, left)] = last
                if last:
                    prev_r = r - step
                    prev_c = left + 1 if step == -1 else left - 1
                    if 0 <= prev_r < ROWS and 0 <= prev_c < COLS and self.board[prev_r][prev_c] is None:
                        break
                    next_row = max(r - 3, 0) if step == -1 else min(r + 3, ROWS)
                    moves.update(self._traverse_left(r + step, next_row, step, color, left - 1, skipped=last))
                    moves.update(self._traverse_right(r + step, next_row, step, color, left + 1, skipped=last))
                break
            elif isinstance(current, Piece) and current.color == color:
                break
            else:
                last = [current]
            left -= 1
        return moves
# Helper method to traverse the board for valid moves in the right direction
    def _traverse_right(self, start, stop, step, color, right, skipped=[]):
        moves = {}
        last = []
        for r in range(start, stop, step):
            if right >= COLS:
                break
            current = self.board[r][right]
            if current == 0 or current is None:
                if skipped and not last:
                    break
                elif skipped:
                    moves[(r, right)] = last + skipped
                else:
                    moves[(r, right)] = last
                if last:
                    prev_r = r - step
                    prev_c = right - 1 if step == -1 else right + 1
                    if 0 <= prev_r < ROWS and 0 <= prev_c < COLS and self.board[prev_r][prev_c] is None:
                        break
                    next_row = max(r - 3, 0) if step == -1 else min(r + 3, ROWS)
                    moves.update(self._traverse_left(r + step, next_row, step, color, right - 1, skipped=last))
                    moves.update(self._traverse_right(r + step, next_row, step, color, right + 1, skipped=last))
                break
            elif isinstance(current, Piece) and current.color == color:
                break
            else:
                last = [current]
            right += 1
        return moves
