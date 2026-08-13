from engine.scene import Scene
from engine.menu import ListMenu


class PartyMenuScene(Scene):
    """Serves both the pause-menu context (mode="pause") and mid-battle
    switching (mode="battle_switch", read back via pop(result=party_index))."""

    blocks_update_below = True
    draws_below = True

    def on_enter(self, mode="pause", **kwargs):
        self.mode = mode
        party = self.app.state.party_manager.party
        labels = [f"{mon.display_name} Lv{mon.level}" for mon in party] or ["(empty)"]
        self.menu = ListMenu(labels)

    def handle_input(self, input_state):
        if input_state.was_pressed("UP"):
            self.menu.move(-1)
        elif input_state.was_pressed("DOWN"):
            self.menu.move(1)
        elif input_state.was_pressed("CANCEL"):
            self.app.scene_stack.pop(result=None)
        elif input_state.was_pressed("CONFIRM"):
            party = self.app.state.party_manager.party
            if not party:
                return
            if self.mode == "battle_switch":
                self.app.scene_stack.pop(result=self.menu.index)

    def update(self, dt):
        pass

    def draw(self, surface):
        surface.fill((235, 235, 245))
        font = self.app.assets.font(14)
        party = self.app.state.party_manager.party
        if not party:
            surface.blit(font.render("No Pokemon in your party yet.", True, (20, 20, 20)), (10, 10))
            return
        self.menu.draw(surface, self.app.assets, (10, 10), color=(20, 20, 20), selected_color=(180, 40, 40))

        mon = party[self.menu.index]
        detail_y = 10 + len(party) * 16 + 10
        stats = mon.get_stats()
        type_label = mon.species.type1.value
        if mon.species.type2:
            type_label += f"/{mon.species.type2.value}"
        lines = [
            f"{mon.display_name}  Lv{mon.level}  {type_label}",
            f"HP {mon.current_hp}/{stats.hp}   Atk {stats.attack}  Def {stats.defense}",
            f"SpA {stats.sp_atk}  SpD {stats.sp_def}  Spe {stats.speed}",
            f"Ability: {mon.ability.name}   Nature: {mon.nature.name}",
            "Moves: " + (", ".join(lm.move.name for lm in mon.moves) if mon.moves else "-"),
        ]
        for i, line in enumerate(lines):
            surface.blit(font.render(line, True, (20, 20, 20)), (10, detail_y + i * 16))
