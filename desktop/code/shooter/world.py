import csv

from .config import COLS, ENEMY, LEVELS_DIR, PLAYER, ROWS, TILE_SIZE
from .entities import ItemBox, ScrollingSprite, Soldier
from .ui import HealthBar

class World:
    def __init__(self, game): self.game, self.obstacle_list = game, []

    @staticmethod
    def load_data(level):
        data = [[-1] * COLS for _ in range(ROWS)]
        with (LEVELS_DIR / f"level{level}_data.csv").open(newline="") as file:
            for row_index, row in enumerate(csv.reader(file)):
                for col_index, tile in enumerate(row): data[row_index][col_index] = int(tile)
        return data

    def process_data(self, data):
        self.level_length = len(data[0])
        player = health_bar = None
        for y, row in enumerate(data):
            for x, tile in enumerate(row):
                if tile < 0: continue
                image, px, py = self.game.assets.tiles[tile], x * TILE_SIZE, y * TILE_SIZE
                if tile <= 8: self.obstacle_list.append((image, image.get_rect(topleft=(px, py))))
                elif tile <= 10: self.game.water_group.add(ScrollingSprite(self.game, image, px, py))
                elif tile <= 14: self.game.decoration_group.add(ScrollingSprite(self.game, image, px, py))
                elif tile == 15:
                    player = Soldier(self.game, "player", px, py, PLAYER["scale"], PLAYER["speed"], PLAYER["ammo"], PLAYER["grenades"])
                    health_bar = HealthBar(10, 10, player.max_health)
                elif tile == 16: self.game.enemy_group.add(Soldier(self.game, "enemy", px, py, ENEMY["scale"], ENEMY["speed"], ENEMY["ammo"], ENEMY["grenades"]))
                elif tile == 17: self.game.item_box_group.add(ItemBox(self.game, "Ammo", px, py))
                elif tile == 18: self.game.item_box_group.add(ItemBox(self.game, "Grenade", px, py))
                elif tile == 19: self.game.item_box_group.add(ItemBox(self.game, "Health", px, py))
                else: self.game.exit_group.add(ScrollingSprite(self.game, image, px, py))
        return player, health_bar

    def draw(self, surface):
        for image, rect in self.obstacle_list:
            rect.x += self.game.screen_scroll
            surface.blit(image, rect)