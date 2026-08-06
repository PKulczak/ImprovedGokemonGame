import os
import pygame

TILESETS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tilesets")


def list_tilesets():
    return sorted(f for f in os.listdir(TILESETS_DIR) if f.lower().endswith(".png"))


class Tileset:
    def __init__(self, filename):
        self.filename = filename
        self.surface = pygame.image.load(os.path.join(TILESETS_DIR, filename)).convert_alpha()

    @property
    def width(self):
        return self.surface.get_width()

    @property
    def height(self):
        return self.surface.get_height()

    #crops an arbitrary rectangle out of the sheet - these sheets aren't uniform grids, so
    #selection is freeform rather than snapped to fixed tile cells
    def crop(self, rect):
        x, y, w, h = rect
        sub = pygame.Surface((w, h), pygame.SRCALPHA)
        sub.blit(self.surface, (0, 0), (x, y, w, h))
        return sub
