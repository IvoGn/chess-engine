# Chess Engine

A fully functional chess engine built in Python with a graphical interface using Pygame. The engine plays chess with proper rule implementation including check detection, castling, and en passant.

## Features

- **Complete Chess Rules**: Implements all standard chess rules including:
  - Check and checkmate detection
  - Castling (kingside and queenside)
  - En passant captures
  - Pawn promotion (basic)
  
- **AI Engine**: Uses minimax algorithm with alpha-beta pruning for intelligent move selection
- **Graphical Interface**: Beautiful Pygame-based GUI with:
  - Visual chessboard with Unicode piece symbols
  - Real-time move validation
  - Check highlighting (red border on king in check)
  - Valid move indicators
  
- **Sound Effects**: Audio feedback for:
  - Regular moves (pleasant C5 note)
  - Piece captures (E5 note)
  - Check detection (ascending tone alert)

- **Game Modes**:
  - Human vs Engine (human plays white, engine plays black)
  - Automatic game over detection with modal popup for checkmate/stalemate

## Installation

### Requirements
- Python 3.7+
- pygame >= 2.1.0
- numpy >= 1.21.0

### Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/chess-engine.git
cd chess-engine
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the game:
```bash
python main.py
```

## How to Play

### Controls
- **Click a piece**: Select it (shows valid moves as green dots)
- **Click a square**: Move the selected piece there
- **Press R**: Restart the game

### Game Rules
- You play as **White** (pieces at bottom)
- The engine plays as **Black** (pieces at top)
- Standard chess rules apply
- When your king is in check, it's highlighted with a red border
- Game ends automatically with a checkmate/stalemate popup

## Project Structure

```
chess-engine/
├── main.py           # Entry point
├── board.py          # Chess board logic and move generation
├── engine.py         # AI engine (minimax + alpha-beta pruning)
├── gui.py            # Pygame interface
├── sounds.py         # Sound effects
├── test_features.py  # Feature tests
└── requirements.txt  # Dependencies
```

## Implementation Details

### Board Representation
- 8x8 array where each square contains either:
  - `None` (empty)
  - `(piece_type, is_white)` tuple

### Piece Types
- `'P'` = Pawn
- `'N'` = Knight
- `'B'` = Bishop
- `'R'` = Rook
- `'Q'` = Queen
- `'K'` = King

### Engine Algorithm
- **Minimax** with **Alpha-Beta Pruning** for efficient move search
- Configurable search depth (currently set to 4 plies)
- **Evaluation Function** using:
  - Piece material values
  - Piece-square position tables

### Move Validation
- Check detection prevents illegal moves
- King safety is enforced
- All special moves (castling, en passant) are validated

## Features Explained

### Check Detection
The engine detects if a king is under attack and prevents moves that leave the king in check or move it into check.

### Castling
Available when:
- King hasn't moved
- Rook hasn't moved
- Path is clear
- King is not in check
- King doesn't move through check

### En Passant
A pawn can capture another pawn that just double-advanced to an adjacent file, capturing it as if it had moved only one square.

## Future Enhancements

- Pawn promotion piece selection
- Move notation (algebraic notation)
- Game history/replay
- Difficulty levels
- Opening book
- Endgame tablebases
- Network multiplayer

## License

MIT License - feel free to use this project for learning or personal use.

## Author

Created as a portfolio project demonstrating:
- Game development (Pygame)
- AI/Game theory (minimax, alpha-beta pruning)
- Python programming
- Chess rule implementation

Built with ❤️ by Ivo Gunis

---

Feel free to fork, improve, and contribute!
