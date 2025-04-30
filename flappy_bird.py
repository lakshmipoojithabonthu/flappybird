import pygame
import sys
import random
import datetime
import os
import math

# Initialize pygame
pygame.init()
pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=4096)
# Set working directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Screen dimensions
WIDTH = 1000
HEIGHT = 700
DASHBOARD_WIDTH = 350
GAME_WIDTH = WIDTH - DASHBOARD_WIDTH
FPS = 60

# Themes
LIGHT_THEME = {
    'background': (135, 206, 250),
    'bird': (255, 255, 0),
    'pipes': (0, 165, 0),
    'ground': (222, 184, 135),
    'text': (0, 0, 0),
    'score_highlight': (128, 0, 128)
}
DARK_THEME = {
    'background': (25, 25, 35),
    'bird': (255, 215, 0),
    'pipes': (100, 200, 100),
    'ground': (50, 50, 50),
    'text': (255, 255, 255),
    'score_highlight': (255, 215, 0)
}
current_theme = LIGHT_THEME

# Game states
INTRO, WAITING_FOR_START, PLAYING, GAME_OVER, PAUSED = 0, 1, 2, 3, 4
game_state = INTRO
intro_start_time = pygame.time.get_ticks()

# Game variables
bird_x, bird_y = 100, HEIGHT // 2
bird_width, bird_height = 40, 40
gravity, velocity, jump_strength = 0.5, 0, -10

pipe_width = 80
base_pipe_gap = 180
pipe_gap = base_pipe_gap
pipe_x = GAME_WIDTH
pipe_height = random.randint(100, HEIGHT - pipe_gap - 100)
passed_pipe = False

score, level, level_up_time = 0, 1, 0
LEVEL_UP_DURATION = 2000
new_high_score = False
start_time = None
total_jumps = 0

# Bird selection
bird_images = ["bird1.png", "bird2.png", "bird3.png"]
current_bird = 0

# Load high score
try:
    with open("highscore.txt", "r") as f:
        high_score = int(f.read())
except:
    high_score = 0

# Setup screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flappy Bird with Dashboard")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Comic Sans MS", 64)
small_font = pygame.font.SysFont(None, 32)
dashboard_font = pygame.font.SysFont("Arial", 24)
title_font = pygame.font.SysFont("Arial", 28, bold=True)
intro_font = pygame.font.SysFont("Comic Sans MS", 80, bold=True)

# Load bird images
bird_images = [pygame.image.load(image) for image in bird_images]
bird_images = [pygame.transform.scale(bird, (bird_width, bird_height)) for bird in bird_images]

# Load sounds
def load_sound(file_name):
    try:
        sound = pygame.mixer.Sound(file_name)
        sound.set_volume(1.0)
        return sound
    except pygame.error as e:
        print(f"Sound load error: {file_name} - {e}")
        return None

jump_sound = load_sound("jump.wav")
hit_sound = load_sound("hit.wav")
pass_sound = load_sound("success.wav")

pygame.mixer.set_num_channels(8)
jump_channel = pygame.mixer.Channel(1)
hit_channel = pygame.mixer.Channel(2)
pass_channel = pygame.mixer.Channel(3)

def toggle_theme():
    global current_theme
    current_theme = DARK_THEME if current_theme == LIGHT_THEME else LIGHT_THEME

show_tutorial = True
tutorial_texts = ["Press P to Pause/Resume"]

def draw_pipes():
    # Upper pipe
    upper_pipe_height = pipe_height
    pygame.draw.rect(screen, current_theme['pipes'], (pipe_x, 0, pipe_width, upper_pipe_height))

    # Lower pipe
    lower_pipe_y = pipe_height + pipe_gap
    lower_pipe_height = HEIGHT - lower_pipe_y - 50  # Subtract ground height
    pygame.draw.rect(screen, current_theme['pipes'], (pipe_x, lower_pipe_y, pipe_width, lower_pipe_height))

# Main game loop
running = True
while running:
    clock.tick(FPS)
    screen.fill(current_theme['background'])

    current_time = pygame.time.get_ticks()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            if score > high_score:
                with open("highscore.txt", "w") as f:
                    f.write(str(score))
            running = False

        if event.type == pygame.KEYDOWN:
            if game_state == INTRO:
                game_state = WAITING_FOR_START
                intro_start_time = pygame.time.get_ticks()
            elif event.key == pygame.K_TAB and game_state == WAITING_FOR_START:
                game_state = PLAYING
                start_time = datetime.datetime.now()
                show_tutorial = False

            if event.key == pygame.K_SPACE:
                if game_state == PLAYING:
                    velocity = jump_strength
                    total_jumps += 1
                    if jump_sound:
                        jump_channel.play(jump_sound)
                elif game_state == GAME_OVER:
                    bird_y = HEIGHT // 2
                    pipe_x = GAME_WIDTH
                    pipe_height = random.randint(100, HEIGHT - pipe_gap - 100)
                    velocity = 0
                    game_state = WAITING_FOR_START
                    if score > high_score:
                        high_score = score
                        new_high_score = True
                        with open("highscore.txt", "w") as f:
                            f.write(str(high_score))
                    else:
                        new_high_score = False
                    score, passed_pipe, level = 0, False, 1
                    pipe_gap = base_pipe_gap
                    total_jumps = 0

            if event.key == pygame.K_r:
                high_score = 0
                with open("highscore.txt", "w") as f:
                    f.write("0")

            if event.key == pygame.K_m:
                toggle_theme()

            if event.key == pygame.K_p and game_state in (PLAYING, PAUSED):
                game_state = PAUSED if game_state == PLAYING else PLAYING

            if event.key == pygame.K_b:
                current_bird = (current_bird + 1) % len(bird_images)

    # INTRO Screen Animation
    if game_state == INTRO:
        elapsed = (current_time - intro_start_time) / 1000.0
        alpha = min(255, int(elapsed * 255 / 2))
        bounce = int(10 * abs(math.sin(elapsed * 2)))
        intro_surface = intro_font.render("Flappy Bird", True, current_theme['text'])
        intro_surface.set_alpha(alpha)
        screen.blit(intro_surface, (GAME_WIDTH // 2 - intro_surface.get_width() // 2, 150 + bounce))

        press_any = small_font.render("Press any key to continue", True, current_theme['text'])
        if int(elapsed * 2) % 2 == 0:
            screen.blit(press_any, (GAME_WIDTH // 2 - press_any.get_width() // 2, 350))

        if elapsed > 4:
            game_state = WAITING_FOR_START

        pygame.display.update()
        continue

    if game_state == PLAYING:
        velocity += gravity
        bird_y += velocity
        pipe_x -= 4

        if pipe_x + pipe_width < 0:
            pipe_x = GAME_WIDTH
            pipe_height = random.randint(100, HEIGHT - pipe_gap - 100)
            passed_pipe = False

        if (
            bird_y < 0 or bird_y + bird_height > HEIGHT - 50 or
            (pipe_x < bird_x + bird_width < pipe_x + pipe_width and
             (bird_y < pipe_height or bird_y + bird_height > pipe_height + pipe_gap))
        ):
            game_state = GAME_OVER
            if hit_sound:
                hit_channel.play(hit_sound)

        if pipe_x + pipe_width < bird_x and not passed_pipe:
            score += 1
            passed_pipe = True
            if score % 5 == 0:
                level += 1
                level_up_time = pygame.time.get_ticks()
                pipe_gap = max(180, base_pipe_gap - (level - 1) * 10)  # Minimum gap of 180
            if pass_sound:
                pass_channel.play(pass_sound)

    # Bird
    screen.blit(bird_images[current_bird], (bird_x, int(bird_y)))

    # Draw pipes - now fully extended with no breaks
    draw_pipes()

    # Ground
    pygame.draw.rect(screen, current_theme['ground'], (0, HEIGHT - 50, GAME_WIDTH, 50))

    if pygame.time.get_ticks() - level_up_time < LEVEL_UP_DURATION:
        level_text = font.render("Level Up!", True, (255, 0, 255))
        screen.blit(level_text, (GAME_WIDTH // 2 - level_text.get_width() // 2, 100))

    if game_state == WAITING_FOR_START:
        start = font.render("  ", True, current_theme['text'])
        screen.blit(start, (GAME_WIDTH // 2 - start.get_width() // 2, HEIGHT // 2 - 30))

        info = small_font.render("SPACE to jump | M to toggle theme | B to change bird", True, current_theme['text'])
        screen.blit(info, (GAME_WIDTH // 2 - info.get_width() // 2, HEIGHT // 2 + 50))

        if show_tutorial:
            for i, text in enumerate(tutorial_texts):
                tutorial_line = small_font.render(text, True, current_theme['text'])
                screen.blit(tutorial_line, (GAME_WIDTH // 2 - tutorial_line.get_width() // 2, HEIGHT // 2 + 100 + i * 40))

    # Dashboard panel
    dashboard_panel = pygame.Surface((DASHBOARD_WIDTH, HEIGHT), pygame.SRCALPHA)
    dashboard_panel.fill((0, 0, 0, 180))
    screen.blit(dashboard_panel, (GAME_WIDTH, 0))
    pygame.draw.rect(screen, (255, 255, 255), (GAME_WIDTH, 0, DASHBOARD_WIDTH, HEIGHT), 2)

    # Dashboard title
    title = title_font.render("GAME DASHBOARD", True, (255, 255, 255))
    screen.blit(title, (GAME_WIDTH + DASHBOARD_WIDTH//2 - title.get_width()//2, 20))

    # Dashboard items
    dashboard_items = [
        ("Score:", str(score)),
        ("High Score:", str(high_score)),
        ("Level:", str(level)),
        ("Pipes Passed:", str(score)),
        ("Pipe Gap:", f"{pipe_gap}px"),
        ("Game State:", ["Intro", "Waiting", "Playing", "Game Over", "Paused"][game_state]),
        ("Gravity:", f"{gravity:.1f}"),
        ("Velocity:", f"{velocity:.1f}"),
        ("Bird Position:", f"{int(bird_x)}, {int(bird_y)}"),
        ("Next Pipe:", f"X: {pipe_x}"),
        ("Current Bird:", ""),
        ("Theme:", "Dark" if current_theme == DARK_THEME else "Light")
    ]

    # Draw dashboard items
    y_offset = 70
    line_height = 30

    for label, value in dashboard_items:
        label_text = dashboard_font.render(label, True, (200, 200, 200))
        screen.blit(label_text, (GAME_WIDTH + 20, y_offset))

        if label != "Current Bird:":
            value_text = dashboard_font.render(value, True, (255, 255, 255))
            screen.blit(value_text, (GAME_WIDTH + 180, y_offset))

        y_offset += line_height

        if label == "Current Bird:":
            screen.blit(pygame.transform.scale(bird_images[current_bird], (40, 40)),
                        (GAME_WIDTH + 180, y_offset - 5))
            y_offset += 40

    pygame.display.update()

pygame.quit()