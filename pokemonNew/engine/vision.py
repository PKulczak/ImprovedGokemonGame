"""Trainer sightline math: pure functions, no pygame.Surface involved, so
they're trivial to unit test in isolation.
"""

from engine.entity import Direction


def tiles_in_sightline(origin, facing, range_tiles, tilemap):
    """Straight line of tiles in front of `origin`, stopping early at the
    first solid (non-walkable) tile."""
    dx, dy = Direction.to_delta(facing)
    ox, oy = origin
    tiles = []
    for step in range(1, range_tiles + 1):
        pos = (ox + dx * step, oy + dy * step)
        if not tilemap.is_walkable(pos):
            break
        tiles.append(pos)
    return tiles


def can_see_player(trainer_pos, facing, range_tiles, player_pos, tilemap):
    return player_pos in tiles_in_sightline(trainer_pos, facing, range_tiles, tilemap)
