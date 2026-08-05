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

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

WIDTH = 800
HEIGHT = 480

#live save data isn't committed to the repo (see .gitignore) - only these bundled defaults are
SAVE_FILE_TEMPLATES = [
    ("NewSave.txt", "Save.txt"),
    ("NewPlayerPokedex.txt", "PlayerPokedex.txt"),
    ("NewPlayerPokemon.txt", "PlayerPokemon.txt"),
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
        self.encounters = self.num_lines = sum(1 for line in open('{}/Fight/Files/PlayerPokedex.txt'.format(BASE_DIR)))
        
        self.lives = 6
        self.player_heal = False
        self.heart_img = simplegui._load_local_image('{}/Overworld/Other/heart.png'.format(BASE_DIR))

        self.player_left = self.pos.x - self.frame_center[0]
        self.player_right = self.pos.x + self.frame_center[0]
        self.player_top = self.pos.y
        self.player_bot = self.pos.y + self.frame_center[1]

        #loads the players pokemon
        self.pokemon_list = []
        with open('{}/Fight/Files/PlayerPokemon.txt'.format(BASE_DIR),"r") as file:
            party = file.readlines()
            for pokemonL in party:
                pokemonL = pokemonL.split()
                pokemon = Pokemon(pokemonL[0], int(pokemonL[1]), int(pokemonL[2]), int(pokemonL[3]), [210, 250], [570, 140])
                self.pokemon_list.append(pokemon)

    #draws the player on screen
    def draw(self, canvas):
        draw_frame(canvas, self.image, self.frame_center, self.frame_index, self.frame_dim, self.pos, self.scale_factor, self.moving)

        canvas.draw_image(self.heart_img, [8,8], [16,16], [16,16], [16,16])
        lives = "x"+str(self.lives)
        canvas.draw_text(lives, [30,20], 24, "Black")

        self.encounters = self.num_lines = sum(1 for line in open('{}/Fight/Files/PlayerPokedex.txt'.format(BASE_DIR)))
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

        self.pokemon_list = []
        with open(('{}/Overworld/NPC/'.format(BASE_DIR))+self.image_name+".txt","r") as file:
            party = file.readlines()
            for pokemonL in party:
                pokemonL = pokemonL.split()
                pokemon = Pokemon(pokemonL[0], int(pokemonL[1]), int(pokemonL[2]), int(pokemonL[3]), [570, 140], [200, 250])
                self.pokemon_list.append(pokemon)

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
    def __init__(self, name, pos):
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
    def __init__(self, name, pos, int_type, location = None):
        super().__init__(name, pos)
        self.location = location
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
            
#creates the background of the map
class Background:
    def __init__(self, Map, width, height, npc_lost=None):
        self.map_name = Map
        self.Map = simplegui._load_local_image(('{}/Overworld/map_img/'.format(BASE_DIR))+self.map_name+".png")
        self.width = width
        self.height = height

        self.orig_width = self.Map.get_width()
        self.orig_height = self.Map.get_height()

        #npc_lost is owned by Game (it's persistent save data); Background just holds a reference to it
        self.npc_lost = npc_lost if npc_lost is not None else []
        self.walls_list = []
        self.npc_list = []

    def draw(self, canvas):
        canvas.draw_image(self.Map, (self.orig_width/2,self.orig_height/2), (self.orig_width,self.orig_height), (self.width/2, self.height/2), (self.width,self.height))

    #loads all the hitboxes for the map from its structured tilemap
    def load_wall(self):
        self.walls_list = []
        self.npc_list = []
        with open(('{}/Overworld/maps/'.format(BASE_DIR))+self.map_name+".json","r") as file:
            map_data = json.load(file)
        for tile in map_data["tiles"]:
            ttype = tile["type"]
            off_x, off_y = TILE_OFFSETS[ttype]
            pos = Vector(off_x+(32*tile["x"]), off_y+(32*tile["y"]))
            if ttype in TILE_WALL_IMAGES:
                wall = Wall(TILE_WALL_IMAGES[ttype], pos)
                self.walls_list.append(wall)
            elif ttype == "interact":
                wall = Interact("tree.png", pos, "interact", tile["location"])
                self.walls_list.append(wall)
            elif ttype == "boss_gate":
                if tile["requires_defeated"] not in self.npc_lost:
                    wall = Wall("tree.png", pos)
                else:
                    wall = Interact("tree.png", pos, "interact", tile["location"])
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

    #loads a new level    
    def new_level(self, location, player):
        map_str = {"map2y": [["route1", Vector(111,43)]],
                   "map": [["route1", Vector(770,338)], ["route2", Vector(58,236)], ["pokecenter", Vector(406,424)]],
                   "map2": [["route1", Vector(111,43)]],
                   "route1": [["map2", Vector(756, 169)], ["map", Vector(58,169)]],
                   "route2": [["map", Vector(768,225)], ["route3a", Vector(56,120)], ["route3b", Vector(47,447)]],
                   "route3": [["route2a", Vector(680,143)], ["route2b", Vector(514,443)], ["map3", Vector(220, 424)], ["route4", Vector(52,319)]],
                   "route4": [["route3", Vector(774,351)], ["bossfight1",Vector(406,424)]],
                   "map3": [["route3",Vector(746,67)], ["gym2",Vector(406,424)], ["pokecenter2",Vector(406,424)]],
                   "gym2": [["map3",Vector(650,143)]],
                   "pokecenter": [["map",Vector(290,261)]],
                   "pokecenter2": [["map3",Vector(172,382)]],
                   "bossfight1": [["route4",Vector(626,200)], ["bossfight2",Vector(406,424)]],
                   "bossfight2": [["bossfight1",Vector(406,70)], ["bossfight3",Vector(406,424)]],
                   "bossfight3": [["bossfight2",Vector(406,70)], ["route4",Vector(626,200)]]}
        
        player.pos = map_str[self.map_name][location][1]
        player.vel = Vector(0,0)
        self.map_name = map_str[self.map_name][location][0]

        if (self.map_name == "route3a") or (self.map_name == "route3b"):
            self.map_name = "route3"
        if (self.map_name == "route2a") or (self.map_name == "route2b"):
            self.map_name = "route2"

        player.interacting = False
        self.Map = simplegui._load_local_image(('{}/Overworld/map_img/'.format(BASE_DIR))+self.map_name+".png")
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
        with open('{}/Fight/Files/PlayerPokedex.txt'.format(BASE_DIR),"r") as file:
            all_lines = file.readlines()
            for pokemon_line in all_lines:
                pokemon = pokemon_line.split()
                self.player_pokedex.append(pokemon[0])

        #fills out the gokedex file
        count = 0
        with open('{}/Fight/Files/Pokedex.txt'.format(BASE_DIR),"r") as file:
            all_lines = file.readlines()
            temp_list = []
            for pokemon_line in all_lines:
                pokemon = pokemon_line.split()
                count += 1
                if pokemon[0] in self.player_pokedex:
                    temp_list.append(str(count)+"    "+pokemon[0])
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

#used to show text from a text file on screen
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
        self.num_lines = sum(1 for line in open(('{}/Text/'.format(BASE_DIR))+self.txtfile+'.txt'))
        with open(('{}/Text/'.format(BASE_DIR))+self.txtfile+'.txt',"r") as file:
            allline = file.readlines()
            self.alltxt = []
            for line in allline:
                line = line.split()
                newline = ""
                for word in line:
                    if word == "{}":
                        newline += player.name
                    else:
                        newline += word
                    newline += " "
                self.alltxt.append(newline)

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
                    self.game.background.new_level(x.location, self.player)

                if player.in_fight == True:
                    rand_int = random.random()
                    if rand_int < 0.007:
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
                    
        self.game.background.draw(canvas)
        self.player.draw(canvas)
        for y in self.game.background.npc_list:
            y.draw(canvas)
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
        allinfo = []
        temp1 = ""
        if self.intro == False:
            temp1 += "F "
        else:
            temp1 += "T "
        if self.complete == False:
            temp1 += "F "
        else:
            temp1 += "T "
        if self.pokecomplete == False:
            temp1 += "F "
        else:
            temp1 += "T "
        temp1 += "\n"
        allinfo.append(temp1)
        temp2 = ""
        for npc in self.npc_lost:
            temp2 += npc
            temp2 += " "
        temp2 += "\n"
        allinfo.append(temp2)
        temp3 = str(self.player.pos.x)+" "+str(self.player.pos.y)+" "+str(self.player.lives)+" "
        if self.player.name == "":
            temp3 += ","
        else:
            temp3 += self.player.name
        temp3 += "\n"
        allinfo.append(temp3)
        temp4 = self.background.map_name
        allinfo.append(temp4)
        text = ""
        for line in allinfo:
            text += line
        with open('{}/Fight/Files/Save.txt'.format(BASE_DIR),"w") as file1:
            file1.write(text)
        poketxt = ""
        for pokemon in self.player.pokemon_list:
            poketxt += pokemon.name+" "+str(pokemon.HP)+" "+str(pokemon.lvl)+" "+str(pokemon.exp)
            if not(pokemon == self.player.pokemon_list[len(self.player.pokemon_list)-1]):
                poketxt += "\n"
        with open('{}/Fight/Files/PlayerPokemon.txt'.format(BASE_DIR),"w") as file2:
            file2.write(poketxt)
                
    #loads the game from the save files; falls back to a fresh game if Save.txt is missing/corrupted
    def load_game(self, allow_fallback=True):
        try:
            with open('{}/Fight/Files/Save.txt'.format(BASE_DIR),"r") as file:
                info = file.readlines()
                allinfo = []
                for line in info:
                    line = line.split()
                    count = 0
                    for element in line:
                        if element == "F":
                            line[count] = False
                        elif element == "T":
                            line[count] = True
                        count += 1
                    allinfo.append(line)
            self.keyboard.startscreen = allinfo[0][0]
            self.intro = allinfo[0][0]
            self.complete = allinfo[0][1]
            self.pokecomplete = allinfo[0][2]
            if not allinfo[1]:
                self.npc_lost = []
            else:
                for npc in allinfo[1]:
                    self.npc_lost.append(npc)
            self.player.pos.x = int(float(allinfo[2][0]))
            self.player.pos.y = int(float(allinfo[2][1]))
            self.player.lives = int(allinfo[2][2])
            if allinfo[2][3] == ",":
                self.player.name = ""
            else:
                self.player.name = allinfo[2][3]
            self.background = Background(allinfo[3][0], WIDTH, HEIGHT, self.npc_lost)
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
            self.player.pokemon_list = []
            with open('{}/Fight/Files/PlayerPokemon.txt'.format(BASE_DIR),"r") as file:
                party = file.readlines()
                for pokemonL in party:
                    pokemonL = pokemonL.split()
                    pokemon = Pokemon(pokemonL[0], int(pokemonL[1]), int(pokemonL[2]), int(pokemonL[3]), [210, 250], [570, 140])
                    self.player.pokemon_list.append(pokemon)
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
                    self.npc_lost.append(self.background.npc_list[0].image_name)
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
