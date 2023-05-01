import pygame
import sys
import math

from tower import Tower
from enemy import Enemy
from projectile import Projectile
from toolbar import Toolbar
from utils import resize_image
from waves import wave_data

pygame.init()

SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Basic Tower Defense')
clock = pygame.time.Clock()

# Define colors
WHITE = (255, 255, 255)

# Load images
background_image = pygame.image.load("assets/background.png")
projectile_image = pygame.image.load("assets/projectiles/projectile.png")

wave_data = wave_data()

towers = pygame.sprite.Group()
enemies = pygame.sprite.Group()
projectiles = pygame.sprite.Group()

spawn_rate = 500  # in milliseconds
last_spawn_time = 0

background_image = resize_image(background_image, SCREEN_WIDTH, SCREEN_HEIGHT)
projectile_image = resize_image(projectile_image, 15, 15)

towers_data = Tower.get_towers_data()

tower_images = []
for tower_data in towers_data:
    image = pygame.image.load(tower_data["filename"])
    size = tower_data["size"]
    resized_image = resize_image(image, size, size)
    tower_data["image"] = resized_image
    tower_images.append(resized_image)

enemy_images_data = [
    {"filename": "assets/enemies/enemy-dark_brown.png", "health": 13},
    {"filename": "assets/enemies/enemy-dark_purple.png", "health": 12},
    {"filename": "assets/enemies/enemy-dark_green.png", "health": 11},
    {"filename": "assets/enemies/enemy-dark_blue.png", "health": 10},
    {"filename": "assets/enemies/enemy-dark_red.png", "health": 9},
    {"filename": "assets/enemies/enemy-black.png", "health": 8},
    {"filename": "assets/enemies/enemy-grey.png", "health": 7},
    {"filename": "assets/enemies/enemy-brown.png", "health": 6},
    {"filename": "assets/enemies/enemy-pink.png", "health": 5},
    {"filename": "assets/enemies/enemy-green.png", "health": 4},
    {"filename": "assets/enemies/enemy-yellow.png", "health": 3},
    {"filename": "assets/enemies/enemy-blue.png", "health": 2},
    {"filename": "assets/enemies/enemy-red.png", "health": 1}
]

enemy_images = []
for enemy_data in enemy_images_data:
    image = pygame.image.load(enemy_data["filename"])
    resized_image = resize_image(image, 40, 40)
    enemy_images.append(resized_image)

# Create a dictionary for easier access based on the enemy's health
enemy_images_dict = {data["health"]: image for data, image in zip(enemy_images_data, enemy_images)}

path_color = (128, 101, 66)  # Brown
path_width = 55
path = [(-25, 310), (110, 310), (110, 120), (270, 120), (270, 360), (480, 360), (480, 240), (800, 240)]
enemy_width, enemy_height = enemy_images[0].get_size()
offset = (enemy_width // 2, enemy_height // 2)

toolbar_width = 100
toolbar = Toolbar(SCREEN_WIDTH - toolbar_width, 0, toolbar_width, SCREEN_HEIGHT, (232, 230, 230), tower_images)

selected_tower_type = None

wave = 0
current_wave = 0

enemies_remaining = 0

game_started = False

font = pygame.font.Font(None, 24)

def resize_image(image, width, height):
    return pygame.transform.scale(image, (width, height))

# Draw Path
def draw_path(screen, path, color, width, offset):
    adjusted_path = [(x + offset[0], y + offset[1]) for x, y in path]
    pygame.draw.lines(screen, color, False, adjusted_path, width)

    # Draw circles at the corner points
    radius = width // 2
    for point in adjusted_path[1:-1]:
        pygame.draw.circle(screen, color, point, radius)

def draw_grid(screen, color, cell_size):
    width, height = screen.get_size()
    for x in range(0, width, cell_size):
        pygame.draw.line(screen, color, (x, 0), (x, height))
    for y in range(0, height, cell_size):
        pygame.draw.line(screen, color, (0, y), (width, y))

def draw_cursor_coordinates(screen, font, color):
    x, y = pygame.mouse.get_pos()
    coordinates_text = font.render(f"({x}, {y})", True, color)
    screen.blit(coordinates_text, (x + 10, y + 10))

def add_tower(position, tower_data): # tower_image, damage, rotatable):
    x, y = position
    tower_image = tower_data["image"]
    centered_x = x - tower_data["placement_center"][0] #tower_image.get_width() // 2
    centered_y = y - tower_data["placement_center"][1] #tower_image.get_height() // 2
    cooldown = 500
    range_radius = 150
    damage = tower_data["damage"]
    rotatable = tower_data["rotatable"]
    angle_threshold = tower_data["angle_threshold"]

    new_tower = Tower(centered_x, centered_y, tower_image, cooldown, range_radius, projectiles, damage, rotatable, tower_data, angle_threshold)
    towers.add(new_tower)

def spawn_enemy():
    global last_spawn_time, enemies_remaining, wave, wave_data
    now = pygame.time.get_ticks()

    if now - last_spawn_time >= spawn_rate and enemies_remaining > 0:
        wave_enemies = wave_data[wave - 1]["enemies"]
        for enemy_data in wave_enemies:
            if enemy_data["num"] > 0:
                enemy = Enemy(enemy_images_dict, enemy_data["health"], 1, path)
                enemies.add(enemy)
                last_spawn_time = now
                enemies_remaining -= 1
                enemy_data["num"] -= 1
                break

def reset_game():
    global enemies, towers, projectiles, last_spawn_time, game_started
    enemies = pygame.sprite.Group()
    towers = pygame.sprite.Group()
    projectiles = pygame.sprite.Group()
    last_spawn_time = 0
    game_started = False

def start_wave():
    global wave, enemies_remaining, game_started, wave_data
    wave += 1
    if wave <= len(wave_data):
        enemies_remaining = sum(enemy["num"] for enemy in wave_data[wave - 1]["enemies"])
        game_started = True
    else:
        print("All waves completed!")

def draw_wave_counter(screen, font, wave, color):
    wave_counter_text = font.render(f"Wave: {wave}", True, color)
    
    # Create a slightly dark and opaque background
    text_rect = wave_counter_text.get_rect()
    background = pygame.Surface((text_rect.width + 10, text_rect.height + 10))
    background.fill((0, 0, 0))
    background.set_alpha(128)
    
    # Draw the background and wave counter text
    background_rect = background.get_rect(topleft=(0, 0))
    screen.blit(background, background_rect)
    screen.blit(wave_counter_text, (background_rect.x + 5, background_rect.y + 5))

while True:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                if toolbar.rect.collidepoint(event.pos):
                    selected_tower_type = toolbar.select_tower(event.pos)
                    if selected_tower_type == 'start':
                        if not enemies and not enemies_remaining:  # If the current wave is complete
                            start_wave()
                    elif selected_tower_type == 'reset':
                        reset_game()
                elif selected_tower_type is not None and isinstance(selected_tower_type, int):
                    tower_image = tower_images[selected_tower_type]
                    tower_damage = towers_data[selected_tower_type]["damage"]
                    tower_rotatable = towers_data[selected_tower_type]["rotatable"]
                    tower_data = towers_data[selected_tower_type]
                    add_tower(event.pos, tower_data)

    # Spawn enemies
    if game_started and enemies_remaining > 0:
        spawn_enemy()

    # Update game objects
    projectile_speed = 3
    projectile_damage = 1
    towers.update(enemies, projectile_image, projectile_speed, projectile_damage)
    
    enemies.update()
    projectiles.update()

    # Move game objects
    enemies.update()

    # Rotate towers towards the closest enemy within range
    for tower in towers:
        enemies_in_range = [enemy for enemy in enemies if math.sqrt((tower.rect.centerx - enemy.rect.centerx) ** 2 + (tower.rect.centery - enemy.rect.centery) ** 2) <= tower.range]
        if enemies_in_range:
            closest_enemy = min(enemies_in_range, key=lambda enemy: math.sqrt((tower.rect.centerx - enemy.rect.centerx) ** 2 + (tower.rect.centery - enemy.rect.centery) ** 2))
            tower.rotate(closest_enemy)

    # Draw background
    screen.blit(background_image, (0, 0))

    # Draw wave counter
    draw_wave_counter(screen, font, wave, WHITE)

    # Draw path
    draw_path(screen, path, path_color, path_width, offset)

    # Draw game objects
    towers.draw(screen)
    enemies.draw(screen)
    projectiles.draw(screen)
    toolbar.draw(screen)

    # TESTING Draw grid (for development purposes)
    # draw_grid(screen, grid_color = (200, 200, 200), cell_size = 40)
    # TESTING Draw cursor coordinates (for development purposes)
    # draw_cursor_coordinates(screen, pygame.font.Font(None, 24), (0, 0, 0))

    # Update display
    pygame.display.flip()

    # Limit frame rate
    clock.tick(60)