# Flappy Bird Game
# A recreation of the classic Flappy Bird game with additional features like:
# Multiple difficulty levels
# Color customization
# High score system
# Volume control
# Pause functionality

import pygame
import sys
import time
import random
import json
import logging
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('flappy_bird.log'),
        logging.StreamHandler()
    ]
)

class GameError(Exception):
    # Base exception class for game-specific errors.
    pass

class AssetLoadError(GameError):
    # Exception raised when game assets fail to load.
    pass

class SaveError(GameError):
    # Exception raised when saving game data fails.
    pass

try:
    pygame.init()
except pygame.error as e:
    logging.critical(f"Failed to initialize Pygame: {e}")
    sys.exit(1)

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

BIRD_COLORS = {
    "Yellow": (255, 255, 0),
    "Blue": (0, 191, 255),
    "Red": (255, 0, 0),
    "Purple": (147, 112, 219),
    "Pink": (255, 192, 203)
}

PIPE_COLORS = {
    "Green": (0, 255, 0),
    "Blue": (0, 191, 255),
    "Red": (255, 0, 0),
    "Purple": (147, 112, 219),
    "Orange": (255, 165, 0),
    "Pink": (255, 192, 203)
}

CURRENT_BIRD_COLOR = "Yellow"
CURRENT_PIPE_COLOR = "Green"

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

PIPE_SCALES = [0.8, 1.0, 1.2]
PIPE_Y_POSITIONS = [200, 250, 300, 350, 400]

FLASH_INTERVAL = 500
last_flash = 0
flash_on = False

bg_colors = [(135, 206, 235), (100, 149, 237), (147, 112, 219)]
bg_color_index = 0
bg_transition_speed = 0.015
bg_transition_progress = 0

def safe_load_image(path, convert_alpha=False):
    try:
        if not Path(path).exists():
            raise FileNotFoundError(f"Image file not found: {path}")
        
        img = pygame.image.load(path)
        if convert_alpha:
            return img.convert_alpha()
        return img
    except (pygame.error, FileNotFoundError) as e:
        logging.error(f"Failed to load image {path}: {e}")
        raise AssetLoadError(f"Failed to load image: {path}")

def create_gradient_text(surface, text, font, start_color, end_color, pos):
    # Creates a gradient text effect from start_color to end_color.
    # This function renders text with a smooth color transition from top to bottom.
    
        # Arguments:
        # surface: The pygame surface to draw on
        # text: The text to render
        # font: The pygame font object to use
        # start_color: RGB tuple for the starting color
        # end_color: RGB tuple for the ending color
        # pos: Tuple of (x, y) coordinates for text center position
    try:
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
    except pygame.error as e:
        logging.error(f"Failed to create gradient text: {e}")
        text_surface = font.render(text, True, start_color)
        surface.blit(text_surface, text_rect)

def update_background_color():
     # Updates the background color with a smooth transition effect.
    # Creates a dynamic background by interpolating between different colors over time.
    # Returns the current interpolated RGB color.
    try:
        global bg_transition_progress, bg_color_index
        bg_transition_progress += bg_transition_speed
        if bg_transition_progress >= 1:
            bg_transition_progress = 0
            bg_color_index = (bg_color_index + 1) % len(bg_colors)
        
        current_color = bg_colors[bg_color_index]
        next_color = bg_colors[(bg_color_index + 1) % len(bg_colors)]
        
        r = current_color[0] + (next_color[0] - current_color[0]) * bg_transition_progress
        g = current_color[1] + (next_color[1] - current_color[1]) * bg_transition_progress
        b = current_color[2] + (next_color[2] - current_color[2]) * bg_transition_progress
        
        return (int(r), int(g), int(b))
    except Exception as e:
        logging.error(f"Error updating background color: {e}")
        return bg_colors[0]

def colorize_surface(surface, color):
     # Applies a color tint to a surface while preserving its transparency.
    # Useful for creating different colored versions of the same sprite.
    
    # Arguments:
        # surface: The source pygame surface
        # color: RGB tuple for the desired color
    # Returns:
        # A new surface with the applied color
    try:
        colored_surface = surface.copy()
        colored_surface.fill(color, special_flags=pygame.BLEND_MULT)
        return colored_surface
    except pygame.error as e:
        logging.error(f"Error colorizing surface: {e}")
        return surface

def scale_surface(surface, scale):
    # Scales a surface by the given factor while maintaining aspect ratio.
    
    # Args:
        # surface: The source pygame surface
        # scale: Float value for scaling factor
    # Returns:
        # A new scaled surface
    try:
        new_size = (int(surface.get_width() * scale), int(surface.get_height() * scale))
        return pygame.transform.scale(surface, new_size)
    except pygame.error as e:
        logging.error(f"Error scaling surface: {e}")
        return surface

def load_scores():
    # Loads the high scores from the scores.json file.
    # Creates a new high scores list if the file doesn't exist.
    
    # Returns:
        # Dictionary containing the list of high scores
    try:
        scores_file = Path('scores.json')
        if not scores_file.exists():
            default_scores = {'high_scores': []}
            with open(scores_file, 'w') as f:
                json.dump(default_scores, f)
            return default_scores
            
        with open(scores_file, 'r') as f:
            data = json.load(f)
            if not isinstance(data, dict) or 'high_scores' not in data:
                raise ValueError("Invalid scores file format")
            return data
    except (json.JSONDecodeError, ValueError) as e:
        logging.error(f"Failed to load scores: {e}")
        return {'high_scores': []}

def save_score(new_score):
    # Saves a new score to the high scores list.
    # Maintains only the top 5 highest scores in descending order.
    
    # Arguments:
        # new_score: Integer value of the new score to save
    try:
        if not isinstance(new_score, (int, float)):
            raise ValueError("Score must be a number")
        
        scores = load_scores()
        scores['high_scores'].append(new_score)
        scores['high_scores'].sort(reverse=True)
        scores['high_scores'] = scores['high_scores'][:5]
        
        with open('scores.json', 'w') as f:
            json.dump(scores, f)
    except (IOError, TypeError, ValueError) as e:
        logging.error(f"Failed to save score: {e}")
        raise SaveError(f"Failed to save score: {e}")

def draw_leaderboard():
    # Renders the high scores leaderboard screen.
    # Displays the top 5 scores with the highest score highlighted in yellow.
    try:
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
    except Exception as e:
        logging.error(f"Error drawing leaderboard: {e}")

def draw_floor():
     # Draws the scrolling floor of the game.
    # Creates an infinite scrolling effect by using two floor images.
    try:
        screen.blit(floor_img, (floor_x, 520))
        screen.blit(floor_img, (floor_x + 448, 520))
    except pygame.error as e:
        logging.error(f"Error drawing floor: {e}")

def create_pipes():
    # Generates a new pair of pipes with random properties.
    # Randomizes pipe height
    # Randomly selects pipe color
    # Applies random scaling to pipes
    
    # Returns:
        # Tuple containing top pipe rect, bottom pipe rect, and pipe surface
    try:
        global CURRENT_PIPE_COLOR
        pipe_y = random.choice(PIPE_Y_POSITIONS)
        
        CURRENT_PIPE_COLOR = random.choice(list(PIPE_COLORS.keys()))
        colored_pipe = colorize_surface(pipe_img, PIPE_COLORS[CURRENT_PIPE_COLOR])
        
        scale = random.choice(PIPE_SCALES)
        scaled_pipe = scale_surface(colored_pipe, scale)
        
        top_pipe = scaled_pipe.get_rect(midbottom=(467, pipe_y - pipe_gap))
        bottom_pipe = scaled_pipe.get_rect(midtop=(467, pipe_y))
        
        return top_pipe, bottom_pipe, scaled_pipe
    except Exception as e:
        logging.error(f"Error creating pipes: {e}")
        return None, None, None

def pipe_animation():
    # Handles pipe movement and collision detection.
    # Moves pipes from right to left
    # Removes pipes that are off screen
    # Checks for collisions with the bird
    # Triggers game over on collision
    try:
        global game_over, score_time
        for pipe, pipe_surface in pipes:
            if pipe.top < 0:
                flipped_pipe = pygame.transform.flip(pipe_surface, False, True)
                screen.blit(flipped_pipe, pipe)
            else:
                screen.blit(pipe_surface, pipe)

            if not game_paused:
                pipe.centerx -= pipe_speed
                if pipe.right < 0:
                    pipes.remove((pipe, pipe_surface))

                if bird_rect.colliderect(pipe):
                    try:
                        collision_sound.play()
                    except pygame.error:
                        logging.warning("Failed to play collision sound")
                    game_over = True
    except Exception as e:
        logging.error(f"Error in pipe animation: {e}")

def score_update():
    # Updates the player's score and high score.
    # Increments score when passing through pipes
    # Updates high score if current score is higher
    # Plays score sound effect
    try:
        global score, score_time, high_score
        if not pipes:
            return
            
        for pipe, _ in pipes:
            if not hasattr(pipe, 'centerx'):
                continue
                
            scoring_zone_width = 10
            scoring_zone_center = 67 
            
            zone_left = scoring_zone_center - scoring_zone_width - pipe_speed
            zone_right = scoring_zone_center + scoring_zone_width + pipe_speed
            
            if zone_left <= pipe.centerx <= zone_right:
                if score_time:
                    score += 1
                    score_time = False
                    try:
                        score_sound.play()
                    except pygame.error:
                        logging.warning("Failed to play score sound")
            elif pipe.centerx < zone_left:
                score_time = True

        if score > high_score:
            high_score = score
            try:
                save_score(score)
            except SaveError as e:
                logging.error(f"Failed to save high score: {e}")
    except Exception as e:
        logging.error(f"Error in score update: {e}")
        pass

def update_game_state():
    try:
        global bird_movement, game_over, floor_x
        
        if game_over or game_paused:
            return
            
        bird_movement = min(bird_movement + gravity, 15)
        new_y = bird_rect.centery + bird_movement
        
        if new_y < 5:
            new_y = 5
            bird_movement = 0
        elif new_y >= 550:
            new_y = 550
            bird_movement = 0
            game_over = True
            try:
                collision_sound.play()
            except pygame.error:
                logging.warning("Failed to play collision sound")
        
        bird_rect.centery = new_y

        floor_x = (floor_x - 1) % -448

        score_update()
        
        if pipes:
            try:
                pipe_animation()
            except Exception as e:
                logging.error(f"Error in pipe animation: {e}")
                pass
                
    except Exception as e:
        logging.error(f"Critical error in game state update: {e}")
        bird_movement = 0
        bird_rect.centery = height // 2

def handle_events():
    try:
        global bird_movement, game_over, game_paused, running, bird_index, bird_img, bird_rect
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if not game_over and not game_paused:
                        bird_movement = max(-7, bird_movement - 7)
                        try:
                            jump_sound.play()
                        except pygame.error:
                            logging.warning("Failed to play jump sound")
                    elif game_over:
                        try:
                            save_score(score)
                        except SaveError as e:
                            logging.error(f"Failed to save score: {e}")
                        reset_game_state()
                
                if event.key == pygame.K_p and not game_over:
                    game_paused = not game_paused
                    if game_paused:
                        pygame.time.set_timer(bird_flap, 0)
                        pygame.time.set_timer(create_pipe, 0)
                    else:
                        pygame.time.set_timer(bird_flap, 150)
                        pygame.time.set_timer(create_pipe, 1200)
                
                if event.key == pygame.K_ESCAPE:
                    running = False
                    reset_game_state()

            if event.type == bird_flap and not game_paused and not game_over:
                try:
                    if 0 <= bird_index < len(birds):
                        bird_index = (bird_index + 1) % len(birds)
                        bird_img = birds[bird_index]
                        bird_rect = bird_img.get_rect(center=bird_rect.center)
                except IndexError:
                    logging.error("Bird animation index out of range")
                    bird_index = 0

            if event.type == create_pipe and not game_paused and not game_over:
                try:
                    new_pipes = create_pipes()
                    if all(new_pipes):
                        pipes.append((new_pipes[0], new_pipes[2]))
                        pipes.append((new_pipes[1], new_pipes[2]))
                except Exception as e:
                    logging.error(f"Failed to create pipes: {e}")
                    
    except Exception as e:
        logging.error(f"Error handling events: {e}")
        pass

def reset_game_state():
    # Resets all game variables to their initial state.
    # Called when:
    # Starting a new game
    # Restarting after game over
    # Returning to main menu
    try:
        global game_over, game_paused, pipes, bird_movement, score, score_time, bird_rect
        game_over = False
        game_paused = False
        pipes = []
        bird_movement = 0
        score = 0
        score_time = True
        
        try:
            bird_rect.center = (67, height // 2)
        except AttributeError:
            logging.error("Failed to reset bird position")
            bird_rect = birds[0].get_rect(center=(67, height // 2))
            
        try:
            pygame.time.set_timer(create_pipe, 1200)
            pygame.time.set_timer(bird_flap, 150)
        except pygame.error as e:
            logging.error(f"Failed to reset game timers: {e}")
            
    except Exception as e:
        logging.error(f"Critical error resetting game state: {e}")
        game_over = False
        game_paused = False
        pipes = []
        bird_movement = 0
        score = 0

def draw_score(game_state):
    # Renders the score display based on game state.
    # During gameplay: Shows current score
    # After game over: Shows final score and high score
    # Also displays the ESC key instruction during gameplay.
    
    # Arguments:
        # game_state: String indicating current game state ("game_on" or "game_over")
    try:
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

            esc_text = small_font.render("ESC: Return to Menu", True, WHITE)
            esc_rect = esc_text.get_rect(topleft=(10, 10))
            screen.blit(esc_text, esc_rect)

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
    except Exception as e:
        logging.error(f"Error drawing score: {e}")

def choose_difficulty():
    # Displays the difficulty selection menu.
    # Allows players to choose between Easy, Medium, Hard, and Expert modes.
    # Each difficulty affects:
    # Pipe movement speed
    # Gap between pipes
    # Gravity strength

    try:
        global pipe_speed, pipe_gap, gravity
        difficulty_selected = False
        
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
                    elif event.key == pygame.K_ESCAPE:
                        return
    except Exception as e:
        logging.error(f"Error in difficulty selection: {e}")
        pipe_speed, pipe_gap, gravity = PIPE_SPEEDS["Medium"], PIPE_GAPS["Medium"], GRAVITY_VALUES["Medium"]

def adjust_volume():
    # Provides a volume control interface.
    # Allows adjustment of sound effects volume
    # Shows visual volume bar
    # Updates all game sounds immediately
    # Saves volume setting for future sessions
    try:
        global VOLUME
        volume_adjusted = False
        
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
                    elif event.key == pygame.K_ESCAPE:
                        return
                        
            try:
                jump_sound.set_volume(VOLUME)
                collision_sound.set_volume(VOLUME)
                score_sound.set_volume(VOLUME)
            except pygame.error:
                logging.warning("Failed to update sound volumes")
    except Exception as e:
        logging.error(f"Error adjusting volume: {e}")

def choose_bird_color():
    # Displays a menu for selecting the bird's color.
    # Allows players to choose from different color options and updates
    # All bird animation frames with the selected color.
    try:
        global CURRENT_BIRD_COLOR, bird_up, bird_mid, bird_down, birds, bird_img, bird_rect
        color_selected = False
        
        original_up = safe_load_image("images/img_47.png", True)
        original_mid = safe_load_image("images/img_48.png", True)
        original_down = safe_load_image("images/img_49.png", True)
        
        while not color_selected:
            screen.fill(BLACK)
            create_gradient_text(screen, "SELECT BIRD COLOR", score_font, BLUE, PURPLE, (width // 2, 100))
            
            y_offset = 200
            for i, (color_name, color_value) in enumerate(BIRD_COLORS.items(), 1):
                colored_bird = colorize_surface(original_mid, color_value)
                bird_rect = colored_bird.get_rect(center=(width // 2 - 100, y_offset))
                screen.blit(colored_bird, bird_rect)
                
                text = score_font.render(f"{i} - {color_name}", True, color_value)
                text_rect = text.get_rect(midleft=(width // 2 - 50, y_offset))
                screen.blit(text, text_rect)
                y_offset += 50
            
            instruction_text = small_font.render("Press 1-5 to select color", True, WHITE)
            instruction_rect = instruction_text.get_rect(center=(width // 2, y_offset + 20))
            screen.blit(instruction_text, instruction_rect)
            
            pygame.display.update()
            
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5]:
                        index = int(event.unicode) - 1
                        CURRENT_BIRD_COLOR = list(BIRD_COLORS.keys())[index]
                        color = BIRD_COLORS[CURRENT_BIRD_COLOR]
                        
                        bird_up = colorize_surface(original_up, color)
                        bird_mid = colorize_surface(original_mid, color)
                        bird_down = colorize_surface(original_down, color)
                        birds = [bird_up, bird_mid, bird_down]
                        bird_img = birds[bird_index]
                        bird_rect = bird_img.get_rect(center=(67, 622 // 2))
                        
                        color_selected = True
                    elif event.key == pygame.K_ESCAPE:
                        return
    except Exception as e:
        logging.error(f"Error in bird color selection: {e}")

def main_menu():
     # Displays and handles the main menu interface.
    # Provides options for:
    # Starting the game
    # Customizing bird color
    # Viewing leaderboard
    # Adjusting volume
    # Quitting the game
    try:
        menu_active = True
        selected_option = 0
        
        while menu_active:
            screen.blit(back_img, (0, 0))
            screen.blit(floor_img, (0, 550))
            
            create_gradient_text(screen, "FLAPPY BIRD", score_font, YELLOW, ORANGE, (width // 2, 150))
            
            options = ["Play", "Bird Color", "Leaderboard", "Volume", "Quit"]
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
                        selected_option = (selected_option - 1) % 5
                    elif event.key == pygame.K_DOWN:
                        selected_option = (selected_option + 1) % 5
                    elif event.key == pygame.K_RETURN:
                        if selected_option == 0:
                            menu_active = False
                            return "play"
                        elif selected_option == 1:
                            return "bird_color"
                        elif selected_option == 2:
                            return "leaderboard"
                        elif selected_option == 3:
                            return "volume"
                        else:
                            pygame.quit()
                            sys.exit()
    except Exception as e:
        logging.error(f"Error in main menu: {e}")
        return "play"

def render_game():
    try:
        bg_color = update_background_color()
        screen.fill(bg_color)
        screen.blit(back_img, (0, 0))
        
        if not game_over and not game_paused:
            rotated_bird = pygame.transform.rotozoom(bird_img, bird_movement * -6, 1)
            screen.blit(rotated_bird, bird_rect)
            
            pipe_animation()
            
            draw_score("game_on")
            
        elif game_paused:
            rotated_bird = pygame.transform.rotozoom(bird_img, bird_movement * -6, 1)
            screen.blit(rotated_bird, bird_rect)
            
            for pipe, pipe_surface in pipes:
                if pipe.top < 0:
                    flipped_pipe = pygame.transform.flip(pipe_surface, False, True)
                    screen.blit(flipped_pipe, pipe)
                else:
                    screen.blit(pipe_surface, pipe)
            
            draw_score("game_on")
            
            pause_text = score_font.render("PAUSED", True, WHITE)
            pause_rect = pause_text.get_rect(center=(width // 2, height // 2))
            screen.blit(pause_text, pause_rect)
            
            resume_text = small_font.render("Press P to Resume", True, GREEN)
            resume_rect = resume_text.get_rect(center=(width // 2, height // 2 + 40))
            screen.blit(resume_text, resume_rect)
        else:
            screen.blit(over_img, over_rect)
            draw_score("game_over")

        draw_floor()
        
        pygame.display.update()
    except Exception as e:
        logging.error(f"Error rendering game: {e}")

def init_game_assets():
    try:
        global back_img, floor_img, bird_up, bird_mid, bird_down, pipe_img, over_img
        global birds, bird_img, bird_rect, over_rect
        
        back_img = safe_load_image("images/img_46.png")
        floor_img = safe_load_image("images/img_50.png")
        bird_up = safe_load_image("images/img_47.png", True)
        bird_mid = safe_load_image("images/img_48.png", True)
        bird_down = safe_load_image("images/img_49.png", True)
        pipe_img = safe_load_image("images/greenpipe.png", True)
        over_img = safe_load_image("images/img_45.png", True)
        
        birds = [bird_up, bird_mid, bird_down]
        bird_img = birds[0]
        bird_rect = bird_img.get_rect(center=(67, 622 // 2))
        over_rect = over_img.get_rect(center=(width // 2, height // 2))
        
        return True
    except AssetLoadError as e:
        logging.critical(f"Failed to initialize game assets: {e}")
        return False

def init_sound_assets():
    try:
        global jump_sound, collision_sound, score_sound
        
        jump_sound = pygame.mixer.Sound("sounds/jump.mp3")
        collision_sound = pygame.mixer.Sound("sounds/collision.mp3")
        score_sound = pygame.mixer.Sound("sounds/score.mp3")
        
        jump_sound.set_volume(VOLUME)
        collision_sound.set_volume(VOLUME)
        score_sound.set_volume(VOLUME)
        
        return True
    except pygame.error as e:
        logging.error(f"Failed to initialize sound assets: {e}")
        return False

try:
    width, height = 350, 622
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Flappy Bird")
except pygame.error as e:
    logging.critical(f"Failed to create game window: {e}")
    sys.exit(1)

try:
    score_font = pygame.font.Font("freesansbold.ttf", 27)
    small_font = pygame.font.Font("freesansbold.ttf", 20)
except pygame.error as e: 
    logging.critical(f"Failed to load fonts: {e}")
    sys.exit(1)

floor_x = 0
bird_index = 0
bird_flap = pygame.USEREVENT
pygame.time.set_timer(bird_flap, 150)
bird_movement = 0
gravity = 0.17
pipes = []
create_pipe = pygame.USEREVENT + 1
pygame.time.set_timer(create_pipe, 1200)
game_over = False
game_paused = False
score = 0
high_score = 0
score_time = True

if not init_game_assets():
    logging.critical("Failed to initialize game assets")
    sys.exit(1)

if not init_sound_assets():
    logging.warning("Failed to initialize sound assets. Game will continue without sound.")

if __name__ == "__main__":
    try:
        while True:
            menu_choice = main_menu()
            
            if menu_choice == "play":
                choose_difficulty()
                reset_game_state()
                
                running = True
                while running:
                    try:
                        clock.tick(120)
                        handle_events()
                        update_game_state()
                        render_game()
                    except Exception as e:
                        logging.error(f"Error in game loop: {e}")
                        running = False
            
            elif menu_choice == "bird_color":
                try:
                    choose_bird_color()
                except Exception as e:
                    logging.error(f"Error in bird color selection: {e}")
            
            elif menu_choice == "leaderboard":
                try:
                    draw_leaderboard()
                    showing_leaderboard = True
                    while showing_leaderboard:
                        for event in pygame.event.get():
                            if event.type == pygame.QUIT:
                                pygame.quit()
                                sys.exit()
                            if event.type == pygame.KEYDOWN:
                                if event.key == pygame.K_SPACE:
                                    showing_leaderboard = False
                        pygame.display.update()
                except Exception as e:
                    logging.error(f"Error showing leaderboard: {e}")
            
            elif menu_choice == "volume":
                try:
                    adjust_volume()
                except Exception as e:
                    logging.error(f"Error adjusting volume: {e}")
    
    except KeyboardInterrupt:
        logging.info("Game terminated by user")
    except Exception as e:
        logging.critical(f"Critical error in main game loop: {e}")
    finally:
        pygame.quit()
        sys.exit()
