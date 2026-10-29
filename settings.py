from pathlib import Path

TITLE = "SELVALUCE DX"
BASE_W, BASE_H = 320, 180
WINDOW_W, WINDOW_H = 960, 540
FPS = 60
TILE = 16
SCALE = 3
MAX_LEVEL = 50

ROOT = Path(__file__).resolve().parent
ASSET_DIR = ROOT / "assets"
SAVE_DIR = Path.home() / ".selvaluce_dx"
SAVE_FILE = SAVE_DIR / "save_v3.json"

# Palette inspired by late-2000s handheld pixel RPGs, but fully original.
COLORS = {
    "ink": (31, 43, 52),
    "deep": (24, 37, 45),
    "panel": (244, 236, 211),
    "panel2": (217, 229, 199),
    "accent": (132, 180, 91),
    "accent2": (238, 196, 105),
    "grass": (128, 178, 97),
    "grass_light": (160, 203, 117),
    "grass_dark": (72, 127, 76),
    "path": (213, 190, 142),
    "path_dark": (184, 156, 111),
    "water": (69, 141, 185),
    "water_light": (132, 200, 218),
    "rock": (132, 125, 114),
    "rock_light": (180, 169, 151),
    "tree": (49, 93, 65),
    "tree_light": (85, 142, 78),
    "wood": (129, 91, 56),
    "white": (248, 245, 226),
    "red": (212, 86, 72),
    "green": (104, 185, 91),
    "blue": (84, 155, 201),
    "shadow": (14, 23, 29),
}

TYPE_COLORS = {
    "Erba": (104, 179, 93),
    "Fuoco": (226, 124, 77),
    "Acqua": (83, 160, 205),
    "Roccia": (173, 151, 115),
    "Normale": (164, 156, 177),
}
