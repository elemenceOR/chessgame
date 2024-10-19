import pygame
import chess

pygame.init()

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (118, 150, 86)
BEIGE = (238, 238, 210)

WIDTH, HEIGHT = 640, 640
SQUARE = WIDTH // 8
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("ChessGame")

pieces_images = {}
pieces = ['p', 'r', 'n', 'b', 'q', 'k', 'wp', 'wr', 'wn', 'wb', 'wq', 'wk']
for piece in pieces:
    pieces_images[piece] = pygame.transform.scale(pygame.image.load("images/" + piece + ".png"), (SQUARE, SQUARE))

board = chess.Board()

def draw_board():
    colors = [BEIGE, GREEN]
    for row in range(8):
        for col in range(8):
            color = colors[(row + col) % 2]
            pygame.draw.rect(screen, color, pygame.Rect(col * SQUARE, row * SQUARE, SQUARE, SQUARE))

def draw_pieces():
    for row in range(8):
        for col in range(8):
            piece = board.piece_at(chess.square(col, 7 - row))
            if piece:
                piece_image = pieces_images[piece.symbol()]
                screen.blit(piece_image, pygame.Rect(col * SQUARE, row * SQUARE, SQUARE, SQUARE))

def main():
    running = True
    selected_square = None
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                col, row = x // SQUARE, y // SQUARE
                square = chess.square(col, 7 - row)
                if selected_square is None:
                    selected_square = square
                else:
                    move = chess.Move(selected_square, square)
                    if move in board.legal_moves:
                        board.push(move)
                    selected_square = None

        draw_board()
        draw_pieces()
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()