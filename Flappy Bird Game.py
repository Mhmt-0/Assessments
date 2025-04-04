import pygame
import sys
import time
import random
import json
from pathlib import Path

pygame.init()

clock = pygame.time.Clock()

VOLUME = 0.5

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
ORANGE = (255, 165, 0)
BLUE = (0, 191, 255)
PURPLE = (147, 112, 219)
PINK = (255, 192, 203)

GRAVITY_VALUES = {
    "Easy": 0.15,
    "Medium": 0.17,
    "Hard": 0.19,
    "Expert": 0.21
}

PIPE_SPEEDS = {
    "Easy": 2,
    "Medium": 3,
    "Hard": 4,
    "Expert": 5
}

PIPE_GAPS = {
    "Easy": 350,
    "Medium": 300,
    "Hard": 250,
    "Expert": 200
}

FLASH_INTERVAL = 500
last_flash = 0
flash_on = False

def create_gradient_text(surface, text, font, start_color, end_color, pos):
    text_surface = font.render(text, True, start_color)
    text_rect = text_surface.get_rect(center=pos)
    
    gradient_surface = pygame.Surface(text_surface.get_size(), pygame.SRCALPHA)
    for y in range(text_surface.get_height()):
        r = start_color[0] + (end_color[0] - start_color[0]) * y / text_surface.get_height()
        g = start_color[1] + (end_color[1] - start_color[1]) * y / text_surface.get_height()
        b = start_color[2] + (end_color[2] - start_color[2]) * y / text_surface.get_height()
        color = (int(r), int(g), int(b))
        pygame.draw.line(gradient_surface, color, (0, y), (text_surface.get_width(), y))
    
    gradient_surface.blit(text_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    surface.blit(gradient_surface, text_rect)

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
    screen.fill(BLACK)
    create_gradient_text(screen, "HIGH SCORES", score_font, BLUE, PURPLE, (width // 2, 100))

    scores = load_scores()
    y_offset = 200
    for i, score in enumerate(scores['high_scores'], 1):
        color = YELLOW if i == 1 else WHITE
        score_text = score_font.render(f"{i}. {score}", True, color)
        score_rect = score_text.get_rect(center=(width // 2, y_offset))
        screen.blit(score_text, score_rect)
        y_offset += 50

    instruction_text = score_font.render("Press SPACE to return", True, GREEN)
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
    global last_flash, flash_on
    
    current_time = pygame.time.get_ticks()
    if current_time - last_flash >= FLASH_INTERVAL:
        flash_on = not flash_on
        last_flash = current_time

    if game_state == "game_on":
        score_color = YELLOW if flash_on and score > high_score else WHITE
        score_text = score_font.render(str(score), True, score_color)
        score_rect = score_text.get_rect(center=(width // 2, 66))
        screen.blit(score_text, score_rect)
    elif game_state == "game_over":
        score_text = score_font.render(f"Score: {score}", True, WHITE)
        score_rect = score_text.get_rect(center=(width // 2, 66))
        screen.blit(score_text, score_rect)

        if score >= high_score:
            create_gradient_text(screen, "NEW HIGH SCORE!", small_font, YELLOW, RED, (width // 2, 120))

        high_score_text = score_font.render(f"High Score: {high_score}", True, YELLOW)
        high_score_rect = high_score_text.get_rect(center=(width // 2, 506))
        screen.blit(high_score_text, high_score_rect)

        if flash_on:
            restart_text = small_font.render("Press SPACE to restart", True, GREEN)
            restart_rect = restart_text.get_rect(center=(width // 2, 550))
            screen.blit(restart_text, restart_rect)

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
    small_font = pygame.font.Font("freesansbold.ttf", 20)
    
    while not difficulty_selected:
        screen.fill(BLACK)
        create_gradient_text(screen, "SELECT DIFFICULTY", score_font, BLUE, PURPLE, (width // 2, 100))
        
        difficulties = [
            ("1 - Easy", GREEN, (PIPE_SPEEDS["Easy"], PIPE_GAPS["Easy"], GRAVITY_VALUES["Easy"])),
            ("2 - Medium", YELLOW, (PIPE_SPEEDS["Medium"], PIPE_GAPS["Medium"], GRAVITY_VALUES["Medium"])),
            ("3 - Hard", ORANGE, (PIPE_SPEEDS["Hard"], PIPE_GAPS["Hard"], GRAVITY_VALUES["Hard"])),
            ("4 - Expert", RED, (PIPE_SPEEDS["Expert"], PIPE_GAPS["Expert"], GRAVITY_VALUES["Expert"]))
        ]
        
        y_offset = 200
        for diff, color, _ in difficulties:
            text = score_font.render(diff, True, color)
            text_rect = text.get_rect(center=(width // 2, y_offset))
            screen.blit(text, text_rect)
            y_offset += 50
        
        info_y = y_offset + 20
        descriptions = [
            ("Easy: Perfect for beginners", GREEN),
            ("Medium: A good challenge", YELLOW),
            ("Hard: For experienced players", ORANGE),
            ("Expert: The ultimate test!", RED)
        ]
        
        for desc, color in descriptions:
            info_text = small_font.render(desc, True, color)
            info_rect = info_text.get_rect(center=(width // 2, info_y))
            screen.blit(info_text, info_rect)
            info_y += 25
            
        pygame.display.update()
        
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4]:
                    index = int(event.unicode) - 1
                    pipe_speed, pipe_gap, gravity = difficulties[index][2]
                    difficulty_selected = True

def adjust_volume():
    global VOLUME
    volume_adjusted = False
    small_font = pygame.font.Font("freesansbold.ttf", 20)
    
    while not volume_adjusted:
        screen.fill(BLACK)
        create_gradient_text(screen, "VOLUME CONTROL", score_font, BLUE, PURPLE, (width // 2, 100))
        
        volume_text = score_font.render(f"{int(VOLUME * 100)}%", True, WHITE)
        volume_rect = volume_text.get_rect(center=(width // 2, 180))
        screen.blit(volume_text, volume_rect)
        
        bar_width = 200
        bar_height = 20
        bar_x = (width - bar_width) // 2
        bar_y = 220
        
        pygame.draw.rect(screen, (100, 100, 100), (bar_x, bar_y, bar_width, bar_height))
        volume_width = int(bar_width * VOLUME)
        volume_color = (
            int(255 * (1 - VOLUME)),
            int(255 * VOLUME),        
            0                         
        )
        pygame.draw.rect(screen, volume_color, (bar_x, bar_y, volume_width, bar_height))
        
        controls = ["↑/↓: Adjust Volume", "ENTER: Save and Return"]
        y_pos = bar_y + 50
        for control in controls:
            text = small_font.render(control, True, WHITE)
            text_rect = text.get_rect(center=(width // 2, y_pos))
            screen.blit(text, text_rect)
            y_pos += 25
        
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
        
        create_gradient_text(screen, "FLAPPY BIRD", score_font, YELLOW, ORANGE, (width // 2, 150))
        
        options = ["Play", "Leaderboard", "Volume", "Quit"]
        y_offset = 300
        
        for i, option in enumerate(options):
            if i == selected_option:
                create_gradient_text(screen, option, score_font, BLUE, PURPLE, (width // 2, y_offset))
            else:
                text = score_font.render(option, True, WHITE)
                text_rect = text.get_rect(center=(width // 2, y_offset))
                screen.blit(text, text_rect)
            y_offset += 50
        
        controls_text = small_font.render("↑/↓: Select   ENTER: Confirm", True, WHITE)
        controls_rect = controls_text.get_rect(center=(width // 2, y_offset + 20))
        screen.blit(controls_text, controls_rect)
            
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
small_font = pygame.font.Font("freesansbold.ttf", 20)

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
