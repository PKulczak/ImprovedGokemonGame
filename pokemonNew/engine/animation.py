"""Slices character walk-cycle spritesheets (player.png / bossN.png-style: a
grid of direction-rows x walk-frame-columns) and drives frame selection from
GridMover's move_progress rather than an independent timer, so footsteps
never visually drift from actual tile-crossing progress.
"""

import pygame

import settings

DIRECTION_ROWS = {"DOWN": 0, "LEFT": 1, "RIGHT": 2, "UP": 3}


class SpriteSheet:
    def __init__(self, image, frame_w, frame_h, render_w=None, render_h=None):
        self.image = image
        self.frame_w = frame_w
        self.frame_h = frame_h
        self.render_w = render_w or frame_w
        self.render_h = render_h or frame_h
        self.cols = image.get_width() // frame_w
        self.rows = image.get_height() // frame_h
        self._cache = {}

    def frame(self, col, row):
        key = (col, row)
        if key not in self._cache:
            x, y = col * self.frame_w, row * self.frame_h
            raw = self.image.subsurface(pygame.Rect(x, y, self.frame_w, self.frame_h))
            if (self.render_w, self.render_h) != (self.frame_w, self.frame_h):
                raw = pygame.transform.smoothscale(raw, (self.render_w, self.render_h))
            else:
                raw = raw.copy()
            self._cache[key] = raw
        return self._cache[key]


class AnimationController:
    def __init__(self, sheet, direction_rows=None, frame_count=4, single_row=False):
        self.sheet = sheet
        self.direction_rows = direction_rows or DIRECTION_ROWS
        self.frame_count = frame_count
        self.single_row = single_row  # True for NPC sheets that only have one direction's worth of frames

    def frame_for(self, facing, moving, move_progress):
        row = 0 if self.single_row else self.direction_rows.get(facing, 0)
        if not moving:
            return self.sheet.frame(0, row)
        col = int(move_progress * self.frame_count) % self.frame_count
        return self.sheet.frame(col, row)


def load_character_sheet(assets, relative_path, single_row=False):
    image = assets.image(relative_path)
    sheet = SpriteSheet(
        image,
        settings.CHAR_SOURCE_FRAME_W,
        settings.CHAR_SOURCE_FRAME_H,
        render_w=settings.CHAR_RENDER_W,
        render_h=settings.CHAR_RENDER_H,
    )
    return AnimationController(sheet, single_row=single_row)
