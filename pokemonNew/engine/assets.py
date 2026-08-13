"""Path-keyed image/font cache. All asset paths are relative to pokemonNew/assets/."""

import os

import pygame

ASSETS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")


class AssetManager:
    def __init__(self, root_dir=ASSETS_DIR):
        self.root_dir = root_dir
        self._image_cache = {}
        self._font_cache = {}

    def image(self, relative_path):
        if relative_path not in self._image_cache:
            full_path = os.path.join(self.root_dir, relative_path)
            surf = pygame.image.load(full_path)
            self._image_cache[relative_path] = surf.convert_alpha()
        return self._image_cache[relative_path]

    def font(self, size, name=None):
        key = (name, size)
        if key not in self._font_cache:
            self._font_cache[key] = pygame.font.Font(name, size)
        return self._font_cache[key]
