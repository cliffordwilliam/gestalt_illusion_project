import pygame as pg
from os.path import join
import pygame.freetype as font
from json import load

pg.init()

# Pngs
PNGS_DIR_PATH = "pngs"
PNGS_PATHS = {
    "player_sprite_sheet.png": join(PNGS_DIR_PATH, "player_sprite_sheet.png"),
    "player_flip_sprite_sheet.png": join(PNGS_DIR_PATH, "player_flip_sprite_sheet.png"),
    "stage_1_sprite_sheet.png": join(PNGS_DIR_PATH, "stage_1_sprite_sheet.png"),
    "stage_0_sprite_sheet.png": join(PNGS_DIR_PATH, "stage_0_sprite_sheet.png"),
    "goblin_sprite_sheet.png": join(PNGS_DIR_PATH, "goblin_sprite_sheet.png"),
    "goblin_flip_sprite_sheet.png": join(PNGS_DIR_PATH, "goblin_flip_sprite_sheet.png"),
}

# Ttfs
TTFS_DIR_PATH = "ttfs"
TTFS_DATA = {
    "cg_pixel_3x5_mono.ttf": {
        "path": join(TTFS_DIR_PATH, "cg_pixel_3x5_mono.ttf"),
        "h": 5,
        "w": 3,
    },
}

# Jsons
JSONS_DIR_PATH = "jsons"
JSONS_PATHS = {
    "player_animation.json": join(JSONS_DIR_PATH, "player_animation.json"),
    "fire_animation.json": join(JSONS_DIR_PATH, "fire_animation.json"),
    "stage0_gym_small_editor.json": join(JSONS_DIR_PATH, "stage0_gym_small_editor.json"),
    "stage0_gym_small_game.json": join(JSONS_DIR_PATH, "stage0_gym_small_game.json"),
    "stage0_gym_wide_editor.json": join(JSONS_DIR_PATH, "stage0_gym_wide_editor.json"),
    "stage0_gym_wide_game.json": join(JSONS_DIR_PATH, "stage0_gym_wide_game.json"),
    "stage0_gym_tall_editor.json": join(JSONS_DIR_PATH, "stage0_gym_tall_editor.json"),
    "stage0_gym_tall_game.json": join(JSONS_DIR_PATH, "stage0_gym_tall_game.json"),
    "stage0_gym_big_editor.json": join(JSONS_DIR_PATH, "stage0_gym_big_editor.json"),
    "stage0_gym_big_game.json": join(JSONS_DIR_PATH, "stage0_gym_big_game.json"),
    "goblin_animation.json": join(JSONS_DIR_PATH, "goblin_animation.json"),
}

# Constants
TILE_S = 16
FPS = 60
NATIVE_W = 320
NATIVE_H = 176
WINDOW_W = 320
WINDOW_H = 180

# Pg constants
NATIVE_SURF = pg.Surface((NATIVE_W, NATIVE_H))
NATIVE_RECT = NATIVE_SURF.get_rect()

CLOCK = pg.time.Clock()
EVENTS = [pg.KEYDOWN, pg.KEYUP, pg.QUIT]

DEBUG_SURF = pg.Surface((NATIVE_W, NATIVE_H))
DEBUG_SURF.set_colorkey("red")
DEBUG_RECT = DEBUG_SURF.get_rect()

# Convenience global font for debug
FONT = font.Font(
    TTFS_DATA["cg_pixel_3x5_mono.ttf"]["path"],
    TTFS_DATA["cg_pixel_3x5_mono.ttf"]["h"],
)
