import pygame

WIDTH, HEIGHT = 600, 600
ROWS, COLS = 10, 10
SQUARE_SIZE = WIDTH // COLS

# Colors
RED = (255, 0, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
GREY = (128, 128, 128)

# Crown image
CROWN = pygame.transform.scale(pygame.image.load('assets/crown.png'), (44, 25))

# Holes (obstacles)
HOLES = [
    (4, 1),
    (4, 5),
    (5, 2),
    (5,6)
]
