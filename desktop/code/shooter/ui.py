import pygame

from .config import BLACK, GREEN, RED, SCREEN_HEIGHT, SCREEN_WIDTH

class Button:
    def __init__(self, x: int, y: int, image: pygame.Surface, scale: float) -> None:
        self.image = pygame.transform.scale(image, (int(image.get_width() * scale), int(image.get_height() * scale)))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.clicked = False

    def draw(self, surface: pygame.Surface) -> bool:
        action = False
        if self.rect.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0] and not self.clicked:
            action, self.clicked = True, True
        if not pygame.mouse.get_pressed()[0]:
            self.clicked = False
        surface.blit(self.image, self.rect)
        return action

class HealthBar:
    def __init__(self, x: int, y: int, max_health: int) -> None:
        self.x, self.y, self.max_health = x, y, max_health

    def draw(self, surface: pygame.Surface, health: int) -> None:
        ratio = max(0, health) / self.max_health
        pygame.draw.rect(surface, BLACK, (self.x - 2, self.y - 2, 154, 24))
        pygame.draw.rect(surface, RED, (self.x, self.y, 150, 20))
        pygame.draw.rect(surface, GREEN, (self.x, self.y, 150 * ratio, 20))

class ScreenFade:
    def __init__(self, direction: int, colour: tuple[int, int, int], speed: int) -> None:
        self.direction, self.colour, self.speed, self.fade_counter = direction, colour, speed, 0

    def fade(self, surface: pygame.Surface) -> bool:
        self.fade_counter += self.speed
        if self.direction == 1:
            pygame.draw.rect(surface, self.colour, (-self.fade_counter, 0, SCREEN_WIDTH // 2, SCREEN_HEIGHT))
            pygame.draw.rect(surface, self.colour, (SCREEN_WIDTH // 2 + self.fade_counter, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
            pygame.draw.rect(surface, self.colour, (0, -self.fade_counter, SCREEN_WIDTH, SCREEN_HEIGHT // 2))
            pygame.draw.rect(surface, self.colour, (0, SCREEN_HEIGHT // 2 + self.fade_counter, SCREEN_WIDTH, SCREEN_HEIGHT))
        else:
            pygame.draw.rect(surface, self.colour, (0, 0, SCREEN_WIDTH, self.fade_counter))
        return self.fade_counter >= SCREEN_WIDTH