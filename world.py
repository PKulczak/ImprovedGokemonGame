import os
import json
from vector import Vector
from image_cache import load_image
from clock import Clock
from entities import Wall, Interact, NPC, NPCWall, Yacht

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

#pixel offset applied to a tile's grid (x,y) from Overworld/maps/*.json, keyed by tile type
TILE_OFFSETS = {
    "tree": (8, 0),
    "wall_up_a": (8, 8),
    "wall_up_b": (8, -8),
    "wall_left_a": (16, 0),
    "wall_left_b": (0, 0),
    "interact": (8, 0),
    "boss_gate": (8, 0),
    "fight": (8, 0),
    "heal": (8, 0),
    "yacht": (8, 0),
    "npc": (8, 0),
}

#sprite image used for each plain-wall tile type
TILE_WALL_IMAGES = {
    "tree": "tree.png",
    "wall_up_a": "up.png",
    "wall_up_b": "up.png",
    "wall_left_a": "left.png",
    "wall_left_b": "left.png",
}

#reads a map's JSON; distinguishes the legacy "tiles" schema from the map-builder "objects" schema
def _load_map_data(map_name):
    with open('{}/Overworld/maps/{}.json'.format(BASE_DIR, map_name), "r") as file:
        return json.load(file)

#background image path: the map-builder format's ground layer, or the legacy full flat map
def _background_image_path(map_name, map_data):
    if "objects" in map_data:
        return '{}/Overworld/{}'.format(BASE_DIR, map_data["ground"])
    return '{}/Overworld/map_img/{}.png'.format(BASE_DIR, map_name)

#a single visually-drawn map-builder object (decoration or a visible collision object, e.g. a tree);
#kept separate from Wall/Interact so it can be Y-sorted against the player/NPCs instead of being
#hidden behind the legacy format's redundant full-background redraw
class MapObject:
    def __init__(self, image, x, y, width, height):
        self.image = image
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def draw(self, canvas):
        canvas.draw_image(self.image, (self.width/2, self.height/2), (self.width, self.height),
                           (self.x, self.y), (self.width, self.height))

    #bottom edge of the object's box - the "feet" position objects are Y-sorted by
    def base_y(self):
        return self.y + self.height/2

#creates the background of the map
class Background:
    def __init__(self, Map, width, height, npc_lost=None):
        self.map_name = Map
        map_data = _load_map_data(Map)
        self.is_object_format = "objects" in map_data
        self.Map = load_image(_background_image_path(Map, map_data))
        self.width = width
        self.height = height

        self.orig_width = self.Map.get_width()
        self.orig_height = self.Map.get_height()

        #npc_lost is owned by Game (it's persistent save data); Background just holds a reference to it
        self.npc_lost = npc_lost if npc_lost is not None else []
        self.walls_list = []
        self.npc_list = []
        self.visual_objects = []

    def draw(self, canvas):
        canvas.draw_image(self.Map, (self.orig_width/2,self.orig_height/2), (self.orig_width,self.orig_height), (self.width/2, self.height/2), (self.width,self.height))

    #loads all the hitboxes (and, for map-builder maps, visual objects) for the map
    def load_wall(self):
        self.walls_list = []
        self.npc_list = []
        self.visual_objects = []
        map_data = _load_map_data(self.map_name)
        if "tiles" in map_data:
            self._load_legacy_tiles(map_data)
        else:
            self._load_objects(map_data)

    #legacy hand-authored format: one flat background image, tile type + grid index + TILE_OFFSETS
    def _load_legacy_tiles(self, map_data):
        for tile in map_data["tiles"]:
            ttype = tile["type"]
            off_x, off_y = TILE_OFFSETS[ttype]
            pos = Vector(off_x+(32*tile["x"]), off_y+(32*tile["y"]))
            if ttype in TILE_WALL_IMAGES:
                wall = Wall(TILE_WALL_IMAGES[ttype], pos)
                self.walls_list.append(wall)
            elif ttype == "interact":
                target_pos = Vector(tile["target_pos"][0], tile["target_pos"][1])
                wall = Interact("tree.png", pos, "interact", tile["target_map"], target_pos)
                self.walls_list.append(wall)
            elif ttype == "boss_gate":
                if tile["requires_defeated"] not in self.npc_lost:
                    wall = Wall("tree.png", pos)
                else:
                    target_pos = Vector(tile["target_pos"][0], tile["target_pos"][1])
                    wall = Interact("tree.png", pos, "interact", tile["target_map"], target_pos)
                self.walls_list.append(wall)
            elif ttype == "fight":
                wall = Interact("tree.png", pos, "fight")
                self.walls_list.append(wall)
            elif ttype == "heal":
                wall = Interact("tree.png", pos, "heal")
                self.walls_list.append(wall)
            elif ttype == "yacht":
                clock = Clock()
                yacht = Yacht("yacht", pos, clock)
                self.npc_list.append(yacht)
            elif ttype == "npc":
                clock = Clock()
                npc_name = self.load_npc()
                if npc_name in self.npc_lost:
                    npc = NPCWall(npc_name, pos, clock)
                else:
                    npc = NPC(npc_name, pos, clock)
                self.npc_list.append(npc)

    #map-builder format: ground image + explicit per-object position/size, Y-sorted at draw time.
    #"npc"/"yacht" still resolve their actual sprite through the existing per-map lookups below,
    #same as the legacy format - the builder only marks where they go, not which species/asset
    def _load_objects(self, map_data):
        for obj in map_data["objects"]:
            if obj["sprite"] is not None:
                image = load_image('{}/Overworld/{}'.format(BASE_DIR, obj["sprite"]))
                self.visual_objects.append(MapObject(image, obj["x"], obj["y"], obj["width"], obj["height"]))

            collision = obj.get("collision")
            if collision is None:
                continue
            ttype = collision["type"]
            pos = Vector(obj["x"], obj["y"])
            dims = (obj["width"], obj["height"])
            if ttype in ("tree", "wall_up_a", "wall_up_b", "wall_left_a", "wall_left_b"):
                self.walls_list.append(Wall(None, pos, dims=dims))
            elif ttype == "interact":
                target_pos = Vector(collision["target_pos"][0], collision["target_pos"][1])
                self.walls_list.append(Interact(None, pos, "interact", collision["target_map"], target_pos, dims=dims))
            elif ttype == "boss_gate":
                if collision["requires_defeated"] not in self.npc_lost:
                    self.walls_list.append(Wall(None, pos, dims=dims))
                else:
                    target_pos = Vector(collision["target_pos"][0], collision["target_pos"][1])
                    self.walls_list.append(Interact(None, pos, "interact", collision["target_map"], target_pos, dims=dims))
            elif ttype == "fight":
                self.walls_list.append(Interact(None, pos, "fight", dims=dims))
            elif ttype == "heal":
                self.walls_list.append(Interact(None, pos, "heal", dims=dims))
            elif ttype == "yacht":
                clock = Clock()
                self.npc_list.append(Yacht("yacht", pos, clock))
            elif ttype == "npc":
                clock = Clock()
                npc_name = self.load_npc()
                if npc_name in self.npc_lost:
                    npc = NPCWall(npc_name, pos, clock)
                else:
                    npc = NPC(npc_name, pos, clock)
                self.npc_list.append(npc)

    #loads a new level, transitioning to the target map/position named on the interact tile that triggered it
    def new_level(self, target_map, target_pos, player):
        player.pos = target_pos
        player.vel = Vector(0,0)
        self.map_name = target_map

        player.interacting = False
        map_data = _load_map_data(self.map_name)
        self.is_object_format = "objects" in map_data
        self.Map = load_image(_background_image_path(self.map_name, map_data))
        self.load_wall()

    #loads the correct npcs
    def load_npc(self):
        npc_str =  {"gym2": "boss1",
                    "bossfight3": "boss2",
                    "bossfight1": "boss3",
                    "bossfight2": "boss4"}
        npc_name = npc_str[self.map_name]
        return npc_name

    #loads the pokemon level range
    def load_pokelvl(self):
        wildpoke = {"map2y": [1,5],
                   "map": [6,10],
                   "map2": [1,5],
                   "map3": [11,15],
                   "route1":[1,5],
                   "route2": [6,10],
                   "route3": [11,15],
                   "route4": [16,21]}
        pokerange = wildpoke[self.map_name]
        return pokerange
