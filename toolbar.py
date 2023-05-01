import pygame

class Toolbar:
    def __init__(self, x, y, width, height, color, tower_images):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.tower_images = tower_images
        self.selected_option = None
        self.start_button = pygame.Rect(x+5, height-110, width-10, 30)
        self.deselect_button = pygame.Rect(x+5, height-70, width-10, 30)
        self.reset_button = pygame.Rect(x+5, height-30, width-10, 30)

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)

        # Define a function to draw and center text on a button
        def draw_button(button, text, text_color, fill_color=None):
            if fill_color:
                pygame.draw.rect(screen, fill_color, button)

            pygame.draw.rect(screen, text_color, button, 2)
            text_surface = pygame.font.Font(None, 24).render(text, True, text_color)
            text_rect = text_surface.get_rect(center=button.center)
            screen.blit(text_surface, text_rect)

        draw_button(self.start_button, "Start", (255, 255, 255), (0, 191, 54))
        draw_button(self.deselect_button, "X", (255, 255, 255), (191, 54, 54))
        draw_button(self.reset_button, "Reset", (255, 255, 255), (191, 54, 191))

        for index, image in enumerate(self.tower_images):
            image = pygame.transform.scale(image, (40, 40))
            tower_rect = image.get_rect()
            tower_rect.x = self.rect.x + (self.rect.width - tower_rect.width) // 2
            tower_rect.y = self.rect.y + self.deselect_button.height + index * (tower_rect.height + 10) + 10
            screen.blit(image, tower_rect)
            if index == self.selected_option:
                pygame.draw.rect(screen, (255, 0, 0), tower_rect, 2)

    def select_option(self, pos):
        x, y = pos
        if self.deselect_button.collidepoint(x, y):
            self.selected_option = None
            return None
        elif self.start_button.collidepoint(x, y):
            # You can handle the start button click here
            self.selected_option = None
            return 'start'
        elif self.reset_button.collidepoint(x, y):
            # You can handle the reset button click here
            self.selected_option = None
            return 'reset'

        y_offset = self.deselect_button.height + 10
        tower_height = self.tower_images[0].get_height()
        spacing = 10
        index = (y - self.rect.y - y_offset) // (tower_height + spacing)

        if 0 <= index < len(self.tower_images):
            self.selected_option = index
            return index
        return None

