import pygame

from engine.scene import Scene
from engine.menu import ListMenu


class PauseMenuScene(Scene):
    blocks_update_below = True
    draws_below = True

    OPTIONS = ["Party", "Bag", "Pokedex", "Save", "Close"]

    def on_enter(self, **kwargs):
        self.menu = ListMenu(list(self.OPTIONS))
        self.message = None

    def handle_input(self, input_state):
        if self.message is not None:
            if input_state.was_pressed("CONFIRM") or input_state.was_pressed("CANCEL"):
                self.message = None
            return
        if input_state.was_pressed("UP"):
            self.menu.move(-1)
        elif input_state.was_pressed("DOWN"):
            self.menu.move(1)
        elif input_state.was_pressed("CANCEL") or input_state.was_pressed("START"):
            self.app.scene_stack.pop()
        elif input_state.was_pressed("CONFIRM"):
            self._select()

    def _select(self):
        choice = self.menu.selected
        if choice == "Party":
            from scenes.party_menu import PartyMenuScene
            self.app.scene_stack.push(PartyMenuScene(self.app), mode="pause")
        elif choice == "Bag":
            from scenes.bag_menu import BagMenuScene
            self.app.scene_stack.push(BagMenuScene(self.app), mode="pause")
        elif choice == "Pokedex":
            from scenes.pokedex import PokedexScene
            self.app.scene_stack.push(PokedexScene(self.app))
        elif choice == "Save":
            self.app.save_manager.save(self.app.state.to_save_data())
            self.message = "Game saved!"
        elif choice == "Close":
            self.app.scene_stack.pop()

    def update(self, dt):
        pass

    def draw(self, surface):
        w, h = surface.get_size()
        panel = pygame.Rect(w - 90, 4, 86, 20 + len(self.OPTIONS) * 16)
        pygame.draw.rect(surface, (250, 250, 250), panel)
        pygame.draw.rect(surface, (30, 30, 30), panel, 2)
        self.menu.draw(surface, self.app.assets, (panel.left + 8, panel.top + 8))
        if self.message:
            msg_rect = pygame.Rect(20, h - 40, w - 40, 30)
            pygame.draw.rect(surface, (250, 250, 250), msg_rect)
            pygame.draw.rect(surface, (30, 30, 30), msg_rect, 2)
            font = self.app.assets.font(14)
            surface.blit(font.render(self.message, True, (20, 20, 20)), (msg_rect.left + 6, msg_rect.top + 6))
