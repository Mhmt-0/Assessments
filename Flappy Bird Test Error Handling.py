# Flappy Bird Game with Enhanced Error Handling

import pygame
import sys
import time
import random
import json
import logging
import traceback
from pathlib import Path
from typing import Optional, Tuple, List, Dict, Any, Union

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
    handlers=[
        logging.FileHandler('flappy_bird.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class GameError(Exception):
    # Base exception class for game-specific errors.
    def __init__(self, message: str, error_code: Optional[int] = None):
        super().__init__(message)
        self.error_code = error_code
        logger.error(f"GameError: {message} (Code: {error_code})")

class AssetLoadError(GameError):
    # Exception raised when game assets fail to load.
    def __init__(self, asset_path: str, original_error: Optional[Exception] = None):
        message = f"Failed to load asset: {asset_path}"
        if original_error:
            message += f" - {str(original_error)}"
        super().__init__(message, error_code=1001)

class SaveError(GameError):
    # Exception raised when saving game data fails.
    def __init__(self, operation: str, original_error: Optional[Exception] = None):
        message = f"Failed to save data during {operation}"
        if original_error:
            message += f" - {str(original_error)}"
        super().__init__(message, error_code=1002)

class ConfigurationError(GameError):
    # Exception raised when game configuration fails.
    def __init__(self, config_type: str, original_error: Optional[Exception] = None):
        message = f"Configuration error in {config_type}"
        if original_error:
            message += f" - {str(original_error)}"
        super().__init__(message, error_code=1003)

class RenderError(GameError):
    # Exception raised when rendering fails.
    def __init__(self, component: str, original_error: Optional[Exception] = None):
        message = f"Failed to render {component}"
        if original_error:
            message += f" - {str(original_error)}"
        super().__init__(message, error_code=1004)

class AudioError(GameError):
    # Exception raised when audio operations fail.
    def __init__(self, operation: str, original_error: Optional[Exception] = None):
        message = f"Audio operation failed: {operation}"
        if original_error:
            message += f" - {str(original_error)}"
        super().__init__(message, error_code=1005)

class InputError(GameError):
    # Exception raised when input handling fails.
    def __init__(self, input_type: str, original_error: Optional[Exception] = None):
        message = f"Input handling failed: {input_type}"
        if original_error:
            message += f" - {str(original_error)}"
        super().__init__(message, error_code=1006)

def error_handler(func):
    # Decorator for handling errors in game functions.
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except GameError as ge:
            logger.error(f"Game Error in {func.__name__}: {str(ge)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in {func.__name__}: {str(e)}\n{traceback.format_exc()}")
            return None
    return wrapper

def validate_game_state(func):
    # Decorator for validating game state before execution.
    def wrapper(*args, **kwargs):
        try:
            if not hasattr(pygame, 'init'):
                raise ConfigurationError("Pygame not initialized")
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Game state validation failed in {func.__name__}: {str(e)}")
            return None
    return wrapper

def retry_operation(max_attempts: int = 3, delay: float = 1.0):
    # Decorator for retrying failed operations.
    def decorator(func):
        def wrapper(*args, **kwargs):
            attempts = 0
            while attempts < max_attempts:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    attempts += 1
                    if attempts == max_attempts:
                        logger.error(f"Operation failed after {max_attempts} attempts: {str(e)}")
                        raise
                    logger.warning(f"Attempt {attempts} failed, retrying in {delay} seconds...")
                    time.sleep(delay)
            return None
        return wrapper
    return decorator

class GameState:
    # Class to manage and validate game state.
    def __init__(self):
        self.initialized = False
        self.assets_loaded = False
        self.sound_loaded = False
        self.running = False
        self.error_count = 0
        self.last_error_time = 0
        self.error_threshold = 5
        self.error_timeout = 60
        self.fps = 120
        self.debug_mode = False

    def log_error(self):
        # Log and track errors to prevent infinite error loops.
        current_time = time.time()
        if current_time - self.last_error_time > self.error_timeout:
            self.error_count = 0
        self.error_count += 1
        self.last_error_time = current_time
        
        if self.error_count >= self.error_threshold:
            logger.critical("Error threshold exceeded. Terminating game.")
            self.terminate_game()

    def terminate_game(self):
        # Safely terminate the game.
        try:
            if self.sound_loaded:
                pygame.mixer.quit()
            pygame.quit()
        except Exception as e:
            logger.error(f"Error during game termination: {e}")
        finally:
            sys.exit(1)

    @error_handler
    def toggle_debug_mode(self):
        # Toggle debug mode for additional logging and visual feedback.
        self.debug_mode = not self.debug_mode
        logger.info(f"Debug mode {'enabled' if self.debug_mode else 'disabled'}")

game_state = GameState()

try:
    pygame.init()
    pygame.mixer.init()
except pygame.error as e:
    logger.critical(f"Failed to initialize Pygame: {e}")
    sys.exit(1)

GAME_CONFIG = {
    'VOLUME': 0.5,
    'COLORS': {
        'WHITE': (255, 255, 255),
        'BLACK': (0, 0, 0),
        'YELLOW': (255, 255, 0),
        'GREEN': (0, 255, 0),
        'RED': (255, 0, 0),
        'ORANGE': (255, 165, 0),
        'BLUE': (0, 191, 255),
        'PURPLE': (147, 112, 219),
        'PINK': (255, 192, 203)
    },
    'BIRD_COLORS': {
        "Yellow": (255, 255, 0),
        "Blue": (0, 191, 255),
        "Red": (255, 0, 0),
        "Purple": (147, 112, 219),
        "Pink": (255, 192, 203)
    },
    'PIPE_COLORS': {
        "Green": (0, 255, 0),
        "Blue": (0, 191, 255),
        "Red": (255, 0, 0),
        "Purple": (147, 112, 219),
        "Orange": (255, 165, 0),
        "Pink": (255, 192, 203)
    },
    'DIFFICULTY': {
        'GRAVITY': {
            "Easy": 0.15,
            "Medium": 0.17,
            "Hard": 0.19,
            "Expert": 0.21
        },
        'PIPE_SPEEDS': {
            "Easy": 2,
            "Medium": 3,
            "Hard": 4,
            "Expert": 5
        },
        'PIPE_GAPS': {
            "Easy": 350,
            "Medium": 300,
            "Hard": 250,
            "Expert": 200
        }
    },
    'PIPE_SCALES': [0.8, 1.0, 1.2],
    'PIPE_Y_POSITIONS': [200, 250, 300, 350, 400],
    'FLASH_INTERVAL': 500
}

game_vars = {
    'current_bird_color': "Yellow",
    'current_pipe_color': "Green",
    'last_flash': 0,
    'flash_on': False,
    'bg_colors': [(135, 206, 235), (100, 149, 237), (147, 112, 219)],
    'bg_color_index': 0,
    'bg_transition_speed': 0.015,
    'bg_transition_progress': 0
}

@error_handler
def safe_load_image(path: str, convert_alpha: bool = False) -> Optional[pygame.Surface]:
    # Safely load an image with error handling.
    try:
        if not Path(path).exists():
            raise FileNotFoundError(f"Image file not found: {path}")
        
        img = pygame.image.load(path)
        if convert_alpha:
            return img.convert_alpha()
        return img
    except (pygame.error, FileNotFoundError) as e:
        raise AssetLoadError(path, e)

@error_handler
def safe_sound_load(path: str) -> Optional[pygame.mixer.Sound]:
    # Safely load a sound file with error handling.
    try:
        if not Path(path).exists():
            raise FileNotFoundError(f"Sound file not found: {path}")
        return pygame.mixer.Sound(path)
    except (pygame.error, FileNotFoundError) as e:
        raise AudioError(f"loading sound: {path}", e)

@validate_game_state
@error_handler
def play_sound(sound: pygame.mixer.Sound) -> None:
    # Safely play a sound with error handling.
    try:
        sound.play()
    except pygame.error as e:
        raise AudioError("playing sound", e)

@validate_game_state
@error_handler
def create_gradient_text(surface: pygame.Surface, text: str, font: pygame.font.Font,
                        start_color: Tuple[int, int, int], end_color: Tuple[int, int, int],
                        pos: Tuple[int, int]) -> None:
    # Create gradient text with error handling.
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
        raise RenderError("gradient text", e)

@validate_game_state
@error_handler
def update_background_color() -> Tuple[int, int, int]:
    # Update background color with error handling.
    try:
        game_vars['bg_transition_progress'] += game_vars['bg_transition_speed']
        if game_vars['bg_transition_progress'] >= 1:
            game_vars['bg_transition_progress'] = 0
            game_vars['bg_color_index'] = (game_vars['bg_color_index'] + 1) % len(game_vars['bg_colors'])
        
        current_color = game_vars['bg_colors'][game_vars['bg_color_index']]
        next_color = game_vars['bg_colors'][(game_vars['bg_color_index'] + 1) % len(game_vars['bg_colors'])]
        
        r = current_color[0] + (next_color[0] - current_color[0]) * game_vars['bg_transition_progress']
        g = current_color[1] + (next_color[1] - current_color[1]) * game_vars['bg_transition_progress']
        b = current_color[2] + (next_color[2] - current_color[2]) * game_vars['bg_transition_progress']
        
        return (int(r), int(g), int(b))
    except Exception as e:
        logger.error(f"Background color update failed: {e}")
        return game_vars['bg_colors'][0]

@validate_game_state
@error_handler
@retry_operation(max_attempts=3)
def load_scores() -> Dict[str, List[int]]:
    # Load scores with error handling and retry capability.
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
    except (json.JSONDecodeError, ValueError, IOError) as e:
        raise SaveError("loading scores", e)

@validate_game_state
@error_handler
@retry_operation(max_attempts=3)
def save_score(new_score: int) -> None:
    # Save score with error handling and retry capability.
    try:
        if not isinstance(new_score, (int, float)):
            raise ValueError("Score must be a number")
        
        scores = load_scores()
        scores['high_scores'].append(new_score)
        scores['high_scores'].sort(reverse=True)
        scores['high_scores'] = scores['high_scores'][:5]
        
        with open('scores.json', 'w') as f:
            json.dump(scores, f)
    except Exception as e:
        raise SaveError("saving score", e)

@validate_game_state
@error_handler
def handle_events() -> None:
    # Handle game events with error handling.
    try:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_state.terminate_game()
            elif event.type == pygame.KEYDOWN:
                handle_keydown_event(event)
    except Exception as e:
        raise InputError("event handling", e)

@validate_game_state
@error_handler
def handle_keydown_event(event: pygame.event.Event) -> None:
    # Handle keyboard events with error handling.
    try:
        if event.key == pygame.K_ESCAPE:
            game_state.terminate_game()
        elif event.key == pygame.K_d and pygame.key.get_mods() & pygame.KMOD_CTRL:
            game_state.toggle_debug_mode()
    except Exception as e:
        raise InputError("keydown handling", e)

@validate_game_state
@error_handler
def render_game() -> None:
    # Render the game with error handling.
    try:
        bg_color = update_background_color()
        screen.fill(bg_color)
        
        pygame.display.flip()
    except Exception as e:
        raise RenderError("game rendering", e)

def main():
    # Main game loop with comprehensive error handling.
    try:
        game_state.initialized = True
        clock = pygame.time.Clock()
        
        while True:
            try:
                clock.tick(game_state.fps)
                handle_events()
                render_game()
                
                if game_state.debug_mode:
                    fps = clock.get_fps()
                    logger.debug(f"FPS: {fps:.2f}")
                
            except Exception as e:
                logger.error(f"Error in game loop: {e}")
                game_state.log_error()
                if game_state.error_count >= game_state.error_threshold:
                    break
                continue
    
    except KeyboardInterrupt:
        logger.info("Game terminated by user")
    except Exception as e:
        logger.critical(f"Critical error in main game loop: {e}")
    finally:
        game_state.terminate_game()

if __name__ == "__main__":
    main()