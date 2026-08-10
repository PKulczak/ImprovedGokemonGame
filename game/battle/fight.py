import pygame
import time
import os
import json
from game.engine.image_cache import load_image
from game.engine import balance
from game.engine.party_grid import PartyGrid
from game.battle import battle_rules

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

#loads each pokemon's base stats from Pokedex.json once, keyed by name
def _load_pokedex():
    with open('{}/Fight/Files/Pokedex.json'.format(BASE_DIR), "r") as file:
        return json.load(file)

POKEDEX = _load_pokedex()

_SEEN_POKEMON_PATH = '{}/Fight/Files/PlayerPokedex.json'.format(BASE_DIR)
_seen_pokemon_cache = None
_seen_pokemon_mtime = None
_seen_pokemon_version = 0

#returns the player's seen-pokemon list, re-reading from disk only when the file's mtime has
#changed since the last read - avoids a full file-open+json-parse every single frame (both
#Player's Gokedex-entry counter and the Pokedex screen itself used to do this) for data that's
#almost always unchanged. Refreshes correctly whether the file changed via _mark_pokemon_seen
#below or via a wholesale save reset (Game.new_game), since both bump the file's mtime.
def load_seen_pokemon():
    global _seen_pokemon_cache, _seen_pokemon_mtime, _seen_pokemon_version
    mtime = os.path.getmtime(_SEEN_POKEMON_PATH)
    if _seen_pokemon_cache is None or mtime != _seen_pokemon_mtime:
        with open(_SEEN_POKEMON_PATH, "r") as file:
            _seen_pokemon_cache = json.load(file)
        _seen_pokemon_mtime = mtime
        _seen_pokemon_version += 1
    return _seen_pokemon_cache

#bumps whenever load_seen_pokemon()'s cache actually changes - lets callers that keep their own
#derived data (e.g. Pokedex's paginated display list) skip rebuilding it on unchanged frames
def seen_pokemon_version():
    return _seen_pokemon_version

#records a pokemon as seen in the player's Pokedex, if it isn't already
def _mark_pokemon_seen(name):
    global _seen_pokemon_mtime, _seen_pokemon_version
    seen = load_seen_pokemon()
    if name not in seen:
        seen.append(name)
        with open(_SEEN_POKEMON_PATH, "w") as file:
            json.dump(seen, file, indent=2)
        _seen_pokemon_mtime = os.path.getmtime(_SEEN_POKEMON_PATH)
        _seen_pokemon_version += 1

class Fight:
    def __init__(self, monster_list, pokemon_list, keyboard, npc):
        self.mons_list = monster_list
        self.monster = monster_list[0]
        self.poke_list = pokemon_list
        self.pokemon = pokemon_list[0]
        self.count = balance.SHORT_MESSAGE_FRAMES
        self.attack = True
        self.kbd = keyboard
        self.npc = npc
        self.info = self.monster.name+" VS "+ self.pokemon.name
        self.image = load_image('{}/Fight/Other/fight_background.png'.format(BASE_DIR))
        self.col1 = "White"
        self.col2 = "Grey"
        self.col3 = "Grey"
        self.col4 = "Grey"
        self.inte = 1
        self.run = False
        self.bag = load_image('{}/Fight/Other/bag.png'.format(BASE_DIR))
        self.light = load_image('{}/Fight/Other/highlight.png'.format(BASE_DIR))
        self.first = True
        self.change = False
        self.catch = False
        self.lost = False
        self.grid = PartyGrid()
        self.end = False

        #which of the fight screen's states is active, dispatched via state_handlers instead of
        #the nested if/elif chain draw() used to be - derived fresh every frame from the exact
        #same flags as before (change/catch/kbd.quit/kbd.select/run/count/attack), same priority
        #order, so this is purely a readability change, not a new/different state machine. Some
        #flag combinations are known dead ends kept as-is rather than "fixed" here - e.g. the
        #catch-overflow confirm branch below never clears kbd.select/change, so the very next
        #frame falls through into the switch-branch of bag_confirm too; count gets overwritten
        #back to PLAYER_TURN_MESSAGE_FRAMES after every resolve_action regardless of what fight()
        #set it to; self.attack only flips in fight()'s "still alive" branch, so a win takes an
        #extra resolve_monster_turn cycle after the fatal hit before "Fight end, you win!" shows.
        self.state_handlers = {
            "bag_browse": self._draw_bag_browse,
            "bag_confirm": self._draw_bag_confirm,
            "bag_cancel": self._draw_bag_cancel,
            "message": self._draw_message,
            "choose_action": self._draw_choose_action,
            "resolve_action": self._draw_resolve_action,
            "resolve_monster_turn": self._draw_resolve_monster_turn,
        }
        self.state = self._resolve_state()

    #derives the active state from the same flags draw() used to branch on inline
    def _resolve_state(self):
        if self.change:
            if self.kbd.quit:
                return "bag_cancel"
            if self.kbd.select:
                return "bag_confirm"
            return "bag_browse"
        if self.run or self.count != 0:
            return "message"
        if self.attack:
            return "resolve_action" if self.kbd.select else "choose_action"
        return "resolve_monster_turn"

    #responsible for drawing the fight
    def draw(self, canvas):
        self.state = self._resolve_state()
        if self.state != "bag_browse" and self.state != "bag_confirm" and self.state != "bag_cancel":
            self._draw_scene(canvas)
        self.state_handlers[self.state](canvas)

    #the fight background, both combatants' name/HP/level, and both sprites - shared by every
    #state except the bag/switch menu (which replaces this whole scene with the party list)
    def _draw_scene(self, canvas):
        canvas.draw_image(self.image, (375,250), (750,500), (400,240), (735,490))
        canvas.draw_text(self.monster.name, (155, 80), 25, 'Black')
        canvas.draw_text("HP:"+str(self.monster.HP)+"   Lvl:"+str(self.monster.lvl), (190, 110), 25, 'Black')
        canvas.draw_text(self.pokemon.name, (530, 255), 25, 'Black')
        canvas.draw_text("HP:"+str(self.pokemon.HP)+"/"+str(self.pokemon.fullhp)+"  Lvl:"+str(self.pokemon.lvl), (530, 295), 25, 'Black')
        self.pokemon.draw(canvas)
        self.monster.draw(canvas)

    #shows the escape message, or the previous turn's result message with its attack-effect
    #animation, counting self.count down either way
    def _draw_message(self, canvas):
        if self.run:
            canvas.draw_text(self.info, (120, 415), 25, 'White')
            self.count = self.count - 1
        else:
            if not self.first:
                if self.attack:
                    self.monster.draw_effect(canvas)
                else:
                    self.pokemon.draw_effect(canvas)
            canvas.draw_text(self.info, (120, 415), 25, 'White')
            self.count = self.count - 1

    #resets the attack-effect sprite frame and clears the one-time "don't show an effect yet"
    #flag - runs once every time a message finishes, before the next choice/resolution is made
    def _reset_effect_frames(self):
        self.monster.frame_index1[1] = 0
        self.pokemon.frame_index1[1] = 0
        self.first = False

    #shows the Attack/Catch/Run/Bag menu and reads the player's choice
    def _draw_choose_action(self, canvas):
        self._reset_effect_frames()
        self.inte = self.interact(self.inte, canvas)

    #the frame the player confirms an action - either resolves it, or opens the bag/switch menu
    def _draw_resolve_action(self, canvas):
        self._reset_effect_frames()
        if self.inte <=3 :
            self.fight(self.pokemon, self.monster, self.inte, canvas)
            self.kbd.select = False
            self.count = balance.PLAYER_TURN_MESSAGE_FRAMES
        elif self.inte == 4:
            self.change = True
            self.kbd.select = False

    #the monster's turn - always resolves immediately, no menu of its own
    def _draw_resolve_monster_turn(self, canvas):
        self._reset_effect_frames()
        self.fight(self.pokemon, self.monster, self.inte, canvas)
        self.count = balance.MONSTER_TURN_MESSAGE_FRAMES

    #browsing the party grid (the bag hotkey, or a forced switch/catch-overflow prompt)
    def _draw_bag_browse(self, canvas):
        self.first = self.grid.update(self.kbd, self.first)
        self.grid.draw_highlight(canvas, self.bag, self.light)
        for i in range(0,len(self.poke_list)):
            if i<3:
                canvas.draw_text(self.poke_list[i].name, (270, 130+(i*120)), 25, 'Black')
                canvas.draw_text("HP:"+str(self.poke_list[i].HP), (350, 160+(i*120)), 25, 'Black')
            else:
                canvas.draw_text(self.poke_list[i].name, (520, 130+(i-3)*120), 25, 'Black')
                canvas.draw_text("HP:"+str(self.poke_list[i].HP), (600, 160+(i-3)*120), 25, 'Black')

    #confirms the currently-highlighted party slot
    def _draw_bag_confirm(self, canvas):
        if self.grid.centre[0] == 0 :
            choice = self.grid.centre[0]+self.grid.centre[1]
        else:
            choice = self.grid.centre[0]+self.grid.centre[1]+2
        if self.catch:
            self.monster.pos = self.pokemon.pos
            self.monster.pos1 = self.pokemon.pos1
            self.poke_list[choice] = self.monster
            self.mons_list.remove(self.monster)
            if len(self.mons_list) == 0:
                self.end = True
            else:
                self.monster = self.mons_list[0]
            self.catch = False
        else:
            if len(self.poke_list)-1>=choice:
                self.pokemon = self.poke_list[choice]
                self.change = False
            self.kbd.select = False

    #cancels the bag/switch menu
    def _draw_bag_cancel(self, canvas):
        self.change = False
        if self.catch:
            self.info = "You release it again."
            self.catch = False

    #does all the calculations for the fight
    def fight(self, pokemon, monster, inte, canvas):
        if pokemon.HP > 0 and monster.HP > 0:
            if not self.attack:
                pokemon.HP = max(0, pokemon.HP - battle_rules.damage_amount(monster.ATK, pokemon.DEF))
                self.info = monster.name+" attack "+pokemon.name
                self.attack = True
            else:
                if inte == 1:
                    monster.HP = max(0, monster.HP - battle_rules.damage_amount(pokemon.ATK, monster.DEF))
                    self.info = pokemon.name+" attack "+monster.name
                    self.attack = False
                elif inte == 2:
                    if battle_rules.escape_succeeds():
                        self.info = "You escaped!"
                        self.run = True
                        self.count = balance.SHORT_MESSAGE_FRAMES
                        self.end = True
                    else:
                        self.info = "Escape failed!"
                        self.attack = False
                elif inte == 3:
                    if battle_rules.catch_succeeds(self.npc):
                        if len(self.poke_list) < balance.MAX_PARTY_SIZE:
                            self.info = "Catch succeed!"
                            self.monster.pos = self.pokemon.pos
                            self.monster.pos1 = self.pokemon.pos1
                            self.poke_list.append(monster)
                            self.mons_list.remove(self.monster)
                            _mark_pokemon_seen(monster.name)
                            if len(self.mons_list) == 0:
                                self.count = 0
                                self.end = True
                            else:
                                self.monster = self.mons_list[0]
                        else:
                            self.change = True
                            self.catch = True
                    else:
                        self.info = "Catch failed!"
                        self.attack = False
                                             
        else:
            if pokemon.HP > 0 and len(self.mons_list) == 0:
                self.info = "Fight end, you win!"
                self.end = True
            elif monster.HP >0:
                survive = False
                for i in range(0,len(self.poke_list)):
                    if self.poke_list[i].HP>0:
                        survive = True
                if survive:
                    self.change = True
                else:
                    self.info = "Fight end,You lose"
                    self.attack = False
                    self.count = balance.SHORT_MESSAGE_FRAMES
                    self.lost = True
                    self.end = True
            elif pokemon.HP > 0:
                pokemon.exp += monster.give_exp
                if pokemon.exp >= pokemon.max_exp:
                    if pokemon.lvl <= balance.MAX_LEVEL:
                        pokemon.lvl += 1
                        base_stats = POKEDEX[pokemon.name]
                        (pokemon.ATK, pokemon.DEF, pokemon.fullhp,
                         pokemon.max_exp, pokemon.give_exp) = battle_rules.level_up_stats(
                            base_stats["ATK"], base_stats["DEF"], base_stats["fullhp"], pokemon.lvl)
                    pokemon.exp -= pokemon.max_exp
                    pokemon.HP = pokemon.fullhp

                _mark_pokemon_seen(monster.name)

                self.mons_list.remove(monster)
                if not(len(self.mons_list) == 0):
                    self.monster = self.mons_list[0]
                
    def interact(self, inte, canvas):
        canvas.draw_text("What will "+self.pokemon.name+" do?", (120, 415), 25, 'White')
        canvas.draw_text("Attack",(500,415), 25, self.col1)
        canvas.draw_text("Catch",(600,415), 25, self.col2)
        canvas.draw_text("Run",(560,450), 25, self.col3)
        canvas.draw_text("Bag",(560,380), 25, self.col4)
        if self.kbd.left:
            self.col1 = "White"
            self.col2 = self.col3 = self.col4 = "Grey"
            inte = 1
        elif self.kbd.down:
            self.col1 = self.col2 = self.col4 = "Grey"
            self.col3 = "White"
            inte = 2
        elif self.kbd.right:
            self.col1 = self.col3 = self.col4 = "Grey"
            self.col2 = "White"
            inte = 3
        elif self.kbd.up:
            self.col1 = self.col2 = self.col3 = "Grey"
            self.col4 = "White"
            inte = 4
        return inte
        
#An object for each pokemon            
class Pokemon:
    def __init__(self, name, HP, lvl, exp, pos, pos1):
        self.name = name
        base_stats = POKEDEX[self.name]
        self.ATK = base_stats["ATK"]
        self.DEF = base_stats["DEF"]
        self.fullhp = base_stats["fullhp"]
        effect_img = base_stats["effect_img"]
        row = base_stats["row"]
        self.count = 0

        #pokemon scaling
        self.lvl = lvl
        self.exp = exp
        (self.ATK, self.DEF, self.fullhp,
         self.max_exp, self.give_exp) = battle_rules.level_up_stats(self.ATK, self.DEF, self.fullhp, self.lvl)
        if HP == -1:
            self.HP = self.fullhp
        else:
            self.HP = HP
        
        # pokemon image
        self.image = load_image(('{}/Fight/pokemon/'.format(BASE_DIR))+name+".png")
        width = self.image.get_width()
        frame_width = width//5
        height = self.image.get_height()
        frame_height = height//row
        self.pos = pos
        self.frame_center = [frame_width/2, frame_height/2]
        self.frame_dim = [frame_width, frame_height]
        self.frame_index = [0,0]
        self.row = row
        
        # attack effect image
        effect_row = {"water" : 3,
                      "fire" : 10,
                      "electric": 9,
                      "grass": 5,
                      "dark": 5,
                      "dragon": 3,
                      "fairy": 12,
                      "flying": 4,
                      "ice": 5,
                      "poison": 3,
                      "psychic": 2,
                      "rock": 2}
        self.effectimg = load_image(('{}/Fight/effects/'.format(BASE_DIR))+effect_img+".png")
        width = self.effectimg.get_width()
        frame_width = width//5
        height = self.effectimg.get_height()
        row1 = effect_row[effect_img]
        frame_height = height//row1
        
        self.pos1 = pos1
        self.frame_center1 = [frame_width/2, frame_height/2]
        self.frame_dim1 = [frame_width, frame_height]
        self.frame_index1 = [0,0]
        self.row1 = row1

    def draw(self, canvas):
            canvas.draw_image(self.image,
                              [self.frame_center[0] + self.frame_index[0] * self.frame_dim[0],
                               self.frame_center[1] + self.frame_index[1] * self.frame_dim[1]],
                              self.frame_dim, [self.pos[0], self.pos[1]],
                              [self.frame_dim[0]*3,self.frame_dim[1]*3])
            if self.count % balance.POKEMON_IDLE_ANIMATION_CADENCE == 0:
                self.next_frame()
            self.count +=1
    
    def next_frame(self):
        self.frame_index[0] += 1
        if self.frame_index[0] >= 5:
            self.frame_index[0] = 0
            self.frame_index[1] +=1
            if self.frame_index[1] >= self.row:
                self.frame_index[1] = 0
                
    def next_effect(self):
        self.frame_index1[0] += 1
        if self.frame_index1[0] >= 5:
            self.frame_index1[0] = 0
            self.frame_index1[1] +=1
            if self.frame_index1[1] >= self.row1:
                self.frame_index1[1] = 0
                
    def draw_effect(self, canvas):
        canvas.draw_image(self.effectimg,
                          [self.frame_center1[0] + self.frame_index1[0] * self.frame_dim1[0],
                           self.frame_center1[1] + self.frame_index1[1] * self.frame_dim1[1]],
                          self.frame_dim1, [self.pos1[0], self.pos1[1]],
                          [self.frame_dim1[0]+35,self.frame_dim1[1]+35])
        if self.count % balance.ATTACK_EFFECT_ANIMATION_CADENCE == 0:
                self.next_effect()

#Sets up the keyboard handlers for fight and gokedex 
class Kbd:
    def __init__(self):
        self.right = False
        self.left = False
        self.up = False
        self.down = False
        self.select = False
        self.quit = False

    def keyDown(self, key):
        if key == pygame.K_RIGHT:
            self.right = True
        if key == pygame.K_LEFT:
            self.left = True
        if key == pygame.K_UP:
            self.up = True
        if key == pygame.K_DOWN:
            self.down = True
        if key == pygame.K_q:
            self.quit = True
        if key == pygame.K_SPACE:
            self.select = True

    def keyUp(self, key):
        if key == pygame.K_RIGHT:
            self.right = False
        if key == pygame.K_LEFT:
            self.left = False
        if key == pygame.K_UP:
            self.up = False
        if key == pygame.K_DOWN:
            self.down = False
        if key == pygame.K_q:
            self.quit = False

    def KeyReset(self):
        self.right = False
        self.left = False
        self.up = False
        self.down = False

