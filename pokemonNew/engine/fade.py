import pygame


class FadeTransition:
    """A simple fade-to-black-and-back effect used between map warps/scene
    changes. `start(on_midpoint=...)` fires the callback once the screen is
    fully black (the right moment to actually swap the map/scene)."""

    def __init__(self, duration=0.25):
        self.duration = duration
        self.t = 0.0
        self.phase = None  # None | "out" | "in"
        self._on_midpoint = None
        self._midpoint_fired = False

    def start(self, on_midpoint=None):
        self.phase = "out"
        self.t = 0.0
        self._on_midpoint = on_midpoint
        self._midpoint_fired = False

    @property
    def active(self):
        return self.phase is not None

    def update(self, dt):
        if self.phase is None:
            return
        self.t += dt
        if self.phase == "out" and self.t >= self.duration:
            if not self._midpoint_fired:
                self._midpoint_fired = True
                if self._on_midpoint:
                    self._on_midpoint()
            self.phase = "in"
            self.t = 0.0
        elif self.phase == "in" and self.t >= self.duration:
            self.phase = None
            self.t = 0.0

    @property
    def alpha(self):
        if self.phase == "out":
            return int(255 * min(self.t / self.duration, 1.0))
        if self.phase == "in":
            return int(255 * (1.0 - min(self.t / self.duration, 1.0)))
        return 0

    def draw(self, surface):
        if self.phase is None:
            return
        a = self.alpha
        if a <= 0:
            return
        overlay = pygame.Surface(surface.get_size())
        overlay.fill((0, 0, 0))
        overlay.set_alpha(a)
        surface.blit(overlay, (0, 0))
