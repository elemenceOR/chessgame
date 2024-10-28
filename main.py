import pygame
import chess
import time

pygame.init()

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (118, 150, 86)
BEIGE = (238, 238, 210)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 225)
GRAY = (128, 128, 128)

WIDTH, HEIGHT = 480, 520
SQUARE = WIDTH // 8
FPS = 60

pygame.font.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("ChessGame")
clock = pygame.time.Clock()

pieces_images = {
    'p':pygame.transform.scale(pygame.image.load(f"images/p.png"), (SQUARE, SQUARE)),
    'r':pygame.transform.scale(pygame.image.load(f"images/r.png"), (SQUARE, SQUARE)),
    'n':pygame.transform.scale(pygame.image.load(f"images/n.png"), (SQUARE, SQUARE)),
    'b':pygame.transform.scale(pygame.image.load(f"images/b.png"), (SQUARE, SQUARE)),
    'q':pygame.transform.scale(pygame.image.load(f"images/q.png"), (SQUARE, SQUARE)),
    'k':pygame.transform.scale(pygame.image.load(f"images/k.png"), (SQUARE, SQUARE)),
    'P':pygame.transform.scale(pygame.image.load(f"images/wP.png"), (SQUARE, SQUARE)),
    'R':pygame.transform.scale(pygame.image.load(f"images/wR.png"), (SQUARE, SQUARE)),
    'N':pygame.transform.scale(pygame.image.load(f"images/wN.png"), (SQUARE, SQUARE)),
    'B':pygame.transform.scale(pygame.image.load(f"images/wB.png"), (SQUARE, SQUARE)),
    'Q':pygame.transform.scale(pygame.image.load(f"images/wQ.png"), (SQUARE, SQUARE)),
    'K':pygame.transform.scale(pygame.image.load(f"images/wK.png"), (SQUARE, SQUARE))
}
                    

class PromotionMenu:
    def __init__(self, square, is_white):
        self.square = square
        self.is_white = is_white
        self.pieces = ['Q', 'R', 'N', 'B'] if is_white else ['q', 'r', 'n', 'b']
        
        menu_x = chess.square_file(square) * SQUARE

        if is_white:
            menu_y = (7 - chess.square_rank(square)) * SQUARE * SQUARE
            self.pieces = self.pieces
        else:
            menu_y = (7 - chess.square_rank(square)) * SQUARE - 3 * SQUARE
            self.pieces = self.pieces[::-1]
        
        self.rect = pygame.Rect(
            menu_x,
            menu_y,
            SQUARE,
            SQUARE * 4
        )

    def draw(self, screen):
        for i, piece in enumerate(self.pieces):
            piece_rect = pygame.Rect(
                self.rect.x,
                self.rect.y + (i * SQUARE),
                SQUARE,
                SQUARE
            )
            pygame.draw.rect(screen, WHITE, piece_rect)
            pygame.draw.rect(screen, BLACK, piece_rect, 1)
            screen.blit(pieces_images[piece], piece_rect)

    def handle_click(self, pos):
        if not self.rect.collidepoint(pos):
            return None
        
        clicked_index = (pos[1] - self.rect.y) // SQUARE
        if 0 <= clicked_index < len(self.pieces):
            return self.pieces[clicked_index]
        return None

class ChessEngine():
    def __init__(self):
        self.board = chess.Board()
        self.selected_sqr = None
        self.game_over = False
        self.font = pygame.font.Font(None, 36)
        self.reset_button = Button(WIDTH // 4, HEIGHT - 30, WIDTH // 2, 20, "Reset Game", GRAY, BLACK)
        self.promotion_menu = None
        self.pending_promotion_move = None
        self.illegal_move_sqr = None
        self.illegal_move_time = 0
        self.illegal_move_duration = 0.5

    def reset(self):
        self.board = chess.Board()
        self.selected_square = None
        self.game_over = False
        self.promotion_menu = None
        self.pending_promotion_move = None
        self.illegal_move_squares = None
        self.illegal_move_time = 0

    def is_promotion_move(self, from_square, to_square):
        legal_moves = [move for move in self.board.legal_moves 
        if move.from_square == from_square and move.to_square == to_square]
        
        return any(move.promotion for move in legal_moves)

    def draw_board(self):
        colors = [BEIGE, GREEN]
        for row in range(8):
            for col in range(8):
                color = colors[(row + col) % 2]
                pygame.draw.rect(screen, color, pygame.Rect(col * SQUARE, row * SQUARE, SQUARE, SQUARE))
        
        if self.selected_sqr is not None:
            row, col = 7 - chess.square_rank(self.selected_sqr), chess.square_file(self.selected_sqr)
            pygame.draw.rect(screen, BLUE, pygame.Rect(col * SQUARE, row * SQUARE, SQUARE, SQUARE), 3)

        if self.illegal_move_sqr and time.time() - self.illegal_move_time < self.illegal_move_duration:
            for square in self.illegal_move_sqr:
                row, col = 7 - chess.square_rank(square), chess.square_file(square)
                pygame.draw.rect(screen, RED, pygame.Rect(col * SQUARE, row * SQUARE, SQUARE, SQUARE), 3)
        else:
            self.illegal_move_sqr = None


    def draw_pieces(self):
        for square in chess.SQUARES:
            piece = self.board.piece_at(square)
            if piece:
                col, row = chess.square_file(square), 7 - chess.square_rank(square)
                piece_image = pieces_images[piece.symbol()]
                screen.blit(piece_image, pygame.Rect(col * SQUARE, row * SQUARE, SQUARE, SQUARE))

    def get_square_from_pos(self, pos):
        x, y = pos
        file = x // SQUARE
        rank = 7 - (y // SQUARE)
        square = chess.square(file, rank)
        return square

    def draw_game_state(self):
        global text
        king_square = self.board.king(self.board.turn)
        col, row = chess.square_file(king_square), 7 - chess.square_rank(king_square)
        
        if self.board.is_checkmate():
            pygame.draw.rect(screen, RED, pygame.Rect(col * SQUARE, row * SQUARE, SQUARE, SQUARE), 5)
            text = "Checkmate! " + ("Black" if self.board.turn == chess.WHITE else "White") + " wins!"
            color = RED
        elif self.board.is_stalemate():
            pygame.draw.rect(screen, YELLOW, pygame.Rect(col * SQUARE, row * SQUARE, SQUARE, SQUARE), 5)
            text = "Stalemate "
            color = BLACK
        elif self.board.is_check():
            pygame.draw.rect(screen, YELLOW, pygame.Rect(col * SQUARE, row * SQUARE, SQUARE, SQUARE), 5)
            return
        else:
            return
        
        text_surface = self.font.render(text, True, color)
        text_rect = text_surface.get_rect(center=(WIDTH//2, HEIGHT//2))
        screen.blit(text_surface, text_rect)

    def handle_click(self, pos):
        if self.reset_button.is_clicked(pos):
            self.reset()
            return

        if self.game_over:
            return

        if pos[1] >= HEIGHT - 40:
            return

        if self.promotion_menu:
            promotion_piece = self.promotion_menu.handle_click(pos)
            if promotion_piece:
                promotion_move = chess.Move(
                    self.pending_promotion_move.from_square,
                    self.pending_promotion_move.to_square,
                    promotion=chess.Piece.from_symbol(promotion_piece).piece_type
                )
                self.board.push(promotion_move)
                if self.board.is_game_over():
                    self.game_over = True
                self.promotion_menu = None
                self.pending_promotion_move = None
            return

        square = self.get_square_from_pos(pos)
        
        if self.selected_sqr is None:
            piece = self.board.piece_at(square)
            if piece and piece.color == self.board.turn:
                self.selected_sqr = square
        else:
            print(f"Attempting move from {chess.square_name(self.selected_sqr)} to {chess.square_name(square)}")
            
            if self.is_promotion_move(self.selected_sqr, square):
                self.pending_promotion_move = chess.Move(self.selected_sqr, square)
                self.promotion_menu = PromotionMenu(square, self.board.turn == chess.WHITE)
            else:
                move = chess.Move(self.selected_sqr, square)
                if move in self.board.legal_moves:
                    self.board.push(move)
                    if self.board.is_game_over():
                        self.game_over = True
                else:
                    self.illegal_move_sqr = (self.selected_sqr, square)
                    self.illegal_move_time = time.time()
                    print("Move is not legal")
            self.selected_sqr = None

    def draw(self):
        screen.fill(BLACK)
        self.draw_board()
        self.draw_pieces()
        self.draw_game_state()
        self.reset_button.draw(screen)
        if self.promotion_menu:
            self.promotion_menu.draw(screen)

class Button:
    def __init__(self, x, y, width, height, text, color, text_color):
        self.rect = pygame.Rect (x, y, width, height)
        self.text = text
        self.color = color
        self.text_color = text_color
        self.font = pygame.font.Font(None, 32)

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

def main():
    game = ChessEngine()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                game.handle_click(event.pos)

        game.draw()
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()