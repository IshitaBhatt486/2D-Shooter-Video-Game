from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
ASSETS_DIR = PROJECT_ROOT / "assets" / "images"
AUDIO_DIR = PROJECT_ROOT / "assets" / "audio"
LEVELS_DIR = PROJECT_ROOT / "assets" / "levels"

SCREEN_WIDTH = 800
SCREEN_HEIGHT = int(SCREEN_WIDTH * 0.8)
FPS = 60
GRAVITY = 0.75
SCROLL_THRESH = 200
ROWS = 16
COLS = 150
TILE_SIZE = SCREEN_HEIGHT // ROWS
TILE_TYPES = 21
MAX_LEVELS = 3
UI = {"level_loading_frames": 50, "panel_width": 500, "panel_height": 240}

PLAYER = {"speed": 5, "ammo": 20, "grenades": 5, "health": 100, "scale": 1.65}
ENEMY = {"speed": 2, "ammo": 20, "grenades": 0, "health": 100, "scale": 1.65, "vision_width": 150, "vision_height": 60}

BG = (144, 201, 120)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
PINK = (235, 65, 54)

TEXT = {
    "window_title": "Quantum Squad Shooter",
    "ammo": "AMMO:",
    "grenades": "GRENADES:",
    "controls_title": "CONTROLS",
    "controls_description": "Use the following controls to play the game:",
    "controls": ("A / D or <-/->: Move", "W or up arrow: Jump", "F: Shoot", "Q: Grenade"),
    "mission_failed": "MISSION FAILED",
    "loading_title": "PREPARING SECTOR",
    "loading_message": "Loading mission assets...",
    "sector": "SECTOR",
    "mission_complete": "MISSION COMPLETE",
    "completion_message": "All sectors secured. Quantum Squad wins.",
    "completion_prompt": "Play again or return to base.",
    "replay": "REPLAY MISSION",
    "exit": "RETURN TO BASE",
}
