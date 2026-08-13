"""One-off dev tool: procedurally paints a small sheet of clean 16x16 base
terrain tiles (grass/path/water/cave/indoor floors/walls/rock) so every
terrain type the game needs exists even where the reused art doesn't cover
it well. Output is a plain horizontal strip, one tile per column, loaded via
the ordinary "grid" tileset mode — nothing about these tiles is special-cased
at runtime beyond that.

Usage:
    python tools/generate_base_tiles.py
"""
import os
import random

from PIL import Image, ImageDraw

TILE = 16
OUT_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "tilesets", "base_tiles.png")

# (name, walkable, encounter_zone or None) — order defines the tile index in the sheet.
TILES = [
    ("grass", True, None),
    ("tall_grass", True, "grass"),
    ("path", True, None),
    ("water", False, "water"),
    ("sand", True, None),
    ("cave_floor", True, None),
    ("cave_wall", False, None),
    ("wood_floor", True, None),
    ("stone_floor", True, None),
    ("wall", False, None),
    ("rock", False, None),
    ("flower_grass", True, None),
    ("ice_floor", True, None),
    ("mud", True, None),
    ("snow", True, None),
    ("dark_wall", False, None),
]


def _fill(draw, color):
    draw.rectangle([0, 0, TILE - 1, TILE - 1], fill=color)


def paint_grass(draw, rng):
    _fill(draw, (86, 168, 74))
    for _ in range(10):
        x, y = rng.randrange(TILE), rng.randrange(TILE)
        draw.point((x, y), fill=(70, 148, 58))


def paint_tall_grass(draw, rng):
    _fill(draw, (58, 128, 56))
    for x in range(1, TILE, 3):
        for y in range(1, TILE, 4):
            draw.line([(x, y + 3), (x, y)], fill=(90, 168, 78))


def paint_path(draw, rng):
    _fill(draw, (214, 188, 138))
    for _ in range(14):
        x, y = rng.randrange(TILE), rng.randrange(TILE)
        draw.point((x, y), fill=(196, 168, 118))


def paint_water(draw, rng):
    _fill(draw, (70, 130, 200))
    for y in range(2, TILE, 4):
        draw.line([(0, y), (TILE - 1, y)], fill=(110, 168, 224))


def paint_sand(draw, rng):
    _fill(draw, (232, 212, 154))
    for _ in range(10):
        x, y = rng.randrange(TILE), rng.randrange(TILE)
        draw.point((x, y), fill=(210, 188, 130))


def paint_cave_floor(draw, rng):
    _fill(draw, (120, 104, 96))
    for _ in range(10):
        x, y = rng.randrange(TILE), rng.randrange(TILE)
        draw.point((x, y), fill=(100, 86, 80))


def paint_cave_wall(draw, rng):
    _fill(draw, (64, 56, 58))
    for _ in range(8):
        x, y = rng.randrange(TILE), rng.randrange(TILE)
        draw.point((x, y), fill=(84, 74, 76))
    draw.rectangle([0, 0, TILE - 1, TILE - 1], outline=(40, 34, 36))


def paint_wood_floor(draw, rng):
    _fill(draw, (176, 132, 88))
    for x in range(0, TILE, 4):
        draw.line([(x, 0), (x, TILE - 1)], fill=(158, 116, 76))


def paint_stone_floor(draw, rng):
    _fill(draw, (176, 176, 182))
    draw.line([(0, 8), (TILE - 1, 8)], fill=(150, 150, 156))
    draw.line([(8, 0), (8, TILE - 1)], fill=(150, 150, 156))


def paint_wall(draw, rng):
    _fill(draw, (150, 108, 74))
    for y in (0, 5, 10, 15):
        draw.line([(0, y), (TILE - 1, y)], fill=(120, 84, 56))


def paint_rock(draw, rng):
    _fill(draw, (86, 168, 74))
    draw.ellipse([2, 3, TILE - 3, TILE - 2], fill=(140, 140, 148), outline=(96, 96, 104))


def paint_flower_grass(draw, rng):
    paint_grass(draw, rng)
    draw.point((4, 4), fill=(230, 120, 150))
    draw.point((11, 9), fill=(240, 220, 90))


def paint_ice_floor(draw, rng):
    _fill(draw, (200, 230, 245))
    draw.line([(0, 0), (TILE - 1, TILE - 1)], fill=(230, 245, 252))
    draw.rectangle([0, 0, TILE - 1, TILE - 1], outline=(160, 205, 225))


def paint_mud(draw, rng):
    _fill(draw, (108, 90, 64))
    for _ in range(10):
        x, y = rng.randrange(TILE), rng.randrange(TILE)
        draw.point((x, y), fill=(88, 72, 50))


def paint_snow(draw, rng):
    _fill(draw, (238, 242, 248))
    for _ in range(8):
        x, y = rng.randrange(TILE), rng.randrange(TILE)
        draw.point((x, y), fill=(210, 220, 232))


def paint_dark_wall(draw, rng):
    _fill(draw, (54, 42, 62))
    for y in (0, 5, 10, 15):
        draw.line([(0, y), (TILE - 1, y)], fill=(38, 28, 46))


PAINTERS = {
    "grass": paint_grass,
    "tall_grass": paint_tall_grass,
    "path": paint_path,
    "water": paint_water,
    "sand": paint_sand,
    "cave_floor": paint_cave_floor,
    "cave_wall": paint_cave_wall,
    "wood_floor": paint_wood_floor,
    "stone_floor": paint_stone_floor,
    "wall": paint_wall,
    "rock": paint_rock,
    "flower_grass": paint_flower_grass,
    "ice_floor": paint_ice_floor,
    "mud": paint_mud,
    "snow": paint_snow,
    "dark_wall": paint_dark_wall,
}


def main():
    rng = random.Random(1234)
    sheet = Image.new("RGBA", (TILE * len(TILES), TILE), (0, 0, 0, 0))
    for i, (name, _walkable, _zone) in enumerate(TILES):
        tile_img = Image.new("RGBA", (TILE, TILE))
        draw = ImageDraw.Draw(tile_img)
        PAINTERS[name](draw, rng)
        sheet.paste(tile_img, (i * TILE, 0))
    sheet.save(OUT_PATH)
    print(f"Wrote {len(TILES)} tiles -> {OUT_PATH}")


if __name__ == "__main__":
    main()
