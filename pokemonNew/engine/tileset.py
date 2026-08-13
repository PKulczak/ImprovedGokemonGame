"""Tile slicing: arithmetic grid mode for clean sheets, manifest-driven atlas
mode for the irregular bin-packed sheets, single mode for standalone props.

No detection logic lives here — atlas manifests are produced offline by
tools/slice_atlas.py and just get read back at runtime.
"""

import json
import os

import pygame


class Tileset:
    def __init__(self, name, config, assets):
        self.name = name
        self.mode = config["mode"]
        self.assets = assets
        self.image = assets.image(config["image"])
        self._tile_cache = {}

        if self.mode == "grid":
            self.tile_w = config["tile_w"]
            self.tile_h = config["tile_h"]
            self.margin = config.get("margin", 0)
            self.spacing = config.get("spacing", 0)
            w, h = self.image.get_width(), self.image.get_height()
            self.cols = config.get("cols") or (w - 2 * self.margin + self.spacing) // (self.tile_w + self.spacing)
            self.rows = config.get("rows") or (h - 2 * self.margin + self.spacing) // (self.tile_h + self.spacing)
            self.tile_meta = config.get("tiles", {})
        elif self.mode == "atlas":
            manifest_path = os.path.join(assets.root_dir, config["manifest"])
            with open(manifest_path) as f:
                self._manifest = json.load(f)
            self.tile_meta = {}
        elif self.mode == "single":
            self.tile_meta = {}
        else:
            raise ValueError(f"unknown tileset mode: {self.mode!r}")

    def get_tile(self, index):
        if index in self._tile_cache:
            return self._tile_cache[index]

        if self.mode == "grid":
            col = index % self.cols
            row = index // self.cols
            x = self.margin + col * (self.tile_w + self.spacing)
            y = self.margin + row * (self.tile_h + self.spacing)
            surf = self.image.subsurface(pygame.Rect(x, y, self.tile_w, self.tile_h)).copy()
        elif self.mode == "atlas":
            entry = self._manifest[index]
            surf = self.image.subsurface(pygame.Rect(entry["x"], entry["y"], entry["w"], entry["h"])).copy()
        else:  # single
            surf = self.image

        self._tile_cache[index] = surf
        return surf

    def tile_size(self, index):
        """Returns (w, h) in pixels for a tile — atlas/single entries aren't necessarily 1 map-tile in size."""
        if self.mode == "grid":
            return self.tile_w, self.tile_h
        if self.mode == "atlas":
            entry = self._manifest[index]
            return entry["w"], entry["h"]
        return self.image.get_width(), self.image.get_height()

    def tile_count(self):
        if self.mode == "grid":
            return self.cols * self.rows
        if self.mode == "atlas":
            return len(self._manifest)
        return 1

    def is_walkable(self, index):
        meta = self.tile_meta.get(str(index))
        if meta is None:
            return True
        return meta.get("walkable", True)

    def encounter_zone(self, index):
        meta = self.tile_meta.get(str(index))
        return meta.get("encounter_zone") if meta else None


class TilesetRegistry:
    def __init__(self, assets, config_path):
        with open(config_path) as f:
            self._config = json.load(f)
        self.assets = assets
        self._cache = {}

    def get(self, name):
        if name not in self._cache:
            self._cache[name] = Tileset(name, self._config[name], self.assets)
        return self._cache[name]
