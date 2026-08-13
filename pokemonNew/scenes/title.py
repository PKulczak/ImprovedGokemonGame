from engine.scene import Scene
from engine.menu import ListMenu


class TitleScene(Scene):
    def on_enter(self, **kwargs):
        self._refresh_options()

    def _refresh_options(self):
        options = ["New Game"]
        if self.app.save_manager.has_save(1):
            options.append("Continue")
        self.menu = ListMenu(options)

    def handle_input(self, input_state):
        if input_state.was_pressed("UP"):
            self.menu.move(-1)
        elif input_state.was_pressed("DOWN"):
            self.menu.move(1)
        elif input_state.was_pressed("CONFIRM"):
            self._select()

    def _select(self):
        choice = self.menu.selected
        if choice == "New Game":
            from scenes.starter_select import StarterSelectScene
            self.app.scene_stack.push(StarterSelectScene(self.app))
        elif choice == "Continue":
            save_data = self.app.save_manager.load(1)
            if save_data is not None:
                from world.game_state import GameState
                self.app.state = GameState(save_data)
                from scenes.overworld import OverworldScene
                self.app.scene_stack.replace(
                    OverworldScene(self.app),
                    map_id=self.app.state.player.map_id,
                    spawn=(self.app.state.player.tile_x, self.app.state.player.tile_y),
                    facing=self.app.state.player.facing,
                )

    def update(self, dt):
        pass

    def draw(self, surface):
        surface.fill((20, 60, 40))
        font = self.app.assets.font(20)
        title = font.render("Pokemon Virelia", True, (255, 255, 255))
        surface.blit(title, (surface.get_width() // 2 - title.get_width() // 2, 30))
        self.menu.draw(surface, self.app.assets, (surface.get_width() // 2 - 40, 90))
