import pygame


class DialogueBox:
    """Text paging + typewriter reveal + a confirm-to-advance state machine.
    Drawn as an overlay; owned by scenes.dialogue_overlay.DialogueScene."""

    def __init__(self, assets, font_size=14, chars_per_second=40):
        self.assets = assets
        self.font = assets.font(font_size)
        self.chars_per_second = chars_per_second
        self.pages = []
        self.page_index = 0
        self.reveal_chars = 0.0
        self.done = True
        try:
            self.box_image = assets.image("ui/box.png")
        except Exception:
            self.box_image = None

    def start(self, pages):
        self.pages = [p for p in pages if p]
        self.page_index = 0
        self.reveal_chars = 0.0
        self.done = len(self.pages) == 0

    @property
    def current_text(self):
        if self.done or not self.pages:
            return ""
        return self.pages[self.page_index]

    @property
    def fully_revealed(self):
        return int(self.reveal_chars) >= len(self.current_text)

    def update(self, dt):
        if self.done:
            return
        if not self.fully_revealed:
            self.reveal_chars += self.chars_per_second * dt

    def advance(self):
        """Call on CONFIRM. Returns True once the whole dialogue has finished."""
        if self.done:
            return True
        if not self.fully_revealed:
            self.reveal_chars = len(self.current_text)
            return False
        self.page_index += 1
        if self.page_index >= len(self.pages):
            self.done = True
            return True
        self.reveal_chars = 0.0
        return False

    def draw(self, surface):
        if self.done:
            return
        w, h = surface.get_size()
        box_h = 40
        box_rect = pygame.Rect(4, h - box_h - 4, w - 8, box_h)
        if self.box_image is not None:
            scaled = pygame.transform.scale(self.box_image, (box_rect.width, box_rect.height))
            surface.blit(scaled, box_rect.topleft)
        else:
            pygame.draw.rect(surface, (250, 250, 250), box_rect)
            pygame.draw.rect(surface, (40, 40, 40), box_rect, 2)

        visible = self.current_text[: int(self.reveal_chars)]
        self._draw_wrapped(surface, visible, box_rect)

    def _draw_wrapped(self, surface, text, box_rect):
        max_width = box_rect.width - 12
        words = text.split(" ")
        lines = []
        current = ""
        for word in words:
            trial = (current + " " + word).strip()
            if self.font.size(trial)[0] > max_width and current:
                lines.append(current)
                current = word
            else:
                current = trial
        if current:
            lines.append(current)
        y = box_rect.top + 6
        for line in lines[:3]:
            rendered = self.font.render(line, True, (20, 20, 20))
            surface.blit(rendered, (box_rect.left + 6, y))
            y += self.font.get_height() + 2
