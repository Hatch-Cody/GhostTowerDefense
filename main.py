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
path_color = (128, 101, 66)  # Brown
tower_placement_circle_color = (0, 0, 0, 70)  # Semi-transparent black

player_health = 100

# Load images
background_image = resize_image(pygame.image.load("assets/background.png"), SCREEN_WIDTH, SCREEN_HEIGHT)
projectile_image = resize_image(pygame.image.load("assets/projectiles/projectile.png"), 15, 15)

projectile_speed = 3
projectile_damage = 1

wave_data = wave_data()

# Sprites
towers = pygame.sprite.Group()
enemies = pygame.sprite.Group()
projectiles = pygame.sprite.Group()

# Enemy
spawn_rate = 500  # in milliseconds
last_spawn_time = 0

towers_data = Tower.get_towers_data()

tower_images = [] # Tower.get_tower_images()
for tower_data in towers_data:
    image = pygame.image.load(tower_data["filename"])
    size = tower_data["size"]
    resized_image = resize_image(image, size, size)
    tower_data["image"] = resized_image
    tower_images.append(resized_image)

enemies_data = Enemy.get_enemies_data()

enemy_images = [] # Enemy.get_enemies_images()
for enemy_data in enemies_data:
    image = pygame.image.load(enemy_data["filename"])
    resized_image = resize_image(image, 40, 40)
    enemy_images.append(resized_image)

# Create a dictionary for easier access based on the enemy's health
enemy_images_dict = {data["health"]: image for data, image in zip(Enemy.get_enemies_data(), enemy_images)}

path_width = 55
path = [(-25, 310), (110, 310), (110, 120), (270, 120), (270, 360), (480, 360), (480, 240), (800, 240)]
enemy_width, enemy_height = enemy_images[0].get_size()
offset = (enemy_width // 2, enemy_height // 2)

toolbar_width = 100
toolbar = Toolbar(SCREEN_WIDTH - toolbar_width, 0, toolbar_width, SCREEN_HEIGHT, (232, 230, 230), tower_images)

selected_option = None

wave = 0
current_wave = 0

enemies_remaining = 0

game_started = False

font = pygame.font.Font(None, 24)

# towers_data = Tower.get_towers_data()

def resize_image(image, width, height):
    return pygame.transform.scale(image, (width, height))

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

def add_tower(position, tower_data):
    x, y = position
    tower_image = tower_data["image"]
    centered_x = x - tower_data["placement_center"][0] 
    centered_y = y - tower_data["placement_center"][1]
    cooldown = 500
    range_radius = 150
    damage = tower_data["damage"]
    rotatable = tower_data["rotatable"]
    angle_threshold = tower_data["angle_threshold"]

    new_tower = Tower(centered_x, centered_y, tower_image, cooldown, range_radius, projectiles, damage, rotatable, tower_data, angle_threshold)
    towers.add(new_tower)

def draw_placement_circle(screen, position, radius, color):
    surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
    pygame.draw.circle(surface, color, (radius, radius), radius)
    rect = surface.get_rect()
    rect.center = position
    screen.blit(surface, rect)

def is_valid_position(new_tower_rect, towers, path_rects):
    # Check if the tower is not on the path
    for path_rect in path_rects:
        if new_tower_rect.colliderect(path_rect):
            return "Path collision"

    # Check if the tower is not overlapping with other towers
    for tower in towers:
        if new_tower_rect.colliderect(tower.rect):
            return "Tower collision"

    return True

def create_path_rect(path, path_width, offset):
    rect_points = [] 
    for i in range(len(path) - 1):
        start = path[i]
        end = path[i + 1]
        
        if start[0] == end[0]:  # vertical segment
            rect_points.append(pygame.Rect((start[0] - path_width // 2)+10, min(start[1], end[1]), path_width, abs(end[1] - start[1])))

        else:  # horizontal segment
            rect_points.append(pygame.Rect(min(start[0], end[0]), (start[1] - path_width // 2)+10, abs(end[0] - start[0]), path_width))
    
    print(rect_points)
    return rect_points

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
    screen.blit(wave_counter_text, (5, 25))

def draw_player_health(screen, font, player_health, color):
    health_text = font.render(f"Health: {player_health}", True, color)

    # Create a slightly dark and opaque background
    text_rect = health_text.get_rect()
    background = pygame.Surface((text_rect.width + 10, text_rect.height + 30))
    background.fill((0, 0, 0))
    background.set_alpha(180)

    # Draw the background and wave counter text
    background_rect = background.get_rect(topleft=(0, 0))
    screen.blit(background, background_rect)
    screen.blit(health_text, (background_rect.x + 5, background_rect.y + 5))

path_rects = create_path_rect(path, 70, offset)

while True:
    is_valid_pos = ''
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                if toolbar.rect.collidepoint(event.pos):
                    selected_option = toolbar.select_option(event.pos)
                    if selected_option == 'start':
                        if not enemies and not enemies_remaining:  # If the current wave is complete
                            start_wave()
                    elif selected_option == 'reset':
                        reset_game()
                elif selected_option is not None and isinstance(selected_option, int):
                    tower_data = towers_data[selected_option]
                    new_tower_rect = pygame.Rect(event.pos[0] - tower_data["tower_base"][0], event.pos[1] - tower_data["tower_base"][1], tower_data["tower_base"][0], tower_data["tower_base"][1])
                    
                    is_valid_pos = is_valid_position(new_tower_rect, towers, path_rects)
                    if is_valid_pos == True:
                        print('adding tower')
                        add_tower(event.pos, tower_data)
                    else:
                        print(is_valid_pos)


    # Spawn enemies
    if game_started and enemies_remaining > 0:
        spawn_enemy()

    # Update game objects
    towers.update(enemies, projectile_image, projectile_speed, projectile_damage)    
    enemies.update()
    projectiles.update()

    # Move game objects
    enemies.update()

    # Update Health
    for enemy in enemies.sprites():
        enemy.update()
        if enemy.rect.right >= SCREEN_WIDTH-80:  # Enemy left the screen
            player_health -= enemy.health
            enemy.kill()  # Remove the enemy from the game

    # Rotate towers towards the closest enemy within range
    for tower in towers:
        enemies_in_range = [enemy for enemy in enemies if math.sqrt((tower.rect.centerx - enemy.rect.centerx) ** 2 + (tower.rect.centery - enemy.rect.centery) ** 2) <= tower.range]
        if enemies_in_range:
            closest_enemy = min(enemies_in_range, key=lambda enemy: math.sqrt((tower.rect.centerx - enemy.rect.centerx) ** 2 + (tower.rect.centery - enemy.rect.centery) ** 2))
            tower.rotate(closest_enemy)

    # Draw background
    screen.blit(background_image, (0, 0))

    # Draw player health
    draw_player_health(screen, font, player_health, WHITE)

    # Draw wave counter
    draw_wave_counter(screen, font, wave, WHITE)

    # Draw path
    draw_path(screen, path, path_color, path_width, offset)

    # Draw game objects
    enemies.draw(screen)
    towers.draw(screen)
    projectiles.draw(screen)
    toolbar.draw(screen)

    # Draw tower placement circle
    if isinstance(selected_option, int) and not toolbar.rect.collidepoint(pygame.mouse.get_pos()):
        tower_data = towers_data[selected_option]
        tower_range = tower_data["range_radius"]
        new_tower_rect = pygame.Rect(pygame.mouse.get_pos()[0] - tower_data["tower_base"][0], pygame.mouse.get_pos()[1] - tower_data["tower_base"][1], tower_data["tower_base"][0], tower_data["tower_base"][1])
        if is_valid_position(new_tower_rect, towers, path_rects) == True:
            draw_placement_circle(screen, pygame.mouse.get_pos(), tower_range, tower_placement_circle_color)
        else:
            invalid_placement_color = (255, 0, 0, 70)  # Semi-transparent red
            draw_placement_circle(screen, pygame.mouse.get_pos(), tower_range, invalid_placement_color)

    # TESTING Draw grid (for development purposes)
    # draw_grid(screen, grid_color = (200, 200, 200), cell_size = 40)
    # TESTING Draw cursor coordinates (for development purposes)
    # draw_cursor_coordinates(screen, pygame.font.Font(None, 24), (0, 0, 0))

    # Update display
    pygame.display.flip()

    # Limit frame rate
    clock.tick(60)