import pygame
import random
import os
import json
from game.engine.vector import Vector
from game.gameplay.Welcome import Welcome
from game.battle.fight import Pokemon
from game.battle.fight import Fight
from game.battle.fight import Kbd
from game.gameplay.entities import _load_pokemon_party
from game.gameplay.world import Background
from game.gameplay.ui import Text, Pokedex
from game.gameplay.clock import Clock
from game.engine import balance

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

WIDTH = 800
HEIGHT = 480

#shown on the pause overlay - the only place these are visible in-game (otherwise README.md only)
PAUSE_CONTROLS = [
    "Arrow keys - Move",
    "Space - Start / advance dialogue",
    "P - Open the Gokedex",
    "S - Save game",
    "Q - Back / quit a screen",
    "T - Open the tutorial",
    "R - Rename your player",
    "N - Reset to a new game",
    "Shift (hold) - Fast-forward",
]

#TEMP: set True to re-enable random wild encounters (disabled for map/collision QA)
WILD_ENCOUNTERS_ENABLED = True

#both Pokecenter interior maps (game/Overworld/maps/pokecenter.json, pokecenter2.json) share this
#exact door-entry position - it's already the target_pos used by the town-side door tiles that
#lead into them (map.json/map3.json), reused here as the "safe interior" spot a game-over respawn
#lands on, rather than inventing a new coordinate
POKECENTER_ENTRY_POS = (406, 424)
POKECENTER_MAPS = ("pokecenter", "pokecenter2")
#used until the player has actually visited either Pokecenter this session (map2y, the starting
#map, has no heal tile of its own)
DEFAULT_POKECENTER_MAP = "pokecenter"

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
        self.select = False
        self.paused = False

    def keyDown(self, key):
        if key == pygame.K_RIGHT:
            self.right = True
        if key == pygame.K_LEFT:
            self.left = True
        if key == pygame.K_UP:
            self.up = True
        if key == pygame.K_DOWN:
            self.down = True
        if key == pygame.K_SPACE:
            if self.start == False:
                self.start = True
            else:
                self.startscreen = True
            #distinct from start/startscreen above (one-shot latches for the welcome/start
            #screens) - this is a per-press "advance the current dialogue line" signal, cleared
            #by whichever Text.draw() call consumes it, same pattern as Kbd.select in battle
            self.select = True
        if key == pygame.K_p:
            self.pokedex = True
        if key == pygame.K_s:
            self.save = True
        if key == pygame.K_q:
            self.back = True
        if key == pygame.K_t:
            self.tutorial = True
        if key == pygame.K_ESCAPE:
            #a plain toggle rather than a one-shot latch (like the pokedex/fight flags below
            #it) - Esc both opens and closes the pause overlay with the same key, standard
            #pause-menu behaviour. Only takes effect in states where self.keyboard is the
            #active keydown handler (welcome/start_menu/overworld/pause), same as every other
            #key here - fight/pokedex swap the handler to their own Kbd instead.
            self.paused = not self.paused


    def keyUp(self, key):
        if key == pygame.K_RIGHT:
            self.right = False
        if key == pygame.K_LEFT:
            self.left = False
        if key == pygame.K_UP:
            self.up = False
        if key == pygame.K_DOWN:
            self.down = False

    def KeyReset(self):
        self.right = False
        self.left = False
        self.up = False
        self.down = False

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
    def draw(self, canvas, dt):
        for x in self.game.background.walls_list:
            x.draw(canvas)
            col = x.collision(self.player)
            if col == True:
                x.interact(self.player)
                if self.player.interacting == True:
                    self.game.background.new_level(x.target_map, x.target_pos, self.player)

                if self.player.in_fight == True:
                    rand_int = random.random()
                    if WILD_ENCOUNTERS_ENABLED and rand_int < balance.WILD_ENCOUNTER_CHANCE * dt:
                        pokerange = self.game.background.load_pokelvl()
                        pokelvl = random.randint(pokerange[0], pokerange[1])
                        with open('{}/Overworld/map_poke/{}.txt'.format(BASE_DIR, self.game.background.map_name), "r") as file:
                            area = file.readlines()
                        pokeName = area[random.randint(0, len(area)-1)].split()[0]
                        Wpokemon = Pokemon(pokeName, -1, pokelvl, 0, [570, 140], [200, 250])
                        self.game.fight = Fight([Wpokemon], self.player.pokemon_list, self.game.Kbd, False)
                        self.game.fightB = True
                    self.player.in_fight = False

        if self.game.background.is_object_format:
            self._draw_sorted(canvas, dt)
        else:
            self.game.background.draw(canvas)
            self.player.draw(canvas, dt)
            for y in self.game.background.npc_list:
                y.draw(canvas, dt)
                self._npc_interact(canvas, y, dt)

    #resolves NPC movement/collision and the resulting dialogue-or-fight trigger; shared by both
    #draw paths below. Returns the NPC to show dialogue for, if its interaction just fired one.
    def _npc_interact(self, canvas, y, dt):
        y.move_to_player(self.player)
        col = y.collision(self.player)
        if col == True:
            fightB = y.interact(self.player)
            if fightB == True:
                self.player.lock = True
                self.game.text = Text(y.image_name, self.player, (50,405), True, self.game.txtcount, self.game.txtclock)
                self.game.text.draw(canvas, dt, select=self.game.keyboard.select)
                self.game.keyboard.select = False
                self.game.txtcount = self.game.text.count
                if self.game.text.display == False:
                    self.player.lock = False
                    self.game.txtcount = 0
                    self.game.fightB = True
                    self.game.fight = Fight(self.game.background.npc_list[0].pokemon_list, self.player.pokemon_list, self.game.Kbd, True)

    #map-builder maps: ground layer once, then player/NPCs/objects drawn in Y-sorted order so a
    #tall object can occlude the player (and vice versa) instead of the player always being on top
    def _draw_sorted(self, canvas, dt):
        self.game.background.draw(canvas)

        drawables = [(self.player.pos.y + (self.player.frame_dim[1]//2)*self.player.scale_factor, self.player.draw)]
        for y in self.game.background.npc_list:
            drawables.append((y.pos.y + (y.frame_dim[1]//2)*y.scale_factor, y.draw))
        for obj in self.game.background.visual_objects:
            drawables.append((obj.base_y(), obj.draw))
        drawables.sort(key=lambda item: item[0])
        for _, draw_fn in drawables:
            draw_fn(canvas, dt)

        for y in self.game.background.npc_list:
            self._npc_interact(canvas, y, dt)

#sets up main class
class Game:
    def __init__(self, welcome, tutorial, player, keyboard, background, frame):
        self.player = player
        self.keyboard = keyboard
        self.welcome = welcome
        self.frame = frame
        self.startscreen = Welcome("StartScreen.png")
        self.credits = Welcome("credits.png")
        self.caughtAll = Welcome("CaughtAll.png")
        self.pauseScreen = Welcome("pause.png")
        self.gameOverScreen = Welcome("gameover.png")
        self.tutorial = tutorial
        self.background = background
        self.npc_lost = []
        self.intro = False
        self.complete = False
        self.pokecomplete = False
        self.game_over = False
        #not persisted to Save.json - a fresh load just falls back to the default Pokecenter,
        #same as a session that hasn't visited one yet
        self.last_pokecenter_map = DEFAULT_POKECENTER_MAP
        self.txtcount = 0
        self.txtclock = Clock()
        self.text = Text("empty",self.player, (0,0), False, self.txtcount, self.txtclock)
        self.inter = Interaction(self.player, self.keyboard, self)
        self.Kbd = Kbd()
        self.pokedex = Pokedex(self.Kbd)
        pokemon2 = Pokemon('Palkia', 19, 5, 50, [210, 250], [570, 140])
        self.fight = Fight([pokemon2], [pokemon2], self.Kbd, False)
        self.fightB = False

        #which top-level screen is active, dispatched via STATE_HANDLERS instead of nested
        #if/elif checks. "tutorial" isn't its own state - it's an overlay toggle within
        #welcome/start_menu (see _draw_welcome/_draw_start_menu), same as the original code.
        self.state_handlers = {
            "welcome": self._draw_welcome,
            "start_menu": self._draw_start_menu,
            "fight": self._draw_fight,
            "pokedex": self._draw_pokedex,
            "pause": self._draw_pause,
            "game_over": self._draw_game_over,
            "overworld": self._draw_overworld,
        }
        self.state = self._resolve_state()

    #derives the current top-level screen from the keyboard/fight flags - same priority order
    #as the original nested if/elif chain (fight takes priority over pokedex; both require
    #keyboard.start and keyboard.startscreen to already be set)
    def _resolve_state(self):
        if not self.keyboard.start:
            return "welcome"
        if not self.keyboard.startscreen:
            return "start_menu"
        if self.fightB:
            return "fight"
        if self.keyboard.pokedex:
            return "pokedex"
        if self.keyboard.paused:
            return "pause"
        if self.game_over:
            return "game_over"
        return "overworld"

    #fires once on the frame a new state is entered - swaps the active keydown/keyup handler
    #to the fight/pokedex-local Kbd. Only fires on entry (not every frame like the original
    #inline calls did) since re-setting the same handler reference every frame was redundant.
    #The handler is swapped *back* to self.keyboard from inside _draw_fight/_draw_pokedex
    #themselves, not here - that swap-back intentionally happens as soon as the battle/pokedex
    #interaction itself concludes, which can be several frames before the state actually changes
    #(e.g. the post-fight win/lose text overlay keeps "fight" active while it plays out).
    def _enter_state(self, state):
        if state in ("fight", "pokedex"):
            self.frame.set_keydown_handler(self.Kbd.keyDown)
            self.frame.set_keyup_handler(self.Kbd.keyUp)

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
    def draw(self, canvas, dt):
        new_state = self._resolve_state()
        if new_state != self.state:
            self._enter_state(new_state)
            self.state = new_state
        self.state_handlers[self.state](canvas, dt)

    #handles the active battle screen, including the win/lose outcome once a fight ends
    def _draw_fight(self, canvas, dt):
        self.fight.draw(canvas, dt)

        if (self.fight.end == True):
            self.Kbd.KeyReset()
            self.frame.set_keydown_handler(self.keyboard.keyDown)
            self.frame.set_keyup_handler(self.keyboard.keyUp)
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
                self.text.draw(canvas, dt, select=self.keyboard.select)
                self.keyboard.select = False
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
                        for pokemon in self.player.pokemon_list:
                            pokemon.HP = pokemon.fullhp

                    if self.fight.run:
                        self.player.pos.x +=50
                        self.player.pos.y +=50
            else:
                if self.fight.lost:
                    self.player.lives -= 1
                    for pokemon in self.player.pokemon_list:
                        pokemon.HP = pokemon.fullhp
                self.fightB = False

    #handles the Gokedex overlay. dt unused - Pokedex has no timing of its own, but every
    #state_handlers entry is invoked through the same uniform (canvas, dt) call in draw()
    def _draw_pokedex(self, canvas, dt):
        self.pokedex.draw(canvas)
        if self.Kbd.quit:
            self.Kbd.KeyReset()
            self.frame.set_keydown_handler(self.keyboard.keyDown)
            self.frame.set_keyup_handler(self.keyboard.keyUp)
            self.keyboard.KeyReset()
            self.keyboard.pokedex = False
            self.Kbd.quit = False

    #handles the pause overlay - a full-screen image + controls list, same pattern as
    #credits/CaughtAll, replacing the overworld draw entirely rather than layering on top of
    #it (so overworld movement/timers are simply not ticked while paused, no extra flag needed).
    #dt unused, same reason as _draw_start_menu/_draw_welcome below
    def _draw_pause(self, canvas, dt):
        self.pauseScreen.draw(canvas)
        canvas.draw_text("Paused", (340, 60), 44, 'White')
        for i, line in enumerate(PAUSE_CONTROLS):
            canvas.draw_text(line, (220, 130 + i * 32), 22, 'White')
        canvas.draw_text("Esc or Q to resume", (250, 130 + len(PAUSE_CONTROLS) * 32 + 20), 24, 'Yellow')

        #Q reuses the same "back out of a screen" key/flag as every other overlay
        #(pokedex/tutorial); Esc itself already toggles keyboard.paused back off in keyDown
        if self.keyboard.back:
            self.keyboard.paused = False
            self.keyboard.back = False

    #handles the "ran out of lives" screen - requires a keypress rather than firing the reset on
    #the very next frame like it used to. No data wipe: unlike new_game("yes"), this keeps
    #Save.json/PlayerPokemon.json/PlayerPokedex.json untouched, just restores lives/HP and drops
    #the player at the last Pokecenter they visited (or the default one if they haven't yet),
    #mirroring a normal fight loss's full-heal rather than mainline Pokemon's cash/item penalty
    def _draw_game_over(self, canvas, dt):
        self.gameOverScreen.draw(canvas)
        canvas.draw_text("Game Over", (270, 140), 48, 'White')
        canvas.draw_text("You ran out of lives.", (250, 210), 24, 'White')
        canvas.draw_text("Your team is fully healed and lives are restored -", (110, 250), 22, 'White')
        canvas.draw_text("no progress lost.", (310, 280), 22, 'White')
        canvas.draw_text("Press Space to continue", (250, 360), 24, 'Yellow')

        if self.keyboard.select:
            self.keyboard.select = False
            self.player.lives = balance.STARTING_LIVES
            for pokemon in self.player.pokemon_list:
                pokemon.HP = pokemon.fullhp
            self.background = Background(self.last_pokecenter_map, WIDTH, HEIGHT, self.npc_lost)
            self.background.load_wall()
            self.player.pos.x, self.player.pos.y = POKECENTER_ENTRY_POS
            self.player.lock = False
            self.game_over = False

    #handles normal overworld movement/interaction and its one-off text overlays
    def _draw_overworld(self, canvas, dt):
        self.inter.update()
        self.player.update(dt)
        self.background.draw(canvas)
        self.inter.draw(canvas, dt)

        if self.keyboard.save:
            self.save_game()
            self.keyboard.save = False

        if (self.complete == False) and ("boss2" in self.npc_lost):
            self.credits.draw(canvas)
            self.txtclock.tick(dt)
            move_on = self.txtclock.transition(balance.CREDITS_AND_COMPLETION_FRAMES)
            if move_on:
                self.complete = True

        if (self.pokecomplete == False) and (self.player.encounters == 79):
            if (self.complete == False) and ("boss2" in self.npc_lost):
                pass
            else:
                self.caughtAll.draw(canvas)
                self.txtclock.tick(dt)
                move_on = self.txtclock.transition(balance.CREDITS_AND_COMPLETION_FRAMES)
                if move_on:
                    self.pokecomplete = True

        if self.player.player_heal:
            self.player.lock = True
            self.player.vel = Vector(0,0)
            self.text = Text("heal", self.player, (50,405), True, self.txtcount, self.txtclock)
            for y in self.player.pokemon_list:
                y.HP = y.fullhp
            self.text.draw(canvas, dt, select=self.keyboard.select)
            self.keyboard.select = False
            self.txtcount = self.text.count
            if self.text.display == False:
                self.player.pos.y += 50
                self.player.player_heal = False
                self.player.lock = False
                self.txtcount = 0

        if not self.intro:
            self.player.lock = True
            self.text = Text("intro", self.player, (50,405), True, self.txtcount, self.txtclock)
            self.text.draw(canvas, dt, select=self.keyboard.select)
            self.keyboard.select = False
            self.txtcount = self.text.count
            if self.text.display == False:
                self.intro = True
                self.player.lock = False
                self.txtcount = 0

        if self.background.map_name in POKECENTER_MAPS:
            self.last_pokecenter_map = self.background.map_name

        if self.player.lives == 0:
            self.game_over = True
            self.player.lock = True
            self.player.vel = Vector(0, 0)

    #handles the start-screen / tutorial toggle shown before pressing space to enter the
    #overworld. dt unused - no timing here - but part of the uniform state_handlers call shape
    def _draw_start_menu(self, canvas, dt):
        if not self.keyboard.tutorial:
            self.startscreen.draw(canvas)
        else:
            self.tutorial.draw(canvas)
            if self.keyboard.back:
                self.keyboard.tutorial = False
                self.keyboard.back = False

    #handles the welcome screen / tutorial shown before pressing space the first time. dt unused,
    #same reason as _draw_start_menu above
    def _draw_welcome(self, canvas, dt):
        if not self.keyboard.tutorial:
            self.welcome.draw(canvas)
        else:
            self.tutorial.draw(canvas)
            if self.keyboard.back:
                self.keyboard.tutorial = False
                self.keyboard.back = False
