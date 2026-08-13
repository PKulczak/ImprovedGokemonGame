import os
import random

import pygame

import settings
from engine.scene import SceneStack
from engine.input import InputState
from engine.assets import AssetManager


class App:
    """Owns the window, the offscreen virtual surface, the clock, and the scene stack,
    plus a small set of cross-scene shared services (assets/rng/game state/save manager).

    `present()` is the only method that ever touches the real display, and it is
    never called from tick()/draw() — headless callers (tests, tools) can drive
    the whole game via tick()/draw() alone and never open a real window.
    """

    def __init__(self, headless=False, save_dir=None, rng=None):
        self.headless = headless
        if headless:
            os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
        pygame.init()
        pygame.font.init()
        pygame.display.set_caption("Pokemon Virelia")
        self.window = pygame.display.set_mode(settings.WINDOW_SIZE)
        self.virtual_surface = pygame.Surface((settings.VIRTUAL_W, settings.VIRTUAL_H)).convert()
        self.clock = pygame.time.Clock()
        self.accumulator = 0.0
        self.scene_stack = SceneStack()
        self.input_state = InputState()
        self.running = True

        self.save_dir = save_dir or os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "..", settings.SAVE_DIR_NAME
        )
        self.assets = AssetManager()
        self.rng = rng or random.Random()

        from save.manager import SaveManager
        from world.game_state import GameState
        self.save_manager = SaveManager(self.save_dir)
        self.state = GameState()
        self.dialogue_text = {}

    def boot(self):
        from scenes.boot import BootScene
        self.scene_stack.push(BootScene(self))

    def run(self):
        while self.running:
            frame_dt = min(self.clock.tick(settings.FPS_CAP) / 1000.0, settings.MAX_FRAME_DT)
            self.pump_events()
            self.accumulator += frame_dt
            while self.accumulator >= settings.LOGIC_DT:
                self.tick(settings.LOGIC_DT)
                self.accumulator -= settings.LOGIC_DT
            self.draw()
            self.present()

    def pump_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            else:
                self.input_state.handle_event(event)

    def tick(self, dt):
        self.scene_stack.handle_input(self.input_state)
        self.scene_stack.update(dt)
        self.input_state.end_frame()

    def draw(self):
        self.virtual_surface.fill((0, 0, 0))
        self.scene_stack.draw(self.virtual_surface)

    def present(self):
        scaled = pygame.transform.scale(self.virtual_surface, settings.WINDOW_SIZE)
        self.window.blit(scaled, (0, 0))
        pygame.display.flip()

    def quit(self):
        self.running = False
