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
        self.velocity = 0
        self.gravity = 0.5
        self.jump_strength = -8

    def update(self):
        self.velocity += self.gravity
        self.y += self.velocity

    def jump(self):
        self.velocity = self.jump_strength

    def draw(self, screen):
        pygame.draw.circle(screen, RED, (self.x, int(self.y)), self.radius)

bird = Bird(WIDTH // 4, HEIGHT // 2)

clock = pygame.time.Clock()

running = True
while running:
    screen.fill(WHITE)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                bird.jump()
    
    bird.update()
    bird.draw(screen)
    
    pygame.display.update()
    clock.tick(30)
    
pygame.quit()

