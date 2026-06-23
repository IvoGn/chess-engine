class Board:
    """Chess board representation using 8x8 array."""

    def __init__(self):
        self.board = self._init_board()
        self.white_to_move = True
        self.move_history = []

        # Castling rights
        self.white_kingside_castling = True
        self.white_queenside_castling = True
        self.black_kingside_castling = True
        self.black_queenside_castling = True

        # En passant target square (or None)
        self.en_passant_target = None

    def _init_board(self):
        """Initialize standard chess starting position."""
        board = [[None for _ in range(8)] for _ in range(8)]

        # Set up pieces: (piece_type, color) where color is True=white, False=black
        # Pawns
        for col in range(8):
            board[1][col] = ('P', False)
            board[6][col] = ('P', True)

        # Rooks
        board[0][0] = ('R', False)
        board[0][7] = ('R', False)
        board[7][0] = ('R', True)
        board[7][7] = ('R', True)

        # Knights
        board[0][1] = ('N', False)
        board[0][6] = ('N', False)
        board[7][1] = ('N', True)
        board[7][6] = ('N', True)

        # Bishops
        board[0][2] = ('B', False)
        board[0][5] = ('B', False)
        board[7][2] = ('B', True)
        board[7][5] = ('B', True)

        # Queens
        board[0][3] = ('Q', False)
        board[7][3] = ('Q', True)

        # Kings
        board[0][4] = ('K', False)
        board[7][4] = ('K', True)

        return board

    def get_piece(self, row, col):
        """Get piece at position (row, col)."""
        if 0 <= row < 8 and 0 <= col < 8:
            return self.board[row][col]
        return None

    def is_white_piece(self, piece):
        """Check if piece belongs to white."""
        return piece and piece[1] is True

    def is_black_piece(self, piece):
        """Check if piece belongs to black."""
        return piece and piece[1] is False

    def is_empty(self, row, col):
        """Check if square is empty."""
        return self.get_piece(row, col) is None

    def can_capture(self, piece, target_piece):
        """Check if piece can capture target piece."""
        if not target_piece:
            return True
        return self.is_white_piece(piece) != self.is_white_piece(target_piece)

    def get_all_moves(self, color_white):
        """Generate all legal moves for a color. Returns list of (from_pos, to_pos) tuples."""
        moves = []

        for row in range(8):
            for col in range(8):
                piece = self.get_piece(row, col)
                if piece and self.is_white_piece(piece) == color_white:
                    moves.extend(self._get_piece_moves(row, col))

        # Filter out moves that leave king in check
        legal_moves = []
        for from_pos, to_pos in moves:
            if self._is_legal_move(from_pos, to_pos, color_white):
                legal_moves.append((from_pos, to_pos))

        return legal_moves

    def _get_piece_moves(self, row, col):
        """Get pseudo-legal moves for piece at (row, col)."""
        piece = self.get_piece(row, col)
        if not piece:
            return []

        piece_type, color = piece
        moves = []

        if piece_type == 'P':
            moves = self._get_pawn_moves(row, col, color)
        elif piece_type == 'N':
            moves = self._get_knight_moves(row, col, piece)
        elif piece_type == 'B':
            moves = self._get_bishop_moves(row, col, piece)
        elif piece_type == 'R':
            moves = self._get_rook_moves(row, col, piece)
        elif piece_type == 'Q':
            moves = self._get_queen_moves(row, col, piece)
        elif piece_type == 'K':
            moves = self._get_king_moves(row, col, piece)

        return [((row, col), (to_row, to_col)) for to_row, to_col in moves]

    def _get_pawn_moves(self, row, col, is_white):
        """Get pawn moves including en passant."""
        moves = []
        direction = -1 if is_white else 1
        start_row = 6 if is_white else 1
        ep_row = 3 if is_white else 4  # Row where en passant capture happens

        # Forward move
        new_row = row + direction
        if 0 <= new_row < 8 and self.is_empty(new_row, col):
            moves.append((new_row, col))

            # Double move from start
            if row == start_row:
                double_row = row + 2 * direction
                if self.is_empty(double_row, col):
                    moves.append((double_row, col))

        # Captures
        for dc in [-1, 1]:
            new_col = col + dc
            new_row = row + direction
            if 0 <= new_row < 8 and 0 <= new_col < 8:
                target = self.get_piece(new_row, new_col)
                if target and self.is_white_piece(target) != is_white:
                    moves.append((new_row, new_col))

        # En passant captures
        if self.en_passant_target and row == ep_row:
            ep_row_target, ep_col_target = self.en_passant_target
            if ep_row_target == row + direction and (ep_col_target == col - 1 or ep_col_target == col + 1):
                moves.append(self.en_passant_target)

        return moves

    def _get_knight_moves(self, row, col, piece):
        """Get knight moves."""
        moves = []
        knight_deltas = [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]

        for dr, dc in knight_deltas:
            new_row, new_col = row + dr, col + dc
            if 0 <= new_row < 8 and 0 <= new_col < 8:
                target = self.get_piece(new_row, new_col)
                if self.can_capture(piece, target):
                    moves.append((new_row, new_col))

        return moves

    def _get_bishop_moves(self, row, col, piece):
        """Get bishop moves."""
        return self._get_sliding_moves(row, col, piece, [(-1, -1), (-1, 1), (1, -1), (1, 1)])

    def _get_rook_moves(self, row, col, piece):
        """Get rook moves."""
        return self._get_sliding_moves(row, col, piece, [(-1, 0), (1, 0), (0, -1), (0, 1)])

    def _get_queen_moves(self, row, col, piece):
        """Get queen moves."""
        directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
        return self._get_sliding_moves(row, col, piece, directions)

    def _get_sliding_moves(self, row, col, piece, directions):
        """Get sliding moves in given directions."""
        moves = []

        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc
            while 0 <= new_row < 8 and 0 <= new_col < 8:
                target = self.get_piece(new_row, new_col)
                if self.can_capture(piece, target):
                    moves.append((new_row, new_col))
                    if target:  # Capture stops the slide
                        break
                else:
                    break
                new_row += dr
                new_col += dc

        return moves

    def _get_king_moves(self, row, col, piece):
        """Get king moves including castling."""
        moves = []
        is_white = self.is_white_piece(piece)
        king_deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

        # Regular king moves
        for dr, dc in king_deltas:
            new_row, new_col = row + dr, col + dc
            if 0 <= new_row < 8 and 0 <= new_col < 8:
                target = self.get_piece(new_row, new_col)
                if self.can_capture(piece, target):
                    moves.append((new_row, new_col))

        # Castling moves
        if is_white:
            # Kingside castling (e1 -> g1)
            if self.white_kingside_castling and not self._is_square_attacked(row, col, not is_white):
                if self.is_empty(row, 5) and self.is_empty(row, 6):
                    if not self._is_square_attacked(row, 5, not is_white):
                        moves.append((row, 6))
            # Queenside castling (e1 -> c1)
            if self.white_queenside_castling and not self._is_square_attacked(row, col, not is_white):
                if self.is_empty(row, 1) and self.is_empty(row, 2) and self.is_empty(row, 3):
                    if not self._is_square_attacked(row, 3, not is_white):
                        moves.append((row, 2))
        else:
            # Kingside castling (e8 -> g8)
            if self.black_kingside_castling and not self._is_square_attacked(row, col, not is_white):
                if self.is_empty(row, 5) and self.is_empty(row, 6):
                    if not self._is_square_attacked(row, 5, not is_white):
                        moves.append((row, 6))
            # Queenside castling (e8 -> c8)
            if self.black_queenside_castling and not self._is_square_attacked(row, col, not is_white):
                if self.is_empty(row, 1) and self.is_empty(row, 2) and self.is_empty(row, 3):
                    if not self._is_square_attacked(row, 3, not is_white):
                        moves.append((row, 2))

        return moves

    def _find_king(self, is_white):
        """Find king position for given color."""
        for row in range(8):
            for col in range(8):
                piece = self.get_piece(row, col)
                if piece and piece[0] == 'K' and self.is_white_piece(piece) == is_white:
                    return (row, col)
        return None

    def _is_square_attacked(self, row, col, by_white):
        """Check if square is attacked by pieces of given color."""
        for r in range(8):
            for c in range(8):
                piece = self.get_piece(r, c)
                if not piece or self.is_white_piece(piece) != by_white:
                    continue

                piece_type = piece[0]

                # Pawn attacks
                if piece_type == 'P':
                    direction = -1 if by_white else 1
                    for dc in [-1, 1]:
                        if r + direction == row and c + dc == col:
                            return True

                # Knight attacks
                elif piece_type == 'N':
                    knight_deltas = [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]
                    for dr, dc in knight_deltas:
                        if r + dr == row and c + dc == col:
                            return True

                # Bishop attacks
                elif piece_type == 'B':
                    for dr, dc in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
                        nr, nc = r + dr, c + dc
                        while 0 <= nr < 8 and 0 <= nc < 8:
                            if nr == row and nc == col:
                                return True
                            if self.get_piece(nr, nc):
                                break
                            nr += dr
                            nc += dc

                # Rook attacks
                elif piece_type == 'R':
                    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        nr, nc = r + dr, c + dc
                        while 0 <= nr < 8 and 0 <= nc < 8:
                            if nr == row and nc == col:
                                return True
                            if self.get_piece(nr, nc):
                                break
                            nr += dr
                            nc += dc

                # Queen attacks
                elif piece_type == 'Q':
                    for dr, dc in [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]:
                        nr, nc = r + dr, c + dc
                        while 0 <= nr < 8 and 0 <= nc < 8:
                            if nr == row and nc == col:
                                return True
                            if self.get_piece(nr, nc):
                                break
                            nr += dr
                            nc += dc

                # King attacks
                elif piece_type == 'K':
                    for dr in [-1, 0, 1]:
                        for dc in [-1, 0, 1]:
                            if dr == 0 and dc == 0:
                                continue
                            if r + dr == row and c + dc == col:
                                return True

        return False

    def _is_legal_move(self, from_pos, to_pos, color_white):
        """Check if move is legal (doesn't leave king in check)."""
        # Check for self-capture
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        piece = self.get_piece(from_row, from_col)
        target = self.get_piece(to_row, to_col)

        if target and self.is_white_piece(target) == color_white:
            return False

        # Simulate move
        self.board[to_row][to_col] = piece
        self.board[from_row][from_col] = None

        # Find king and check if under attack
        king_pos = self._find_king(color_white)
        if not king_pos:
            # Restore board
            self.board[from_row][from_col] = piece
            self.board[to_row][to_col] = target
            return False

        king_row, king_col = king_pos
        legal = not self._is_square_attacked(king_row, king_col, not color_white)

        # Restore board
        self.board[from_row][from_col] = piece
        self.board[to_row][to_col] = target

        return legal

    def make_move(self, from_pos, to_pos):
        """Make a move on the board."""
        from_row, from_col = from_pos
        to_row, to_col = to_pos

        piece = self.get_piece(from_row, from_col)
        if not piece:
            return False

        captured_piece = self.get_piece(to_row, to_col)

        # Store castling and en passant state before move
        castling_rights_before = (
            self.white_kingside_castling,
            self.white_queenside_castling,
            self.black_kingside_castling,
            self.black_queenside_castling,
        )
        en_passant_target_before = self.en_passant_target

        # Make the move
        self.board[to_row][to_col] = piece
        self.board[from_row][from_col] = None

        # Handle en passant capture
        if piece[0] == 'P' and self.en_passant_target and (to_row, to_col) == self.en_passant_target:
            # Remove captured pawn
            capture_row = from_row
            self.board[capture_row][to_col] = None
            captured_piece = ('P', not piece[1])

        # Handle castling
        if piece[0] == 'K' and abs(to_col - from_col) == 2:
            # King moved 2 squares - handle rook
            if to_col > from_col:  # Kingside castling
                rook = self.get_piece(to_row, 7)
                self.board[to_row][5] = rook
                self.board[to_row][7] = None
            else:  # Queenside castling
                rook = self.get_piece(to_row, 0)
                self.board[to_row][3] = rook
                self.board[to_row][0] = None

        # Update castling rights
        if piece[0] == 'K':
            if piece[1]:  # White king
                self.white_kingside_castling = False
                self.white_queenside_castling = False
            else:  # Black king
                self.black_kingside_castling = False
                self.black_queenside_castling = False
        elif piece[0] == 'R':
            if piece[1]:  # White rook
                if from_row == 7:
                    if from_col == 0:
                        self.white_queenside_castling = False
                    elif from_col == 7:
                        self.white_kingside_castling = False
            else:  # Black rook
                if from_row == 0:
                    if from_col == 0:
                        self.black_queenside_castling = False
                    elif from_col == 7:
                        self.black_kingside_castling = False

        # Handle capturing rook
        if captured_piece and captured_piece[0] == 'R':
            if captured_piece[1]:  # Captured white rook
                if to_row == 7:
                    if to_col == 0:
                        self.white_queenside_castling = False
                    elif to_col == 7:
                        self.white_kingside_castling = False
            else:  # Captured black rook
                if to_row == 0:
                    if to_col == 0:
                        self.black_queenside_castling = False
                    elif to_col == 7:
                        self.black_kingside_castling = False

        # Set en passant target for next move
        if piece[0] == 'P' and abs(to_row - from_row) == 2:
            # Pawn double-advanced
            self.en_passant_target = (from_row + (to_row - from_row) // 2, to_col)
        else:
            self.en_passant_target = None

        # Store move in history
        self.move_history.append((from_pos, to_pos, captured_piece, castling_rights_before, en_passant_target_before))
        self.white_to_move = not self.white_to_move
        return True

    def undo_move(self):
        """Undo last move."""
        if not self.move_history:
            return False

        from_pos, to_pos, captured_piece, castling_rights_before, en_passant_target_before = self.move_history.pop()
        from_row, from_col = from_pos
        to_row, to_col = to_pos

        piece = self.get_piece(to_row, to_col)

        # Restore piece to original position
        self.board[from_row][from_col] = piece
        self.board[to_row][to_col] = captured_piece

        # Handle castling undo
        if piece and piece[0] == 'K' and abs(to_col - from_col) == 2:
            if to_col > from_col:  # Kingside castling
                rook = self.get_piece(to_row, 5)
                self.board[to_row][7] = rook
                self.board[to_row][5] = None
            else:  # Queenside castling
                rook = self.get_piece(to_row, 3)
                self.board[to_row][0] = rook
                self.board[to_row][3] = None

        # Handle en passant undo
        if piece and piece[0] == 'P' and en_passant_target_before and (to_row, to_col) == en_passant_target_before:
            # Restore captured pawn
            capture_row = from_row
            captured_pawn_color = not piece[1]
            self.board[capture_row][to_col] = ('P', captured_pawn_color)

        # Restore castling and en passant state
        (
            self.white_kingside_castling,
            self.white_queenside_castling,
            self.black_kingside_castling,
            self.black_queenside_castling,
        ) = castling_rights_before
        self.en_passant_target = en_passant_target_before

        self.white_to_move = not self.white_to_move
        return True

    def __str__(self):
        """String representation of board."""
        output = "  a b c d e f g h\n"
        for row in range(8):
            output += f"{8-row} "
            for col in range(8):
                piece = self.get_piece(row, col)
                if piece:
                    symbol = piece[0]
                    symbol = symbol.upper() if piece[1] else symbol.lower()
                    output += symbol + " "
                else:
                    output += ". "
            output += f"{8-row}\n"
        output += "  a b c d e f g h\n"
        return output
