from pathlib import Path
import math
import struct

import pygame

from .config import ASSETS_DIR, AUDIO_DIR, TILE_SIZE, TILE_TYPES

def load_image(*parts: str, scale: tuple[int, int] | None = None) -> pygame.Surface:
    image = pygame.image.load(Path(ASSETS_DIR, *parts)).convert_alpha()
    return pygame.transform.scale(image, scale) if scale else image

class Assets:

    def __init__(self) -> None:
        self.start_img = load_image("start_btn.png")
        self.exit_img = load_image("exit_btn.png")
        self.restart_img = load_image("restart_btn.png")
        self.pine1_img = load_image("background", "pine1.png")
        self.pine2_img = load_image("background", "pine2.png")
        self.mountain_img = load_image("background", "mountain.png")
        self.sky_img = load_image("background", "sky_cloud.png")
        self.tiles = [load_image("tile", f"{index}.png", scale=(TILE_SIZE, TILE_SIZE)) for index in range(TILE_TYPES)]
        self.bullet_img = load_image("icons", "bullet.png")
        self.grenade_img = load_image("icons", "grenade.png")
        self.item_boxes = {
            "Health": load_image("icons", "health_box.png"),
            "Ammo": load_image("icons", "ammo_box.png"),
            "Grenade": load_image("icons", "grenade_box.png"),
        }
        self.jump_fx = self._sound("jump.wav")
        self.shot_fx = self._sound("shot.wav")
        self.grenade_fx = self._sound("grenade.wav")
        # Generated UI/combat cues keep the project self-contained: no extra
        # binary assets are required for feedback that did not exist before.
        self.hit_fx = self._tone(180, 0.10, 0.28, "square")
        self.death_fx = self._tone(110, 0.34, 0.34, "sine", end_frequency=45)
        self.menu_fx = self._tone(720, 0.07, 0.18, "sine")
        self.complete_fx = self._tone(520, 0.16, 0.18, "sine", end_frequency=780)

    @staticmethod
    def _sound(filename: str) -> pygame.mixer.Sound:
        sound = pygame.mixer.Sound(AUDIO_DIR / filename)
        sound.set_volume(0.05)
        return sound

    @staticmethod
    def _tone(frequency: float, duration: float, volume: float, wave: str, end_frequency: float | None = None) -> pygame.mixer.Sound:
        sample_rate = 22_050
        frames = []
        for index in range(int(sample_rate * duration)):
            progress = index / (sample_rate * duration)
            current_frequency = frequency + ((end_frequency or frequency) - frequency) * progress
            value = math.sin(2 * math.pi * current_frequency * index / sample_rate)
            if wave == "square":
                value = 1.0 if value >= 0 else -1.0
            envelope = min(1, index / 300) * (1 - progress)
            frames.append(struct.pack("<h", int(32_767 * volume * envelope * value)))
        return pygame.mixer.Sound(buffer=b"".join(frames))

    def animation(self, character: str, action: str, scale: float) -> list[pygame.Surface]:
        folder = ASSETS_DIR / character / action
        frames = []
        for path in sorted(folder.glob("*.png"), key=lambda item: int(item.stem)):
            image = pygame.image.load(path).convert_alpha()
            frames.append(pygame.transform.scale(image, (int(image.get_width() * scale), int(image.get_height() * scale))))
        return frames

    def explosion_frames(self, scale: float) -> list[pygame.Surface]:
        return [load_image("explosion", f"exp{index}.png", scale=(int(pygame.image.load(ASSETS_DIR / "explosion" / f"exp{index}.png").get_width() * scale), int(pygame.image.load(ASSETS_DIR / "explosion" / f"exp{index}.png").get_height() * scale))) for index in range(1, 6)]