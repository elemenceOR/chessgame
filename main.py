import pygame
import chess

pygame.init()

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (118, 150, 86)
BEIGE = (238, 238, 210)
YELLOW = (255, 255, 0)

# Game constants
WIDTH, HEIGHT = 480, 480
SQUARE = WIDTH // 8
FPS = 60

# Initialize screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("ChessGame")
clock = pygame.time.Clock()

# Load piece images
pieces_images = {piece: pygame.transform.scale(pygame.image.load(f"images/{piece}.png"), (SQUARE, SQUARE))
                for piece in 'prnbqkPRNBQK'}

board = chess.Board()

def draw_board(selected_square=None):
    colors = [BEIGE, GREEN]
    for row in range(8):
        for col in range(8):
            color = colors[(row + col) % 2]
            pygame.draw.rect(screen, color, pygame.Rect(col * SQUARE, row * SQUARE, SQUARE, SQUARE))
    
    if selected_square:
        row, col = 7 - chess.square_rank(selected_square), chess.square_file(selected_square)
        pygame.draw.rect(screen, YELLOW, pygame.Rect(col * SQUARE, row * SQUARE, SQUARE, SQUARE), 3)

def draw_pieces():
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            col, row = chess.square_file(square), 7 - chess.square_rank(square)
            piece_image = pieces_images[piece.symbol()]
            screen.blit(piece_image, pygame.Rect(col * SQUARE, row * SQUARE, SQUARE, SQUARE))

def get_square_from_pos(pos):
    x, y = pos
    col, row = x // SQUARE, y // SQUARE
    return chess.square(col, 7 - row)

def main():
    running = True
    selected_square = None
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                square = get_square_from_pos(event.pos)
                if selected_square is None:
                    if board.piece_at(square):
                        selected_square = square
                else:
                    move = chess.Move(selected_square, square)
                    if move in board.legal_moves:
                        board.push(move)
                    selected_square = None

        screen.fill(BLACK)
        draw_board(selected_square)
        draw_pieces()
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()