"""Layered tile grid loaded from JSON: ground/decoration_below/decoration_above,
an optional collision-override grid, per-map encounter tables, warps, and NPCs.

Each ground-layer cell is either null or a 2-element [tileset_name, index] pair.
Walkability and encounter zones come entirely from the ground layer's tileset
metadata plus collision_overrides; decoration layers are purely visual.
"""

import json
import os

import settings


class TileMap:
    def __init__(self, map_id, data, tileset_registry):
        self.map_id = map_id
        self.width = data["width"]
        self.height = data["height"]
        self.layers = data.get("layers", {})
        self.collision_overrides = data.get("collision_overrides")
        self.encounter_tables = data.get("encounter_tables", {})
        self.warps = data.get("warps", [])
        self.edge_warps = data.get("edge_warps", {})
        self.npcs = data.get("npcs", [])
        self.tilesets = tileset_registry

    @classmethod
    def load(cls, map_id, maps_dir, tileset_registry):
        path = os.path.join(maps_dir, f"{map_id}.json")
        with open(path) as f:
            data = json.load(f)
        return cls(map_id, data, tileset_registry)

    def in_bounds(self, pos):
        x, y = pos
        return 0 <= x < self.width and 0 <= y < self.height

    def _cell(self, layer_name, pos):
        x, y = pos
        layer = self.layers.get(layer_name)
        if not layer:
            return None
        return layer[y][x]

    def is_walkable(self, pos):
        if not self.in_bounds(pos):
            return False
        if self.collision_overrides is not None:
            x, y = pos
            if self.collision_overrides[y][x]:
                return False
        cell = self._cell("ground", pos)
        if cell is None:
            return False
        tileset_name, index = cell
        return self.tilesets.get(tileset_name).is_walkable(index)

    def encounter_zone(self, pos):
        cell = self._cell("ground", pos)
        if cell is None:
            return None
        tileset_name, index = cell
        return self.tilesets.get(tileset_name).encounter_zone(index)

    def encounter_table_for(self, pos):
        zone = self.encounter_zone(pos)
        if zone is None:
            return None
        return self.encounter_tables.get(zone)

    def warp_at(self, pos):
        x, y = pos
        for warp in self.warps:
            if warp["x"] == x and warp["y"] == y:
                return warp
        return None

    def pixel_size(self):
        return self.width * settings.TILE_SIZE, self.height * settings.TILE_SIZE

    def draw(self, surface, camera):
        self._draw_layer(surface, camera, "ground")
        self._draw_layer(surface, camera, "decoration_below")

    def draw_above(self, surface, camera):
        self._draw_layer(surface, camera, "decoration_above")

    def _draw_layer(self, surface, camera, layer_name):
        layer = self.layers.get(layer_name)
        if not layer:
            return
        start_x, start_y, end_x, end_y = camera.visible_tile_range(self.width, self.height)
        for y in range(start_y, end_y):
            row = layer[y]
            for x in range(start_x, end_x):
                cell = row[x]
                if cell is None:
                    continue
                tileset_name, index = cell
                tile_surf = self.tilesets.get(tileset_name).get_tile(index)
                sx, sy = camera.world_to_screen(x * settings.TILE_SIZE, y * settings.TILE_SIZE)
                surface.blit(tile_surf, (sx, sy))
