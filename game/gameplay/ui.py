import os
import json
from game.engine.image_cache import load_image
from game.engine import balance
from game.engine import sound
from game.engine.party_grid import PartyGrid, draw_party_slot
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
    #backdrop (item 14 - an illustrated orange-panel-on-cream frame matching bag.png/box.png's
    #own palette, with a grey "window" behind the sprite and another behind the stats block,
    #rather than the flat placeholder fill this used to be) layered over the 6-box bag.png grid.
    #Q returns to the grid, consumed here (rather than left for Game._draw_pokedex's own
    #Kbd.quit check) so backing out of the detail view doesn't also close the whole Gokedex in
    #the same press
    def _draw_detail(self, canvas):
        name = self.detail_name
        stats = POKEDEX[name]
        image, frame_dim = self._sprite(name, stats["row"])
        canvas.draw_image(self.detail_bg, (400,240), (800,480), (400,240), (800,480))
        canvas.draw_image(image, (frame_dim[0]/2, frame_dim[1]/2), frame_dim,
                           (220,260), (frame_dim[0]*5, frame_dim[1]*5))
        canvas.draw_text(name, (470,110), 32, 'Black')
        canvas.draw_text("Type: "+stats["effect_img"].capitalize(), (470,160), 22, 'Black')
        canvas.draw_text("ATK: "+str(stats["ATK"]), (470,200), 22, 'Black')
        canvas.draw_text("DEF: "+str(stats["DEF"]), (470,235), 22, 'Black')
        canvas.draw_text("HP: "+str(stats["fullhp"]), (470,270), 22, 'Black')
        canvas.draw_text("SPD: "+str(stats.get("SPD", balance.DEFAULT_SPD)), (470,305), 22, 'Black')
        canvas.draw_text("Press Q to go back", (300,440), 22, 'White')
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

#shifts the whole bag_plain.png backdrop (and everything drawn relative to it) up from
#PartyGrid's normal position - frees enough plain background below the panel for a real
#two-line hint (the panel's default bottom edge leaves only ~26px of clear background there,
#not enough for two font-20 lines); doesn't touch PartyGrid.draw_highlight itself, so Pokedex/
#Shop's own layout is unaffected
TEAM_Y_OFFSET = -38

#lets the player reorder their own party (item 15) from the overworld, not just mid-battle -
#reuses the same PartyGrid/bag.png presentation as the Bag/Gokedex screens, but on bag_plain.png
#(a copy of bag.png with its baked-in "Back to Q fight" caption blanked out - wrong on every
#non-battle screen that reuses bag.png, but only fixed here since this is the one that got
#flagged) rather than bag.png itself. Space picks up a slot, Space on a second slot swaps them;
#persisted the same way PlayerPokemon.json already round-trips player.pokemon_list today
#(Game.save_game), no new save format needed. Slot order matters beyond display - it's also who
#leads a fresh fight (Fight.__init__ auto-skips a fainted lead but otherwise always opens on
#slot 0), so this doubles as "choose your lead"
class TeamOrder:
    def __init__(self, kbd):
        self.kbd = kbd
        self.first = True
        self.grid = PartyGrid()
        self.bag = load_image('{}/Fight/Other/bag_plain.png'.format(BASE_DIR))
        self.light = load_image('{}/Fight/Other/highlight.png'.format(BASE_DIR))
        #index of the slot picked up, waiting for a second slot to swap with; None if nothing
        #is currently picked up
        self.picked = None
        #True for exactly the frame a swap actually happens, so Game knows to save - TeamOrder
        #itself has no reason to know about Game.save_game
        self.changed = False

    #PartyGrid.draw_highlight draws both the backdrop and the selection box at fixed
    #coordinates; reimplemented here with TEAM_Y_OFFSET applied to both so they stay aligned
    #with each other (and with this screen's own shifted text/sprites below). Shifting the
    #backdrop image up also drags its bottom edge up with it (it only overhung the 480-tall
    #canvas by 5px to begin with) - the plain-background rect below patches the resulting gap
    #at the very bottom of the screen so the hint text still has its cream background there
    #instead of whatever's behind the canvas (black, same as this screen's own bag_plain.png
    #outer colour so the seam is invisible)
    def _draw_shifted_backdrop(self, canvas):
        canvas.draw_image(self.bag, (375,250), (750,500), (400,240+TEAM_Y_OFFSET), (735,490))
        canvas.draw_rect((400, 465), (800, 40), (228, 228, 222))
        pos = self.grid.POSITIONS[self.grid.centre[0]][self.grid.centre[1]]
        canvas.draw_image(self.light, (116,45), (233,91),
                           (pos[0], pos[1]+TEAM_Y_OFFSET), (233,91))

    def draw(self, canvas, pokemon_list):
        self.changed = False
        self.first = self.grid.update(self.kbd, self.first)
        self._draw_shifted_backdrop(canvas)
        canvas.draw_text("Reorder Team", (270, 60+TEAM_Y_OFFSET), 28, 'Black')
        for i, mon in enumerate(pokemon_list):
            colour = 'Yellow' if i == self.picked else 'Black'
            name_x = 270 if i < 3 else 520
            row_y = 130+TEAM_Y_OFFSET+((i if i < 3 else i-3)*120)
            draw_party_slot(canvas, mon, name_x, row_y, colour)

        #two lines, sized up from the single-line version this replaced, landing fully in the
        #plain background TEAM_Y_OFFSET freed up below the panel (see its own comment) rather
        #than straddling the panel's bottom edge the way one line at the old position did
        if self.picked is None:
            lines = ("Space to pick up a slot", "Q to close")
        else:
            lines = ("Space on another slot to swap", "same slot again to cancel")
        canvas.draw_text_centered(lines[0], (473, 436), 20, 'Black')
        canvas.draw_text_centered(lines[1], (473, 463), 20, 'Black')

        if self.kbd.select:
            self.kbd.select = False
            idx = self.grid.selected_index()
            if idx < len(pokemon_list):
                if self.picked is None:
                    self.picked = idx
                elif self.picked == idx:
                    self.picked = None
                else:
                    pokemon_list[self.picked], pokemon_list[idx] = pokemon_list[idx], pokemon_list[self.picked]
                    self.picked = None
                    self.changed = True

        if self.kbd.quit:
            self.picked = None

#fast travel's world map (item 13) - the 7 hubs it can jump between; every other real map
#groups onto one of these for the "you are here" highlight (see MAP_DIAGRAM_NODE below), since
#the diagram only has room for the major hubs, not every Pokecenter/gym/boss room individually
MAP_DIAGRAM_NATIVE_SIZE = (1020, 600)
MAP_DIAGRAM_BOX_DIM = (150, 74)
MAP_DIAGRAM_NODE_POS = {
    "map2":   (150, 360),
    "route1": (330, 360),
    "map":    (510, 360),
    "route2": (690, 360),
    "route3": (870, 240),
    "map3":   (870, 120),
    "route4": (870, 480),
}

#arrow-key adjacency between the 7 hubs, matching the diagram's own layout - horizontal along
#the map2-route1-map-route2 chain, vertical for route2's two branches (route3/map3 up, route4
#down), rather than the diagonal directions the diagram draws them at (plain arrow keys only
#have 4 directions to work with)
MAP_DIAGRAM_EDGES = {
    "map2":   {"right": "route1"},
    "route1": {"left": "map2", "right": "map"},
    "map":    {"left": "route1", "right": "route2"},
    "route2": {"left": "map", "up": "route3", "down": "route4"},
    "route3": {"down": "route2", "up": "map3"},
    "map3":   {"down": "route3"},
    "route4": {"up": "route2"},
}

#which hub lights up for a "you are here" highlight while standing on a given real map - the 7
#hubs are their own key (identity, via .get fallback below); every side location groups onto
#whichever hub it's a single door-hop off of in world.py's graph (pokecenter/map2y each have
#exactly one such neighbour; pokecenter2/gym2 share map3's; bossfight1/2/3 are grouped under
#route4 - the branch they all hang off, even though 2/3 are further nested behind 1 - rather
#than nested one-under-the-next, since none of the three bossfight rooms gets its own hub)
MAP_DIAGRAM_NODE = {
    "map2y": "map2",
    "pokecenter": "map",
    "pokecenter2": "map3",
    "gym2": "map3",
    "bossfight1": "route4",
    "bossfight2": "route4",
    "bossfight3": "route4",
}

#display label for every real map that can appear as either a hub or a "you are here" caption
MAP_DISPLAY_NAMES = {
    "map2y": "Starting Dock",
    "map": "Town",
    "map2": "North Town",
    "map3": "Gym Town",
    "pokecenter": "Pokecenter",
    "pokecenter2": "Pokecenter (North)",
    "gym2": "Gym",
    "route1": "Route 1",
    "route2": "Route 2",
    "route3": "Route 3",
    "route4": "Route 4",
    "bossfight1": "Boss Arena 1",
    "bossfight2": "Boss Arena 2",
    "bossfight3": "Boss Arena 3",
}

HERE_COLOR = (232, 115, 74)     #deep orange - the player's actual current hub
CURSOR_COLOR = (255, 214, 51)   #yellow - the hub the cursor would travel to on Space

#fast travel's map-select screen (item 13) - navigate the world map itself (arrow keys move
#a cursor along MAP_DIAGRAM_EDGES, Space travels to it) rather than picking off a text list.
#Only ever offers the 7 hubs above as destinations - individual Pokecenters/gyms/boss rooms
#aren't separately selectable, only whichever hub they're grouped under
class FastTravel:
    def __init__(self, kbd):
        self.kbd = kbd
        self.first = True
        self.cursor = "map2"
        self.map_image = load_image('{}/Text/map_layout.png'.format(BASE_DIR))

    #called by Game._enter_state on opening the screen, so the cursor always starts on
    #wherever the player actually is rather than wherever it was last left
    def reset(self, current_node):
        self.cursor = current_node
        self.first = True

    #moves the cursor along MAP_DIAGRAM_EDGES, debounced the same "wait for keys to release"
    #way PartyGrid.update is; a hub not yet in visited_hubs is treated as unreachable - the
    #cursor simply can't step onto it, same as it never appearing in the old text list at all
    def _update_cursor(self, visited_hubs):
        if not self.first:
            moved = False
            for direction, kbd_flag in (("left", self.kbd.left), ("right", self.kbd.right),
                                         ("up", self.kbd.up), ("down", self.kbd.down)):
                if kbd_flag:
                    target = MAP_DIAGRAM_EDGES.get(self.cursor, {}).get(direction)
                    if target is not None and target in visited_hubs:
                        self.cursor = target
                        moved = True
                    break
            if moved:
                self.first = True
                sound.play_sfx("menu_move")
        else:
            if not (self.kbd.left or self.kbd.right or self.kbd.up or self.kbd.down):
                self.first = False

    #visited_hubs is which of MAP_DIAGRAM_NODE_POS's 7 keys the player has actually set foot
    #on (a subset of Game.visited_maps); current_map/current_label are the player's real
    #current map id and its own display name (may not be one of the 7 hubs). Returns the
    #chosen hub's id the frame Space confirms a reachable selection, else None
    def draw(self, canvas, visited_hubs, current_map, current_label):
        current_node = MAP_DIAGRAM_NODE.get(current_map, current_map)
        self._update_cursor(visited_hubs)

        native_w, native_h = MAP_DIAGRAM_NATIVE_SIZE
        dest_w, dest_h = 760, native_h * 760 / native_w
        dest_center = (400, 260)
        scale = dest_w / native_w
        offset_x = dest_center[0] - native_w / 2 * scale
        offset_y = dest_center[1] - native_h / 2 * scale

        canvas.draw_image(self.map_image, (native_w/2, native_h/2), (native_w, native_h),
                           dest_center, (dest_w, dest_h))

        box_w, box_h = MAP_DIAGRAM_BOX_DIM[0]*scale, MAP_DIAGRAM_BOX_DIM[1]*scale
        for node, color in ((current_node, HERE_COLOR), (self.cursor, CURSOR_COLOR)):
            if node not in MAP_DIAGRAM_NODE_POS:
                continue
            nx, ny = MAP_DIAGRAM_NODE_POS[node]
            center = (offset_x + nx*scale, offset_y + ny*scale)
            canvas.draw_rect(center, (box_w, box_h), color, border_radius=8)
            canvas.draw_text_centered(node, center, 22, 'Black')

        #both lines land inside the cream diagram (which starts at offset_y, ~36px down) -
        #any higher and 'Black' text sits on the screen's plain black margin, invisible
        canvas.draw_text("Fast Travel", (20, offset_y+22), 24, 'Black')
        canvas.draw_text("You are here: "+current_label, (20, offset_y+48), 18, 'Black')
        cursor_label = MAP_DISPLAY_NAMES.get(self.cursor, self.cursor)
        canvas.draw_text("Travel to: "+cursor_label, (20, 425), 20, 'Black')
        canvas.draw_text("Arrows move - Space travels - Q closes", (20, 455), 18, 'Black')

        if self.kbd.select:
            self.kbd.select = False
            if self.cursor in visited_hubs:
                return self.cursor
        return None

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
