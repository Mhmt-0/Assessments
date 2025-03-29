import pygame

pygame.init()

WIDTH, HEIGHT = 400, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flappy Bird")

WHITE = (255, 255, 255)
RED = (255, 0, 0)

class Bird:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 15

    def draw(self, screen):
        pygame.draw.circle(screen, RED, (self.x, self.y), self.radius)

bird = Bird(WIDTH // 4, HEIGHT // 2)

running = True
while running:
    screen.fill(WHITE) 
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    bird.draw(screen)
    
    pygame.display.update()
    
pygame.quit()
