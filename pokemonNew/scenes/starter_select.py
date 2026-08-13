from engine.scene import Scene
from engine.menu import ListMenu


class StarterSelectScene(Scene):
    def on_enter(self, **kwargs):
        self.starters = {}
        self.error = None
        try:
            from data.starters import STARTERS
            self.starters = STARTERS
        except ImportError:
            self.error = "Starters not available yet."
        self.menu = ListMenu(list(self.starters.keys())) if self.starters else None

    def handle_input(self, input_state):
        if self.menu is None:
            return
        if input_state.was_pressed("LEFT"):
            self.menu.move(-1)
        elif input_state.was_pressed("RIGHT"):
            self.menu.move(1)
        elif input_state.was_pressed("CONFIRM"):
            self._confirm()

    def _confirm(self):
        name = self.menu.selected
        preset = self.starters[name]
        mon = preset.instantiate(self.app.rng)
        self.app.state.party_manager.add(mon)
        self.app.state.pokedex_seen.add(mon.species.dex_number)
        self.app.state.pokedex_caught.add(mon.species.dex_number)
        self.app.state.story_flags.set("starter_choice", name)
        self._grant_starting_items()
        from scenes.overworld import OverworldScene
        self.app.scene_stack.replace(
            OverworldScene(self.app),
            map_id="sagewood_town",
            spawn=(5, 5),
            facing="DOWN",
        )

    def _grant_starting_items(self):
        inv = self.app.state.inventory
        inv.add("Poke Ball", 5)
        inv.add("Potion", 3)
        inv.add("Antidote", 1)

    def update(self, dt):
        pass

    def draw(self, surface):
        surface.fill((30, 90, 60))
        font = self.app.assets.font(16)
        if self.error:
            surface.blit(font.render(self.error, True, (255, 255, 255)), (10, 10))
            return
        prompt = font.render("Choose your starter!", True, (255, 255, 255))
        surface.blit(prompt, (surface.get_width() // 2 - prompt.get_width() // 2, 10))
        self.menu.draw(surface, self.app.assets, (surface.get_width() // 2 - 40, 60))
