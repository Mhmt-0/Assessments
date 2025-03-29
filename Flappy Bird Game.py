import pygame
import random

pygame.init()

WIDTH, HEIGHT = 400, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flappy Bird")

WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

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

class Pipe:
    def __init__(self, x):
        self.x = x
        self.width = 50
        self.gap = 150
        self.height_top = random.randint(100, 300)
        self.height_bottom = HEIGHT - self.height_top - self.gap
        self.speed = 3

    def update(self):
        self.x -= self.speed

    def draw(self, screen):
        pygame.draw.rect(screen, GREEN, (self.x, 0, self.width, self.height_top))
        pygame.draw.rect(screen, GREEN, (self.x, HEIGHT - self.height_bottom, self.width, self.height_bottom))

bird = Bird(WIDTH // 4, HEIGHT // 2)
pipes = [Pipe(WIDTH + i * 200) for i in range(3)]

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
    for pipe in pipes:
        pipe.update()
        pipe.draw(screen)
    
    bird.draw(screen)
    
    pygame.display.update()
    clock.tick(30)
    
pygame.quit()


