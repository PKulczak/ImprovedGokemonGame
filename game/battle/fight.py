import pygame
import time
import os
import json
from game.engine.image_cache import load_image
from game.engine import balance
from game.engine import sound
from game.engine.party_grid import PartyGrid, draw_party_slot
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

_ITEMS_PATH = '{}/Fight/Files/PlayerItems.json'.format(BASE_DIR)

#public (unlike the seen-pokemon helpers' leading underscore) - the overworld shop (ui.py's Shop)
#reads/writes the same PlayerItems.json outside of any battle. Loaded fresh each call - unlike
#load_seen_pokemon, nothing needs the mtime-cache dance since it's read/written by whichever of
#Fight/Shop is currently active, never both at once
def load_items():
    with open(_ITEMS_PATH, "r") as file:
        return json.load(file)

def save_items(items):
    with open(_ITEMS_PATH, "w") as file:
        json.dump(items, file, indent=2)

#display/iteration order for the item menu - cheapest ball first, Potion last. Also the order
#Fight._default_ball() picks from for the dedicated Catch button, so a routine catch spends the
#cheapest ball on hand instead of silently burning a rarer one the player might be saving
ITEM_ORDER = ["Poke Ball", "Great Ball", "Ultra Ball", "Potion"]
BALL_MULTIPLIERS = {"Poke Ball": 1.0, "Great Ball": 1.5, "Ultra Ball": 2.0}

class Fight:
    def __init__(self, monster_list, pokemon_list, keyboard, npc):
        self.mons_list = monster_list
        self.monster = monster_list[0]
        self.poke_list = pokemon_list
        #skips a fainted lead (e.g. it fainted in an earlier fight this session and hasn't been
        #healed since) and opens on the first Pokemon that can actually still battle, rather
        #than starting the fight on a dead one. Falls back to pokemon_list[0] if the whole party
        #is somehow fainted - shouldn't happen, since losing a fight already fully heals the
        #party before the player's back in the overworld to trigger a new one
        self.pokemon = next((p for p in pokemon_list if p.HP > 0), pokemon_list[0])
        self.count = balance.SHORT_MESSAGE_FRAMES
        #True is just a neutral default here - it no longer gates whether the player gets to
        #choose an action (see _resolve_state/_draw_resolve_turn below, which always show the
        #choose-action menu first regardless of speed). It's only still meaningful as the
        #trigger for _draw_resolve_monster_turn, the one remaining place that still bypasses a
        #speed check entirely: an item/potion use always resolves immediately, with the monster
        #getting an unconditional free follow-up turn after, same as before this change
        self.attack = True
        #the player's committed action for the current round (set once they confirm Attack/Run/
        #Catch, cleared once the round is fully resolved) - see _draw_resolve_turn for why a
        #round needs this instead of resolving the instant the player picks something: both
        #sides' actions are decided before either is revealed, then whoever's faster (checked
        #fresh every round, via self._player_first) goes first
        self.queued_inte = None
        self.queued_move = None
        self._actions_done = 0
        self._player_first = True
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
        self.items = load_items()
        self.item_menu = False
        self.item_grid = PartyGrid()
        #tallied here rather than touching Player directly - Fight doesn't otherwise know about
        #Player at all; game.py credits this to self.player.money once the fight ends, the same
        #place lives/HP already get applied post-fight
        self.money_earned = 0
        #picking "Attack" opens this move-choice sub-menu instead of resolving immediately -
        #left/right between the two moves (see Pokemon.moves), same left/right-to-highlight
        #convention as the top-level Attack/Catch/Run/Bag choice
        self.move_menu = False
        self.move_index = 0

        #which of the fight screen's states is active, dispatched via state_handlers instead of
        #a nested if/elif chain. Some flag combinations are known dead ends kept as-is rather
        #than "fixed" here - e.g. the catch-overflow confirm branch below never clears
        #kbd.select/change, so the very next frame falls through into the switch-branch of
        #bag_confirm too; count gets overwritten back to PLAYER_TURN_MESSAGE_FRAMES after every
        #resolve_action regardless of what fight() set it to.
        self.state_handlers = {
            "bag_browse": self._draw_bag_browse,
            "bag_confirm": self._draw_bag_confirm,
            "bag_cancel": self._draw_bag_cancel,
            "item_browse": self._draw_item_browse,
            "item_confirm": self._draw_item_confirm,
            "item_cancel": self._draw_item_cancel,
            "move_browse": self._draw_move_browse,
            "move_confirm": self._draw_move_confirm,
            "move_cancel": self._draw_move_cancel,
            "message": self._draw_message,
            "choose_action": self._draw_choose_action,
            "resolve_action": self._draw_resolve_action,
            "resolve_turn": self._draw_resolve_turn,
            "resolve_monster_turn": self._draw_resolve_monster_turn,
        }
        self.state = self._resolve_state()

    #derives the active state from the same flags draw() used to branch on inline. count > 0
    #(not != 0) since count is now a real-time countdown (see _draw_message) that can overshoot
    #past exactly zero in one dt step, rather than an integer that only ever decremented to it.
    #choose_action is always reachable here regardless of speed - a faster monster no longer
    #gets an automatic free attack before the player even picks something (see _draw_resolve_turn)
    def _resolve_state(self):
        if self.move_menu:
            if self.kbd.quit:
                return "move_cancel"
            if self.kbd.select:
                return "move_confirm"
            return "move_browse"
        if self.item_menu:
            if self.kbd.quit:
                return "item_cancel"
            if self.kbd.select:
                return "item_confirm"
            return "item_browse"
        if self.change:
            if self.kbd.quit:
                return "bag_cancel"
            if self.kbd.select:
                return "bag_confirm"
            return "bag_browse"
        if self.run or self.count > 0:
            return "message"
        if self.queued_inte is not None:
            return "resolve_turn"
        if not self.attack:
            return "resolve_monster_turn"
        return "resolve_action" if self.kbd.select else "choose_action"

    #states that replace the whole battle scene with a menu, rather than drawing over it
    _MENU_STATES = ("bag_browse", "bag_confirm", "bag_cancel", "item_browse", "item_confirm", "item_cancel")

    #responsible for drawing the fight
    def draw(self, canvas, dt):
        self.state = self._resolve_state()
        if self.state not in self._MENU_STATES:
            self._draw_scene(canvas, dt)
        self.state_handlers[self.state](canvas, dt)

    #the fight background, both combatants' name/HP/level, and both sprites - shared by every
    #state except the bag/switch menu (which replaces this whole scene with the party list)
    def _draw_scene(self, canvas, dt):
        canvas.draw_image(self.image, (375,250), (750,500), (400,240), (735,490))
        canvas.draw_text(self.monster.name, (155, 80), 25, 'Black')
        canvas.draw_text("HP:"+str(self.monster.HP)+"   Lvl:"+str(self.monster.lvl), (190, 110), 25, 'Black')
        canvas.draw_text(self.pokemon.name, (530, 255), 25, 'Black')
        canvas.draw_text("HP:"+str(self.pokemon.HP)+"/"+str(self.pokemon.fullhp)+"  Lvl:"+str(self.pokemon.lvl), (530, 295), 25, 'Black')
        self.pokemon.draw(canvas, dt)
        self.monster.draw(canvas, dt)

    #shows the escape message, or the previous turn's result message with its attack-effect
    #animation, counting self.count down either way
    def _draw_message(self, canvas, dt):
        if self.run:
            canvas.draw_text(self.info, (120, 415), 25, 'White')
            self.count = self.count - dt
        else:
            if not self.first:
                if self.attack:
                    self.monster.draw_effect(canvas)
                else:
                    self.pokemon.draw_effect(canvas)
            canvas.draw_text(self.info, (120, 415), 25, 'White')
            self.count = self.count - dt
        #lets the player fast-forward this message's countdown instead of waiting it out - the
        #same select key already used to confirm menu choices, safe to consume here since no
        #other state handler reads it while "message" is the active state
        if self.kbd.select:
            self.count = 0
            self.kbd.select = False

    #resets the attack-effect sprite frame and clears the one-time "don't show an effect yet"
    #flag - runs once every time a message finishes, before the next choice/resolution is made
    def _reset_effect_frames(self):
        self.monster.frame_index1[1] = 0
        self.pokemon.frame_index1[1] = 0
        self.first = False

    #shows the Attack/Catch/Run/Bag menu and reads the player's choice. dt is unused here and in
    #every other state handler below - only _draw_scene/_draw_message have their own timing -
    #but all of state_handlers is invoked through one uniform (canvas, dt) call in draw()
    def _draw_choose_action(self, canvas, dt):
        self._reset_effect_frames()
        self.inte = self.interact(self.inte, canvas)

    #the frame the player confirms an action - either opens the move/bag menu, or (Run/Catch)
    #commits the action for _draw_resolve_turn to resolve once speed order is decided, rather
    #than resolving it immediately here
    def _draw_resolve_action(self, canvas, dt):
        self._reset_effect_frames()
        if self.inte == 1:
            self.move_menu = True
            self.move_index = 0
            self.kbd.select = False
        elif self.inte <=3 :
            self.kbd.select = False
            self.queued_inte = self.inte
            self.queued_move = None
        elif self.inte == 4:
            self.item_menu = True
            self.kbd.select = False

    #the monster's automatic follow-up after an item/potion use, which (unlike Attack/Run/Catch)
    #still always resolves the item immediately and unconditionally gives the monster the next
    #turn, regardless of speed - see the comment on self.attack in __init__
    def _draw_resolve_monster_turn(self, canvas, dt):
        self._reset_effect_frames()
        self.fight(self.pokemon, self.monster, self.inte, canvas)
        self.count = balance.MONSTER_TURN_MESSAGE_FRAMES

    #a round's resolution, once the player has committed an action (self.queued_inte) - whichever
    #side is faster (checked fresh each round via self.pokemon.SPD/self.monster.SPD) resolves
    #first, automatically, with no further input; if the fight is still going normally afterward,
    #the other side's action (the monster's AI move, or the player's own already-chosen one)
    #follows the same way. This is what makes both sides effectively choose blind - the player's
    #choice is locked in before they see what a faster opponent does, not after.
    #
    #Runs more than twice in a row if fight() itself needs extra bookkeeping-only cycles after a
    #fatal hit (see its own comments on the win/lose message needing an extra cycle) - "both
    #still alive" is the actual signal a round is over, not "two actions happened", since the
    #second action might only be bookkeeping rather than a real attack.
    def _draw_resolve_turn(self, canvas, dt):
        self._reset_effect_frames()
        if self._actions_done == 0:
            self._player_first = self.pokemon.SPD >= self.monster.SPD
            resolving_player = self._player_first
        else:
            resolving_player = not self._player_first
        self.attack = resolving_player
        self.fight(self.pokemon, self.monster, self.queued_inte, canvas, move=self.queued_move)
        self.count = balance.PLAYER_TURN_MESSAGE_FRAMES if resolving_player else balance.MONSTER_TURN_MESSAGE_FRAMES
        self._actions_done += 1

        both_alive = self.pokemon.HP > 0 and self.monster.HP > 0
        if self.end or self.change or (self._actions_done >= 2 and both_alive):
            self.queued_inte = None
            self.queued_move = None
            self._actions_done = 0
            self.attack = True

    #picking a move - up/down toggles between the two, matching the vertical stack they're
    #drawn in (unlike the top-level Attack/Catch/Run/Bag choice, these aren't side by side)
    def _draw_move_browse(self, canvas, dt):
        move1, move2 = self.pokemon.moves
        canvas.draw_text("Choose a move for "+self.pokemon.name+":", (120, 415), 22, 'White')
        col1 = "White" if self.move_index == 0 else "Grey"
        col2 = "White" if self.move_index == 1 else "Grey"
        canvas.draw_text(move1["name"]+" (Pow "+str(move1["power"])+")", (450, 400), 20, col1)
        canvas.draw_text(move2["name"]+" (Pow "+str(move2["power"])+")", (450, 435), 20, col2)
        if self.kbd.up:
            self.move_index = 0
        elif self.kbd.down:
            self.move_index = 1

    #confirms the highlighted move - commits it for _draw_resolve_turn, same as Run/Catch above
    def _draw_move_confirm(self, canvas, dt):
        self.kbd.select = False
        self.move_menu = False
        self.queued_inte = 1
        self.queued_move = self.pokemon.moves[self.move_index]

    #cancels the move menu, back to Attack/Catch/Run/Bag with no turn spent
    def _draw_move_cancel(self, canvas, dt):
        self.move_menu = False

    #browsing the party grid (the bag hotkey, or a forced switch/catch-overflow prompt) - same
    #per-slot layout (icon, name, level, HP) as the overworld party-reorder screen (ui.py's
    #TeamOrder), via the shared draw_party_slot. A fainted (HP 0) Pokemon can't be sent out to
    #battle, so its name/HP are DarkRed (rather than the move-menu's Grey - the party grid's
    #own tile backdrop is already light grey, so plain Grey text nearly disappears against it)
    #and its icon is greyed out (draw_party_slot's own doing) to match _draw_bag_confirm below
    #refusing to select it
    def _draw_bag_browse(self, canvas, dt):
        self.first = self.grid.update(self.kbd, self.first)
        self.grid.draw_highlight(canvas, self.bag, self.light)
        for i, mon in enumerate(self.poke_list):
            colour = 'DarkRed' if mon.HP <= 0 else 'Black'
            name_x = 270 if i < 3 else 520
            row_y = 130+((i if i < 3 else i-3)*120)
            draw_party_slot(canvas, mon, name_x, row_y, colour)

    #confirms the currently-highlighted party slot
    def _draw_bag_confirm(self, canvas, dt):
        choice = self.grid.selected_index()
        if self.catch:
            #swapping OUT an existing party member for the newly caught one - a fainted member
            #is a perfectly sensible (often preferred) pick here, so no HP restriction
            self.monster.pos = self.pokemon.pos
            self.monster.pos1 = self.pokemon.pos1
            self.poke_list[choice] = self.monster
            self.mons_list.remove(self.monster)
            if len(self.mons_list) == 0:
                self.end = True
            else:
                #no speed recompute needed - _draw_resolve_turn checks it fresh every round
                self.monster = self.mons_list[0]
            self.catch = False
        else:
            #sending this Pokemon out to battle - a fainted (HP 0) one can't fight, so the
            #selection is simply ignored (same "stay on the menu, nothing happens" pattern as
            #an empty item slot) rather than letting a 0-HP Pokemon become the active battler
            if len(self.poke_list)-1>=choice and self.poke_list[choice].HP > 0:
                self.pokemon = self.poke_list[choice]
                self.change = False
            self.kbd.select = False

    #cancels the bag/switch menu
    def _draw_bag_cancel(self, canvas, dt):
        self.change = False
        if self.catch:
            self.info = "You release it again."
            self.catch = False

    #the cheapest ball currently in stock (Poke > Great > Ultra) - what the dedicated Catch
    #button throws, so a routine catch doesn't silently spend a rarer ball the player is saving
    def _default_ball(self):
        for name in ("Poke Ball", "Great Ball", "Ultra Ball"):
            if self.items.get(name, 0) > 0:
                return name, BALL_MULTIPLIERS[name]
        return None, None

    #one line per item slot: "<name> x<count>" for each entry in ITEM_ORDER, plus a trailing
    #"Switch Pokemon" slot that hands off to the existing party-switch grid unchanged
    def _item_labels(self):
        labels = [name+" x"+str(self.items.get(name, 0)) for name in ITEM_ORDER]
        labels.append("Switch Pokemon")
        return labels

    #resolves a catch attempt with the given ball - shared by the dedicated Catch button
    #(cheapest ball owned, auto-picked) and manually throwing a specific tier from the item menu.
    #Consumes the ball regardless of outcome, same as mainline - a failed throw still costs you.
    def _attempt_catch(self, ball_name, ball_multiplier):
        self.items[ball_name] -= 1
        save_items(self.items)
        monster = self.monster
        hp_fraction = monster.HP / monster.fullhp
        if not self.npc and battle_rules.catch_succeeds(ball_multiplier, hp_fraction):
            sound.play_sfx("catch")
            if len(self.poke_list) < balance.MAX_PARTY_SIZE:
                self.info = "Caught with a "+ball_name+"!"
                monster.pos = self.pokemon.pos
                monster.pos1 = self.pokemon.pos1
                self.poke_list.append(monster)
                self.mons_list.remove(monster)
                _mark_pokemon_seen(monster.name)
                if len(self.mons_list) == 0:
                    self.count = 0
                    self.end = True
                else:
                    #no speed recompute needed - _draw_resolve_turn checks it fresh every round
                    self.monster = self.mons_list[0]
            else:
                self.change = True
                self.catch = True
        else:
            self.info = "Catch failed!" if self.npc else ball_name+" failed to catch it!"
            self.attack = False
            sound.play_sfx("catch_fail")

    #browsing the item menu - Potion/ball counts plus a Switch Pokemon entry, same 6-slot grid
    #backdrop as the old party-switch-only Bag menu
    def _draw_item_browse(self, canvas, dt):
        self.first = self.item_grid.update(self.kbd, self.first)
        self.item_grid.draw_highlight(canvas, self.bag, self.light)
        for i, label in enumerate(self._item_labels()):
            if i < 3:
                canvas.draw_text(label, (270, 145+(i*120)), 22, 'Black')
            else:
                canvas.draw_text(label, (520, 145+(i-3)*120), 22, 'Black')

    #confirms the currently-highlighted item slot
    def _draw_item_confirm(self, canvas, dt):
        labels = self._item_labels()
        index = self.item_grid.selected_index()
        self.kbd.select = False
        if index >= len(labels):
            return
        if index == len(ITEM_ORDER):
            #"Switch Pokemon" - hand off to the existing party-switch flow unchanged
            self.item_menu = False
            self.change = True
            return
        name = ITEM_ORDER[index]
        if name == "Potion":
            if self.items.get(name, 0) > 0 and self.pokemon.HP < self.pokemon.fullhp:
                self.items[name] -= 1
                save_items(self.items)
                self.pokemon.HP = min(self.pokemon.fullhp, self.pokemon.HP + balance.POTION_HEAL_AMOUNT)
                self.info = "Used a Potion on "+self.pokemon.name+"!"
                self.item_menu = False
                self.attack = False
                self.count = balance.PLAYER_TURN_MESSAGE_FRAMES
            #else: no potions left, or already at full HP - stay on the menu, nothing happens
        elif self.items.get(name, 0) > 0:
            self.item_menu = False
            self._attempt_catch(name, BALL_MULTIPLIERS[name])
            self.count = balance.PLAYER_TURN_MESSAGE_FRAMES
        #else: that ball's stock is empty - stay on the menu, nothing happens

    #cancels the item menu, no turn spent
    def _draw_item_cancel(self, canvas, dt):
        self.item_menu = False

    #a trainer's Pokemon picks whichever of its moves would deal the most damage against the
    #player's current Pokemon (power and type effectiveness both factored in via the same
    #formula the player's own attacks use) instead of always leading with its first move - wild
    #Pokemon stay simple (always moves[0]) so trainer fights start to feel distinct from wild
    #encounters now that there's more than one move to choose between (item 5)
    def _choose_monster_move(self, monster, pokemon):
        if not self.npc:
            return monster.moves[0]
        return max(monster.moves, key=lambda m: battle_rules.type_effective_damage(
            monster.ATK, pokemon.DEF, m["type"], pokemon.effect_img, power=m["power"]))

    #does all the calculations for the fight. move is the player's chosen move (inte == 1 only) -
    #the monster's own move choice is _choose_monster_move's job (trainers pick the strongest
    #option, wild Pokemon always lead with their first move)
    def fight(self, pokemon, monster, inte, canvas, move=None):
        if pokemon.HP > 0 and monster.HP > 0:
            if not self.attack:
                monster_move = self._choose_monster_move(monster, pokemon)
                hp_before = pokemon.HP
                pokemon.HP = max(0, pokemon.HP - battle_rules.type_effective_damage(
                    monster.ATK, pokemon.DEF, monster_move["type"], pokemon.effect_img,
                    power=monster_move["power"]))
                sound.play_sfx("hit")
                #only warns about the player's own Pokemon, and only on the hit that actually
                #crosses the threshold - staying below it for several turns in a row isn't a
                #fresh warning each time
                low_hp_now = pokemon.HP / pokemon.fullhp <= balance.LOW_HP_WARNING_FRACTION
                low_hp_before = hp_before / pokemon.fullhp <= balance.LOW_HP_WARNING_FRACTION
                if low_hp_now and not low_hp_before and pokemon.HP > 0:
                    sound.play_sfx("low_hp")
                self.info = monster.name+" used "+monster_move["name"]+"!"
                self.attack = True
            else:
                if inte == 1:
                    monster.HP = max(0, monster.HP - battle_rules.type_effective_damage(
                        pokemon.ATK, monster.DEF, move["type"], monster.effect_img,
                        power=move["power"]))
                    sound.play_sfx("hit")
                    self.info = pokemon.name+" used "+move["name"]+"!"
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
                    if self.npc:
                        self.info = "Catch failed!"
                        self.attack = False
                    else:
                        ball_name, ball_multiplier = self._default_ball()
                        if ball_name is None:
                            self.info = "No Poke Balls left!"
                            self.attack = False
                        else:
                            self._attempt_catch(ball_name, ball_multiplier)
                                             
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
                if not self.npc:
                    #wild Pokemon only - beating a trainer's Pokemon doesn't pay out, matching
                    #the plan's explicit ask ("money from beating wild pokemon")
                    self.money_earned += balance.WILD_DEFEAT_BASE_MONEY + balance.WILD_DEFEAT_MONEY_PER_LEVEL * monster.lvl
                if pokemon.exp >= pokemon.max_exp:
                    if pokemon.lvl <= balance.MAX_LEVEL:
                        pokemon.lvl += 1
                        base_stats = POKEDEX[pokemon.name]
                        (pokemon.ATK, pokemon.DEF, pokemon.fullhp, pokemon.SPD,
                         pokemon.max_exp, pokemon.give_exp) = battle_rules.level_up_stats(
                            base_stats["ATK"], base_stats["DEF"], base_stats["fullhp"],
                            base_stats.get("SPD", balance.DEFAULT_SPD), pokemon.lvl)
                        sound.play_sfx("level_up")
                        #a small, renewable trickle of the cheapest ball tier on top of the
                        #Pokecenter shop (ui.py's Shop) - keeps a floor of catch resources even
                        #before the player has any money
                        self.items["Poke Ball"] = self.items.get("Poke Ball", 0) + 1
                        save_items(self.items)
                    pokemon.exp -= pokemon.max_exp
                    pokemon.HP = pokemon.fullhp

                _mark_pokemon_seen(monster.name)

                self.mons_list.remove(monster)
                if not(len(self.mons_list) == 0):
                    #no speed recompute needed - _draw_resolve_turn checks it fresh every round
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
        self.SPD = base_stats.get("SPD", balance.DEFAULT_SPD)
        effect_img = base_stats["effect_img"]
        self.effect_img = effect_img
        self.moves = base_stats["moves"]
        row = base_stats["row"]
        self.count = 0
        self._prev_count = 0

        #pokemon scaling
        self.lvl = lvl
        self.exp = exp
        (self.ATK, self.DEF, self.fullhp, self.SPD,
         self.max_exp, self.give_exp) = battle_rules.level_up_stats(self.ATK, self.DEF, self.fullhp, self.SPD, self.lvl)
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

    def draw(self, canvas, dt):
            canvas.draw_image(self.image,
                              [self.frame_center[0] + self.frame_index[0] * self.frame_dim[0],
                               self.frame_center[1] + self.frame_index[1] * self.frame_dim[1]],
                              self.frame_dim, [self.pos[0], self.pos[1]],
                              [self.frame_dim[0]*3,self.frame_dim[1]*3])
            self._prev_count = self.count
            self.count += dt
            if self._cadence_crossed(balance.POKEMON_IDLE_ANIMATION_CADENCE):
                self.next_frame()

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

    #true once per real-time interval of `cadence` frame-equivalents since draw() last advanced
    #self.count - a boundary-crossing check rather than the exact modulo-equality this replaced,
    #so it still fires correctly even when a single dt step skips straight past a boundary
    def _cadence_crossed(self, cadence):
        return int(self._prev_count // cadence) != int(self.count // cadence)

    def draw_effect(self, canvas):
        canvas.draw_image(self.effectimg,
                          [self.frame_center1[0] + self.frame_index1[0] * self.frame_dim1[0],
                           self.frame_center1[1] + self.frame_index1[1] * self.frame_dim1[1]],
                          self.frame_dim1, [self.pos1[0], self.pos1[1]],
                          [self.frame_dim1[0]+35,self.frame_dim1[1]+35])
        if self._cadence_crossed(balance.ATTACK_EFFECT_ANIMATION_CADENCE):
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
            sound.play_sfx("select")

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

