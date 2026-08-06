try:
    import simplegui
except ImportError:
    import SimpleGUICS2Pygame.simpleguics2pygame as simplegui
import random
import os
import json
from vector import Vector
from Welcome import Welcome
from fight import Pokemon
from fight import Fight
from fight import Kbd
from fight import POKEDEX

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

WIDTH = 800
HEIGHT = 480

#TEMP: set True to re-enable random wild encounters (disabled for map/collision QA)
WILD_ENCOUNTERS_ENABLED = False

#live save data isn't committed to the repo (see .gitignore) - only these bundled defaults are
SAVE_FILE_TEMPLATES = [
    ("NewSave.json", "Save.json"),
    ("NewPlayerPokedex.json", "PlayerPokedex.json"),
    ("NewPlayerPokemon.json", "PlayerPokemon.json"),
]

#overwrites a live save file with its bundled default
def copy_template(template_name, live_name):
    with open('{}/Fight/Files/{}'.format(BASE_DIR, template_name), "r") as src:
        text = src.read()
    with open('{}/Fight/Files/{}'.format(BASE_DIR, live_name), "w") as dst:
        dst.write(text)

#creates the live save files from the bundled defaults if they don't exist yet -
#e.g. right after cloning the repo, since the live files themselves aren't committed
def ensure_save_files_exist():
    for template_name, live_name in SAVE_FILE_TEMPLATES:
        live_path = '{}/Fight/Files/{}'.format(BASE_DIR, live_name)
        if not os.path.exists(live_path):
            copy_template(template_name, live_name)

#builds a party of Pokemon from a JSON file of {"name", "hp", "lvl", "exp"} entries
def _load_pokemon_party(path, pos, pos1):
    with open(path, "r") as file:
        party = json.load(file)
    return [Pokemon(entry["name"], entry["hp"], entry["lvl"], entry["exp"], pos, pos1) for entry in party]

#Used for animation/transitioning
class Clock:
    def __init__(self):
        self.time = 0
        
    def tick(self):
        self.time += 1
    
    def transition(self,frame_duration):
        if self.time >= frame_duration:
            self.time = 0
            return True
        else:
            return False

#Sets up the keyboard handlers for overworld
class Keyboard:
    def __init__(self):
        self.right = False
        self.left = False
        self.up = False
        self.down = False
        self.pokedex = False
        self.start = False
        self.startscreen = False
        self.tutorial = False
        self.back = False
        self.save = False

    def keyDown(self, key):
        if key == simplegui.KEY_MAP['right']:
            self.right = True
        if key == simplegui.KEY_MAP['left']:
            self.left = True
        if key == simplegui.KEY_MAP['up']:
            self.up = True
        if key == simplegui.KEY_MAP['down']:
            self.down = True
        if key == simplegui.KEY_MAP['space']:
            if self.start == False:
                self.start = True
            else:
                self.startscreen = True
        if key == simplegui.KEY_MAP['p']:
            self.pokedex = True
        if key == simplegui.KEY_MAP['s']:
            self.save = True
        if key == simplegui.KEY_MAP['q']:
            self.back = True
        if key == simplegui.KEY_MAP['t']:
            self.tutorial = True


    def keyUp(self, key):
        if key == simplegui.KEY_MAP['right']:
            self.right = False
        if key == simplegui.KEY_MAP['left']:
            self.left = False
        if key == simplegui.KEY_MAP['up']:
            self.up = False
        if key == simplegui.KEY_MAP['down']:
            self.down = False

    def KeyReset(self):
        self.right = False
        self.left = False
        self.up = False
        self.down = False

#shared by Player/NPC draw(): blits the current animation frame, using column 0 when idle
def draw_frame(canvas, image, frame_center, frame_index, frame_dim, pos, scale_factor, moving):
    col = frame_index[0] if moving else 0
    canvas.draw_image(image,
            [frame_center[0] + col * frame_dim[0],
             frame_center[1] + frame_index[1] * frame_dim[1]],
            frame_dim, [pos.x, pos.y], [frame_dim[0]*scale_factor, frame_dim[1]*scale_factor])

#shared by Player/NPC next_frame(): advances to the next animation column, wrapping at columns
def advance_frame(frame_index, columns):
    frame_index[0] += 1
    if frame_index[0] >= columns:
        frame_index[0] = 0

#shared by Wall/NPC collision(): axis-aligned bounding box overlap check
def aabb_overlap(a_left, a_right, a_top, a_bot, b_left, b_right, b_top, b_bot):
    col_left = (a_left - b_right) >= 0
    col_right = (b_left - a_right) >= 0
    col_top = (a_top - b_bot) >= 0
    col_bot = (b_top - a_bot) >= 0

    collision = True
    if (col_right):
        collision = False
    if (col_left):
        collision = False
    if (col_bot):
        collision = False
    if (col_top):
        collision = False

    return collision

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

#Makes player class
class Player:
    def __init__(self, clock): 
        self.clock = clock
        self.name = ""
        self.image = simplegui._load_local_image('{}/Overworld/Other/player.png'.format(BASE_DIR))
        self.rows = 4
        self.columns = 4
        
        width = self.image.get_width()
        frame_width = width//self.columns
        height = self.image.get_height()
        frame_height = height//self.rows

        self.pos = Vector(552, 224)
        self.frame_center = [frame_width/2, frame_height/2]
        self.frame_dim = [frame_width, frame_height]
        self.frame_index = [0,0]

        #saves the states
        self.vel = Vector(0,0)
        self.moving = False
        self.in_fight = False
        self.interacting = False
        self.lock = False
        self.scale_factor = 0.26
        with open('{}/Fight/Files/PlayerPokedex.json'.format(BASE_DIR), "r") as file:
            self.encounters = self.num_lines = len(json.load(file))

        self.lives = 6
        self.player_heal = False
        self.heart_img = simplegui._load_local_image('{}/Overworld/Other/heart.png'.format(BASE_DIR))

        self.player_left = self.pos.x - self.frame_center[0]
        self.player_right = self.pos.x + self.frame_center[0]
        self.player_top = self.pos.y
        self.player_bot = self.pos.y + self.frame_center[1]

        #loads the players pokemon
        self.pokemon_list = _load_pokemon_party(
            '{}/Fight/Files/PlayerPokemon.json'.format(BASE_DIR), [210, 250], [570, 140])

    #draws the player on screen
    def draw(self, canvas):
        draw_frame(canvas, self.image, self.frame_center, self.frame_index, self.frame_dim, self.pos, self.scale_factor, self.moving)

        canvas.draw_image(self.heart_img, [8,8], [16,16], [16,16], [16,16])
        lives = "x"+str(self.lives)
        canvas.draw_text(lives, [30,20], 24, "Black")

        with open('{}/Fight/Files/PlayerPokedex.json'.format(BASE_DIR), "r") as file:
            self.encounters = self.num_lines = len(json.load(file))
        canvas.draw_text("Gokedex entries: "+str(self.encounters), [300,20], 24, "Black")
            
        self.clock.tick()
        move_on = self.clock.transition(6)
        if move_on == True:
            self.next_frame()

    #switches frames
    def next_frame(self):
        advance_frame(self.frame_index, self.columns)

    def update(self):
        self.pos.add(self.vel)

    def add_name(self, name):
        self.name = name

#similar to Player but controlled by computer
class NPC:
    def __init__(self, img_name, pos, clock):
        self.clock = clock
        self.image_name = img_name
        self.image = simplegui._load_local_image(('{}/Overworld/NPC/'.format(BASE_DIR))+self.image_name+".png")
        
        self.rows = 1
        self.columns = 4
        
        width = self.image.get_width()
        frame_width = width//self.columns
        height = self.image.get_height()
        frame_height = height//self.rows

        self.pos = pos
        self.frame_center = [frame_width/2, frame_height/2]
        self.frame_dim = [frame_width, frame_height]
        self.frame_index = [0,0]
        
        self.vel = Vector(0,0)
        self.moving = False
        self.scale_factor = 0.26

        self.wall_left = self.pos.x - (self.frame_dim[0]//2*self.scale_factor)
        self.wall_right = self.pos.x + (self.frame_dim[0]//2*self.scale_factor)
        self.wall_top = self.pos.y - (self.frame_dim[1]//2*self.scale_factor)
        self.wall_bot = self.pos.y + (self.frame_dim[1]//2*self.scale_factor)

        self.pokemon_list = _load_pokemon_party(
            ('{}/Overworld/NPC/'.format(BASE_DIR))+self.image_name+".json", [570, 140], [200, 250])

    #draws the NPC on screen
    def draw(self, canvas):
        draw_frame(canvas, self.image, self.frame_center, self.frame_index, self.frame_dim, self.pos, self.scale_factor, self.moving)

        if self.moving:
            self.update()
        self.clock.tick()
        move_on = self.clock.transition(6)
        if move_on == True:
            self.next_frame()

    def next_frame(self):
        advance_frame(self.frame_index, self.columns)

    def update(self):
        self.pos.add(self.vel)

    #checks for collision between the player and NPC
    def collision(self, player):
        player.player_left = player.pos.x - ((player.frame_dim[0]//2)*player.scale_factor)
        player.player_right = player.pos.x + ((player.frame_dim[0]//2)*player.scale_factor)
        player.player_top = player.pos.y - ((player.frame_dim[1]//2)*player.scale_factor)
        player.player_bot = player.pos.y + ((player.frame_dim[1]//2)*player.scale_factor)

        self.wall_left = self.pos.x - (self.frame_dim[0]//2*self.scale_factor)
        self.wall_right = self.pos.x + (self.frame_dim[0]//2*self.scale_factor)
        self.wall_top = self.pos.y - (self.frame_dim[1]//2*self.scale_factor)
        self.wall_bot = self.pos.y + (self.frame_dim[1]//2*self.scale_factor)

        return aabb_overlap(self.wall_left, self.wall_right, self.wall_top, self.wall_bot,
                             player.player_left, player.player_right, player.player_top, player.player_bot)

    def interact(self, player):
        self.vel = Vector(0,0)
        self.moving = False
        return True

    #moves the npc towards the player
    def move_to_player(self,player):
        player.player_left = player.pos.x - ((player.frame_dim[0]//2)*player.scale_factor)
        player.player_right = player.pos.x + ((player.frame_dim[0]//2)*player.scale_factor)

        col_left = ((self.wall_left - player.player_right) >= 0)
        col_right = ((player.player_left - self.wall_right) >= 0)
        
        distance = player.pos.y - self.pos.y
        if distance < 96:
            if player.pos.y > self.pos.y:
                if (col_left == False) and (col_right == False):
                    player.vel = Vector(0,0)
                    player.moving = False
                    player.lock = True
                    self.moving = True
                    self.vel = Vector(0,2)

#changes NPC to a normal wall
class NPCWall(NPC):
    def __init__(self, img_name, pos, clock):
        super().__init__(img_name, pos, clock)

    def interact(self, player):
        if player.vel.x > 0:
            player.pos.x = self.wall_left-((player.frame_dim[0]//2)*player.scale_factor)-1
        if player.vel.x < 0:
            player.pos.x = self.wall_right+((player.frame_dim[0]//2)*player.scale_factor)+1
        if player.vel.y > 0:
            player.pos.y = self.wall_top-((player.frame_dim[1]//2)*player.scale_factor)-1
        if player.vel.y < 0:
            player.pos.y = self.wall_bot+((player.frame_dim[1]//2)*player.scale_factor)+1
        return False
        
    def move_to_player(self,player):
        pass

#Used specifically for the yacht at the start of game
class Yacht(NPC):
    def __init__(self, img_name, pos, clock):
        super().__init__(img_name, pos, clock)
        self.vel = Vector(0, -0.01)
        self.moving = True

        width = self.image.get_width()
        height = self.image.get_height()
        self.frame_center = [width/2, height/2]
        self.frame_dim = [width, height]
        
    def draw(self, canvas):
        if self.pos.y > -100:
            canvas.draw_image(self.image, 
                    [self.frame_center[0] + 0 * self.frame_dim[0], 
                    self.frame_center[1] + self.frame_index[1] * self.frame_dim[1]], 
                    self.frame_dim, [self.pos.x,self.pos.y], [self.frame_dim[0]*self.scale_factor,self.frame_dim[1]*self.scale_factor])
        if self.moving:
            self.update()
        
        self.clock.tick()
        move_on = self.clock.transition(20)
        if move_on == True:
            self.vel.add(self.vel)
            self.clock.time = 0

    #accelerates away off screen        
    def update(self):
        self.pos.add(self.vel)

    def move_to_player(self,player):
        pass

    def interact(self, player):
        return False

#makes a wall which doesn't allow for player to walk through
class Wall:
    #dims=(width,height) skips loading a named asset - used for map-builder objects, which
    #already carry their own explicit box size and are drawn separately (see MapObject)
    def __init__(self, name, pos, dims=None):
        if dims is not None:
            self.image = None
            self.width, self.height = dims
        else:
            self.image = simplegui._load_local_image(('{}/Overworld/Other/'.format(BASE_DIR))+name)
            self.width = self.image.get_width()
            self.height = self.image.get_height()
        self.pos = pos
        self.frame_dim = [self.width, self.height]

        self.wall_left = self.pos.x - (self.frame_dim[0]//2)
        self.wall_right = self.pos.x + (self.frame_dim[0]//2)
        self.wall_top = self.pos.y - (self.frame_dim[1]//2)
        self.wall_bot = self.pos.y + (self.frame_dim[1]//2)


    def draw(self, canvas):
        if self.image is None:
            return
        canvas.draw_image(self.image,
                    [self.width//2, self.height//2],
                     [self.width, self.height], [self.pos.x,self.pos.y], [self.frame_dim[0],self.frame_dim[1]])

    #checks for collision
    def collision(self, player):
        player.player_left = player.pos.x - ((player.frame_dim[0]//2)*player.scale_factor)
        player.player_right = player.pos.x + ((player.frame_dim[0]//2)*player.scale_factor)
        player.player_top = player.pos.y
        player.player_bot = player.pos.y + ((player.frame_dim[1]//2)*player.scale_factor)

        return aabb_overlap(self.wall_left, self.wall_right, self.wall_top, self.wall_bot,
                             player.player_left, player.player_right, player.player_top, player.player_bot)

    #blocks the player from moving through
    def interact(self, player):
        if player.vel.x > 0:
            player.pos.x = self.wall_left-((player.frame_dim[0]//2)*player.scale_factor)-1
        if player.vel.x < 0:
            player.pos.x = self.wall_right+((player.frame_dim[0]//2)*player.scale_factor)+1
        if player.vel.y > 0:
            player.pos.y = self.wall_top-((player.frame_dim[1]//2)*player.scale_factor)-1
        if player.vel.y < 0:
            player.pos.y = self.wall_bot+1

#creates an Interactive wall (subclass of wall)
class Interact(Wall):
    def __init__(self, name, pos, int_type, target_map = None, target_pos = None, dims = None):
        super().__init__(name, pos, dims=dims)
        self.target_map = target_map
        self.target_pos = target_pos
        self.int_type = int_type

    #checks for what kind of interaction is happening
    def interact(self, player):
        if self.int_type == "fight":
            if player.moving:
                player.in_fight = True
        if self.int_type == "interact":
            player.interacting = True
        if self.int_type == "heal":
            player.player_heal = True
            
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
        self.Map = simplegui._load_local_image(_background_image_path(Map, map_data))
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
                image = simplegui._load_local_image('{}/Overworld/{}'.format(BASE_DIR, obj["sprite"]))
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
        self.Map = simplegui._load_local_image(_background_image_path(self.map_name, map_data))
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

#creates the Gokedex
class Pokedex:
    def __init__(self, kbd):
        self.player_pokedex = []
        self.pokedex = []
        self.kbd = kbd
        self.centre = [0,0]
        self.first = True
        self.poke_list =[]
        self.index = 0
        self.bag = simplegui._load_local_image('{}/Fight/Other/bag.png'.format(BASE_DIR))
        self.light = simplegui._load_local_image('{}/Fight/Other/highlight.png'.format(BASE_DIR))
        self.pos = [[(348,145),(348,265),(348,380)],[(598,145),(598,265),(598,380)]]

    def draw(self, canvas):
        self.player_pokedex = []
        self.pokedex = []
        #loads the gokemon the player has in their gokedex
        with open('{}/Fight/Files/PlayerPokedex.json'.format(BASE_DIR),"r") as file:
            self.player_pokedex = json.load(file)

        #fills out the gokedex file
        count = 0
        temp_list = []
        for name in POKEDEX:
            count += 1
            if name in self.player_pokedex:
                temp_list.append(str(count)+"    "+name)
            else:
                temp_list.append(str(count)+"    ?????")
            if len(temp_list) >= 6:
                self.pokedex.append(temp_list)
                temp_list = []
        if len(temp_list) != 0:
            self.pokedex.append(temp_list)
            temp_list = []
        #draws gokedex       
        self.poke_list = self.pokedex[self.index]
        canvas.draw_image(self.bag, (375,250), (750,500), (400,240), (735,490))
        if not self.first:
            if self.kbd.left and self.centre[0] == 1:
                self.centre[0] = 0
                self.first = True
            elif self.kbd.down and self.centre[1] < 2:
                self.centre[1] += 1
                self.first = True
            elif self.kbd.down and self.centre[1] == 2:
                if not (self.index == len(self.pokedex)-1):
                    self.index += 1
                self.first = True
            elif self.kbd.up and self.centre[1] == 0:
                if not (self.index == 0):
                    self.index -= 1
                self.first = True
            elif self.kbd.right and self.centre[0] == 0:
                self.centre[0] = 1
                self.first = True
            elif self.kbd.up and self.centre[1] > 0:
                self.centre[1] -= 1
                self.first = True
        else:
            if not(self.kbd.left or self.kbd.right or self.kbd.up or self.kbd.down):
                self.first = False
        canvas.draw_image(self.light, (116,45), (233,91), self.pos[self.centre[0]][self.centre[1]], (233,91))
        for i in range(0,len(self.poke_list)):
            if i<3:
                canvas.draw_text(self.poke_list[i], (290, 150+(i*120)), 25, 'Black')
            else:
                canvas.draw_text(self.poke_list[i], (540, 150+(i-3)*120), 25, 'Black')

#loads all dialogue text once from Text/dialogue.json
def _load_dialogue():
    with open('{}/Text/dialogue.json'.format(BASE_DIR), "r") as file:
        return json.load(file)

DIALOGUE = _load_dialogue()

#looks up the lines for a dialogue id (e.g. "boss1", "boss1W" for its win text, "boss1L" for its lose text)
def dialogue_lines(dialogue_id):
    entry = DIALOGUE.get(dialogue_id)
    if entry is not None and "lines" in entry:
        return entry["lines"]
    if dialogue_id.endswith("W") and dialogue_id[:-1] in DIALOGUE:
        return DIALOGUE[dialogue_id[:-1]]["win"]
    if dialogue_id.endswith("L") and dialogue_id[:-1] in DIALOGUE:
        return DIALOGUE[dialogue_id[:-1]]["lose"]
    return DIALOGUE[dialogue_id]["pre_fight"]

#used to show text from the dialogue data on screen
class Text:
    def __init__(self, txtfile, player, pos, box, count, clock):
        self.txtfile = txtfile
        self.pos = pos
        self.player = player
        self.count = count
        self.box = box
        self.display = True
        self.clock = clock
        self.txtbox = simplegui._load_local_image('{}/Text/box.png'.format(BASE_DIR))
        self.alltxt = [line.format(player_name=player.name) for line in dialogue_lines(txtfile)]
        self.num_lines = len(self.alltxt)

    def draw(self, canvas):
        if self.display:
            if self.box:
                canvas.draw_image(self.txtbox, (400,75), (800,150), (400,405), (800,150))
            canvas.draw_text(self.alltxt[self.count], self.pos, 20, 'White')

                            
        self.clock.tick()
        move_on = self.clock.transition(140)
        if move_on:
            self.count += 1
            if self.count >= self.num_lines:
                self.display = False

#responsible for collisions           
class Interaction:
    def __init__(self, player, keyboard, game):
        self.player = player
        self.keyboard = keyboard
        self.game = game

    #sets the players velocity
    def update(self):
        if self.keyboard.start:
            if self.player.lock == False:
                if self.keyboard.right:
                    self.player.vel = Vector(2, 0)
                    self.player.frame_index[1] = 2
                    self.player.moving = True
                elif self.keyboard.left:
                    self.player.vel = Vector(-2,0)
                    self.player.frame_index[1] = 1
                    self.player.moving = True
                elif self.keyboard.up:
                    self.player.vel = Vector(0,-2)
                    self.player.frame_index[1] = 3
                    self.player.moving = True
                elif self.keyboard.down:
                    self.player.vel = Vector(0,2)
                    self.player.frame_index[1] = 0
                    self.player.moving = True
                else:
                    self.player.moving = False
                    self.player.vel = Vector(0,0)

    #goes through the wall and npc lists
    def draw(self, canvas):
        for x in self.game.background.walls_list:
            x.draw(canvas)
            col = x.collision(self.player)
            if col == True:
                x.interact(self.player)
                if player.interacting == True:
                    self.game.background.new_level(x.target_map, x.target_pos, self.player)

                if player.in_fight == True:
                    rand_int = random.random()
                    if WILD_ENCOUNTERS_ENABLED and rand_int < 0.007:
                        pokerange = self.game.background.load_pokelvl()
                        pokelvl = random.randint(pokerange[0], pokerange[1])
                        num_lines = sum(1 for line in open(('{}/Overworld/map_poke/'.format(BASE_DIR))+self.game.background.map_name+".txt"))
                        poke_num = random.randint(1,num_lines)
                        with open(('{}/Overworld/map_poke/'.format(BASE_DIR))+self.game.background.map_name+".txt","r") as file:
                            area = file.readlines()
                            count = 1
                            for pokemon in area:
                                pokemon = pokemon.split()
                                if count == poke_num:
                                    pokeName = pokemon[0]
                                count += 1
                        Wpokemon = Pokemon(pokeName, -1, pokelvl, 0, [570, 140], [200, 250])
                        self.game.fight = Fight([Wpokemon], self.player.pokemon_list, self.game.Kbd, False)
                        self.game.fightB = True
                    player.in_fight = False

        if self.game.background.is_object_format:
            self._draw_sorted(canvas)
        else:
            self.game.background.draw(canvas)
            self.player.draw(canvas)
            for y in self.game.background.npc_list:
                y.draw(canvas)
                self._npc_interact(canvas, y)

    #resolves NPC movement/collision and the resulting dialogue-or-fight trigger; shared by both
    #draw paths below. Returns the NPC to show dialogue for, if its interaction just fired one.
    def _npc_interact(self, canvas, y):
        y.move_to_player(self.player)
        col = y.collision(self.player)
        if col == True:
            fightB = y.interact(self.player)
            if fightB == True:
                self.player.lock = True
                self.game.text = Text(y.image_name, self.player, (50,405), True, self.game.txtcount, self.game.txtclock)
                self.game.text.draw(canvas)
                self.game.txtcount = self.game.text.count
                if self.game.text.display == False:
                    self.player.lock = False
                    self.game.txtcount = 0
                    self.game.fightB = True
                    self.game.fight = Fight(self.game.background.npc_list[0].pokemon_list, self.player.pokemon_list, self.game.Kbd, True)

    #map-builder maps: ground layer once, then player/NPCs/objects drawn in Y-sorted order so a
    #tall object can occlude the player (and vice versa) instead of the player always being on top
    def _draw_sorted(self, canvas):
        self.game.background.draw(canvas)

        drawables = [(self.player.pos.y + (self.player.frame_dim[1]//2)*self.player.scale_factor, self.player.draw)]
        for y in self.game.background.npc_list:
            drawables.append((y.pos.y + (y.frame_dim[1]//2)*y.scale_factor, y.draw))
        for obj in self.game.background.visual_objects:
            drawables.append((obj.base_y(), obj.draw))
        drawables.sort(key=lambda item: item[0])
        for _, draw_fn in drawables:
            draw_fn(canvas)

        for y in self.game.background.npc_list:
            self._npc_interact(canvas, y)

#sets up main class
class Game:
    def __init__(self, welcome, tutorial, player, keyboard, background):
        self.player = player
        self.keyboard = keyboard
        self.welcome = welcome
        self.startscreen = Welcome("StartScreen.png")
        self.credits = Welcome("credits.png")
        self.caughtAll = Welcome("CaughtAll.png")
        self.tutorial = tutorial
        self.background = background
        self.npc_lost = []
        self.intro = False
        self.complete = False
        self.pokecomplete = False
        self.txtcount = 0
        self.txtclock = Clock()
        self.text = Text("empty",self.player, (0,0), False, self.txtcount, clock)
        self.inter = Interaction(self.player, self.keyboard, self)
        self.Kbd = Kbd()
        self.pokedex = Pokedex(self.Kbd)
        pokemon2 = Pokemon('Palkia', 19, 5, 50, [210, 250], [570, 140])
        self.fight = Fight([pokemon2], [pokemon2], self.Kbd, False)
        self.fightB = False

    #saves the current progress of player
    def save_game(self):
        save_data = {
            "intro": self.intro,
            "complete": self.complete,
            "pokecomplete": self.pokecomplete,
            "npc_lost": list(self.npc_lost),
            "player": {
                "x": self.player.pos.x,
                "y": self.player.pos.y,
                "lives": self.player.lives,
                "name": self.player.name if self.player.name != "" else None,
            },
            "map": self.background.map_name,
        }
        with open('{}/Fight/Files/Save.json'.format(BASE_DIR),"w") as file1:
            json.dump(save_data, file1, indent=2)
        party_data = [{"name": pokemon.name, "hp": pokemon.HP, "lvl": pokemon.lvl, "exp": pokemon.exp}
                      for pokemon in self.player.pokemon_list]
        with open('{}/Fight/Files/PlayerPokemon.json'.format(BASE_DIR),"w") as file2:
            json.dump(party_data, file2, indent=2)
                
    #loads the game from the save files; falls back to a fresh game if Save.json is missing/corrupted
    def load_game(self, allow_fallback=True):
        try:
            with open('{}/Fight/Files/Save.json'.format(BASE_DIR),"r") as file:
                save_data = json.load(file)
            self.intro = save_data["intro"]
            self.keyboard.startscreen = self.intro
            self.complete = save_data["complete"]
            self.pokecomplete = save_data["pokecomplete"]
            self.npc_lost = list(save_data["npc_lost"])
            player_data = save_data["player"]
            self.player.pos.x = int(player_data["x"])
            self.player.pos.y = int(player_data["y"])
            self.player.lives = int(player_data["lives"])
            self.player.name = player_data["name"] if player_data["name"] is not None else ""
            self.background = Background(save_data["map"], WIDTH, HEIGHT, self.npc_lost)
            self.background.load_wall()
        except (OSError, IndexError, ValueError, KeyError) as error:
            if not allow_fallback:
                raise
            print("Save data missing or corrupted ({}) - starting a new game.".format(error))
            self.new_game("yes")

    #creates a new game by replacing files
    def new_game(self, confirmation):
        if confirmation == "yes":
            for template_name, live_name in SAVE_FILE_TEMPLATES:
                copy_template(template_name, live_name)
            self.player.pokemon_list = _load_pokemon_party(
                '{}/Fight/Files/PlayerPokemon.json'.format(BASE_DIR), [210, 250], [570, 140])
            self.load_game(allow_fallback=False)

    #runs main game loop
    def draw(self, canvas):
        if self.keyboard.start:
            if self.keyboard.startscreen:
                if self.fightB:
                    self._draw_fight(canvas)
                elif self.keyboard.pokedex:
                    self._draw_pokedex(canvas)
                else:
                    self._draw_overworld(canvas)
            else:
                self._draw_start_menu(canvas)
        else:
            self._draw_welcome(canvas)

    #handles the active battle screen, including the win/lose outcome once a fight ends
    def _draw_fight(self, canvas):
        frame.set_keydown_handler(self.Kbd.keyDown)
        frame.set_keyup_handler(self.Kbd.keyUp)
        self.fight.draw(canvas)

        if (self.fight.end == True):
            self.Kbd.KeyReset()
            frame.set_keydown_handler(self.keyboard.keyDown)
            frame.set_keyup_handler(self.keyboard.keyUp)
            self.keyboard.KeyReset()

            if self.fight.npc:
                if (self.fight.catch == False) and (self.fight.run == False) and (self.fight.lost == False):
                    npc_name = self.background.npc_list[0].image_name
                    if npc_name not in self.npc_lost:
                        self.npc_lost.append(npc_name)
                    fight_state = "W"
                else:
                    fight_state = "L"

                self.text = Text(self.background.npc_list[0].image_name+fight_state, self.player, (50,405), True, self.txtcount, self.txtclock)
                self.text.draw(canvas)
                self.txtcount = self.text.count

                if self.text.display == False:
                    self.background = Background(self.background.map_name, WIDTH, HEIGHT, self.npc_lost)
                    self.background.load_wall()
                    self.player.lock = False
                    self.txtcount = 0
                    self.fightB = False

                    if self.fight.lost:
                        self.player.pos.x +=50
                        self.player.pos.y +=50
                        self.player.lives -= 1
                        for pokemon in player.pokemon_list:
                            pokemon.HP = pokemon.fullhp

                    if self.fight.run:
                        self.player.pos.x +=50
                        self.player.pos.y +=50
            else:
                if self.fight.lost:
                    self.player.lives -= 1
                    for pokemon in player.pokemon_list:
                        pokemon.HP = pokemon.fullhp
                self.fightB = False

    #handles the Gokedex overlay
    def _draw_pokedex(self, canvas):
        frame.set_keydown_handler(self.Kbd.keyDown)
        frame.set_keyup_handler(self.Kbd.keyUp)
        self.pokedex.draw(canvas)
        if self.Kbd.quit:
            self.Kbd.KeyReset()
            frame.set_keydown_handler(self.keyboard.keyDown)
            frame.set_keyup_handler(self.keyboard.keyUp)
            self.keyboard.KeyReset()
            self.keyboard.pokedex = False
            self.Kbd.quit = False

    #handles normal overworld movement/interaction and its one-off text overlays
    def _draw_overworld(self, canvas):
        self.inter.update()
        self.player.update()
        self.background.draw(canvas)
        self.inter.draw(canvas)

        if self.keyboard.save:
            self.save_game()
            self.keyboard.save = False

        if (self.complete == False) and ("boss2" in self.npc_lost):
            self.credits.draw(canvas)
            self.txtclock.tick()
            move_on = self.txtclock.transition(200)
            if move_on:
                self.complete = True

        if (self.pokecomplete == False) and (self.player.encounters == 79):
            if (self.complete == False) and ("boss2" in self.npc_lost):
                pass
            else:
                self.caughtAll.draw(canvas)
                self.txtclock.tick()
                move_on = self.txtclock.transition(200)
                if move_on:
                    self.pokecomplete = True

        if self.player.player_heal:
            self.player.lock = True
            self.player.vel = Vector(0,0)
            self.text = Text("heal", self.player, (50,405), True, self.txtcount, self.txtclock)
            for y in self.player.pokemon_list:
                y.HP = y.fullhp
            self.text.draw(canvas)
            self.txtcount = self.text.count
            if self.text.display == False:
                self.player.pos.y += 50
                self.player.player_heal = False
                self.player.lock = False
                self.txtcount = 0

        if not self.intro:
            self.player.lock = True
            self.text = Text("intro", self.player, (50,405), True, self.txtcount, self.txtclock)
            self.text.draw(canvas)
            self.txtcount = self.text.count
            if self.text.display == False:
                self.intro = True
                self.player.lock = False
                self.txtcount = 0

        if self.player.lives == 0:
            self.player.lives = 6
            self.new_game("yes")

    #handles the start-screen / tutorial toggle shown before pressing space to enter the overworld
    def _draw_start_menu(self, canvas):
        if not self.keyboard.tutorial:
            self.startscreen.draw(canvas)
        else:
            self.tutorial.draw(canvas)
            if self.keyboard.back:
                self.keyboard.tutorial = False
                self.keyboard.back = False

    #handles the welcome screen / tutorial shown before pressing space the first time
    def _draw_welcome(self, canvas):
        if not self.keyboard.tutorial:
            self.welcome.draw(canvas)
        else:
            self.tutorial.draw(canvas)
            if self.keyboard.back:
                self.keyboard.tutorial = False
                self.keyboard.back = False

#sets up all the objects
ensure_save_files_exist()
kbd = Keyboard()
clock = Clock()
player = Player(clock)
welcome = Welcome("welcome.png")
tutorial = Welcome("tutorial.png")
background = Background("map2y", WIDTH, HEIGHT)
game = Game(welcome, tutorial, player, kbd, background)
game.load_game()

#sets up frame and all the event handlers
frame = simplegui.create_frame('Gokemon', WIDTH, HEIGHT)
frame.set_canvas_background('Black')
frame.add_input("Player Name:", player.add_name, 100)
frame.add_input("Type 'yes' to start a new game:", game.new_game, 50)
frame.set_draw_handler(game.draw)
frame.set_keydown_handler(kbd.keyDown)
frame.set_keyup_handler(kbd.keyUp)
frame.start()
