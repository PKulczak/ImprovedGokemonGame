"""The real battle scene, wired to the battle-mechanics package.

Consumes only `battle.events.BattleEvent` objects out of `Battle.run_turn()`
(never reaches into Battle internals for rendering) and pushes plain text
messages + a couple of simple menus on top of a minimal battle backdrop.
"""

import pygame

from engine.scene import Scene
from engine.menu import ListMenu
from battle.battle_state import Battle, BattleSide, Battler, MoveAction, SwitchAction
from battle.schemas import AITier, TrainerPokemonPreset
from battle.ai import choose_move
from battle.catching import attempt_catch_with_item
from battle.experience import check_level_up_evolution, apply_evolution


class Phase:
    MESSAGE = "message"
    MENU = "menu"
    MOVE_SELECT = "move_select"
    SWITCH_SELECT = "switch_select"
    BAG_SELECT = "bag_select"
    DONE = "done"


BALL_NAMES = ("Poke Ball", "Great Ball", "Ultra Ball", "Master Ball")


def _species_by_dex():
    from data.species import SPECIES
    return {s.dex_number: s for s in SPECIES.values()}


class BattleScene(Scene):
    def on_enter(self, wild=None, trainer=None, **kwargs):
        self.wild = wild
        self.trainer_npc = trainer
        self.rng = self.app.rng

        party = self.app.state.party_manager.party
        lead = self.app.state.party_manager.first_healthy_index() or 0
        self.player_side = BattleSide(
            active=Battler(pokemon=party[lead]),
            bench=[m for i, m in enumerate(party) if i != lead],
        )

        self.trainer_data = None
        if trainer is not None:
            from data.trainers import TRAINERS
            self.trainer_data = TRAINERS[trainer.trainer_id]
            team = [preset.instantiate(self.rng) for preset in self.trainer_data.team]
            self.ai_tier = self.trainer_data.ai_tier
            intro = f"{self.trainer_data.trainer_class} {self.trainer_data.name} wants to battle!"
        else:
            from data.species import SPECIES
            species = SPECIES[wild["species"]]
            preset = TrainerPokemonPreset(species=species, level=wild["level"])
            team = [preset.instantiate(self.rng)]
            self.ai_tier = AITier.WILD
            intro = f"A wild {team[0].display_name} appeared!"
            self.app.state.pokedex_seen.add(species.dex_number)

        self.enemy_side = BattleSide(active=Battler(pokemon=team[0]), bench=team[1:])
        self.battle = Battle(self.player_side, self.enemy_side, self.rng, trainer_battle=trainer is not None)

        self.phase = Phase.MESSAGE
        self.queue = [intro]
        self._after_queue = self._show_menu
        self.menu = None
        self.result = {}
        self._battle_over_handled = False

    # ------------------------------------------------------------------ #
    # Message queue
    # ------------------------------------------------------------------ #

    def _say(self, texts, then):
        self.queue.extend(t for t in texts if t)
        self._after_queue = then
        self.phase = Phase.MESSAGE
        if not self.queue:
            self._advance_queue()

    def _advance_queue(self):
        if self.queue:
            self.queue.pop(0)
        if self.queue:
            return
        callback, self._after_queue = self._after_queue, None
        if callback:
            callback()

    def _event_text(self, e):
        cls = type(e).__name__
        table = {
            "MoveUsed": lambda: f"{e.pokemon_name} used {e.move_name}!",
            "Missed": lambda: f"{e.pokemon_name}'s attack missed!",
            "CriticalHit": lambda: "A critical hit!",
            "HealDealt": lambda: f"{e.pokemon_name} recovered some HP!",
            "StatusInflicted": lambda: f"{e.pokemon_name} was afflicted with {e.status}!",
            "StatusCured": lambda: f"{e.pokemon_name}'s {e.status} was cured!",
            "StatStageChanged": lambda: f"{e.pokemon_name}'s {e.stat} {'rose' if e.delta > 0 else 'fell'}!",
            "Fainted": lambda: f"{e.pokemon_name} fainted!",
            "SwitchedIn": lambda: f"{e.pokemon_name} was sent out!",
            "WeatherChanged": lambda: f"The weather turned to {e.weather}!",
            "WeatherEnded": lambda: f"The {e.weather} subsided.",
            "Flinched": lambda: f"{e.pokemon_name} flinched!",
            "ConfusionSelfHit": lambda: f"{e.pokemon_name} hurt itself in its confusion!",
            "FullyParalyzed": lambda: f"{e.pokemon_name} is paralyzed! It can't move!",
            "WokeUp": lambda: f"{e.pokemon_name} woke up!",
            "Thawed": lambda: f"{e.pokemon_name} thawed out!",
            "ItemConsumed": lambda: f"{e.pokemon_name}'s {e.item_name} activated!",
            "Message": lambda: e.text,
        }
        fn = table.get(cls)
        return fn() if fn else None

    # ------------------------------------------------------------------ #
    # Turn submission
    # ------------------------------------------------------------------ #

    def _submit_turn(self, player_action):
        enemy_battler = self.enemy_side.active
        enemy_move = None
        if not enemy_battler.pokemon.is_fainted():
            enemy_move = choose_move(self.ai_tier, enemy_battler, self.player_side.active, self.rng)
        enemy_action = None
        if enemy_move is not None:
            for i, lm in enumerate(enemy_battler.pokemon.moves):
                if lm.move is enemy_move:
                    enemy_action = MoveAction(move_index=i)
                    break

        events = self.battle.run_turn(player_action, enemy_action)
        texts = [t for t in (self._event_text(e) for e in events) if t]
        self._check_evolutions()
        self._say(texts, self._after_turn)

    def _check_evolutions(self):
        for battler in (self.player_side.active, self.enemy_side.active):
            mon = battler.pokemon
            rule = check_level_up_evolution(mon)
            if rule is not None:
                old_name = mon.display_name
                new_species = apply_evolution(mon, rule, _species_by_dex())
                self.queue.append(f"{old_name} evolved into {new_species.name}!")

    def _after_turn(self):
        if self.battle.is_over():
            self._finish_battle()
        else:
            self._show_menu()

    def _finish_battle(self):
        if self._battle_over_handled:
            self._end_scene()
            return
        self._battle_over_handled = True
        winner = self.battle.winner()
        texts = []
        result = {"outcome": winner}
        if winner == "player":
            if self.trainer_npc is not None:
                texts.append(f"You defeated {self.trainer_data.name}!")
                result["trainer_defeated"] = self.trainer_npc
                result["prize_money"] = self.trainer_data.prize_money
                self.app.state.money += self.trainer_data.prize_money
            else:
                texts.append(f"{self.enemy_side.active.pokemon.display_name} fainted!" if self.enemy_side.active.pokemon.is_fainted() else "You won the battle!")
        elif winner == "enemy":
            texts.append("You have no more Pokemon that can fight!")
        self.result = result
        self._say(texts, self._end_scene)

    def _end_scene(self):
        self.app.scene_stack.pop(result=self.result or {"outcome": self.battle.winner()})

    # ------------------------------------------------------------------ #
    # Menus
    # ------------------------------------------------------------------ #

    def _show_menu(self):
        options = ["Fight", "Pokemon", "Bag"]
        if self.wild is not None:
            options.append("Run")
        self.menu = ListMenu(options)
        self.phase = Phase.MENU

    def _show_moves(self):
        mon = self.player_side.active.pokemon
        labels = [f"{lm.move.name} ({lm.current_pp}/{lm.move.pp})" for lm in mon.moves]
        if not labels:
            labels = ["Struggle"]
        self.menu = ListMenu(labels)
        self.phase = Phase.MOVE_SELECT

    def _show_switch(self):
        labels = [f"{m.display_name} Lv{m.level}" for m in self.player_side.bench]
        if not labels:
            self._say(["There's no one else to send out!"], self._show_menu)
            return
        self.menu = ListMenu(labels)
        self.phase = Phase.SWITCH_SELECT

    def _show_bag(self):
        if self.wild is None:
            self._say(["You can't use items on someone else's Pokemon!"], self._show_menu)
            return
        inv = self.app.state.inventory
        owned = [name for name in BALL_NAMES if inv.has(name, 1)]
        if not owned:
            self._say(["You don't have any Poke Balls!"], self._show_menu)
            return
        self.menu = ListMenu(owned)
        self.phase = Phase.BAG_SELECT

    # ------------------------------------------------------------------ #
    # Input
    # ------------------------------------------------------------------ #

    def handle_input(self, input_state):
        if self.phase == Phase.MESSAGE:
            if input_state.was_pressed("CONFIRM"):
                self._advance_queue()
            return

        if self.menu is None:
            return
        if input_state.was_pressed("UP"):
            self.menu.move(-1)
        elif input_state.was_pressed("DOWN"):
            self.menu.move(1)
        elif input_state.was_pressed("CANCEL") and self.phase != Phase.MENU:
            self._show_menu()
        elif input_state.was_pressed("CONFIRM"):
            self._confirm()

    def _confirm(self):
        if self.phase == Phase.MENU:
            choice = self.menu.selected
            if choice == "Fight":
                self._show_moves()
            elif choice == "Pokemon":
                self._show_switch()
            elif choice == "Bag":
                self._show_bag()
            elif choice == "Run":
                self._say(["Got away safely!"], self._run_away)
        elif self.phase == Phase.MOVE_SELECT:
            self._submit_turn(MoveAction(move_index=self.menu.index))
        elif self.phase == Phase.SWITCH_SELECT:
            self._submit_turn(SwitchAction(bench_index=self.menu.index))
        elif self.phase == Phase.BAG_SELECT:
            self._attempt_catch(self.menu.selected)

    def _run_away(self):
        self.result = {"outcome": "ran"}
        self.app.scene_stack.pop(result=self.result)

    def _attempt_catch(self, ball_name):
        from data.items import ITEMS
        item = ITEMS[ball_name]
        self.app.state.inventory.use(ball_name, 1)
        target = self.enemy_side.active.pokemon
        caught = attempt_catch_with_item(target, item, self.rng)
        if caught:
            self.app.state.pokedex_caught.add(target.species.dex_number)
            self.app.state.party_manager.add(target)
            self.result = {"outcome": "caught"}
            self._say([f"Gotcha! {target.display_name} was caught!"], self._end_scene)
        else:
            self._say([f"Oh no! {target.display_name} broke free!"], lambda: self._submit_turn(None))

    # ------------------------------------------------------------------ #
    # Update / draw
    # ------------------------------------------------------------------ #

    def update(self, dt):
        pass

    SPRITE_SIZE = 40

    def _draw_hp_bar(self, surface, pos, current, maximum, width=90, height=6):
        x, y = pos
        pygame.draw.rect(surface, (60, 60, 60), (x, y, width, height))
        frac = 0 if maximum <= 0 else max(0.0, min(1.0, current / maximum))
        color = (60, 200, 90) if frac > 0.5 else (230, 190, 40) if frac > 0.2 else (220, 60, 60)
        pygame.draw.rect(surface, color, (x, y, int(width * frac), height))
        pygame.draw.rect(surface, (20, 20, 20), (x, y, width, height), 1)

    def _draw_sprite(self, surface, relative_path, pos):
        try:
            img = self.app.assets.image(relative_path)
        except Exception:
            return
        scaled = pygame.transform.smoothscale(img, (self.SPRITE_SIZE, self.SPRITE_SIZE))
        surface.blit(scaled, pos)

    def draw(self, surface):
        surface.fill((18, 18, 48))
        font = self.app.assets.font(10)
        player_mon = self.player_side.active.pokemon
        enemy_mon = self.enemy_side.active.pokemon

        surface.blit(font.render(
            f"{enemy_mon.display_name} Lv{enemy_mon.level}", True, (255, 255, 255)), (10, 4))
        self._draw_hp_bar(surface, (10, 18), enemy_mon.current_hp, enemy_mon.get_stats().hp)
        self._draw_sprite(surface, f"pokemon/{enemy_mon.species.name.lower()}/front.png",
                           (surface.get_width() - self.SPRITE_SIZE - 14, 16))

        self._draw_sprite(surface, f"pokemon/{player_mon.species.name.lower()}/back.png",
                           (10, 74))
        surface.blit(font.render(
            f"{player_mon.display_name} Lv{player_mon.level}", True, (255, 255, 255)), (60, 78))
        surface.blit(font.render(
            f"HP {player_mon.current_hp}/{player_mon.get_stats().hp}", True, (255, 255, 255)), (60, 90))
        self._draw_hp_bar(surface, (60, 102), player_mon.current_hp, player_mon.get_stats().hp)

        box = pygame.Rect(4, surface.get_height() - 46, surface.get_width() - 8, 42)
        pygame.draw.rect(surface, (250, 250, 250), box)
        pygame.draw.rect(surface, (20, 20, 20), box, 2)

        if self.phase == Phase.MESSAGE:
            text = self.queue[0] if self.queue else ""
            surface.blit(font.render(text, True, (20, 20, 20)), (box.left + 6, box.top + 6))
        elif self.menu is not None:
            self.menu.draw(surface, self.app.assets, (box.left + 6, box.top + 3), font_size=10, line_height=10,
                            color=(20, 20, 20), selected_color=(180, 40, 40))
