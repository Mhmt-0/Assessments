import pygame
import sys
import time
import random

pygame.init()

clock = pygame.time.Clock()

def draw_floor():
    screen.blit(floor_img, (floor_x, 520))
    screen.blit(floor_img, (floor_x + 448, 520))

def create_pipes():
    pipe_y = random.choice(pipe_height)
    top_pipe = pipe_img.get_rect(midbottom=(467, pipe_y - 300))
    bottom_pipe = pipe_img.get_rect(midtop=(467, pipe_y))
    return top_pipe, bottom_pipe

def pipe_animation():
    global game_over, score_time
    for pipe in pipes:
        if pipe.top < 0:
            flipped_pipe = pygame.transform.flip(pipe_img, False, True)
            screen.blit(flipped_pipe, pipe)
        else:
            screen.blit(pipe_img, pipe)

        pipe.centerx -= 3
        if pipe.right < 0:
            pipes.remove(pipe)

        if bird_rect.colliderect(pipe):
            collision_sound.play()
            game_over = True

def draw_score(game_state):
    if game_state == "game_on":
        shadow_text = score_font.render(str(score), True, (50, 50, 50))
        shadow_rect = shadow_text.get_rect(center=(width // 2 + 2, 68))
        screen.blit(shadow_text, shadow_rect)

        score_text = score_font.render(str(score), True, (255, 215, 0))
        score_rect = score_text.get_rect(center=(width // 2, 66))
        screen.blit(score_text, score_rect)
    elif game_state == "game_over":
        shadow_text = score_font.render(f" Score: {score}", True, (50, 50, 50))
        shadow_rect = shadow_text.get_rect(center=(width // 2 + 2, 68))
        screen.blit(shadow_text, shadow_rect)

        score_text = score_font.render(f" Score: {score}", True, (255, 215, 0))
        score_rect = score_text.get_rect(center=(width // 2, 66))
        screen.blit(score_text, score_rect)

        high_score_text = score_font.render(f"High Score: {high_score}", True, (255, 215, 0))
        high_score_rect = high_score_text.get_rect(center=(width // 2, 506))
        screen.blit(high_score_text, high_score_rect)

def score_update():
    global score, score_time, high_score
    if pipes:
        for pipe in pipes:
            if 65 < pipe.centerx < 69 and score_time:
                score += 1
                score_time = False
                score_sound.play()
            if pipe.left <= 0:
                score_time = True

    if score > high_score:
        high_score = score

width, height = 350, 622
clock = pygame.time.Clock()
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Flappy Bird")

back_img = pygame.image.load("/Users/mehmet/Downloads/img_46.png")
floor_img = pygame.image.load("/Users/mehmet/Downloads/img_50.png")
floor_x = 0

bird_up = pygame.image.load("/Users/mehmet/Downloads/img_47.png")
bird_down = pygame.image.load("/Users/mehmet/Downloads/img_48.png")
bird_mid = pygame.image.load("/Users/mehmet/Downloads/img_49.png")
birds = [bird_up, bird_mid, bird_down]
bird_index = 0
bird_flap = pygame.USEREVENT
pygame.time.set_timer(bird_flap, 200)
bird_img = birds[bird_index]
bird_rect = bird_img.get_rect(center=(67, 622 // 2))
bird_movement = 0
gravity = 0.17

pipe_img = pygame.image.load("/Users/mehmet/Downloads/greenpipe.png")
pipe_height = [400, 350, 533, 490]

pipes = []
create_pipe = pygame.USEREVENT + 1
pygame.time.set_timer(create_pipe, 1200)

game_over = False
over_img = pygame.image.load("/Users/mehmet/Downloads/img_45.png").convert_alpha()
over_rect = over_img.get_rect(center=(width // 2, height // 2))

score = 0
high_score = 0
score_time = True
score_font = pygame.font.Font("freesansbold.ttf", 30)

jump_sound = pygame.mixer.Sound("/Users/mehmet/Downloads/jump.mp3")
collision_sound = pygame.mixer.Sound("/Users/mehmet/Downloads/collision.mp3")
score_sound = pygame.mixer.Sound("/Users/mehmet/Downloads/score.mp3")

running = True
while running:
    clock.tick(120)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and not game_over:
                bird_movement = 0
                bird_movement = -7
                jump_sound.play()
                bird_index = 1

            if event.key == pygame.K_SPACE and game_over:
                game_over = False
                pipes = []
                bird_movement = 0
                bird_rect = bird_img.get_rect(center=(67, 622 // 2))
                score_time = True
                score = 0

        if event.type == bird_flap:
            bird_index = (bird_index + 1) % 3
            bird_img = birds[bird_index]
            bird_rect = bird_up.get_rect(center=bird_rect.center)

        if event.type == create_pipe:
            pipes.extend(create_pipes())

    screen.blit(floor_img, (floor_x, 550))
    screen.blit(back_img, (0, 0))

    if not game_over:
        bird_movement += gravity
        bird_rect.centery += bird_movement
        rotated_bird = pygame.transform.rotozoom(bird_img, bird_movement * -6, 1)

        if bird_rect.top < 5 or bird_rect.bottom >= 550:
            collision_sound.play()
            game_over = True

        screen.blit(rotated_bird, bird_rect)
        pipe_animation()
        score_update()
        draw_score("game_on")
    else:
        screen.blit(over_img, over_rect)
        draw_score("game_over")

    floor_x -= 1
    if floor_x < -448:
        floor_x = 0

    draw_floor()

    pygame.display.update()

pygame.quit()
sys.exit()
