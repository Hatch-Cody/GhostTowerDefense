import pygame

class Projectile(pygame.sprite.Sprite):
    def __init__(self, x, y, target, image, speed, damage, slow_duration=0, slow_factor=1.0):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.target = target
        self.speed = speed
        self.damage = damage
        self.slow_duration = slow_duration
        self.slow_factor = slow_factor

    def move(self):
        dx, dy = self.target.rect.x - self.rect.x, self.target.rect.y - self.rect.y
        distance = (dx ** 2 + dy ** 2) ** 0.5

        if distance > 0:
            unit_x, unit_y = dx / distance, dy / distance
            self.rect.x += unit_x * self.speed
            self.rect.y += unit_y * self.speed
        else:
            self.kill()

    def collide_with_target(self):
        return pygame.sprite.collide_rect(self, self.target)

    def update(self):
        if self.target.alive():
            self.move()
            if self.rect.colliderect(self.target.rect):
                if self.slow_duration > 0:
                    self.target.apply_slow(self.slow_duration, self.slow_factor)
                self.target.hit(self.damage)
                self.kill()
        else:
            self.kill()