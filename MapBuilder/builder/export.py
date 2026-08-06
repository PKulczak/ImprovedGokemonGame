import hashlib
import json
import os
import pygame

from .project import MAP_WIDTH, MAP_HEIGHT
from .tileset import Tileset

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "output")
TILE_SIZE = 32


#exports a project to MapBuilder/output/<name>/ as map_img/<name>_ground.png + objects/<name>/*.png
#+ <name>.json, mirroring the Overworld/ layout so the bundle can be copied straight across.
#Sprites are content-hashed and deduplicated - placing the same crop many times only saves it once.
def export_project(project):
    out_dir = os.path.join(OUTPUT_DIR, project.name)
    map_img_dir = os.path.join(out_dir, "map_img")
    objects_dir = os.path.join(out_dir, "objects", project.name)
    os.makedirs(map_img_dir, exist_ok=True)
    os.makedirs(objects_dir, exist_ok=True)

    ground_filename = "{}_ground.png".format(project.name)
    pygame.image.save(project.ground_surface, os.path.join(map_img_dir, ground_filename))

    tileset_cache = {}
    hash_to_relpath = {}
    objects_json = []
    for p in project.placements:
        sprite_rel = None
        if p.tileset_name is not None:
            if p.tileset_name not in tileset_cache:
                tileset_cache[p.tileset_name] = Tileset(p.tileset_name)
            cropped = tileset_cache[p.tileset_name].crop(p.rect)
            digest = hashlib.sha1(pygame.image.tostring(cropped, "RGBA")).hexdigest()[:16]
            if digest not in hash_to_relpath:
                filename = digest + ".png"
                pygame.image.save(cropped, os.path.join(objects_dir, filename))
                hash_to_relpath[digest] = "objects/{}/{}".format(project.name, filename)
            sprite_rel = hash_to_relpath[digest]

        objects_json.append({
            "sprite": sprite_rel,
            "x": p.x, "y": p.y, "width": p.width, "height": p.height,
            "collision": p.collision,
        })

    map_data = {
        "width": MAP_WIDTH // TILE_SIZE, "height": MAP_HEIGHT // TILE_SIZE, "tile_size": TILE_SIZE,
        "ground": "map_img/{}".format(ground_filename),
        "objects": objects_json,
    }
    with open(os.path.join(out_dir, project.name + ".json"), "w") as f:
        json.dump(map_data, f, indent=2)

    return out_dir
