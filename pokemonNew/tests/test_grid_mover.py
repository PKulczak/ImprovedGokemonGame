from engine.entity import GridMover, Direction


class FakeTileMap:
    def __init__(self, blocked=()):
        self.blocked = set(blocked)

    def is_walkable(self, pos):
        return pos not in self.blocked


def test_try_move_starts_a_step_and_faces_direction():
    mover = GridMover(2, 2, step_duration=0.2)
    tilemap = FakeTileMap()
    started = mover.try_move(1, 0, tilemap)
    assert started is True
    assert mover.moving is True
    assert mover.facing == Direction.RIGHT
    assert mover.to_tile == (3, 2)
    assert mover.tile_pos == (2, 2)  # hasn't arrived yet


def test_blocked_tile_still_turns_but_does_not_move():
    mover = GridMover(2, 2, step_duration=0.2)
    tilemap = FakeTileMap(blocked={(2, 1)})
    started = mover.try_move(0, -1, tilemap)
    assert started is False
    assert mover.moving is False
    assert mover.facing == Direction.UP  # turned to face it anyway


def test_cannot_start_new_move_while_already_moving():
    mover = GridMover(2, 2, step_duration=0.2)
    tilemap = FakeTileMap()
    assert mover.try_move(1, 0, tilemap) is True
    assert mover.try_move(0, 1, tilemap) is False


def test_update_completes_step_after_full_duration_and_reports_arrival():
    mover = GridMover(2, 2, step_duration=0.2)
    tilemap = FakeTileMap()
    mover.try_move(1, 0, tilemap)

    arrived = mover.update(0.1)
    assert arrived is None
    assert mover.moving is True

    arrived = mover.update(0.1)
    assert arrived == (3, 2)
    assert mover.moving is False
    assert mover.tile_pos == (3, 2)


def test_pixel_pos_interpolates_mid_step():
    mover = GridMover(0, 0, step_duration=0.2)
    tilemap = FakeTileMap()
    mover.try_move(1, 0, tilemap)
    mover.update(0.1)  # halfway through a 0.2s step
    px, py = mover.pixel_pos
    assert 0 < px < 16
    assert py == 0


def test_pixel_pos_matches_tile_when_idle():
    mover = GridMover(3, 4, step_duration=0.2)
    assert mover.pixel_pos == (48, 64)


def test_occupancy_blocks_movement_onto_another_entity():
    mover = GridMover(0, 0, step_duration=0.2)
    tilemap = FakeTileMap()
    occupancy = {(1, 0): object()}
    assert mover.try_move(1, 0, tilemap, occupancy) is False
