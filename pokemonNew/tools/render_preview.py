"""One-off dev tool: loads a map and renders one frame to a PNG for visual review.

Usage:
    python tools/render_preview.py <map_id> [--maps-dir data/maps] [--out preview.png] [--scale 4]
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

from engine.assets import AssetManager, DATA_DIR
from engine.tileset import TilesetRegistry
from engine.tilemap import TileMap
from engine.camera import Camera


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("map_id")
    parser.add_argument("--maps-dir", default=os.path.join(DATA_DIR, "maps"))
    parser.add_argument("--out", default=None)
    parser.add_argument("--scale", type=int, default=4)
    args = parser.parse_args()

    pygame.init()
    pygame.display.set_mode((1, 1))

    assets = AssetManager()
    registry = TilesetRegistry(assets, os.path.join(DATA_DIR, "tilesets.json"))
    tilemap = TileMap.load(args.map_id, args.maps_dir, registry)

    px_w, px_h = tilemap.pixel_size()
    surface = pygame.Surface((px_w, px_h))
    surface.fill((0, 0, 0))
    camera = Camera(viewport_w=px_w, viewport_h=px_h)
    camera.follow((px_w / 2, px_h / 2), px_w, px_h)
    tilemap.draw(surface, camera)
    tilemap.draw_above(surface, camera)

    scaled = pygame.transform.scale(surface, (px_w * args.scale, px_h * args.scale))
    out_path = args.out or f"{args.map_id}.preview.png"
    pygame.image.save(scaled, out_path)
    print(f"Rendered {args.map_id} ({tilemap.width}x{tilemap.height} tiles) -> {out_path}")


if __name__ == "__main__":
    main()
