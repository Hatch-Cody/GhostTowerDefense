import copy
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
gold = 200
floating_texts = []

# Load images
background_image = resize_image(pygame.image.load("assets/background.png"), SCREEN_WIDTH, SCREEN_HEIGHT)
projectile_image = resize_image(pygame.image.load("assets/projectiles/projectile.png"), 15, 15)

projectile_speed = 3

_original_wave_data = wave_data()
wave_data = copy.deepcopy(_original_wave_data)

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
toolbar = Toolbar(SCREEN_WIDTH - toolbar_width, 0, toolbar_width, SCREEN_HEIGHT, (232, 230, 230), tower_images, towers_data)

selected_option = None

wave = 0
current_wave = 0

enemies_remaining = 0

game_started = False
game_state = "playing"  # "playing", "game_over", "victory"

font = pygame.font.Font(None, 24)
large_font = pygame.font.Font(None, 72)
medium_font = pygame.font.Font(None, 36)

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
    cooldown = tower_data["cooldown"]
    range_radius = tower_data["range_radius"]
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
    
    return rect_points

def award_kill(enemy):
    global gold
    gold += enemy.reward
    spawn_floating_text(f"+{enemy.reward}g", enemy.rect.centerx, enemy.rect.centery)

def spawn_floating_text(text, x, y, color=(255, 215, 0)):
    floating_texts.append({"text": text, "x": x, "y": float(y), "timer": 45, "color": color})

def spawn_enemy():
    global last_spawn_time, enemies_remaining, wave, wave_data
    now = pygame.time.get_ticks()

    if now - last_spawn_time >= spawn_rate and enemies_remaining > 0:
        wave_enemies = wave_data[wave - 1]["enemies"]
        for enemy_data in wave_enemies:
            if enemy_data["num"] > 0:
                enemy = Enemy(enemy_images_dict, enemy_data["health"], 1, path, on_kill_callback=award_kill)
                enemies.add(enemy)
                last_spawn_time = now
                enemies_remaining -= 1
                enemy_data["num"] -= 1
                break

def reset_game():
    global enemies, towers, projectiles, last_spawn_time, game_started
    global wave_data, wave, enemies_remaining, player_health, game_state
    global gold, floating_texts
    enemies = pygame.sprite.Group()
    towers = pygame.sprite.Group()
    projectiles = pygame.sprite.Group()
    last_spawn_time = 0
    game_started = False
    game_state = "playing"
    wave = 0
    enemies_remaining = 0
    player_health = 100
    gold = 200
    floating_texts = []
    wave_data = copy.deepcopy(_original_wave_data)

def draw_overlay(screen, title, subtitle, button_text):
    """Draw a semi-transparent overlay with title text, subtitle, and a button.
    Returns the button rect for click detection."""
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 160))
    screen.blit(overlay, (0, 0))

    title_surface = large_font.render(title, True, WHITE)
    title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
    screen.blit(title_surface, title_rect)

    sub_surface = medium_font.render(subtitle, True, (200, 200, 200))
    sub_rect = sub_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 10))
    screen.blit(sub_surface, sub_rect)

    button_rect = pygame.Rect(0, 0, 160, 40)
    button_rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 70)
    pygame.draw.rect(screen, (0, 191, 54), button_rect)
    pygame.draw.rect(screen, WHITE, button_rect, 2)
    btn_text = medium_font.render(button_text, True, WHITE)
    btn_text_rect = btn_text.get_rect(center=button_rect.center)
    screen.blit(btn_text, btn_text_rect)

    return button_rect

def start_wave():
    global wave, enemies_remaining, game_started, wave_data
    if wave < len(wave_data):
        wave += 1
        enemies_remaining = sum(enemy["num"] for enemy in wave_data[wave - 1]["enemies"])
        game_started = True

def draw_hud(screen, font, player_health, wave, gold):
    health_text = font.render(f"Health: {player_health}", True, WHITE)
    wave_text = font.render(f"Wave: {wave}/{len(wave_data)}", True, WHITE)
    gold_text = font.render(f"Gold: {gold}", True, (255, 215, 0))

    # Dark background behind HUD
    bg_width = max(health_text.get_width(), wave_text.get_width(), gold_text.get_width()) + 15
    background = pygame.Surface((bg_width, 65))
    background.fill((0, 0, 0))
    background.set_alpha(180)
    screen.blit(background, (0, 0))

    screen.blit(health_text, (5, 5))
    screen.blit(wave_text, (5, 25))
    screen.blit(gold_text, (5, 45))

def draw_floating_texts(screen, font):
    for ft in floating_texts[:]:
        ft["timer"] -= 1
        ft["y"] -= 1
        if ft["timer"] <= 0:
            floating_texts.remove(ft)
            continue
        alpha = int(255 * (ft["timer"] / 45))
        text_surface = font.render(ft["text"], True, ft["color"])
        text_surface.set_alpha(alpha)
        screen.blit(text_surface, (ft["x"], int(ft["y"])))

path_rects = create_path_rect(path, 70, offset)
overlay_button = None

while True:
    is_valid_pos = ''
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 3 and game_state == "playing":  # Right-click to sell
                for tower in towers:
                    if tower.rect.collidepoint(event.pos):
                        refund = int(tower.tower_data["cost"] * 0.6)
                        gold += refund
                        spawn_floating_text(f"+{refund}g", tower.rect.centerx, tower.rect.centery)
                        tower.kill()
                        break
            if event.button == 1:  # Left mouse button
                # Handle overlay button clicks (game over / victory)
                if game_state in ("game_over", "victory") and overlay_button and overlay_button.collidepoint(event.pos):
                    reset_game()
                    continue
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
                    if is_valid_pos == True and gold >= tower_data["cost"]:
                        gold -= tower_data["cost"]
                        add_tower(event.pos, tower_data)


    # Only update gameplay when playing
    if game_state == "playing":
        # Spawn enemies
        if game_started and enemies_remaining > 0:
            spawn_enemy()

        # Update game objects
        towers.update(enemies, projectile_image, projectile_speed)
        enemies.update()
        projectiles.update()

        # Check for enemies that reached the end
        for enemy in enemies.sprites():
            if enemy.rect.right >= SCREEN_WIDTH - 80:
                player_health -= enemy.health
                enemy.kill()

        # Check for game over
        if player_health <= 0:
            player_health = 0
            game_state = "game_over"

        # Check for victory
        if (game_started
                and wave >= len(wave_data)
                and enemies_remaining == 0
                and len(enemies) == 0):
            game_state = "victory"

    # Rotate towers towards the closest enemy within range
    for tower in towers:
        enemies_in_range = [enemy for enemy in enemies if math.sqrt((tower.rect.centerx - enemy.rect.centerx) ** 2 + (tower.rect.centery - enemy.rect.centery) ** 2) <= tower.range]
        if enemies_in_range:
            closest_enemy = min(enemies_in_range, key=lambda enemy: math.sqrt((tower.rect.centerx - enemy.rect.centerx) ** 2 + (tower.rect.centery - enemy.rect.centery) ** 2))
            tower.rotate(closest_enemy)

    # Draw background
    screen.blit(background_image, (0, 0))

    # Draw HUD
    draw_hud(screen, font, player_health, wave, gold)

    # Draw path
    draw_path(screen, path, path_color, path_width, offset)

    # Draw game objects
    enemies.draw(screen)
    towers.draw(screen)
    projectiles.draw(screen)
    toolbar.draw(screen, gold)

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

    # Draw floating texts
    draw_floating_texts(screen, font)

    # Draw game-over or victory overlay
    overlay_button = None
    if game_state == "game_over":
        overlay_button = draw_overlay(screen, "GAME OVER", f"Reached wave {wave}", "Restart")
    elif game_state == "victory":
        overlay_button = draw_overlay(screen, "VICTORY!", f"All {len(wave_data)} waves cleared!", "Play Again")

    # Update display
    pygame.display.flip()

    # Limit frame rate
    clock.tick(60)