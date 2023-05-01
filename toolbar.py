import pygame

class Toolbar:
    def __init__(self, x, y, width, height, color, tower_images):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.tower_images = tower_images
        self.selected_tower = None
        self.deselect_button = pygame.Rect(x, height-80, width-10, 30)
        self.start_button = pygame.Rect(x, height-50, width-10, 30)
        self.reset_button = pygame.Rect(x, height-20, width-10, 30)

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
        pygame.draw.rect(screen, (191, 54, 54), self.deselect_button, 2)
        screen.blit(pygame.font.Font(None, 24).render("Deselect", True, (191, 54, 54)), self.deselect_button)
        
        pygame.draw.rect(screen, (0, 191, 54), self.start_button, 2)
        screen.blit(pygame.font.Font(None, 24).render("Start", True, (0, 191, 54)), self.start_button)
        
        pygame.draw.rect(screen, (191, 54, 191), self.reset_button, 2)
        screen.blit(pygame.font.Font(None, 24).render("Reset", True, (191, 54, 191)), self.reset_button)

        for index, image in enumerate(self.tower_images):
            image = pygame.transform.scale(image, (40, 40))
            tower_rect = image.get_rect()
            tower_rect.x = self.rect.x + (self.rect.width - tower_rect.width) // 2
            tower_rect.y = self.rect.y + self.deselect_button.height + index * (tower_rect.height + 10) + 10
            screen.blit(image, tower_rect)
            if index == self.selected_tower:
                pygame.draw.rect(screen, (255, 0, 0), tower_rect, 2)

    def select_tower(self, pos):
        x, y = pos
        if self.deselect_button.collidepoint(x, y):
            self.selected_tower = None
            return None
        elif self.start_button.collidepoint(x, y):
            # You can handle the start button click here
            self.selected_tower = None
            return 'start'
        elif self.reset_button.collidepoint(x, y):
            # You can handle the reset button click here
            self.selected_tower = None
            return 'reset'

        y_offset = self.deselect_button.height + 10
        tower_height = self.tower_images[0].get_height()
        spacing = 10
        index = (y - self.rect.y - y_offset) // (tower_height + spacing)

        if 0 <= index < len(self.tower_images):
            self.selected_tower = index
            return index
        return None

