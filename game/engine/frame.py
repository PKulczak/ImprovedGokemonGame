import sys
import pygame

from game.engine import balance

pygame.font.init()

_PROMPT_FONT_SIZE = 28


#blocking text-entry overlay, drawn directly onto the real screen - adapted from
#MapBuilder/builder/editor.py's prompt_text(), same visual language. Returns the typed
#text on Enter, or None on Escape/window-close (caller treats None as "cancelled").
def _prompt_text(screen, label):
    font = pygame.font.SysFont(None, _PROMPT_FONT_SIZE)
    text = ""
    clock = pygame.time.Clock()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return text
                if event.key == pygame.K_ESCAPE:
                    return None
                if event.key == pygame.K_BACKSPACE:
                    text = text[:-1]
                elif event.unicode and event.unicode.isprintable():
                    text += event.unicode
        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 190))
        screen.blit(overlay, (0, 0))
        screen.blit(font.render(label, True, (255, 255, 255)), (40, 40))
        screen.blit(font.render(text + "_", True, (255, 255, 0)), (40, 80))
        screen.blit(font.render("Enter to confirm, Esc to cancel", True, (200, 200, 200)), (40, 130))
        pygame.display.flip()
        clock.tick(30)


#drop-in replacement for SimpleGUICS2Pygame's Frame - same method names as the shim so
#existing call sites (Game._enter_state/_draw_fight/_draw_pokedex, bottom-of-file setup)
#don't need to change. add_input's 3rd arg changes meaning from "box pixel width" to a
#trigger pygame.K_* key: instead of a permanent always-visible side-panel text box, the
#input is a keyboard-triggered blocking modal (see _prompt_text), available in any game
#state since the hotkey is checked here in the main loop rather than in Keyboard/Kbd.
class Frame:
    def __init__(self, screen, canvas, fps=60):
        self.screen = screen
        self.canvas = canvas
        self.fps = fps
        self.bg_color = pygame.Color('black')
        self._draw_handler = None
        self._keydown_handler = None
        self._keyup_handler = None
        self._inputs = []
        self._running = False

    def set_canvas_background(self, color):
        self.bg_color = pygame.Color(color)

    def set_draw_handler(self, handler):
        self._draw_handler = handler

    def set_keydown_handler(self, handler):
        self._keydown_handler = handler

    def set_keyup_handler(self, handler):
        self._keyup_handler = handler

    def add_input(self, label, callback, key):
        self._inputs.append((label, callback, key))

    def stop(self):
        self._running = False

    def start(self):
        self._running = True
        clock = pygame.time.Clock()
        #dt is in frame-equivalents (1.0 == one frame at the nominal self.fps design rate),
        #derived from how long the *previous* iteration actually took - there's no way to know
        #the current one's duration before it happens, so every real-time game loop works one
        #iteration behind like this. Starts at exactly 1.0 (one nominal frame) since there's no
        #previous iteration yet, and is capped so a one-off stall can't blow through walls,
        #fast-forward a message to its end, or spike the wild-encounter roll in a single jump
        dt = 1.0
        while self._running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self._running = False
                elif event.type == pygame.KEYDOWN:
                    matched = next((inp for inp in self._inputs if inp[2] == event.key), None)
                    if matched is not None:
                        label, callback, _key = matched
                        result = _prompt_text(self.screen, label)
                        if result is not None:
                            callback(result)
                    elif self._keydown_handler is not None:
                        self._keydown_handler(event.key)
                elif event.type == pygame.KEYUP:
                    if self._keyup_handler is not None:
                        self._keyup_handler(event.key)

            self.screen.fill(self.bg_color)
            if self._draw_handler is not None:
                self._draw_handler(self.canvas, dt)
            pygame.display.flip()
            elapsed_ms = clock.tick(self.fps)
            #holding Shift fast-forwards the whole game (movement/animation/dialogue/message
            #timers all read dt, so multiplying it here speeds all of them up uniformly) -
            #polled directly rather than tracked via KEYDOWN/KEYUP so it can't get stuck on if a
            #KEYUP is ever missed (e.g. released while the R/N text-entry modal has focus)
            keys = pygame.key.get_pressed()
            fast_forward = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]
            multiplier = balance.FAST_FORWARD_MULTIPLIER if fast_forward else 1
            dt = min((elapsed_ms / 1000.0) * self.fps * multiplier, balance.MAX_DT_FRAMES)
