import random

import pygame

from .assets import Assets
from .config import BG, BLACK, FPS, MAX_LEVELS, PINK, SCREEN_HEIGHT, SCREEN_WIDTH, TEXT, UI, WHITE
from .entities import Grenade
from .ui import Button, ScreenFade
from .world import World

class Game:
    def __init__(self):
        pygame.mixer.init(); pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT)); pygame.display.set_caption(TEXT["window_title"])
        self.clock, self.font, self.title_font, self.small_font, self.assets = pygame.time.Clock(), pygame.font.SysFont("Futura", 30), pygame.font.SysFont("Futura", 44), pygame.font.SysFont("Futura", 20), Assets()
        self.level, self.bg_scroll, self.screen_scroll = 1, 0, 0
        self.damage_flash, self.shake_frames, self.death_overlay = 0, 0, 0
        self.start_game, self.start_intro, self.game_complete, self.running = False, False, False, True
        self.loading_frames = 0
        self.moving_left = self.moving_right = self.shoot = self.grenade = self.grenade_thrown = False
        self.intro_fade, self.death_fade = ScreenFade(1, BLACK, 4), ScreenFade(2, PINK, 4)
        self.start_button = Button(SCREEN_WIDTH // 2 - 130, SCREEN_HEIGHT // 2 - 150, self.assets.start_img, 1)
        self.exit_button = Button(SCREEN_WIDTH // 2 - 110, SCREEN_HEIGHT // 2 + 50, self.assets.exit_img, 1)
        self.restart_button = Button(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 50, self.assets.restart_img, 2)
        self.complete_restart_button = Button(SCREEN_WIDTH // 2 - 170, SCREEN_HEIGHT // 2 + 75, self.assets.restart_img, 1.2)
        self.complete_exit_button = Button(SCREEN_WIDTH // 2 + 35, SCREEN_HEIGHT // 2 + 75, self.assets.exit_img, 0.9)
        self.create_groups(); self.load_level()

    def create_groups(self):
        for name in ("enemy", "bullet", "grenade", "explosion", "item_box", "decoration", "water", "exit"):
            setattr(self, f"{name}_group", pygame.sprite.Group())

    def load_level(self):
        for group in self.groups(): group.empty()
        self.world = World(self); self.player, self.health_bar = self.world.process_data(World.load_data(self.level))
        self.loading_frames = UI["level_loading_frames"]

    def groups(self): return [self.enemy_group, self.bullet_group, self.grenade_group, self.explosion_group, self.item_box_group, self.decoration_group, self.water_group, self.exit_group]

    def draw_background(self):
        self.screen.fill(BG); width = self.assets.sky_img.get_width()
        for index in range(5):
            x = index * width
            self.screen.blit(self.assets.sky_img, (x - self.bg_scroll * .5, 0))
            self.screen.blit(self.assets.mountain_img, (x - self.bg_scroll * .6, SCREEN_HEIGHT - self.assets.mountain_img.get_height() - 300))
            self.screen.blit(self.assets.pine1_img, (x - self.bg_scroll * .7, SCREEN_HEIGHT - self.assets.pine1_img.get_height() - 150))
            self.screen.blit(self.assets.pine2_img, (x - self.bg_scroll * .8, SCREEN_HEIGHT - self.assets.pine2_img.get_height()))

    def draw_hud(self):
        self.health_bar.draw(self.screen, self.player.health)
        self.text(TEXT["ammo"], 10, 35); self.text(TEXT["grenades"], 10, 60)
        for index in range(self.player.ammo): self.screen.blit(self.assets.bullet_img, (90 + index * 10, 40))
        for index in range(self.player.grenades): self.screen.blit(self.assets.grenade_img, (135 + index * 15, 60))

    def text(self, value, x, y): self.screen.blit(self.font.render(value, True, WHITE), (x, y))

    def draw_panel(self, title, lines, accent):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((5, 14, 20, 175))
        self.screen.blit(overlay, (0, 0))
        panel = pygame.Rect(0, 0, UI["panel_width"], UI["panel_height"])
        panel.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        pygame.draw.rect(self.screen, (11, 31, 38), panel, border_radius=10)
        pygame.draw.rect(self.screen, accent, panel, 3, border_radius=10)
        title_image = self.title_font.render(title, True, accent)
        self.screen.blit(title_image, title_image.get_rect(center=(panel.centerx, panel.y + 55)))
        for index, line in enumerate(lines):
            message = self.small_font.render(line, True, WHITE)
            self.screen.blit(message, message.get_rect(center=(panel.centerx, panel.y + 112 + index * 28)))
        return panel

    def draw_loading_screen(self):
        panel = self.draw_panel(TEXT["loading_title"], (f"{TEXT['sector']} {self.level} / {MAX_LEVELS}", TEXT["loading_message"]), (231, 200, 105))
        progress = 1 - self.loading_frames / UI["level_loading_frames"]
        bar = pygame.Rect(panel.x + 55, panel.bottom - 46, panel.width - 110, 14)
        pygame.draw.rect(self.screen, BLACK, bar, border_radius=7)
        pygame.draw.rect(self.screen, (65, 181, 91), (bar.x, bar.y, bar.width * progress, bar.height), border_radius=7)

    def draw_completion_screen(self):
        self.draw_background()
        self.draw_panel(TEXT["mission_complete"], (TEXT["completion_message"], TEXT["completion_prompt"]), (99, 218, 128))
        if self.complete_restart_button.draw(self.screen):
            self.level, self.bg_scroll, self.game_complete, self.start_intro = 1, 0, False, True
            self.load_level()
        if self.complete_exit_button.draw(self.screen): self.running = False

    def draw_control_guide(self):
        panel = pygame.Rect(15, 15, 280, 145)
        pygame.draw.rect(self.screen, BLACK, panel)
        pygame.draw.rect(self.screen, WHITE, panel, 2)
        heading = pygame.font.SysFont("Futura", 24).render(TEXT["controls_title"], True, WHITE)
        self.screen.blit(heading, heading.get_rect(center=(panel.centerx, panel.y + 20)))
        for index, line in enumerate(TEXT["controls"]): self.text(line, panel.x + 16, panel.y + 45 + index * 23)

    def update_gameplay(self):
        self.draw_background(); self.world.draw(self.screen); self.draw_hud()
        if self.loading_frames:
            self.player.draw(self.screen)
            self.draw_loading_screen()
            self.loading_frames -= 1
            return
        self.player.update(); self.player.draw(self.screen)
        for enemy in self.enemy_group: enemy.enemy_behavior(); enemy.update(); enemy.draw(self.screen)
        for group in self.groups()[1:]: group.update(); group.draw(self.screen)
        self.draw_combat_feedback()
        if self.start_intro and self.intro_fade.fade(self.screen): self.start_intro, self.intro_fade.fade_counter = False, 0
        if self.player.alive: self.update_player()
        elif self.death_fade.fade(self.screen) and self.restart_button.draw(self.screen):
            self.death_fade.fade_counter = 0; self.start_intro = True; self.bg_scroll = 0; self.load_level()

    def update_player(self):
        if self.shoot: self.player.shoot()
        elif self.grenade and not self.grenade_thrown and self.player.grenades:
            self.grenade_group.add(Grenade(self, self.player.rect.centerx + .5 * self.player.rect.width * self.player.direction, self.player.rect.top, self.player.direction))
            self.player.grenades -= 1; self.grenade_thrown = True
        self.player.update_action(2 if self.player.in_air else 1 if self.moving_left or self.moving_right else 0)
        self.screen_scroll, complete = self.player.move(self.moving_left, self.moving_right); self.bg_scroll -= self.screen_scroll
        if complete:
            self.level += 1
            if self.level <= MAX_LEVELS:
                self.assets.complete_fx.play(); self.start_intro = True; self.bg_scroll = 0; self.load_level()
            else:
                self.assets.complete_fx.play()
                self.game_complete = True

    def player_hit(self):
        self.assets.hit_fx.play(); self.damage_flash = 7; self.shake_frames = 9

    def player_died(self):
        self.assets.death_fx.play(); self.death_overlay = 0; self.shake_frames = 18

    def draw_combat_feedback(self):
        if self.shake_frames:
            self.shake_frames -= 1
            # A brief, reversible jitter makes a hit or defeat easier to feel.
            offset = random.randint(-3, 3)
            self.screen.blit(self.screen.copy(), (offset, 0))
        if self.damage_flash:
            self.damage_flash -= 1
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((255, 45, 35, 55))
            self.screen.blit(overlay, (0, 0))
        if not self.player.alive:
            self.death_overlay = min(150, self.death_overlay + 3)
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((75, 0, 0, self.death_overlay))
            self.screen.blit(overlay, (0, 0))
            # Fade the defeat message in with the overlay; the restart button
            # remains the next interaction once the transition completes.
            title = pygame.font.SysFont("Futura", 42).render(TEXT["mission_failed"], True, (255, 230, 230))
            title.set_alpha(self.death_overlay)
            self.screen.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 120)))

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT: self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_a, pygame.K_LEFT): self.moving_left = True
                if event.key in (pygame.K_d, pygame.K_RIGHT): self.moving_right = True
                if event.key == pygame.K_f: self.shoot = True
                if event.key == pygame.K_q: self.grenade = True
                if event.key in (pygame.K_w, pygame.K_UP) and self.player.alive: self.player.jump = True; self.assets.jump_fx.play()
            if event.type == pygame.KEYUP:
                if event.key in (pygame.K_a, pygame.K_LEFT): self.moving_left = False
                if event.key in (pygame.K_d, pygame.K_RIGHT): self.moving_right = False
                if event.key == pygame.K_f: self.shoot = False
                if event.key == pygame.K_q: self.grenade = self.grenade_thrown = False
                if event.key in (pygame.K_w, pygame.K_UP): self.player.jump = False

    def run(self):
        while self.running:
            self.clock.tick(FPS)
            if not self.start_game:
                self.screen.fill(BG)
                self.draw_control_guide()
                if self.start_button.draw(self.screen): self.assets.menu_fx.play(); self.start_game = self.start_intro = True
                if self.exit_button.draw(self.screen): self.running = False
            elif self.game_complete:
                self.draw_completion_screen()
            else: self.update_gameplay()
            self.handle_events(); pygame.display.update()
        pygame.quit()