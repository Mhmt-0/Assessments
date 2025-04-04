import pygame
import sys
import time
import random
import json
from pathlib import Path

pygame.init()

clock = pygame.time.Clock()

VOLUME = 0.5

def load_scores():
    try:
        with open('scores.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {'high_scores': []}

def save_score(new_score):
    scores = load_scores()
    scores['high_scores'].append(new_score)
    scores['high_scores'].sort(reverse=True)
    scores['high_scores'] = scores['high_scores'][:5]
    with open('scores.json', 'w') as f:
        json.dump(scores, f)

def draw_leaderboard():
    screen.fill((0, 0, 0))
    title_text = score_font.render("HIGH SCORES", True, (255, 255, 255))
    title_rect = title_text.get_rect(center=(width // 2, 100))
    screen.blit(title_text, title_rect)

    scores = load_scores()
    y_offset = 200
    for i, score in enumerate(scores['high_scores'], 1):
        score_text = score_font.render(f"{i}. {score}", True, (255, 255, 255))
        score_rect = score_text.get_rect(center=(width // 2, y_offset))
        screen.blit(score_text, score_rect)
        y_offset += 50

    instruction_text = score_font.render("Press SPACE to play", True, (255, 255, 255))
    instruction_rect = instruction_text.get_rect(center=(width // 2, 500))
    screen.blit(instruction_text, instruction_rect)

def draw_floor():
    screen.blit(floor_img, (floor_x, 520))
    screen.blit(floor_img, (floor_x + 448, 520))

def create_pipes():
    pipe_y = random.choice(pipe_height)
    top_pipe = pipe_img.get_rect(midbottom=(467, pipe_y - pipe_gap))
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

        pipe.centerx -= pipe_speed
        if pipe.right < 0:
            pipes.remove(pipe)

        if bird_rect.colliderect(pipe):
            collision_sound.play()
            game_over = True

def draw_score(game_state):
    if game_state == "game_on":
        score_text = score_font.render(str(score), True, (255, 255, 255))
        score_rect = score_text.get_rect(center=(width // 2, 66))
        screen.blit(score_text, score_rect)
    elif game_state == "game_over":
        score_text = score_font.render(f" Score: {score}", True, (255, 255, 255))
        score_rect = score_text.get_rect(center=(width // 2, 66))
        screen.blit(score_text, score_rect)

        high_score_text = score_font.render(f"High Score: {high_score}", True, (255, 255, 255))
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

def choose_difficulty():
    global pipe_speed, pipe_gap, gravity
    difficulty_selected = False
    while not difficulty_selected:
        screen.fill((0, 0, 0))
        options = ["1 - Easy", "2 - Medium", "3 - Hard", "4 - Expert"]
        y_offset = 200
        for option in options:
            text = score_font.render(option, True, (255, 255, 255))
            text_rect = text.get_rect(center=(width // 2, y_offset))
            screen.blit(text, text_rect)
            y_offset += 50
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    pipe_speed, pipe_gap, gravity = 2, 350, 0.15
                    difficulty_selected = True
                elif event.key == pygame.K_2:
                    pipe_speed, pipe_gap, gravity = 3, 300, 0.17
                    difficulty_selected = True
                elif event.key == pygame.K_3:
                    pipe_speed, pipe_gap, gravity = 4, 250, 0.19
                    difficulty_selected = True
                elif event.key == pygame.K_4:
                    pipe_speed, pipe_gap, gravity = 5, 200, 0.21
                    difficulty_selected = True

def adjust_volume():
    global VOLUME
    volume_adjusted = False
    while not volume_adjusted:
        screen.fill((0, 0, 0))
        title_text = score_font.render("VOLUME SETTINGS", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(width // 2, 150))
        screen.blit(title_text, title_rect)
        
        volume_text = score_font.render(f"Current Volume: {int(VOLUME * 100)}%", True, (255, 255, 255))
        volume_rect = volume_text.get_rect(center=(width // 2, 250))
        screen.blit(volume_text, volume_rect)
        
        instruction_text = score_font.render("Up/Down to adjust, ENTER to confirm", True, (255, 255, 255))
        instruction_rect = instruction_text.get_rect(center=(width // 2, 350))
        screen.blit(instruction_text, instruction_rect)
        
        pygame.display.update()
        
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    VOLUME = min(1.0, VOLUME + 0.1)
                elif event.key == pygame.K_DOWN:
                    VOLUME = max(0.0, VOLUME - 0.1)
                elif event.key == pygame.K_RETURN:
                    volume_adjusted = True
                    
        jump_sound.set_volume(VOLUME)
        collision_sound.set_volume(VOLUME)
        score_sound.set_volume(VOLUME)

def main_menu():
    menu_active = True
    selected_option = 0
    
    while menu_active:
        screen.blit(back_img, (0, 0))
        screen.blit(floor_img, (0, 550))
        
        title_text = score_font.render("FLAPPY BIRD", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(width // 2, 150))
        screen.blit(title_text, title_rect)
        
        options = ["Play", "Leaderboard", "Volume Settings", "Quit"]
        y_offset = 300
        
        for i, option in enumerate(options):
            color = (255, 255, 0) if i == selected_option else (255, 255, 255)
            text = score_font.render(option, True, color)
            text_rect = text.get_rect(center=(width // 2, y_offset))
            screen.blit(text, text_rect)
            y_offset += 50
            
        pygame.display.update()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected_option = (selected_option - 1) % 4
                elif event.key == pygame.K_DOWN:
                    selected_option = (selected_option + 1) % 4
                elif event.key == pygame.K_RETURN:
                    if selected_option == 0:
                        menu_active = False
                        return "play"
                    elif selected_option == 1:
                        return "leaderboard"
                    elif selected_option == 2:
                        return "volume"
                    else:
                        pygame.quit()
                        sys.exit()

width, height = 350, 622
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
score_font = pygame.font.Font("freesansbold.ttf", 27)

jump_sound = pygame.mixer.Sound("/Users/mehmet/Downloads/jump.mp3")
collision_sound = pygame.mixer.Sound("/Users/mehmet/Downloads/collision.mp3")
score_sound = pygame.mixer.Sound("/Users/mehmet/Downloads/score.mp3")

jump_sound.set_volume(VOLUME)
collision_sound.set_volume(VOLUME)
score_sound.set_volume(VOLUME)

while True:
    menu_choice = main_menu()
    
    if menu_choice == "play":
        choose_difficulty()
        
        running = True
        while running:
            clock.tick(120)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE and not game_over:
                        bird_movement = 0
                        bird_movement = -7
                        jump_sound.play()
                        bird_index = 1

                    if event.key == pygame.K_SPACE and game_over:
                        save_score(score)
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
    
    elif menu_choice == "leaderboard":
        showing_leaderboard = True
        while showing_leaderboard:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        showing_leaderboard = False
            
            draw_leaderboard()
            pygame.display.update()
    
    elif menu_choice == "volume":
        adjust_volume()
