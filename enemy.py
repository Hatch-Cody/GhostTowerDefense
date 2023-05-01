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
        distance = (dx ** 2 + dy ** 2) ** 0.5
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
