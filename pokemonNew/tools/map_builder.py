"""Small authoring helper for hand-building map JSON files consistently.
Not imported by the running game — offline content-authoring tool only.

Usage pattern:
    m = MapBuilder("sagewood_town", 16, 14, base_tile="grass")
    m.fill_rect(0, 0, 15, 0, "wall")   # etc
    m.place_building(2, 1, 4, 3)
    m.add_warp(8, 13, "route_101", 8, 1)
    m.save(MAPS_DIR)
"""
import json
import os

BASE_TILE_INDEX = {
    "grass": 0, "tall_grass": 1, "path": 2, "water": 3, "sand": 4,
    "cave_floor": 5, "cave_wall": 6, "wood_floor": 7, "stone_floor": 8,
    "wall": 9, "rock": 10, "flower_grass": 11,
    "ice_floor": 12, "mud": 13, "snow": 14, "dark_wall": 15,
}

BASE_TILE_ZONE = {
    "tall_grass": "grass",
    "water": "water",
}


class MapBuilder:
    def __init__(self, map_id, width, height, base_tile="grass", tileset="base"):
        self.map_id = map_id
        self.width = width
        self.height = height
        self.tileset = tileset
        self.ground = [[[tileset, BASE_TILE_INDEX[base_tile]] for _ in range(width)] for _ in range(height)]
        self.decoration_below = [[None for _ in range(width)] for _ in range(height)]
        self.decoration_above = [[None for _ in range(width)] for _ in range(height)]
        self.collision_overrides = [[False for _ in range(width)] for _ in range(height)]
        self.encounter_tables = {}
        self.warps = []
        self.edge_warps = {}
        self.npcs = []

    def in_bounds(self, x, y):
        return 0 <= x < self.width and 0 <= y < self.height

    def set_tile(self, x, y, tile_name, layer="ground", tileset=None):
        idx = BASE_TILE_INDEX[tile_name]
        grid = getattr(self, layer)
        grid[y][x] = [tileset or self.tileset, idx]

    def clear_tile(self, x, y, layer="decoration_below"):
        getattr(self, layer)[y][x] = None

    def fill_rect(self, x0, y0, x1, y1, tile_name, layer="ground", tileset=None):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                if self.in_bounds(x, y):
                    self.set_tile(x, y, tile_name, layer=layer, tileset=tileset)

    def border(self, tile_name="rock"):
        self.fill_rect(0, 0, self.width - 1, 0, tile_name)
        self.fill_rect(0, self.height - 1, self.width - 1, self.height - 1, tile_name)
        self.fill_rect(0, 0, 0, self.height - 1, tile_name)
        self.fill_rect(self.width - 1, 0, self.width - 1, self.height - 1, tile_name)

    def set_solid(self, x, y, solid=True):
        if self.in_bounds(x, y):
            self.collision_overrides[y][x] = solid

    def place_building(self, x0, y0, w, h, door_x_offset=None, floor_tile="wall"):
        """Fills a w x h rectangle as a building exterior with one door tile
        (walkable) centered on the south wall. Returns the door's (x, y)."""
        x1, y1 = x0 + w - 1, y0 + h - 1
        self.fill_rect(x0, y0, x1, y1, floor_tile)
        door_x = x0 + (w // 2 if door_x_offset is None else door_x_offset)
        self.set_tile(door_x, y1, "path")
        return (door_x, y1)

    def place_tree(self, x, y):
        self.decoration_above[y][x] = ["tree_prop", 0]
        self.set_solid(x, y, True)

    def add_warp(self, x, y, to_map, to_x, to_y, to_facing="DOWN", trigger="step"):
        self.warps.append({
            "x": x, "y": y, "trigger": trigger,
            "to_map": to_map, "to_x": to_x, "to_y": to_y, "to_facing": to_facing,
        })

    def add_npc(self, npc_id, x, y, facing="DOWN", sprite="boss1", dialogue_id=None,
                npc_type="static", trainer_ref=None, vision_range=4, patrol=None, condition=None):
        entry = {"id": npc_id, "type": npc_type, "x": x, "y": y, "facing": facing, "sprite": sprite}
        if dialogue_id:
            entry["dialogue_id"] = dialogue_id
        if npc_type == "trainer":
            entry["trainer_ref"] = trainer_ref
            entry["vision_range"] = vision_range
        if patrol:
            entry["patrol"] = patrol
        if condition:
            entry["condition"] = condition
        self.npcs.append(entry)

    def set_encounter_zone_tile(self, x, y, zone_tile, table_id):
        self.set_tile(x, y, zone_tile)
        zone_name = BASE_TILE_ZONE[zone_tile]
        self.encounter_tables[zone_name] = table_id

    def to_dict(self):
        return {
            "id": self.map_id,
            "width": self.width,
            "height": self.height,
            "layers": {
                "ground": self.ground,
                "decoration_below": self.decoration_below,
                "decoration_above": self.decoration_above,
            },
            "collision_overrides": self.collision_overrides,
            "encounter_tables": self.encounter_tables,
            "warps": self.warps,
            "edge_warps": self.edge_warps,
            "npcs": self.npcs,
        }

    def save(self, maps_dir):
        os.makedirs(maps_dir, exist_ok=True)
        path = os.path.join(maps_dir, f"{self.map_id}.json")
        with open(path, "w") as f:
            json.dump(self.to_dict(), f, indent=2)
        return path
