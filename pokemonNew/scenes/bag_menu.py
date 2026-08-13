from engine.scene import Scene
from engine.menu import ListMenu


class BagMenuScene(Scene):
    blocks_update_below = True
    draws_below = True

    def on_enter(self, mode="pause", **kwargs):
        self.mode = mode
        items = self.app.state.inventory.items
        self._names = sorted(items.keys())
        labels = [f"{name} x{items[name]}" for name in self._names] or ["(bag is empty)"]
        self.menu = ListMenu(labels)

    def handle_input(self, input_state):
        if input_state.was_pressed("UP"):
            self.menu.move(-1)
        elif input_state.was_pressed("DOWN"):
            self.menu.move(1)
        elif input_state.was_pressed("CANCEL"):
            self.app.scene_stack.pop(result=None)
        elif input_state.was_pressed("CONFIRM"):
            if self._names:
                self.app.scene_stack.pop(result=self._names[self.menu.index])

    def update(self, dt):
        pass

    def draw(self, surface):
        surface.fill((235, 235, 245))
        font = self.app.assets.font(14)
        surface.blit(font.render("Bag", True, (20, 20, 20)), (10, 6))
        self.menu.draw(surface, self.app.assets, (10, 26), color=(20, 20, 20), selected_color=(180, 40, 40))
