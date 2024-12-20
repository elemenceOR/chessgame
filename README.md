# Python Chess Game with Pygame

![image](https://github.com/user-attachments/assets/0c666410-d4d8-44ad-a211-9b1fa1bde735)

A fully-featured chess game implementation using Python and Pygame, featuring a modern UI design, timer functionality, and complete chess rules enforcement.

## Features
- Complete chess rules implementation using the python-chess library
- Modern, clean user interface with a pleasing color scheme

- Game features:

  - Move highlighting and legal move validation
  - Check and checkmate detection
  - Pawn promotion interface
  - Move history with undo/redo functionality
  - Last move highlights
  - Chess timer (10 minutes per player. Can be changed)
  - Resignation option
  - Coordinate notation display

- Visual feedback for:

  - Selected pieces
  - Legal moves
  - Check positions
  - Illegal moves
  - Last move made
  - Game end conditions

## Installation

1. Clone this repository:

```bash
git clone https://github.com/elemenceOR/chessgame.git
cd chessgame
```

2. Install the required packages:
```bash
pip install pygame python-chess
```

3. Set up the images folder:

Create an images directory in the project root
Add piece images with the following naming convention:

- Black pieces: p.png, r.png, n.png, b.png, q.png, k.png
- White pieces: wP.png, wR.png, wN.png, wB.png, wQ.png, wK.png

## Usage

Run the game:
```bash
python main.py
```
### Controls
- Click to select a piece and click again to move it
- Use the "New Game" button to start a fresh game
- Use "Undo" and "Redo" buttons to navigate through move history
- Click "Resign" to forfeit the current game

### Game Interface
- The game board is displayed in the center of the window
- Chess coordinates are shown around the board (a-h, 1-8)
- Player timers are displayed on the right side
- Control buttons are located below the board
- Last move notation is shown on the left side
- Game status messages appear at the top

## Features in Detail
### Timer System

- Each player starts with 10 minutes
- Timer counts down during the player's turn
- Game ends if a player runs out of time

### Move Validation

- Only legal chess moves are allowed
- Visual feedback for illegal moves
- Highlights for available moves of selected piece

### Game End Conditions

- Checkmate
- Stalemate
- Time out
- Resignation

### Move History

- Undo/Redo functionality
- Maintains complete game state
- Visual display of the last move made

## Code Structure

- ``ChessEngine``: Main game logic class
- ``Button``: UI button implementation
- ``PromotionMenu``: Pawn promotion interface
- ``ChessTimer``: Chess clock implementation

## UML
![Untitled diagram-2024-11-22-124417](https://github.com/user-attachments/assets/068dadad-90f8-4aae-b3b2-d28dcf2e593d)

## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.

## Future Work
- Improve notation display
    - add piece take (x)
    - add checkmate (#)
    - add castling (0-0-0, 0-0)
- Add draw method
    - draw by repetition (once side has the same move as last 3 moves)
- .......

## License

[MIT](https://choosealicense.com/licenses/mit/)

## Acknowledgments

- python-chess for chess logic
- Pygame for the graphics engine
