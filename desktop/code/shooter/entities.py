import pygame

from .config import ENEMY, GRAVITY, PLAYER, SCREEN_HEIGHT, SCREEN_WIDTH, TILE_SIZE


class Soldier(pygame.sprite.Sprite):
    def __init__(self, game, char_type, x, y, scale, speed, ammo, grenades):
        super().__init__()
        self.game, self.alive, self.char_type = game, True, char_type
        self.speed, self.ammo, self.start_ammo, self.grenades = speed, ammo, ammo, grenades
        starting_health = ENEMY["health"] if char_type == "enemy" else PLAYER["health"]
        self.shoot_cooldown, self.health, self.max_health = 0, starting_health, starting_health
        self.direction, self.vel_y, self.jump, self.in_air, self.flip = 1, 0, False, True, False
        self.animation_list = [game.assets.animation(char_type, action, scale) for action in ("idle", "run", "jump", "death")]
        self.frame_index, self.action, self.update_time = 0, 0, pygame.time.get_ticks()
        self.move_counter, self.vision, self.idling, self.idling_counter = 0, pygame.Rect(0, 0, ENEMY["vision_width"], 20), False, 0
        self.image = self.animation_list[0][0]
        self.rect = self.image.get_rect(center=(x, y))
        self.width, self.height = self.image.get_size()

    def update(self):
        self.update_animation(); self.check_alive()
        if self.shoot_cooldown > 0: self.shoot_cooldown -= 1

    def move(self, left, right):
        scroll, dx, dy = 0, 0, 0
        if left: dx, self.flip, self.direction = -self.speed, True, -1
        if right: dx, self.flip, self.direction = self.speed, False, 1
        ground_probe = pygame.Rect(self.rect.x + 2, self.rect.bottom, self.width - 4, 2)
        on_ground = any(tile.colliderect(ground_probe) for _, tile in self.game.world.obstacle_list)
        if self.jump and on_ground:
            self.vel_y, self.jump, self.in_air = -14, False, True
        if not on_ground or self.vel_y < 0:
            self.vel_y = min(self.vel_y + GRAVITY, 10)
            dy += self.vel_y
        else:
            self.vel_y, self.in_air = 0, False
        for _, tile in self.game.world.obstacle_list:
            if tile.colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                dx = 0
                if self.char_type == "enemy": self.direction, self.move_counter = -self.direction, 0
            if tile.colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                if self.vel_y < 0: self.vel_y, dy = 0, tile.bottom - self.rect.top
                else: self.vel_y, self.in_air, dy = 0, False, tile.top - self.rect.bottom
        if pygame.sprite.spritecollide(self, self.game.water_group, False): self.health = 0
        complete = bool(pygame.sprite.spritecollide(self, self.game.exit_group, False))
        if self.rect.bottom > SCREEN_HEIGHT: self.health = 0
        if self.char_type == "player" and (self.rect.left + dx < 0 or self.rect.right + dx > SCREEN_WIDTH): dx = 0
        self.rect.x += dx; self.rect.y += dy
        if self.char_type == "player" and ((self.rect.right > SCREEN_WIDTH - 200 and self.game.bg_scroll < self.game.world.level_length * TILE_SIZE - SCREEN_WIDTH) or (self.rect.left < 200 and self.game.bg_scroll > abs(dx))):
            self.rect.x -= dx; scroll = -dx
        return scroll, complete

    def shoot(self):
        if self.shoot_cooldown == 0 and self.ammo > 0:
            self.shoot_cooldown = 20; self.ammo -= 1
            self.game.bullet_group.add(Bullet(self.game, self, self.rect.centerx + .75 * self.rect.width * self.direction, self.rect.centery, self.direction))
            self.game.assets.shot_fx.play()

    def enemy_behavior(self):
        import random
        player = self.game.player
        if self.alive and player.alive:
            distance_x = player.rect.centerx - self.rect.centerx
            distance_y = abs(player.rect.centery - self.rect.centery)
            player_in_sight = abs(distance_x) <= ENEMY["vision_width"] and distance_y <= ENEMY["vision_height"]
            if player_in_sight:
                self.direction = 1 if distance_x >= 0 else -1
                self.flip = self.direction == -1
                self.vision.center = (self.rect.centerx + 75 * self.direction, self.rect.centery)
            if not self.idling and random.randint(1, 200) == 1: self.update_action(0); self.idling, self.idling_counter = True, 50
            if player_in_sight:
                self.update_action(0)
                self.shoot()
            elif not self.idling:
                right = self.direction == 1; self.move(not right, right); self.update_action(1); self.move_counter += 1
                self.vision.center = (self.rect.centerx + 75 * self.direction, self.rect.centery)
                if self.move_counter > TILE_SIZE: self.direction, self.move_counter = -self.direction, -self.move_counter
            else:
                self.idling_counter -= 1
                if self.idling_counter <= 0: self.idling = False
        self.rect.x += self.game.screen_scroll
        self.vision.x += self.game.screen_scroll

    def update_animation(self):
        self.image = self.animation_list[self.action][self.frame_index]
        if pygame.time.get_ticks() - self.update_time > 100: self.update_time, self.frame_index = pygame.time.get_ticks(), self.frame_index + 1
        if self.frame_index >= len(self.animation_list[self.action]): self.frame_index = len(self.animation_list[self.action]) - 1 if self.action == 3 else 0

    def update_action(self, action):
        if action != self.action: self.action, self.frame_index, self.update_time = action, 0, pygame.time.get_ticks()

    def check_alive(self):
        if self.health <= 0 and self.alive:
            self.health, self.speed, self.alive = 0, 0, False
            self.update_action(3)
            if self.char_type == "player": self.game.player_died()

    def take_damage(self, amount):
        self.health -= amount
        if self.char_type == "player": self.game.player_hit()

    def draw(self, surface):
        surface.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)
        if self.char_type == "enemy" and self.alive:
            bar = pygame.Rect(self.rect.x, self.rect.y - 10, self.rect.width, 6)
            pygame.draw.rect(surface, (20, 20, 20), bar)
            pygame.draw.rect(surface, (54, 186, 74), (bar.x + 1, bar.y + 1, (bar.width - 2) * self.health / self.max_health, bar.height - 2))


class ScrollingSprite(pygame.sprite.Sprite):
    def __init__(self, game, image, x, y):
        super().__init__(); self.game, self.image = game, image
        self.rect = image.get_rect(midtop=(x + TILE_SIZE // 2, y + TILE_SIZE - image.get_height()))
    def update(self): self.rect.x += self.game.screen_scroll

class ItemBox(ScrollingSprite):
    def __init__(self, game, item_type, x, y): super().__init__(game, game.assets.item_boxes[item_type], x, y); self.item_type = item_type
    def update(self):
        super().update(); player = self.game.player
        if pygame.sprite.collide_rect(self, player):
            if self.item_type == "Health": player.health = min(player.max_health, player.health + 25)
            elif self.item_type == "Ammo": player.ammo += 15
            else: player.grenades += 3
            self.kill()

class Bullet(pygame.sprite.Sprite):
    def __init__(self, game, owner, x, y, direction):
        super().__init__(); self.game, self.owner, self.direction, self.speed = game, owner, direction, 10; self.image = game.assets.bullet_img; self.rect = self.image.get_rect(center=(x, y))
    def update(self):
        self.rect.x += self.direction * self.speed + self.game.screen_scroll
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH: self.kill(); return
        if any(tile.colliderect(self.rect) for _, tile in self.game.world.obstacle_list): self.kill(); return
        if self.owner.char_type == "enemy":
            targets = [(self.game.player, 5)]
        else:
            targets = [(enemy, 25) for enemy in self.game.enemy_group]
        for target, damage in targets:
            if target.alive and self.rect.colliderect(target.rect): target.take_damage(damage); self.kill(); break

class Grenade(pygame.sprite.Sprite):
    def __init__(self, game, x, y, direction):
        super().__init__(); self.game, self.timer, self.vel_y, self.speed, self.direction = game, 100, -11, 7, direction
        self.image = game.assets.grenade_img; self.rect = self.image.get_rect(center=(x, y)); self.width, self.height = self.image.get_size()
    def update(self):
        self.vel_y += GRAVITY; dx, dy = self.direction * self.speed, self.vel_y
        for _, tile in self.game.world.obstacle_list:
            if tile.colliderect(self.rect.x + dx, self.rect.y, self.width, self.height): self.direction *= -1; dx = self.direction * self.speed
            if tile.colliderect(self.rect.x, self.rect.y + dy, self.width, self.height): self.speed = 0; self.vel_y = 0; dy = tile.bottom - self.rect.top if dy < 0 else tile.top - self.rect.bottom
        self.rect.x += dx + self.game.screen_scroll; self.rect.y += dy; self.timer -= 1
        if self.timer <= 0:
            self.kill(); self.game.assets.grenade_fx.play(); self.game.explosion_group.add(Explosion(self.game, *self.rect.center))
            for soldier in [self.game.player, *self.game.enemy_group]:
                if abs(self.rect.centerx - soldier.rect.centerx) < TILE_SIZE * 2 and abs(self.rect.centery - soldier.rect.centery) < TILE_SIZE * 2: soldier.take_damage(50)

class Explosion(pygame.sprite.Sprite):
    def __init__(self, game, x, y): super().__init__(); self.game, self.images, self.frame_index, self.counter = game, game.assets.explosion_frames(.5), 0, 0; self.image = self.images[0]; self.rect = self.image.get_rect(center=(x, y))
    def update(self):
        self.rect.x += self.game.screen_scroll; self.counter += 1
        if self.counter >= 4:
            self.counter, self.frame_index = 0, self.frame_index + 1
            if self.frame_index >= len(self.images): self.kill()
            else: self.image = self.images[self.frame_index]
