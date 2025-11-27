import pygame
import chess
import time

pygame.init()

# Color Constants
DARK_SQUARE = (118, 150, 86)      # Darker green
LIGHT_SQUARE = (238, 238, 210)    # Light beige
BACKGROUND = (40, 40, 40)         # Dark gray background
HIGHLIGHT_BLUE = (0, 0, 255)      # Selected Piece
HIGHLIGHT_YELLOW = (255, 255, 0)  # Move, Check
HIGHLIGHT_RED = (220, 80, 80)     # Checkmate, Illegal
TEXT_COLOR = (230, 230, 230)      # Off-white
BUTTON_COLOR = (70, 70, 70)       # Medium gray
BUTTON_HOVER_COLOR = (90, 90, 90) # Lighter gray for hover
BUTTON_TEXT = (230, 230, 230)     # Off-white text

# Display Constants
WIDTH, HEIGHT = 800, 700
BOARD_SIZE = 480
SQUARE = BOARD_SIZE // 8
BOARD_OFFSET_X = (WIDTH - BOARD_SIZE) // 2
BOARD_OFFSET_Y = (HEIGHT - BOARD_SIZE) // 2
FPS = 60

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("ChessGame")
clock = pygame.time.Clock()

# Load and scale piece images
pieces_images = {
    'p': pygame.transform.scale(pygame.image.load(f"images/p.png"), (SQUARE, SQUARE)),
    'r': pygame.transform.scale(pygame.image.load(f"images/r.png"), (SQUARE, SQUARE)),
    'n': pygame.transform.scale(pygame.image.load(f"images/n.png"), (SQUARE, SQUARE)),
    'b': pygame.transform.scale(pygame.image.load(f"images/b.png"), (SQUARE, SQUARE)),
    'q': pygame.transform.scale(pygame.image.load(f"images/q.png"), (SQUARE, SQUARE)),
    'k': pygame.transform.scale(pygame.image.load(f"images/k.png"), (SQUARE, SQUARE)),
    'P': pygame.transform.scale(pygame.image.load(f"images/wP.png"), (SQUARE, SQUARE)),
    'R': pygame.transform.scale(pygame.image.load(f"images/wR.png"), (SQUARE, SQUARE)),
    'N': pygame.transform.scale(pygame.image.load(f"images/wN.png"), (SQUARE, SQUARE)),
    'B': pygame.transform.scale(pygame.image.load(f"images/wB.png"), (SQUARE, SQUARE)),
    'Q': pygame.transform.scale(pygame.image.load(f"images/wQ.png"), (SQUARE, SQUARE)),
    'K': pygame.transform.scale(pygame.image.load(f"images/wK.png"), (SQUARE, SQUARE))
}

class Button:
    """Represents a clickable button in the UI."""
    def __init__(self, x, y, width, height, text, color, text_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.text_color = text_color
        self.hover = False
        self.font = pygame.font.Font(None, 28)

    def draw(self, surface):
        color = BUTTON_HOVER_COLOR if self.hover else self.color
        # Draw button with rounded corners
        pygame.draw.rect(surface, color, self.rect, border_radius=5)
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def update_hover(self, pos):
        self.hover = self.rect.collidepoint(pos)
    
    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

class PromotionMenu:
    """Handles pawn promotion UI when a pawn reaches the final rank."""
    def __init__(self, square, is_white):
        self.square = square
        self.is_white = is_white
        pieces = ['Q', 'R', 'N', 'B'] if is_white else ['q', 'r', 'n', 'b']
        
        menu_x = chess.square_file(square) * SQUARE + BOARD_OFFSET_X
        menu_y = (7 - chess.square_rank(square)) * SQUARE + BOARD_OFFSET_Y
        
        # Reverse piece order for black pawns promoting from rank 1
        if not is_white:
            menu_y -= 3 * SQUARE
            pieces = pieces[::-1]
        
        self.pieces = pieces
        self.rect = pygame.Rect(menu_x, menu_y, SQUARE, SQUARE * 4)

    def draw(self, screen):
        for i, piece in enumerate(self.pieces):
            piece_rect = pygame.Rect(
                self.rect.x,
                self.rect.y + (i * SQUARE),
                SQUARE,
                SQUARE
            )
            pygame.draw.rect(screen, LIGHT_SQUARE, piece_rect)
            pygame.draw.rect(screen, BACKGROUND, piece_rect, 1)
            screen.blit(pieces_images[piece], piece_rect)

    def handle_click(self, pos):
        if not self.rect.collidepoint(pos):
            return None
        
        clicked_index = (pos[1] - self.rect.y) // SQUARE
        if 0 <= clicked_index < len(self.pieces):
            return self.pieces[clicked_index]
        return None

class ChessTimer:
    """Manages game timer for both players."""
    def __init__(self, initial_time_minutes=10):
            self.initial_time = initial_time_minutes * 60  
            self.white_time = self.initial_time
            self.black_time = self.initial_time
            self.last_update = time.time()
            self.running = False
            self.current_player = chess.WHITE
            self.font = pygame.font.Font(None, 36)

    def start(self):
        """Start the timer."""
        self.running = True
        self.last_update = time.time()

    def stop(self):
        """Stop the timer."""
        self.running = False

    def reset(self):
        """Reset the timer to initial time."""
        self.white_time = self.initial_time
        self.black_time = self.initial_time
        self.running = False

    def switch_player(self):
        """Switch the active player's timer."""
        self.current_player = not self.current_player
        self.last_update = time.time()

    def update(self):
        """Update the current player's remaining time."""
        if self.running:
            current_time = time.time()
            elapsed = current_time - self.last_update
            if self.current_player == chess.WHITE:
                self.white_time -= elapsed
            else:
                self.black_time -= elapsed
            self.last_update = current_time

    def is_time_up(self):
        """Check if either player has run out of time."""
        return self.white_time <= 0 or self.black_time <= 0

    def get_time_str(self, seconds):
        """Format seconds as MM:SS string."""
        minutes = int(seconds // 60)
        seconds = int(seconds % 60)
        return f"{minutes:02d}:{seconds:02d}"

    def draw(self, screen):
        """Draw the timer display on screen."""
        # White's timer
        white_text = self.font.render(f"{self.get_time_str(max(0, self.white_time))}", True, TEXT_COLOR)
        screen.blit(white_text, (WIDTH - 120, BOARD_OFFSET_Y + 5))

        # Black's timer
        black_text = self.font.render(f"{self.get_time_str(max(0, self.black_time))}", True, TEXT_COLOR)
        screen.blit(black_text, (WIDTH - 120, BOARD_OFFSET_Y + BOARD_SIZE - 35))

class ChessEngine:
    """Main chess game engine handling board state, moves, and UI rendering."""
    def __init__(self):
        self.board = chess.Board()
        self.selected_square = None
        self.game_over = False
        self.font = pygame.font.Font(None, 32)
        
        self._init_buttons()
        
        self.promotion_menu = None
        self.pending_promotion_move = None
        self.illegal_move_squares = None
        self.illegal_move_time = 0
        self.illegal_move_duration = 0.5
        self.board_history = [chess.Board().fen()]
        self.current_position = 0
        self.last_move = None
        self.timer = ChessTimer()
        self.game_started = False
        self.highlighted_moves = []
        self.resigned = False
        self.winner_by_resignation = None
    
    def _init_buttons(self):
        """Initialize UI buttons."""
        button_width = 120
        button_height = 35
        button_spacing = 20
        buttons_total_width = 3 * button_width + 2 * button_spacing
        buttons_start_x = (WIDTH - buttons_total_width) // 2
        buttons_y = BOARD_OFFSET_Y + BOARD_SIZE + 30

        self.reset_button = Button(
            buttons_start_x, 
            buttons_y,
            button_width, 
            button_height,
            "New Game",
            BUTTON_COLOR,
            BUTTON_TEXT
        )
        
        self.undo_button = Button(
            buttons_start_x + button_width + button_spacing,
            buttons_y,
            button_width,
            button_height,
            "Undo",
            BUTTON_COLOR,
            BUTTON_TEXT
        )
        
        self.redo_button = Button(
            buttons_start_x + 2 * (button_width + button_spacing),
            buttons_y,
            button_width,
            button_height,
            "Redo",
            BUTTON_COLOR,
            BUTTON_TEXT
        )
        
        self.resign_button = Button(
            WIDTH - 120,
            HEIGHT // 2 - 20,
            100,
            40,
            "Resign",
            HIGHLIGHT_RED,
            TEXT_COLOR
        )
        
        self.promotion_menu = None
        self.pending_promotion_move = None
        self.illegal_move_squares = None
        self.illegal_move_time = 0
        self.illegal_move_duration = 0.5
        self.board_history = [chess.Board().fen()]
        self.current_position = 0
        self.last_move = None
        self.last_move_was_capture = False
        self.timer = ChessTimer()
        self.game_started = False
        self.highlighted_moves = []
        self.resigned = False
        self.winner_by_resignation = None

    def draw_board(self):
        """Draw the chess board with squares and coordinates."""
        # Draw board background
        board_background = pygame.Rect(
            BOARD_OFFSET_X - 20,
            BOARD_OFFSET_Y - 20,
            BOARD_SIZE + 40,
            BOARD_SIZE + 40
        )
        pygame.draw.rect(screen, (60, 60, 60), board_background, border_radius=10)
        
        # Draw squares
        colors = [LIGHT_SQUARE, DARK_SQUARE]
        for row in range(8):
            for col in range(8):
                color = colors[(row + col) % 2]
                pygame.draw.rect(
                    screen,
                    color,
                    pygame.Rect(
                        BOARD_OFFSET_X + col * SQUARE,
                        BOARD_OFFSET_Y + row * SQUARE,
                        SQUARE,
                        SQUARE
                    )
                )
        
        # Draw coordinates
        coord_font = pygame.font.Font(None, 24)
        for i in range(8):
            # Draw file labels (a-h)
            file_label = coord_font.render(chess.FILE_NAMES[i], True, TEXT_COLOR)
            x = BOARD_OFFSET_X + i * SQUARE + SQUARE//2 - file_label.get_width()//2
            screen.blit(file_label, (x, BOARD_OFFSET_Y + BOARD_SIZE + 5))
            
            # Draw rank labels (1-8)
            rank_label = coord_font.render(str(8-i), True, TEXT_COLOR)
            y = BOARD_OFFSET_Y + i * SQUARE + SQUARE//2 - rank_label.get_height()//2
            screen.blit(rank_label, (BOARD_OFFSET_X - 20, y))
        
        if self.selected_square is not None:
            row, col = chess.square_rank(self.selected_square), chess.square_file(self.selected_square)
            pygame.draw.rect(screen, HIGHLIGHT_BLUE, pygame.Rect(BOARD_OFFSET_X + col * SQUARE, BOARD_OFFSET_Y + (7 - row) * SQUARE, SQUARE, SQUARE), 5)

        if self.illegal_move_squares and time.time() - self.illegal_move_time < self.illegal_move_duration:
            for square in self.illegal_move_squares:
                row, col = chess.square_rank(square), chess.square_file(square)
                pygame.draw.rect(screen, HIGHLIGHT_RED, pygame.Rect(BOARD_OFFSET_X + col * SQUARE, BOARD_OFFSET_Y + (7 - row) * SQUARE, SQUARE, SQUARE), 5)
        else:
            self.illegal_move_squares = None

        for move in self.highlighted_moves:
            from_row, from_col = chess.square_rank(move.from_square), chess.square_file(move.from_square)
            to_row, to_col = chess.square_rank(move.to_square), chess.square_file(move.to_square)
            pygame.draw.rect(screen, HIGHLIGHT_YELLOW, pygame.Rect(BOARD_OFFSET_X + to_col * SQUARE, BOARD_OFFSET_Y + (7 - to_row) * SQUARE, SQUARE, SQUARE), 5)

    def draw_pieces(self):
        """Draw all pieces on the board."""
        for square in chess.SQUARES:
            piece = self.board.piece_at(square)
            if piece:
                file, rank = chess.square_file(square), chess.square_rank(square)
                x = BOARD_OFFSET_X + file * SQUARE
                y = BOARD_OFFSET_Y + (7 - rank) * SQUARE
                piece_image = pieces_images[piece.symbol()]
                screen.blit(piece_image, (x, y))

    def draw_game_state(self):
        """Draw game state indicators like check, checkmate, and move notation."""
        king_square = self.board.king(self.board.turn)
        col, row = chess.square_file(king_square), 7 - chess.square_rank(king_square)

        if self.last_move:
            from_file, from_rank = chess.square_file(self.last_move.from_square), chess.square_rank(self.last_move.from_square)
            to_file, to_rank = chess.square_file(self.last_move.to_square), chess.square_rank(self.last_move.to_square)

            # Determine move notation
            if self.last_move.from_square == chess.E1 and self.last_move.to_square == chess.G1:
                notation = "w.O-O"
            elif self.last_move.from_square == chess.E1 and self.last_move.to_square == chess.C1:
                notation = "w.O-O-O"
            elif self.last_move.from_square == chess.E8 and self.last_move.to_square == chess.G8:
                notation = "b.O-O"
            elif self.last_move.from_square == chess.E8 and self.last_move.to_square == chess.C8:
                notation = "b.O-O-O"
            else:
                piece = self.board.piece_at(self.last_move.to_square)
                piece_name = piece.symbol().upper() if piece else ""
                if piece_name == 'P':
                    piece_name = ""
                
                capture_symbol = "x" if self.last_move_was_capture else ""

                notation = f"{piece_name}{chess.square_name(self.last_move.from_square)}{capture_symbol}{chess.square_name(self.last_move.to_square)}"
            
            # Add checkmate or check symbol
            if self.board.is_checkmate():
                notation += "#"
            elif self.board.is_check():
                notation += "+"

            last_move_surface = self.font.render(notation, True, TEXT_COLOR)
            last_move_rect = last_move_surface.get_rect(topleft=(WIDTH - 760, HEIGHT // 2 - 10))
            screen.blit(last_move_surface, last_move_rect)
            
            # Highlight last move squares
            pygame.draw.rect(
                screen,
                HIGHLIGHT_YELLOW,
                pygame.Rect(
                    BOARD_OFFSET_X + from_file * SQUARE,
                    BOARD_OFFSET_Y + (7 - from_rank) * SQUARE,
                    SQUARE,
                    SQUARE
                ),
                5
            )
            pygame.draw.rect(
                screen,
                HIGHLIGHT_YELLOW,
                pygame.Rect(
                    BOARD_OFFSET_X + to_file * SQUARE,
                    BOARD_OFFSET_Y + (7 - to_rank) * SQUARE,
                    SQUARE,
                    SQUARE
                ),
                5
            )
        
        # Draw game status messages
        status_text = ""
        if self.resigned:
            status_text = "White resigns! Black wins!" if self.winner_by_resignation == chess.BLACK else "Black resigns! White wins!"
        elif self.timer.white_time <= 0:
            status_text = "Black wins on time!"
        elif self.timer.black_time <= 0:
            status_text = "White wins on time!"
        elif self.board.is_checkmate():
            status_text = "0-1" if self.board.turn == chess.WHITE else "1-0"
            pygame.draw.rect(screen, HIGHLIGHT_RED, pygame.Rect(BOARD_OFFSET_X + col * SQUARE, BOARD_OFFSET_Y + (row) * SQUARE, SQUARE, SQUARE), 5)
        elif self.board.is_stalemate():
            status_text = "Stalemate"
        elif self.board.is_variant_draw():
            status_text = "1/2-1/2"
            pygame.draw.rect(screen, HIGHLIGHT_RED, pygame.Rect(BOARD_OFFSET_X + col * SQUARE, BOARD_OFFSET_Y + (row) * SQUARE, SQUARE, SQUARE), 5)
        elif self.board.is_check():
            pygame.draw.rect(screen, HIGHLIGHT_YELLOW, pygame.Rect(BOARD_OFFSET_X + col * SQUARE, BOARD_OFFSET_Y + (row) * SQUARE, SQUARE, SQUARE), 5)
            return
        
        if status_text:
            text_surface = self.font.render(status_text, True, TEXT_COLOR)
            text_rect = text_surface.get_rect(center=(WIDTH//2, 30))
            bg_rect = text_rect.copy()
            bg_rect.inflate_ip(20, 10)
            pygame.draw.rect(screen, (*BACKGROUND, 200), bg_rect, border_radius=5)
            screen.blit(text_surface, text_rect)

    def draw(self):
        """Main draw method that renders all game elements."""
        screen.fill(BACKGROUND)
        self.draw_board()
        self.draw_pieces()
        self.draw_game_state()
        self.timer.draw(screen)
        
        # Update button hover states
        mouse_pos = pygame.mouse.get_pos()
        for button in [self.reset_button, self.undo_button, self.redo_button, self.resign_button]:
            button.update_hover(mouse_pos)
            button.draw(screen)
        
        if self.promotion_menu:
            self.promotion_menu.draw(screen)
    
    def reset(self):
        """Reset the game to initial state."""
        self.board = chess.Board()
        self.selected_square = None
        self.game_over = False
        self.promotion_menu = None
        self.pending_promotion_move = None
        self.illegal_move_squares = None
        self.illegal_move_time = 0
        self.board_history = [chess.Board().fen()]
        self.current_position = 0
        self.last_move = None
        self.last_move_was_capture = False
        self.timer.reset()
        self.game_started = False
        self.resigned = False
        self.winner_by_resignation = None
        self.highlighted_moves = []
    
    def resign_game(self):
        """Current player resigns the game."""
        if not self.game_over and self.game_started:
            self.resigned = True
            self.game_over = True
            self.winner_by_resignation = chess.BLACK if self.board.turn == chess.WHITE else chess.WHITE
            self.timer.stop()

    def undo_move(self):
        """Undo the last move."""
        if self.current_position > 0 and not self.promotion_menu:
            self.current_position -= 1
            self.board = chess.Board(self.board_history[self.current_position])
            self.game_over = False
            self.selected_square = None
            self.highlighted_moves = []
    
    def redo_move(self):
        """Redo a previously undone move."""
        if self.current_position + 1 < len(self.board_history) and not self.promotion_menu:
            self.current_position += 1
            self.board = chess.Board(self.board_history[self.current_position])
            self.game_over = self.board.is_game_over()
            self.selected_square = None
            self.highlighted_moves = []
    
    def make_move(self, move):
        """Execute a move if it's legal and update game state."""
        if move in self.board.legal_moves:
            if not self.game_started:
                self.timer.start()
                self.game_started = True
            
            # Store capture status before making the move
            self.last_move_was_capture = self.board.is_capture(move)
            self.board.push(move)
            self.timer.switch_player()
            self.current_position += 1
            self.board_history = self.board_history[:self.current_position]
            self.board_history.append(self.board.fen())
            self.last_move = move
            
            if self.board.is_game_over() or self.timer.is_time_up():
                self.game_over = True
                self.timer.stop()
            return True
        return False

    def is_promotion_move(self, from_square, to_square):
        """Check if a move from from_square to to_square is a pawn promotion."""
        legal_moves = [move for move in self.board.legal_moves
                       if move.from_square == from_square and move.to_square == to_square]
        return any(move.promotion for move in legal_moves)
    
    def get_square_from_pos(self, pos):
        """Convert screen coordinates to chess square index."""
        x, y = pos
        col = (x - BOARD_OFFSET_X) // SQUARE
        row = 7 - (y - BOARD_OFFSET_Y) // SQUARE
        
        if col < 0 or col >= 8 or row < 0 or row >= 8:
            return None
        
        return row * 8 + col
    
    def handle_click(self, pos):
        """Handle mouse click events on the board and UI."""
        if self.reset_button.is_clicked(pos):
            self.reset()
            return
        
        if self.undo_button.is_clicked(pos):
            self.undo_move()
            return
        
        if self.redo_button.is_clicked(pos):
            self.redo_move()
            return
        
        if self.resign_button.is_clicked(pos):
            self.resign_game()
            return

        if self.game_over:
            return
        
        # Check if click is within board bounds
        if (pos[0] < BOARD_OFFSET_X or pos[0] >= BOARD_OFFSET_X + BOARD_SIZE or
            pos[1] < BOARD_OFFSET_Y or pos[1] >= BOARD_OFFSET_Y + BOARD_SIZE):
            return

        if self.promotion_menu:
            promotion_piece = self.promotion_menu.handle_click(pos)
            if promotion_piece:
                promotion_move = chess.Move(
                    self.pending_promotion_move.from_square,
                    self.pending_promotion_move.to_square,
                    promotion=chess.Piece.from_symbol(promotion_piece).piece_type
                )
                if self.make_move(promotion_move):
                    self.promotion_menu = None
                    self.pending_promotion_move = None
            return

        square = self.get_square_from_pos(pos)
        if square is None:
            return
        
        if self.selected_square is None:
            piece = self.board.piece_at(square)
            if piece and piece.color == self.board.turn:
                self.selected_square = square
                self.highlighted_moves = [move for move in self.board.legal_moves if move.from_square == square]
        else:
            if self.is_promotion_move(self.selected_square, square):
                self.pending_promotion_move = chess.Move(self.selected_square, square)
                self.promotion_menu = PromotionMenu(square, self.board.turn == chess.WHITE)
            else:
                move = chess.Move(self.selected_square, square)
                if not self.make_move(move) and self.selected_square != square:
                    self.illegal_move_squares = (self.selected_square, square)
                    self.illegal_move_time = time.time()
            self.selected_square = None
            self.highlighted_moves = []

def main():
    """Main game loop."""
    game = ChessEngine()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                game.handle_click(event.pos)

        game.timer.update()
        game.draw()
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()

if __name__ == "__main__":
    main()