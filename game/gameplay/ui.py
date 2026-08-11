import os
import json
from game.engine.image_cache import load_image
from game.engine import balance
from game.engine.party_grid import PartyGrid
from game.battle.fight import POKEDEX, load_seen_pokemon, seen_pokemon_version, ITEM_ORDER, load_items, save_items

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

#creates the Gokedex
class Pokedex:
    def __init__(self, kbd):
        self.player_pokedex = []
        self.pokedex = []
        self.name_pages = []
        self.kbd = kbd
        self.first = True
        self.poke_list =[]
        self.index = 0
        self.grid = PartyGrid(on_page=self._turn_page)
        self.bag = load_image('{}/Fight/Other/bag.png'.format(BASE_DIR))
        self.light = load_image('{}/Fight/Other/highlight.png'.format(BASE_DIR))
        #forces the first draw() to build self.pokedex, since no real version is ever -1
        self._built_from_version = -1
        #species sprite sheets for the detail view, loaded lazily and cached per name - the
        #same sheets Fight's Pokemon class loads, but the Gokedex only ever needs the single
        #idle frame [col0,row0], never the walk/attack animation cycle
        self._sprite_cache = {}
        self.detail_active = False
        self.detail_name = None
        #a dedicated full-screen backdrop for the detail view rather than the 6-box bag.png -
        #the grid's box dividers would otherwise show through behind the sprite/stats
        self.detail_bg = load_image('{}/Text/pokedex_detail.png'.format(BASE_DIR))

    #turns to the next/previous page of 6 pokedex entries, called by the grid when down is
    #pressed at the bottom row or up is pressed at the top row
    def _turn_page(self, direction):
        if direction > 0:
            if not (self.index == len(self.pokedex)-1):
                self.index += 1
        else:
            if not (self.index == 0):
                self.index -= 1

    def draw(self, canvas):
        #loads the gokemon the player has in their gokedex - a cheap mtime check unless
        #something actually changed (a catch, or a save reset), rather than a raw file
        #open+parse every frame
        self.player_pokedex = load_seen_pokemon()
        version = seen_pokemon_version()
        if version != self._built_from_version:
            #rebuilds the paginated ?????/name display list (and the matching page-of-species-
            #names list the detail view resolves the grid cursor against) - only needed when
            #the seen-list itself changed, not every frame the Gokedex screen happens to be open
            self.pokedex = []
            self.name_pages = []
            count = 0
            temp_list = []
            temp_names = []
            for name in POKEDEX:
                count += 1
                if name in self.player_pokedex:
                    temp_list.append(str(count)+"    "+name)
                else:
                    temp_list.append(str(count)+"    ?????")
                temp_names.append(name)
                if len(temp_list) >= 6:
                    self.pokedex.append(temp_list)
                    self.name_pages.append(temp_names)
                    temp_list = []
                    temp_names = []
            if len(temp_list) != 0:
                self.pokedex.append(temp_list)
                self.name_pages.append(temp_names)
                temp_list = []
                temp_names = []
            self._built_from_version = version

        #a caught entry's detail panel blocks the grid until Q returns to the list, same
        #popup-blocks-input pattern as the shop's purchase-result popup
        if self.detail_active:
            self._draw_detail(canvas)
            return

        #draws gokedex
        self.poke_list = self.pokedex[self.index]
        self.first = self.grid.update(self.kbd, self.first)
        self.grid.draw_highlight(canvas, self.bag, self.light)
        for i in range(0,len(self.poke_list)):
            if i<3:
                canvas.draw_text(self.poke_list[i], (290, 150+(i*120)), 25, 'Black')
            else:
                canvas.draw_text(self.poke_list[i], (540, 150+(i-3)*120), 25, 'Black')

        #selecting a caught entry opens its detail panel; unseen (?????) entries have nothing
        #to show yet, so selecting one is a no-op rather than revealing anything about it
        if self.kbd.select:
            self.kbd.select = False
            names = self.name_pages[self.index]
            idx = self.grid.selected_index()
            if idx < len(names) and names[idx] in self.player_pokedex:
                self.detail_name = names[idx]
                self.detail_active = True

    #a caught species' sprite (idle frame) plus its base ATK/DEF/HP/type, on its own full-screen
    #backdrop (same Welcome-style full-image pattern as pause/game-over) rather than layered over
    #the 6-box bag.png grid. Q returns to the grid, consumed here (rather than left for
    #Game._draw_pokedex's own Kbd.quit check) so backing out of the detail view doesn't also
    #close the whole Gokedex in the same press
    def _draw_detail(self, canvas):
        name = self.detail_name
        stats = POKEDEX[name]
        image, frame_dim = self._sprite(name, stats["row"])
        canvas.draw_image(self.detail_bg, (400,240), (800,480), (400,240), (800,480))
        canvas.draw_image(image, (frame_dim[0]/2, frame_dim[1]/2), frame_dim,
                           (220,260), (frame_dim[0]*5, frame_dim[1]*5))
        canvas.draw_text(name, (470,110), 32, 'White')
        canvas.draw_text("Type: "+stats["effect_img"].capitalize(), (470,160), 22, 'White')
        canvas.draw_text("ATK: "+str(stats["ATK"]), (470,200), 22, 'White')
        canvas.draw_text("DEF: "+str(stats["DEF"]), (470,235), 22, 'White')
        canvas.draw_text("HP: "+str(stats["fullhp"]), (470,270), 22, 'White')
        canvas.draw_text("SPD: "+str(stats.get("SPD", balance.DEFAULT_SPD)), (470,305), 22, 'White')
        canvas.draw_text("Press Q to go back", (300,440), 22, 'Yellow')
        if self.kbd.quit:
            self.kbd.quit = False
            self.detail_active = False

    #loads (and caches) a species' sprite sheet plus its idle [col0,row0] frame dimensions -
    #same sheet Fight's Pokemon class loads for battle, sliced the same way (width/5 columns,
    #height/row rows), but the Gokedex only ever needs that one static frame
    def _sprite(self, name, row):
        cached = self._sprite_cache.get(name)
        if cached is not None:
            return cached
        image = load_image('{}/Fight/pokemon/'.format(BASE_DIR)+name+".png")
        frame_dim = (image.get_width()//5, image.get_height()//row)
        self._sprite_cache[name] = (image, frame_dim)
        return self._sprite_cache[name]

#buyable at a Pokecenter counter (see Game._draw_shop) - a fixed price list for the same items
#the battle Bag menu already tracks in PlayerItems.json (game/battle/fight.py's ITEM_ORDER)
SHOP_PRICES = {"Poke Ball": 50, "Great Ball": 150, "Ultra Ball": 300, "Potion": 30}

#a small Pokecenter shop, offered after healing - same 6-slot grid/backdrop as the Gokedex and
#the battle item menu (only 4 of the 6 slots are used, one per ITEM_ORDER entry)
class Shop:
    def __init__(self, kbd):
        self.kbd = kbd
        self.first = True
        self.grid = PartyGrid()
        self.bag = load_image('{}/Fight/Other/bag.png'.format(BASE_DIR))
        self.light = load_image('{}/Fight/Other/highlight.png'.format(BASE_DIR))
        self.txtbox = load_image('{}/Text/box.png'.format(BASE_DIR))
        self.message = ""
        #a purchase result (bought/not enough money) blocks the grid until dismissed with
        #Space, same box.png dialogue pattern used for heal/intro/battle-win text elsewhere
        self.popup_active = False

    def draw(self, canvas, player):
        items = load_items()
        #frozen while the popup is up - only Space (handled below) does anything until dismissed
        if not self.popup_active:
            self.first = self.grid.update(self.kbd, self.first)
        self.grid.draw_highlight(canvas, self.bag, self.light)
        for i, name in enumerate(ITEM_ORDER):
            label = name+" x"+str(items.get(name, 0))+" - $"+str(SHOP_PRICES[name])
            if i < 3:
                canvas.draw_text(label, (270, 145+(i*120)), 20, 'Black')
            else:
                canvas.draw_text(label, (520, 145+(i-3)*120), 20, 'Black')
        canvas.draw_text("Money: $"+str(player.money), (30, 30), 24, 'Black')

        if self.popup_active:
            canvas.draw_image(self.txtbox, (400,75), (800,150), (400,405), (800,150))
            canvas.draw_text(self.message, (50, 385), 22, 'White')
            canvas.draw_text("Press Space to continue", (50, 435), 18, 'White')
            if self.kbd.select:
                self.kbd.select = False
                self.popup_active = False
            return

        #buying is a one-shot per select press, same debounce-by-consumption pattern used
        #everywhere else kbd.select drives a menu confirm
        if self.kbd.select:
            self.kbd.select = False
            index = self.grid.selected_index()
            if index < len(ITEM_ORDER):
                name = ITEM_ORDER[index]
                price = SHOP_PRICES[name]
                if player.money >= price:
                    player.money -= price
                    items[name] = items.get(name, 0) + 1
                    save_items(items)
                    self.message = "Bought a "+name+"!"
                else:
                    self.message = "Not enough money!"
                self.popup_active = True

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
        self.txtbox = load_image('{}/Text/box.png'.format(BASE_DIR))
        self.alltxt = [line.format(player_name=player.name) for line in dialogue_lines(txtfile)]
        self.num_lines = len(self.alltxt)

    #select fast-forwards the current line's countdown instead of waiting it out, advancing by
    #exactly one line, same as the timer completing naturally would
    def draw(self, canvas, dt, select=False):
        if self.display:
            if self.box:
                canvas.draw_image(self.txtbox, (400,75), (800,150), (400,405), (800,150))
            canvas.draw_text(self.alltxt[self.count], self.pos, 20, 'White')


        self.clock.tick(dt)
        move_on = self.clock.transition(balance.DIALOGUE_LINE_FRAMES)
        if select and not move_on:
            move_on = True
            self.clock.time = 0
        if move_on:
            self.count += 1
            if self.count >= self.num_lines:
                self.display = False
