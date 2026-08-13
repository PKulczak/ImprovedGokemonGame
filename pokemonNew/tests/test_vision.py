from engine.vision import tiles_in_sightline, can_see_player


class FakeTileMap:
    def __init__(self, blocked=()):
        self.blocked = set(blocked)

    def is_walkable(self, pos):
        return pos not in self.blocked


def test_sightline_extends_full_range_when_clear():
    tilemap = FakeTileMap()
    tiles = tiles_in_sightline((5, 5), "UP", 3, tilemap)
    assert tiles == [(5, 4), (5, 3), (5, 2)]


def test_sightline_stops_at_first_solid_tile():
    tilemap = FakeTileMap(blocked={(5, 3)})
    tiles = tiles_in_sightline((5, 5), "UP", 5, tilemap)
    assert tiles == [(5, 4)]


def test_can_see_player_true_when_in_line():
    tilemap = FakeTileMap()
    assert can_see_player((2, 2), "RIGHT", 4, (5, 2), tilemap) is True


def test_can_see_player_false_when_out_of_range():
    tilemap = FakeTileMap()
    assert can_see_player((2, 2), "RIGHT", 2, (5, 2), tilemap) is False


def test_can_see_player_false_when_blocked():
    tilemap = FakeTileMap(blocked={(4, 2)})
    assert can_see_player((2, 2), "RIGHT", 4, (5, 2), tilemap) is False


def test_can_see_player_false_when_wrong_direction():
    tilemap = FakeTileMap()
    assert can_see_player((2, 2), "LEFT", 4, (5, 2), tilemap) is False
