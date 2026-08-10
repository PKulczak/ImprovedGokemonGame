import os
import json
from game.engine.image_cache import load_image
from game.engine import balance
from game.engine.party_grid import PartyGrid
from game.battle.fight import POKEDEX, load_seen_pokemon, seen_pokemon_version

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

#creates the Gokedex
class Pokedex:
    def __init__(self, kbd):
        self.player_pokedex = []
        self.pokedex = []
        self.kbd = kbd
        self.first = True
        self.poke_list =[]
        self.index = 0
        self.grid = PartyGrid(on_page=self._turn_page)
        self.bag = load_image('{}/Fight/Other/bag.png'.format(BASE_DIR))
        self.light = load_image('{}/Fight/Other/highlight.png'.format(BASE_DIR))
        #forces the first draw() to build self.pokedex, since no real version is ever -1
        self._built_from_version = -1

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
            #rebuilds the paginated ?????/name display list - only needed when the seen-list
            #itself changed, not every frame the Gokedex screen happens to be open
            self.pokedex = []
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
            self._built_from_version = version
        #draws gokedex
        self.poke_list = self.pokedex[self.index]
        self.first = self.grid.update(self.kbd, self.first)
        self.grid.draw_highlight(canvas, self.bag, self.light)
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
        self.txtbox = load_image('{}/Text/box.png'.format(BASE_DIR))
        self.alltxt = [line.format(player_name=player.name) for line in dialogue_lines(txtfile)]
        self.num_lines = len(self.alltxt)

    def draw(self, canvas):
        if self.display:
            if self.box:
                canvas.draw_image(self.txtbox, (400,75), (800,150), (400,405), (800,150))
            canvas.draw_text(self.alltxt[self.count], self.pos, 20, 'White')


        self.clock.tick()
        move_on = self.clock.transition(balance.DIALOGUE_LINE_FRAMES)
        if move_on:
            self.count += 1
            if self.count >= self.num_lines:
                self.display = False
