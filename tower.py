import pygame
import math

from enemy import Enemy
from projectile import Projectile

class Tower(pygame.sprite.Sprite):
    def __init__(
        self,
        x,
        y,
        image,
        cooldown,
        range_radius,
        projectiles_group,
        damage,
        rotatable,
        tower_data,
        angle_threshold=5,
    ):
        super().__init__()
        self.image = image
        self.original_image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.cooldown = cooldown
        self.range_radius = range_radius
        self.last_shot = pygame.time.get_ticks()
        self.projectiles = projectiles_group
        self.range = 150
        self.angle = 180  # Set the initial angle
        self.rotation_speed = 3  # Degrees per frame
        self.damage = damage
        self.rotatable = rotatable
        self.angle_threshold = angle_threshold
        self.tower_data = tower_data

    def in_range(self, enemy):
        distance = (
            (
                (self.rect.x + self.rect.width // 2)
                - (enemy.rect.x + enemy.rect.width // 2)
            )
            ** 2
            + (
                (self.rect.y + self.rect.height // 2)
                - (enemy.rect.y + enemy.rect.height // 2)
            )
            ** 2
        ) ** 0.5
        return distance <= self.tower_data['range_radius']

    def can_shoot(self):
        now = pygame.time.get_ticks()
        return now - self.last_shot >= self.cooldown

    def angle_diff(a1, a2):
        return (a1 - a2 + 180) % 360 - 180

    def shoot(self, enemy, projectile_image, projectile_speed, projectile_damage):
        # Calculate the position of the projectile based on the tower's angle and size
        tower_center_x = self.rect.centerx
        tower_center_y = self.rect.centery
        tower_radius = self.rect.width // 2

        # Calculate the position of the projectile using trigonometry
        projectile_x = tower_center_x
        projectile_y = tower_center_y

        # Create the projectile and add it to the projectiles group
        projectile = Projectile(
            projectile_x,
            projectile_y,
            enemy,
            projectile_image,
            projectile_speed,
            projectile_damage,
        )
        self.projectiles.add(projectile)
        self.last_shot = pygame.time.get_ticks()

    def rotate(self, target):
        if self.rotatable:
            dx = target.rect.x - self.rect.x
            dy = target.rect.y - self.rect.y
            target_angle = math.degrees(math.atan2(-dy, dx))
            angle_diff = (target_angle - self.angle) % 360

            if angle_diff > 180:
                angle_diff -= 360

            if abs(angle_diff) <= self.rotation_speed:
                self.angle = target_angle
            else:
                self.angle += math.copysign(self.rotation_speed, angle_diff)

            self.image = pygame.transform.rotate(self.original_image, self.angle)
            self.rect = self.image.get_rect(center=self.rect.center)

    def update(self, enemies, projectile_image, projectile_speed, projectile_damage):
        target = None
        min_distance = float("inf")

        for enemy in enemies:
            if self.in_range(enemy):
                distance = (
                    (self.rect.x - enemy.rect.x) ** 2
                    + (self.rect.y - enemy.rect.y) ** 2
                ) ** 0.5
                if distance < min_distance:
                    target = enemy
                    min_distance = distance

        if target and self.in_range(target):  # Check if the target is in range
            self.rotate(target)
            dx = target.rect.x - self.rect.x
            dy = target.rect.y - self.rect.y
            target_angle = math.degrees(math.atan2(-dy, dx))
            angle_diff = (target_angle - self.angle) % 360

            if angle_diff > 180:
                angle_diff -= 360

            # Use the angle_threshold attribute
            if abs(angle_diff) <= self.angle_threshold and self.can_shoot():
                self.shoot(
                    target, projectile_image, projectile_speed, projectile_damage
                )

    def get_towers_data():
        return [
            {
                "name:": "Cannon",
                "filename": "assets/towers/cannon.png",
                "size": 40,
                "placement_center": (20, 20),
                "tower_base": (20, 20),
                "damage": 2,
                "rotatable": True,
                "angle_threshold": 5,
                "range_radius": 100
            },
            {
                "name:": "Archer Tower",
                "filename": "assets/towers/archer-tower.png",
                "size": 80,
                "placement_center": (40, 60),
                "tower_base": (20, 20),
                "damage": 1,
                "rotatable": False,
                "angle_threshold": 365,
                "range_radius": 70
            },
        ]

    def get_tower_images():
        towers_data = Tower.get_towers_data()
        tower_images = []

        for tower_data in towers_data:
            image = pygame.image.load(tower_data["filename"])
            size = tower_data["size"]
            resized_image = pygame.transform.scale(image, (size, size))
            tower_data["image"] = resized_image
            tower_images.append(resized_image)

        return tower_images