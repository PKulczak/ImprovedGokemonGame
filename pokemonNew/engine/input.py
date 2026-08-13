"""Translates raw pygame key events into abstract, rebindable actions.

Also supports synthetic injection (press/release/tap) so scenes can be
driven programmatically in headless tests without a real event loop.
"""

import pygame

KEY_ACTIONS = {
    pygame.K_UP: "UP", pygame.K_w: "UP",
    pygame.K_DOWN: "DOWN", pygame.K_s: "DOWN",
    pygame.K_LEFT: "LEFT", pygame.K_a: "LEFT",
    pygame.K_RIGHT: "RIGHT", pygame.K_d: "RIGHT",
    pygame.K_z: "CONFIRM", pygame.K_RETURN: "CONFIRM", pygame.K_SPACE: "CONFIRM",
    pygame.K_x: "CANCEL", pygame.K_BACKSPACE: "CANCEL",
    pygame.K_ESCAPE: "START",
    pygame.K_LSHIFT: "RUN", pygame.K_RSHIFT: "RUN",
}

ALL_ACTIONS = ("UP", "DOWN", "LEFT", "RIGHT", "CONFIRM", "CANCEL", "START", "RUN")


class InputState:
    def __init__(self):
        self.held = set()
        self.pressed = set()
        self.released = set()

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            action = KEY_ACTIONS.get(event.key)
            if action:
                self.press(action)
        elif event.type == pygame.KEYUP:
            action = KEY_ACTIONS.get(event.key)
            if action:
                self.release(action)

    def is_held(self, action):
        return action in self.held

    def was_pressed(self, action):
        return action in self.pressed

    def was_released(self, action):
        return action in self.released

    def end_frame(self):
        self.pressed.clear()
        self.released.clear()

    def press(self, action):
        if action not in self.held:
            self.held.add(action)
            self.pressed.add(action)

    def release(self, action):
        if action in self.held:
            self.held.discard(action)
            self.released.add(action)

    def tap(self, action):
        self.press(action)
