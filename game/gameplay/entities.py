import os
import json
from game.engine.vector import Vector
from game.battle.fight import Pokemon
from game.engine.image_cache import load_image
from game.engine import balance

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

#builds a party of Pokemon from a JSON file of {"name", "hp", "lvl", "exp"} entries
def _load_pokemon_party(path, pos, pos1):
    with open(path, "r") as file:
        party = json.load(file)
    return [Pokemon(entry["name"], entry["hp"], entry["lvl"], entry["exp"], pos, pos1) for entry in party]

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

#Makes player class
class Player:
    def __init__(self, clock):
        self.clock = clock
        self.name = ""
        self.image = load_image('{}/Overworld/Other/player.png'.format(BASE_DIR))
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

        self.lives = balance.STARTING_LIVES
        self.player_heal = False
        self.heart_img = load_image('{}/Overworld/Other/heart.png'.format(BASE_DIR))

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
        move_on = self.clock.transition(balance.WALK_ANIMATION_CADENCE_FRAMES)
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
        self.image = load_image(('{}/Overworld/NPC/'.format(BASE_DIR))+self.image_name+".png")

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
        move_on = self.clock.transition(balance.WALK_ANIMATION_CADENCE_FRAMES)
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
        move_on = self.clock.transition(balance.YACHT_ACCELERATION_INTERVAL_FRAMES)
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
            self.image = load_image(('{}/Overworld/Other/'.format(BASE_DIR))+name)
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
