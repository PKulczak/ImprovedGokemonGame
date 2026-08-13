"""Grid-stepping movement: position truth is integer tile coords plus a 0->1
move-progress interpolated over a fixed step duration. Encounter/warp/vision
checks fire once on arrival at a tile center (not mid-slide), matching real
Pokemon step semantics and avoiding double-triggers.
"""

import settings


class Direction:
    DOWN = "DOWN"
    LEFT = "LEFT"
    RIGHT = "RIGHT"
    UP = "UP"

    _DELTA_TO_DIR = {
        (0, 1): DOWN,
        (0, -1): UP,
        (-1, 0): LEFT,
        (1, 0): RIGHT,
    }

    _DIR_TO_DELTA = {v: k for k, v in _DELTA_TO_DIR.items()}

    @classmethod
    def from_delta(cls, dx, dy):
        return cls._DELTA_TO_DIR.get((dx, dy), cls.DOWN)

    @classmethod
    def to_delta(cls, direction):
        return cls._DIR_TO_DELTA.get(direction, (0, 1))


class GridMover:
    def __init__(self, tile_x, tile_y, facing=Direction.DOWN, step_duration=None):
        self.tile_x = tile_x
        self.tile_y = tile_y
        self.facing = facing
        self.step_duration = step_duration or settings.STEP_DURATION
        self.moving = False
        self.from_tile = (tile_x, tile_y)
        self.to_tile = (tile_x, tile_y)
        self.move_progress = 0.0

    @property
    def tile_pos(self):
        return (self.tile_x, self.tile_y)

    def try_move(self, dx, dy, tilemap, occupancy=None):
        """Attempt to step one tile in direction (dx, dy). Always turns to face
        that direction even if the step is blocked (Pokemon-authentic feel).
        Returns True if a step was started."""
        if dx or dy:
            self.facing = Direction.from_delta(dx, dy)
        if self.moving:
            return False
        target = (self.tile_x + dx, self.tile_y + dy)
        if not tilemap.is_walkable(target):
            return False
        if occupancy is not None and occupancy.get(target) is not None:
            return False
        self.from_tile = self.tile_pos
        self.to_tile = target
        self.moving = True
        self.move_progress = 0.0
        return True

    def update(self, dt):
        """Advances the current step. Returns the arrived-at tile coord the
        instant a step completes, else None."""
        if not self.moving:
            return None
        self.move_progress += dt / self.step_duration
        if self.move_progress >= 1.0:
            self.tile_x, self.tile_y = self.to_tile
            self.moving = False
            self.move_progress = 0.0
            return self.tile_pos
        return None

    @property
    def pixel_pos(self):
        if not self.moving:
            return (self.tile_x * settings.TILE_SIZE, self.tile_y * settings.TILE_SIZE)
        fx, fy = self.from_tile
        tx, ty = self.to_tile
        t = self.move_progress
        return (
            (fx + (tx - fx) * t) * settings.TILE_SIZE,
            (fy + (ty - fy) * t) * settings.TILE_SIZE,
        )


class Entity:
    def __init__(self, tile_x, tile_y, animation=None, facing=Direction.DOWN):
        self.mover = GridMover(tile_x, tile_y, facing=facing)
        self.animation = animation

    @property
    def tile_pos(self):
        return self.mover.tile_pos

    @property
    def facing(self):
        return self.mover.facing

    @property
    def moving(self):
        return self.mover.moving

    def update(self, dt):
        return self.mover.update(dt)

    def draw(self, surface, camera):
        if self.animation is None:
            return
        frame = self.animation.frame_for(self.mover.facing, self.mover.moving, self.mover.move_progress)
        px, py = self.mover.pixel_pos
        sx, sy = camera.world_to_screen(px, py)
        offset_x = (settings.TILE_SIZE - frame.get_width()) // 2
        offset_y = settings.TILE_SIZE - frame.get_height()
        surface.blit(frame, (sx + offset_x, sy + offset_y))
