import pygame
import random

pygame.init()

WIDTH, HEIGHT = 400, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flappy Bird")

WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)

font = pygame.font.Font(None, 36)

background = pygame.image.load("/Users/mehmet/Downloads/dg34rsu-29a3d144-dc3f-473e-a949-f73a4ba1ef7c.png")
background = pygame.transform.scale(background, (WIDTH, HEIGHT))

jump_sound = pygame.mixer.Sound("jump.wav")
collision_sound = pygame.mixer.Sound("collision.wav")
score_sound = pygame.mixer.Sound("score.wav")

def show_start_screen():
    screen.blit(background, (0, 0))
    text = font.render("Press SPACE to Start", True, BLACK)
    screen.blit(text, (WIDTH // 4, HEIGHT // 2))
    pygame.display.update()
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    waiting = False

def show_game_over_screen(score):
    screen.blit(background, (0, 0))
    text1 = font.render("Game Over!", True, BLACK)
    text2 = font.render(f"Score: {score}", True, BLACK)
    text3 = font.render("Press SPACE to Restart", True, BLACK)
    screen.blit(text1, (WIDTH // 3, HEIGHT // 3))
    screen.blit(text2, (WIDTH // 3, HEIGHT // 2))
    screen.blit(text3, (WIDTH // 6, HEIGHT // 1.5))
    pygame.display.update()
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    waiting = False

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
        jump_sound.play()

    def draw(self, screen):
        pygame.draw.circle(screen, RED, (self.x, int(self.y)), self.radius)
    
    def get_rect(self):
        return pygame.Rect(self.x - self.radius, self.y - self.radius, self.radius * 2, self.radius * 2)

class Pipe:
    def __init__(self, x):
        self.x = x
        self.width = 50
        self.gap = 150
        self.height_top = random.randint(100, 300)
        self.height_bottom = HEIGHT - self.height_top - self.gap
        self.speed = 3
        self.passed = False

    def update(self):
        self.x -= self.speed

    def draw(self, screen):
        pygame.draw.rect(screen, GREEN, (self.x, 0, self.width, self.height_top))
        pygame.draw.rect(screen, GREEN, (self.x, HEIGHT - self.height_bottom, self.width, self.height_bottom))
    
    def get_rects(self):
        return [
            pygame.Rect(self.x, 0, self.width, self.height_top),
            pygame.Rect(self.x, HEIGHT - self.height_bottom, self.width, self.height_bottom)
        ]

def check_collision(bird, pipes):
    bird_rect = bird.get_rect()
    for pipe in pipes:
        for pipe_rect in pipe.get_rects():
            if bird_rect.colliderect(pipe_rect):
                collision_sound.play()
                return True
    if bird.y - bird.radius <= 0 or bird.y + bird.radius >= HEIGHT:
        collision_sound.play()
        return True
    return False

def draw_score(screen, score):
    text = font.render(f"Score: {score}", True, BLACK)
    screen.blit(text, (10, 10))

while True:
    show_start_screen()
    bird = Bird(WIDTH // 4, HEIGHT // 2)
    pipes = [Pipe(WIDTH + i * 200) for i in range(3)]
    score = 0
    clock = pygame.time.Clock()
    running = True
    
    while running:
        screen.blit(background, (0, 0))
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    bird.jump()
        
        bird.update()
        
        for pipe in pipes:
            pipe.update()
            pipe.draw(screen)
            
            if pipe.x + pipe.width < bird.x and not pipe.passed:
                score += 1
                pipe.passed = True
                score_sound.play()
            
            if pipe.x + pipe.width < 0:
                pipes.remove(pipe)
                new_pipe = Pipe(WIDTH)
                pipes.append(new_pipe)
        
        bird.draw(screen)
        draw_score(screen, score)
        
        if check_collision(bird, pipes):
            running = False
        
        pygame.display.update()
        clock.tick(30)
        
    show_game_over_screen(score)

