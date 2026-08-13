import os

import pygame
import pytest

from engine.assets import AssetManager, DATA_DIR
from engine.tileset import TilesetRegistry
from engine.tilemap import TileMap
from engine.camera import Camera

FIXTURES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures")


@pytest.fixture
def registry():
    pygame.display.set_mode((1, 1))  # a video mode must exist before convert_alpha() works
    assets = AssetManager()
    return TilesetRegistry(assets, os.path.join(DATA_DIR, "tilesets.json"))


@pytest.fixture
def test_map(registry):
    return TileMap.load("test_room", FIXTURES_DIR, registry)


def test_map_dimensions(test_map):
    assert test_map.width == 10
    assert test_map.height == 8
    assert test_map.pixel_size() == (160, 128)


def test_border_is_solid_rock(test_map):
    assert test_map.is_walkable((0, 0)) is False
    assert test_map.is_walkable((9, 7)) is False
    assert test_map.is_walkable((5, 0)) is False


def test_interior_grass_is_walkable(test_map):
    assert test_map.is_walkable((2, 2)) is True


def test_out_of_bounds_is_not_walkable(test_map):
    assert test_map.is_walkable((-1, 3)) is False
    assert test_map.is_walkable((100, 3)) is False


def test_tall_grass_zone_is_walkable_and_tagged(test_map):
    assert test_map.is_walkable((4, 4)) is True
    assert test_map.encounter_zone((4, 4)) == "grass"
    assert test_map.encounter_table_for((4, 4)) == "test_room_grass"


def test_plain_grass_has_no_encounter_zone(test_map):
    assert test_map.encounter_zone((2, 2)) is None
    assert test_map.encounter_table_for((2, 2)) is None


def test_warp_lookup(test_map):
    warp = test_map.warp_at((1, 1))
    assert warp is not None
    assert warp["to_map"] == "test_room"
    warp_none = test_map.warp_at((2, 2))
    assert warp_none is None


def test_render_to_png_looks_right(test_map, tmp_path):
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    surface = pygame.Surface((160, 128))
    surface.fill((0, 0, 0))
    camera = Camera(viewport_w=160, viewport_h=128)
    camera.follow((80, 64), *test_map.pixel_size())
    test_map.draw(surface, camera)
    test_map.draw_above(surface, camera)

    out_path = tmp_path / "test_room.png"
    pygame.image.save(surface, str(out_path))
    assert out_path.exists()

    # corner should be rock (not the black background fill)
    assert surface.get_at((4, 4))[:3] != (0, 0, 0)
    # a pixel inside the tall-grass patch should differ from plain grass
    grass_px = surface.get_at((2 * 16 + 8, 2 * 16 + 8))[:3]
    tall_px = surface.get_at((4 * 16 + 8, 4 * 16 + 8))[:3]
    assert grass_px != tall_px
