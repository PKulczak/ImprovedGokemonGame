import pygame
import random
import os
import json
from game.engine.vector import Vector
from game.engine.image_cache import load_image
from game.gameplay.Welcome import Welcome
from game.battle.fight import Pokemon
from game.battle.fight import Fight
from game.battle.fight import Kbd
from game.battle.fight import POKEDEX, load_seen_pokemon
from game.gameplay.entities import _load_pokemon_party
from game.gameplay.world import Background
from game.gameplay.ui import Text, Pokedex, Shop, FastTravel, MAP_DIAGRAM_NODE, MAP_DISPLAY_NAMES
from game.gameplay.clock import Clock
from game.engine import balance
from game.engine import sound

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

WIDTH = 800
HEIGHT = 480

#shown on the pause overlay - the only place these are visible in-game (otherwise README.md only)
PAUSE_CONTROLS = [
    "Arrow keys - Move",
    "Space - Start / advance dialogue",
    "P - Open the Gokedex",
    "L - Open the progress log",
    "S - Save game",
    "M - Fast travel (arrows to move, Space to travel)",
    "Q - Back / quit a screen",
    "T - Open the tutorial",
    "R - Rename your player",
    "N - Reset to a new game",
    "Shift (hold) - Fast-forward",
]

#TEMP: set True to re-enable random wild encounters (disabled for map/collision QA)
WILD_ENCOUNTERS_ENABLED = True

#which looping background track (game/Sound/music/<zone>.ogg, see sound.py) plays for each of
#the 14 maps - grouped into a handful of zones rather than one track per map, since most maps
#within a group share the same overworld "feel". Falls back to "town" for any map not listed.
MAP_MUSIC_ZONES = {
    "map": "town", "map2": "town", "map2y": "town", "map3": "town",
    "route1": "route", "route2": "route", "route3": "route", "route4": "route",
    "pokecenter": "pokecenter", "pokecenter2": "pokecenter",
    "gym2": "gym",
    "bossfight1": "boss", "bossfight2": "boss", "bossfight3": "boss",
}

#where fast travel (item 13) drops the player in each of its 7 world-map hubs (ui.py's
#MAP_DIAGRAM_NODE_POS) - the only maps it can ever land on, since FastTravel's own screen only
#ever offers those 7. Reuses the exact target_pos an existing door into that map already lands
#on (see world.py's per-map door graph in Overworld/maps/*.json) rather than inventing new
#coordinates
MAP_ENTRY_POINTS = {
    "map2": (756, 169),
    "route1": (770, 338),
    "map": (58, 169),
    "route2": (58, 236),
    "route3": (746, 67),
    "map3": (650, 143),
    "route4": (626, 200),
}

#the 4 trainer NPCs that can appear in self.npc_lost (see the "npc_species" field of
#gym2/bossfight1-3.json) - every other map's npc_species is one of these 4, so this doubles as
#"every boss there is" for the progress screen's "bosses defeated" count
BOSS_NPCS = ("boss1", "boss2", "boss3", "boss4")

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
    ("NewPlayerItems.json", "PlayerItems.json"),
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
        self.progress = False
        self.fast_travel = False
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
            elif self.startscreen == False:
                self.startscreen = True
            else:
                #distinct from start/startscreen above (one-shot latches for the welcome/start
                #screens) - this is a per-press "advance the current dialogue line" signal,
                #cleared by whichever Text.draw() call consumes it, same pattern as Kbd.select
                #in battle. Deliberately NOT set by the two presses above that flip start/
                #startscreen themselves - a returning save (intro already True) skips the one
                #block that normally drains this flag every frame (_draw_overworld's "if not
                #self.intro" block), so a leftover True from the "start the game" press would
                #otherwise survive into the player's first frame of control and silently
                #auto-confirm the first menu that happens to read it (e.g. instantly picking
                #"Heal" if they're standing on a Pokecenter tile already)
                self.select = True
            sound.play_sfx("select")
        if key == pygame.K_p:
            self.pokedex = True
        if key == pygame.K_l:
            self.progress = True
        if key == pygame.K_m:
            self.fast_travel = True
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
                    #autosave on every map transition - a natural, frequent checkpoint, silent
                    #(no "Saved!" flash) since it's automatic rather than a deliberate keypress
                    self.game.save_game()
                    #picks up on a zone change even though the game *state* stays "overworld"
                    #the whole time (_enter_state alone only fires when the state itself changes)
                    self.game._play_zone_music()

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
        self.progressScreen = Welcome("progress.png")
        self.tutorial = tutorial
        self.background = background
        self.npc_lost = []
        #maps the player has actually set foot in this save (see _draw_overworld) - the pool
        #the fast-travel screen (item 13) offers, in MAP_ORDER regardless of visit order
        self.visited_maps = []
        self.intro = False
        self.complete = False
        self.pokecomplete = False
        self.game_over = False
        #not persisted to Save.json - a fresh load just falls back to the default Pokecenter,
        #same as a session that hasn't visited one yet
        self.last_pokecenter_map = DEFAULT_POKECENTER_MAP
        #counts down real frame-equivalents left to show the "Saved!" flash after manual save
        self.save_flash_count = 0
        #counts up towards the next timer-based autosave (see AUTOSAVE_INTERVAL_FRAMES) - reset
        #on every save regardless of what triggered it, so a manual/transition save also pushes
        #the next timer-based one back rather than firing needlessly soon after
        self.autosave_count = 0
        self.txtcount = 0
        self.txtclock = Clock()
        self.text = Text("empty",self.player, (0,0), False, self.txtcount, self.txtclock)
        self.inter = Interaction(self.player, self.keyboard, self)
        self.Kbd = Kbd()
        self.pokedex = Pokedex(self.Kbd)
        self.shop = Shop(self.Kbd)
        self.fast_travel_ui = FastTravel(self.Kbd)
        self.shop_open = False
        #the heal tile opens a Heal-or-Shop choice (pokecenter_menu) instead of always healing;
        #pokecenter_healing is the confirmed-Heal follow-up (shows the "heal" dialogue and
        #actually restores HP) - picking Shop instead just sets shop_open, no healing happens
        self.pokecenter_box = load_image('{}/Text/box.png'.format(BASE_DIR))
        self.pokecenter_choice = 0
        self.pokecenter_healing = False
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
            "progress": self._draw_progress,
            "fast_travel": self._draw_fast_travel,
            "pause": self._draw_pause,
            "game_over": self._draw_game_over,
            "shop": self._draw_shop,
            "pokecenter_menu": self._draw_pokecenter_menu,
            "pokecenter_heal": self._draw_pokecenter_heal,
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
        if self.keyboard.progress:
            return "progress"
        if self.keyboard.fast_travel:
            return "fast_travel"
        if self.keyboard.paused:
            return "pause"
        if self.game_over:
            return "game_over"
        if self.shop_open:
            return "shop"
        if self.player.player_heal:
            return "pokecenter_menu"
        if self.pokecenter_healing:
            return "pokecenter_heal"
        return "overworld"

    #fires once on the frame a new state is entered - swaps the active keydown/keyup handler
    #to the fight/pokedex/shop/fast_travel-local Kbd. Only fires on entry (not every frame like
    #the original inline calls did) since re-setting the same handler reference every frame was
    #redundant. The handler is swapped *back* to self.keyboard from inside _draw_fight/
    #_draw_pokedex/_draw_shop/_draw_fast_travel themselves, not here - that swap-back
    #intentionally happens as soon as the battle/pokedex/shop/fast-travel interaction itself
    #concludes, which can be several frames before the state actually changes (e.g. the
    #post-fight win/lose text overlay keeps "fight" active while it plays out).
    def _enter_state(self, state):
        if state in ("fight", "pokedex", "shop", "fast_travel"):
            self.frame.set_keydown_handler(self.Kbd.keyDown)
            self.frame.set_keyup_handler(self.Kbd.keyUp)
        if state == "fight":
            sound.play_music("battle")
        elif state == "fast_travel":
            #the cursor always starts on wherever the player actually is, not wherever it
            #was last left open
            self.fast_travel_ui.reset(MAP_DIAGRAM_NODE.get(self.background.map_name, self.background.map_name))
        elif state == "overworld":
            #covers both "just returned from a fight/menu" and "just walked into a different
            #zone" (the latter re-fires this same call from Interaction.draw on every map
            #transition, since state stays "overworld" the whole time and _enter_state alone
            #wouldn't otherwise notice the map changed)
            self._play_zone_music()

    #resumes whichever zone track the player's current map belongs to; a no-op if that track is
    #already playing (see sound.play_music)
    def _play_zone_music(self):
        zone = MAP_MUSIC_ZONES.get(self.background.map_name, "town")
        sound.play_music(zone)

    #saves the current progress of player
    def save_game(self):
        save_data = {
            "intro": self.intro,
            "complete": self.complete,
            "pokecomplete": self.pokecomplete,
            "npc_lost": list(self.npc_lost),
            "visited_maps": list(self.visited_maps),
            "player": {
                "x": self.player.pos.x,
                "y": self.player.pos.y,
                "lives": self.player.lives,
                "money": self.player.money,
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
        #however this save was triggered (manual, map-transition, or the autosave timer itself),
        #push the next timer-based autosave back rather than letting it fire redundantly soon after
        self.autosave_count = 0

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
            #.get with a fallback, not save_data["visited_maps"] - lets a save file written
            #before fast travel existed load cleanly (falling back to just its current map,
            #same as a brand new visit to it) instead of hitting the except-and-wipe fallback
            #below over a merely-missing (not corrupted) field
            self.visited_maps = list(save_data.get("visited_maps", [save_data["map"]]))
            player_data = save_data["player"]
            self.player.pos.x = int(player_data["x"])
            self.player.pos.y = int(player_data["y"])
            self.player.lives = int(player_data["lives"])
            #.get with a fallback, not player_data["money"] - lets a save file written before
            #the money/shop feature existed load cleanly instead of hitting the except-and-wipe
            #fallback below over a merely-missing (not corrupted) field
            self.player.money = int(player_data.get("money", balance.STARTING_MONEY))
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
                self.player.money += self.fight.money_earned
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

    #a read-only progress/achievement summary (item 12) - bosses defeated, Gokedex completion,
    #money, and the current party. Reuses self.keyboard directly rather than swapping to Kbd,
    #same as pause/game_over, since there's nothing to navigate here, just a Q to close
    def _draw_progress(self, canvas, dt):
        self.progressScreen.draw(canvas)
        canvas.draw_text("Progress", (300, 55), 40, 'White')

        defeated = len(self.npc_lost)
        canvas.draw_text("Bosses defeated: "+str(defeated)+"/"+str(len(BOSS_NPCS)), (60, 110), 22, 'White')
        for i, boss in enumerate(BOSS_NPCS):
            beaten = boss in self.npc_lost
            status = "Defeated" if beaten else "Not yet"
            colour = 'Yellow' if beaten else 'Grey'
            canvas.draw_text("Boss "+str(i+1)+": "+status, (80, 145 + i * 28), 20, colour)

        seen_count = len(load_seen_pokemon())
        canvas.draw_text("Gokedex: "+str(seen_count)+"/"+str(len(POKEDEX))+" seen", (60, 275), 22, 'White')
        canvas.draw_text("Money: $"+str(self.player.money), (60, 305), 22, 'White')

        canvas.draw_text("Your team:", (460, 110), 22, 'White')
        for i, mon in enumerate(self.player.pokemon_list):
            label = mon.name+" Lv."+str(mon.lvl)+"  HP:"+str(mon.HP)+"/"+str(mon.fullhp)
            canvas.draw_text(label, (460, 145 + i * 28), 18, 'White')

        canvas.draw_text("Q to close", (330, 445), 22, 'Yellow')

        #back (Q) reuses the same "close an overlay" flag as pause/tutorial - no Kbd swap
        #happened on entry, so nothing needs undoing beyond clearing the two flags
        if self.keyboard.back:
            self.keyboard.progress = False
            self.keyboard.back = False

    #handles the Pokecenter shop, reached either from _draw_pokecenter_menu's "Visit the shop"
    #choice or (unrelated to the Pokecenter) never otherwise. Same swap-the-keydown-handler-
    #back-on-quit pattern as _draw_pokedex above
    def _draw_shop(self, canvas, dt):
        self.shop.draw(canvas, self.player)
        if self.Kbd.quit:
            self.Kbd.KeyReset()
            self.frame.set_keydown_handler(self.keyboard.keyDown)
            self.frame.set_keyup_handler(self.keyboard.keyUp)
            self.keyboard.KeyReset()
            self.shop.message = ""
            self.shop.popup_active = False
            self.shop_open = False
            self.Kbd.quit = False

    #the fast-travel screen (item 13) - navigate the 7-hub world map itself (arrow keys move a
    #cursor along FastTravel's own adjacency graph, Space travels to it) rather than picking off
    #a text list. Picking a hub drops the player at that map's MAP_ENTRY_POINTS spot (the same
    #landing spot an existing door into it already uses) and closes the screen in the same
    #frame; Q closes it without travelling
    def _draw_fast_travel(self, canvas, dt):
        visited_hubs = set(self.visited_maps) & set(MAP_ENTRY_POINTS)
        current_map = self.background.map_name
        current_label = MAP_DISPLAY_NAMES.get(current_map, current_map)
        target = self.fast_travel_ui.draw(canvas, visited_hubs, current_map, current_label)

        if target is not None:
            self.background = Background(target, WIDTH, HEIGHT, self.npc_lost)
            self.background.load_wall()
            self.player.pos.x, self.player.pos.y = MAP_ENTRY_POINTS[target]
            #a deliberate checkpoint, same reasoning as the map-transition autosave in
            #Interaction.draw - a free teleport is exactly the kind of position change that
            #shouldn't be able to roll back on a crash before the next save
            self.save_game()
            self._play_zone_music()

        if target is not None or self.Kbd.quit:
            self.Kbd.KeyReset()
            self.frame.set_keydown_handler(self.keyboard.keyDown)
            self.frame.set_keyup_handler(self.keyboard.keyUp)
            self.keyboard.KeyReset()
            self.keyboard.fast_travel = False
            self.Kbd.quit = False

    #the Pokecenter counter's Heal-or-Shop choice, shown the moment the player steps on a heal
    #tile (player.player_heal) instead of always auto-healing. Up/Down to pick, Space to
    #confirm, Q ("back") to leave without doing either - uses self.keyboard directly rather
    #than swapping to the fight/pokedex-local Kbd, same as the pause/game_over screens, since
    #the overworld draw (and so player movement) simply isn't invoked while this state is active
    def _draw_pokecenter_menu(self, canvas, dt):
        self.player.lock = True
        self.player.vel = Vector(0,0)
        self.background.draw(canvas)
        self.player.draw(canvas, dt)
        canvas.draw_image(self.pokecenter_box, (400,75), (800,150), (400,405), (800,150))
        canvas.draw_text("Heal your team, or visit the shop?", (50, 385), 20, 'White')
        heal_col = "Yellow" if self.pokecenter_choice == 0 else "White"
        shop_col = "Yellow" if self.pokecenter_choice == 1 else "White"
        canvas.draw_text("Heal my team", (50, 420), 20, heal_col)
        canvas.draw_text("Visit the shop", (50, 450), 20, shop_col)

        if self.keyboard.up:
            self.pokecenter_choice = 0
        elif self.keyboard.down:
            self.pokecenter_choice = 1

        if self.keyboard.select:
            self.keyboard.select = False
            self.player.player_heal = False
            if self.pokecenter_choice == 0:
                self.pokecenter_healing = True
                self.text = Text("heal", self.player, (50,405), True, self.txtcount, self.txtclock)
            else:
                self.shop_open = True
                self.player.pos.y += 50
                self.player.lock = False
        elif self.keyboard.back:
            self.keyboard.back = False
            self.player.player_heal = False
            self.player.pos.y += 50
            self.player.lock = False

    #the confirmed-Heal follow-up - shows the "heal" dialogue line while actually restoring HP,
    #same beat the old always-heal flow had, just no longer forced or followed by the shop
    def _draw_pokecenter_heal(self, canvas, dt):
        self.background.draw(canvas)
        self.player.draw(canvas, dt)
        for y in self.player.pokemon_list:
            y.HP = y.fullhp
        self.text.draw(canvas, dt, select=self.keyboard.select)
        self.keyboard.select = False
        self.txtcount = self.text.count
        if self.text.display == False:
            self.player.pos.y += 50
            self.pokecenter_healing = False
            self.player.lock = False
            self.txtcount = 0

    #handles the pause overlay - a full-screen image + controls list, same pattern as
    #credits/CaughtAll, replacing the overworld draw entirely rather than layering on top of
    #it (so overworld movement/timers are simply not ticked while paused, no extra flag needed).
    #dt unused, same reason as _draw_start_menu/_draw_welcome below
    def _draw_pause(self, canvas, dt):
        #left/right are free to repurpose here - overworld movement isn't ticked while paused
        #(_draw_overworld simply isn't called), so there's no conflict with their normal job.
        #Manually zeroed after each press (rather than waiting for the natural keyUp) so holding
        #the key down only steps the volume once per press, not once per frame held. Handled
        #before drawing (not after) so the percentage below reflects this frame's own keypress
        #instead of lagging a frame behind it
        if self.keyboard.left:
            self.keyboard.left = False
            sound.set_volume(sound.get_volume() - 0.1)
        elif self.keyboard.right:
            self.keyboard.right = False
            sound.set_volume(sound.get_volume() + 0.1)

        self.pauseScreen.draw(canvas)
        canvas.draw_text("Paused", (340, 40), 40, 'White')
        #a tighter per-line height than most other screens use, purely so this list has
        #headroom to grow (it's grown twice already) without pushing the volume/resume lines
        #below the bottom of the 480px-tall screen
        line_height = 26
        for i, line in enumerate(PAUSE_CONTROLS):
            canvas.draw_text(line, (200, 100 + i * line_height), 20, 'White')
        volume_line_y = 100 + len(PAUSE_CONTROLS) * line_height + 20
        volume_pct = int(round(sound.get_volume()*100))
        canvas.draw_text("Volume: "+str(volume_pct)+"% (Left/Right to adjust)", (200, volume_line_y), 20, 'White')
        canvas.draw_text("Esc or Q to resume", (230, volume_line_y + 30), 24, 'Yellow')

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
            self.save_flash_count = balance.SAVE_FLASH_FRAMES
            sound.play_sfx("save")

        if self.save_flash_count > 0:
            canvas.draw_text("Saved!", (340, 55), 26, 'Black')
            self.save_flash_count -= dt

        #a fixed-interval safety net alongside the map-transition autosave in Interaction.draw -
        #silent, same as that one, so it doesn't compete with the manual-save flash above
        self.autosave_count += dt
        if self.autosave_count >= balance.AUTOSAVE_INTERVAL_FRAMES:
            self.save_game()

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

        #fast travel's (item 13) pool of offerable destinations - grows the first time the
        #player actually sets foot on each map, same "seen it once, it's unlocked" shape as
        #the Gokedex's own seen-list
        if self.background.map_name not in self.visited_maps:
            self.visited_maps.append(self.background.map_name)

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
