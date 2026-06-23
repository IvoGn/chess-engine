"""Chess engine - search and evaluation."""

PIECE_VALUES = {
    'P': 1,
    'N': 3,
    'B': 3,
    'R': 5,
    'Q': 9,
    'K': 0,
}

PIECE_SQUARE_TABLES = {
    'P': [
        [0, 0, 0, 0, 0, 0, 0, 0],
        [5, 10, 10, -20, -20, 10, 10, 5],
        [5, -5, -10, 0, 0, -10, -5, 5],
        [0, 0, 0, 20, 20, 0, 0, 0],
        [5, 5, 10, 25, 25, 10, 5, 5],
        [10, 10, 20, 30, 30, 20, 10, 10],
        [50, 50, 50, 50, 50, 50, 50, 50],
        [0, 0, 0, 0, 0, 0, 0, 0],
    ],
    'N': [
        [-50, -40, -30, -30, -30, -30, -40, -50],
        [-40, -20, 0, 0, 0, 0, -20, -40],
        [-30, 0, 10, 15, 15, 10, 0, -30],
        [-30, 5, 15, 20, 20, 15, 5, -30],
        [-30, 0, 15, 20, 20, 15, 0, -30],
        [-30, 5, 10, 15, 15, 10, 5, -30],
        [-40, -20, 0, 5, 5, 0, -20, -40],
        [-50, -40, -30, -30, -30, -30, -40, -50],
    ],
    'B': [
        [-20, -10, -10, -10, -10, -10, -10, -20],
        [-10, 0, 0, 0, 0, 0, 0, -10],
        [-10, 0, 5, 10, 10, 5, 0, -10],
        [-10, 5, 5, 10, 10, 5, 5, -10],
        [-10, 0, 10, 10, 10, 10, 0, -10],
        [-10, 10, 10, 10, 10, 10, 10, -10],
        [-10, 5, 0, 0, 0, 0, 5, -10],
        [-20, -10, -10, -10, -10, -10, -10, -20],
    ],
    'R': [
        [0, 0, 0, 0, 0, 0, 0, 0],
        [5, 10, 10, 10, 10, 10, 10, 5],
        [-5, 0, 0, 0, 0, 0, 0, -5],
        [-5, 0, 0, 0, 0, 0, 0, -5],
        [-5, 0, 0, 0, 0, 0, 0, -5],
        [-5, 0, 0, 0, 0, 0, 0, -5],
        [-5, 0, 0, 0, 0, 0, 0, -5],
        [0, 0, 0, 5, 5, 0, 0, 0],
    ],
}


def evaluate(board):
    """Evaluate board position. Positive = white advantage, negative = black advantage."""
    score = 0

    for row in range(8):
        for col in range(8):
            piece = board.get_piece(row, col)
            if piece:
                piece_type, is_white = piece
                piece_value = PIECE_VALUES[piece_type]

                # Piece-square table bonus
                table = PIECE_SQUARE_TABLES.get(piece_type)
                if table:
                    if is_white:
                        square_bonus = table[row][col]
                    else:
                        square_bonus = table[7 - row][col]
                else:
                    square_bonus = 0

                piece_score = piece_value + square_bonus
                score += piece_score if is_white else -piece_score

    return score


def minimax(board, depth, is_white, alpha=float('-inf'), beta=float('inf')):
    """Minimax with alpha-beta pruning."""

    if depth == 0:
        return evaluate(board)

    moves = board.get_all_moves(is_white)

    if not moves:
        return evaluate(board)

    if is_white:
        max_eval = float('-inf')
        for from_pos, to_pos in moves:
            board.make_move(from_pos, to_pos)
            eval_score = minimax(board, depth - 1, False, alpha, beta)
            board.undo_move()

            max_eval = max(max_eval, eval_score)
            alpha = max(alpha, eval_score)
            if beta <= alpha:
                break

        return max_eval
    else:
        min_eval = float('inf')
        for from_pos, to_pos in moves:
            board.make_move(from_pos, to_pos)
            eval_score = minimax(board, depth - 1, True, alpha, beta)
            board.undo_move()

            min_eval = min(min_eval, eval_score)
            beta = min(beta, eval_score)
            if beta <= alpha:
                break

        return min_eval


def find_best_move(board, depth):
    """Find best move for current side using minimax."""
    moves = board.get_all_moves(board.white_to_move)

    if not moves:
        return None

    best_move = None
    best_score = float('-inf') if board.white_to_move else float('inf')

    for from_pos, to_pos in moves:
        board.make_move(from_pos, to_pos)
        score = minimax(board, depth - 1, not board.white_to_move)
        board.undo_move()

        if board.white_to_move:
            if score > best_score:
                best_score = score
                best_move = (from_pos, to_pos)
        else:
            if score < best_score:
                best_score = score
                best_move = (from_pos, to_pos)

    return best_move
