"""Pygame GUI for chess engine."""

import pygame
import sys
import threading
import copy
from board import Board
from engine import find_best_move
from sounds import SoundEffects

# Constants
WINDOW_SIZE = 800
BOARD_SIZE = 8
SQUARE_SIZE = WINDOW_SIZE // BOARD_SIZE
FPS = 60

# Colors
WHITE_SQUARE = (240, 217, 181)
BLACK_SQUARE = (181, 136, 99)
HIGHLIGHT_COLOR = (186, 202, 43)
VALID_MOVE_COLOR = (186, 202, 43, 100)
SELECTED_COLOR = (240, 217, 181)
CHECK_COLOR = (255, 0, 0)

# Piece symbols
PIECE_SYMBOLS = {
    ('P', True): '♙',
    ('P', False): '♟',
    ('N', True): '♘',
    ('N', False): '♞',
    ('B', True): '♗',
    ('B', False): '♝',
    ('R', True): '♖',
    ('R', False): '♜',
    ('Q', True): '♕',
    ('Q', False): '♛',
    ('K', True): '♔',
    ('K', False): '♚',
}


class ChessGUI:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
        pygame.display.set_caption("Chess Engine")
        self.clock = pygame.time.Clock()

        # Try to find a font that supports Unicode chess symbols
        font_names = ['segoe ui symbol', 'symbola', 'dejavu sans', 'arial unicode ms', 'arial']
        self.font = None
        for font_name in font_names:
            try:
                self.font = pygame.font.SysFont(font_name, 60)
                break
            except:
                pass
        if not self.font:
            self.font = pygame.font.Font(None, 60)

        self.small_font = pygame.font.Font(None, 24)

        self.board = Board()
        self.selected_piece = None
        self.valid_moves = []
        self.engine_depth = 4
        self.game_over = False
        self.status_message = "Your move (White)"

        # Sound effects
        self.sounds = SoundEffects()

        # Check state
        self.in_check = False

        # Engine state
        self.engine_thinking = False
        self.pending_engine_move = None
        self.engine_finished = False  # Track when engine is done thinking

        # Game over state
        self.game_over_reason = None  # "checkmate", "stalemate", or None

    def pos_to_pixel(self, row, col):
        """Convert board position to pixel coordinates."""
        return col * SQUARE_SIZE, row * SQUARE_SIZE

    def pixel_to_pos(self, x, y):
        """Convert pixel coordinates to board position."""
        col = x // SQUARE_SIZE
        row = y // SQUARE_SIZE
        if 0 <= row < 8 and 0 <= col < 8:
            return (row, col)
        return None

    def draw_board(self):
        """Draw the chessboard."""
        for row in range(8):
            for col in range(8):
                x, y = self.pos_to_pixel(row, col)
                color = WHITE_SQUARE if (row + col) % 2 == 0 else BLACK_SQUARE
                pygame.draw.rect(self.screen, color, (x, y, SQUARE_SIZE, SQUARE_SIZE))

    def draw_highlights(self):
        """Draw selected piece and valid move highlights."""
        # Highlight check - highlight the king that's in check
        if self.in_check:
            # Determine which king is in check based on whose turn it is
            # After human moves, it's engine's turn (black), so we highlight black king if in check
            # After engine moves, it's human's turn (white), so we highlight white king if in check
            king_pos = self.board._find_king(self.board.white_to_move)
            if king_pos:
                row, col = king_pos
                x, y = self.pos_to_pixel(row, col)
                pygame.draw.rect(self.screen, CHECK_COLOR, (x, y, SQUARE_SIZE, SQUARE_SIZE), 5)

        if self.selected_piece:
            row, col = self.selected_piece
            x, y = self.pos_to_pixel(row, col)
            pygame.draw.rect(self.screen, HIGHLIGHT_COLOR, (x, y, SQUARE_SIZE, SQUARE_SIZE), 4)

        for to_row, to_col in self.valid_moves:
            x, y = self.pos_to_pixel(to_row, to_col)
            pygame.draw.circle(
                self.screen, HIGHLIGHT_COLOR, (x + SQUARE_SIZE // 2, y + SQUARE_SIZE // 2), 8
            )

    def draw_pieces(self):
        """Draw all pieces on the board."""
        for row in range(8):
            for col in range(8):
                piece = self.board.get_piece(row, col)
                if piece:
                    symbol = PIECE_SYMBOLS[piece]
                    x, y = self.pos_to_pixel(row, col)
                    text = self.font.render(symbol, True, (0, 0, 0))
                    text_rect = text.get_rect(
                        center=(x + SQUARE_SIZE // 2, y + SQUARE_SIZE // 2)
                    )
                    self.screen.blit(text, text_rect)

    def draw_status(self):
        """Draw status message at bottom."""
        text = self.small_font.render(self.status_message, True, (0, 0, 0))
        # Draw on a background for readability
        bg_rect = text.get_rect()
        bg_rect.topleft = (10, WINDOW_SIZE - 30)
        pygame.draw.rect(self.screen, (200, 200, 200), bg_rect.inflate(10, 5))
        self.screen.blit(text, bg_rect.topleft)

    def draw_game_over_modal(self):
        """Draw game over modal popup."""
        if not self.game_over or not self.game_over_reason:
            return

        # Determine title and message
        if self.game_over_reason == "checkmate":
            title = "CHECKMATE!"
            message = "White wins!"
        else:
            title = "STALEMATE!"
            message = "Draw"

        # Draw semi-transparent overlay
        overlay = pygame.Surface((WINDOW_SIZE, WINDOW_SIZE))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        # Draw modal box
        modal_width = 400
        modal_height = 250
        modal_x = (WINDOW_SIZE - modal_width) // 2
        modal_y = (WINDOW_SIZE - modal_height) // 2

        pygame.draw.rect(self.screen, (255, 255, 255), (modal_x, modal_y, modal_width, modal_height))
        pygame.draw.rect(self.screen, (0, 0, 0), (modal_x, modal_y, modal_width, modal_height), 3)

        # Draw title
        title_font = pygame.font.Font(None, 48)
        title_text = title_font.render(title, True, (255, 0, 0))
        title_rect = title_text.get_rect(center=(WINDOW_SIZE // 2, modal_y + 50))
        self.screen.blit(title_text, title_rect)

        # Draw message
        message_text = self.small_font.render(message, True, (0, 0, 0))
        message_rect = message_text.get_rect(center=(WINDOW_SIZE // 2, modal_y + 120))
        self.screen.blit(message_text, message_rect)

        # Draw restart instruction
        restart_text = self.small_font.render("Press R to restart", True, (100, 100, 100))
        restart_rect = restart_text.get_rect(center=(WINDOW_SIZE // 2, modal_y + 180))
        self.screen.blit(restart_text, restart_rect)

    def handle_click(self, x, y):
        """Handle mouse click."""
        # Don't allow moves while engine is thinking
        if self.engine_thinking:
            return

        pos = self.pixel_to_pos(x, y)
        if not pos or self.game_over or not self.board.white_to_move:
            return

        row, col = pos
        piece = self.board.get_piece(row, col)

        if self.selected_piece:
            from_pos = self.selected_piece
            to_pos = (row, col)

            # Try to make the move
            if to_pos in self.valid_moves:
                # Check if it's a capture
                is_capture = self.board.get_piece(to_pos[0], to_pos[1]) is not None

                self.board.make_move(from_pos, to_pos)
                self.sounds.play_move(is_capture=is_capture)
                self.selected_piece = None
                self.valid_moves = []

                # Check if black king is in check
                black_king_pos = self.board._find_king(False)
                if black_king_pos:
                    self.in_check = self.board._is_square_attacked(*black_king_pos, True)
                    if self.in_check:
                        self.sounds.play_check()
                else:
                    self.in_check = False

                self.status_message = "Engine thinking..."
                self.engine_move()
            else:
                # Reselect a different piece
                if piece and self.board.is_white_piece(piece):
                    self.selected_piece = (row, col)
                    self.valid_moves = [move[1] for move in self.board.get_all_moves(True) if move[0] == (row, col)]
                else:
                    self.selected_piece = None
                    self.valid_moves = []
        else:
            # Select a piece
            if piece and self.board.is_white_piece(piece):
                self.selected_piece = (row, col)
                self.valid_moves = [move[1] for move in self.board.get_all_moves(True) if move[0] == (row, col)]
            else:
                self.selected_piece = None
                self.valid_moves = []

    def engine_move(self):
        """Start engine thinking in a separate thread."""
        if not self.engine_thinking:
            self.engine_thinking = True
            thread = threading.Thread(target=self._engine_think)
            thread.daemon = True
            thread.start()

    def _engine_think(self):
        """Engine thinking logic (runs in separate thread)."""
        # Make a copy of the board so engine doesn't modify the real one
        board_copy = copy.deepcopy(self.board)
        move = find_best_move(board_copy, self.engine_depth)
        self.pending_engine_move = move
        self.engine_finished = True

    def _apply_engine_move(self):
        """Apply the engine move to the board (runs in main thread)."""
        if self.pending_engine_move:
            move = self.pending_engine_move

            # Check if it's a capture
            is_capture = self.board.get_piece(move[1][0], move[1][1]) is not None

            self.board.make_move(move[0], move[1])
            self.sounds.play_move(is_capture=is_capture)

            # Check if white is now in check
            white_king_pos = self.board._find_king(True)
            if white_king_pos:
                self.in_check = self.board._is_square_attacked(*white_king_pos, False)
                if self.in_check:
                    self.sounds.play_check()
                    self.status_message = "Your move (White) - IN CHECK!"
                else:
                    self.status_message = "Your move (White)"
            else:
                self.status_message = "Your move (White)"
                self.in_check = False

            # Check if white has any legal moves
            white_moves = self.board.get_all_moves(True)
            if not white_moves:
                self.game_over = True
                if self.in_check:
                    self.game_over_reason = "checkmate"
                    self.status_message = "Checkmate! Black wins!"
                else:
                    self.game_over_reason = "stalemate"
                    self.status_message = "Stalemate!"

            self.pending_engine_move = None
        else:
            # No move available for engine - game over
            self.game_over = True
            if self.in_check:
                self.game_over_reason = "checkmate"
                self.status_message = "Checkmate! White wins!"
            else:
                self.game_over_reason = "stalemate"
                self.status_message = "Stalemate!"

        self.engine_thinking = False

    def run(self):
        """Main game loop."""
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    x, y = pygame.mouse.get_pos()
                    self.handle_click(x, y)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        self.board = Board()
                        self.selected_piece = None
                        self.valid_moves = []
                        self.game_over = False
                        self.game_over_reason = None
                        self.status_message = "Your move (White)"
                        self.in_check = False
                        self.engine_thinking = False
                        self.engine_finished = False
                        self.pending_engine_move = None

            # Check if engine move is ready
            if self.engine_finished:
                self._apply_engine_move()
                self.engine_finished = False

            self.screen.fill((200, 200, 200))
            self.draw_board()
            self.draw_highlights()
            self.draw_pieces()
            self.draw_status()
            self.draw_game_over_modal()

            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()
