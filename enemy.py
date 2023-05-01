import pygame


class Enemy(pygame.sprite.Sprite):
    def __init__(self, images_dict, health, speed, path):
        super().__init__()
        self.images_dict = images_dict
        self.health = health
        self.image = self.images_dict[self.health]
        self.rect = self.image.get_rect()
        self.speed = speed
        self.path = path
        self.path_index = 0
        self.rect.topleft = path[0]

    def hit(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.kill()
        else:
            self.image = self.images_dict[self.health]

    def move(self):
        target_x, target_y = self.path[self.path_index]
        dx, dy = target_x - self.rect.x, target_y - self.rect.y
        distance = (dx**2 + dy**2) ** 0.5
        if distance <= self.speed:
            self.rect.topleft = self.path[self.path_index]
            self.path_index += 1
        else:
            direction = (dx / distance, dy / distance)
            self.rect.x += direction[0] * self.speed
            self.rect.y += direction[1] * self.speed

    def take_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.kill()

    def update(self):
        if self.path_index < len(self.path):
            self.move()
        else:
            self.kill()

    def get_enemies_data():
        return [
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
            {"filename": "assets/enemies/enemy-red.png", "health": 1},
        ]
    
    def get_enemies_images():
        enemy_images = []
        enemies_data = Enemy.get_enemies_data()

        for enemy_data in enemies_data:
            image = pygame.image.load(enemy_data["filename"])
            resized_image = pygame.transform.scale(image, (40, 40))
            enemy_images.append(resized_image)

        return enemy_images
