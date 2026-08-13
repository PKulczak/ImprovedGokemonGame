import random

from engine.entity import Entity
from world.npc_behavior import StaticNPC, PatrolNPC, WanderNPC


class FakeTileMap:
    def is_walkable(self, pos):
        return True


def test_static_npc_never_moves():
    npc = Entity(2, 2)
    behavior = StaticNPC()
    assert behavior.decide(npc, FakeTileMap(), 0.016) is None


def test_patrol_npc_walks_toward_next_waypoint():
    npc = Entity(0, 0)
    behavior = PatrolNPC([(2, 0), (2, 2)])
    move = behavior.decide(npc, FakeTileMap(), 0.016)
    assert move == (1, 0)


def test_patrol_npc_advances_waypoint_on_arrival():
    npc = Entity(2, 0)
    behavior = PatrolNPC([(2, 0), (2, 2)])
    move = behavior.decide(npc, FakeTileMap(), 0.016)
    assert behavior.target_index == 1
    assert move == (0, 1)


def test_patrol_npc_does_not_redirect_mid_step():
    npc = Entity(0, 0)
    npc.mover.try_move(1, 0, FakeTileMap())
    behavior = PatrolNPC([(5, 0)])
    assert behavior.decide(npc, FakeTileMap(), 0.016) is None


def test_wander_npc_stays_within_radius():
    rng = random.Random(7)
    npc = Entity(5, 5)
    behavior = WanderNPC(home=(5, 5), radius=1, rng=rng)
    for _ in range(50):
        move = behavior.decide(npc, FakeTileMap(), 0.016)
        if move:
            dx, dy = move
            tx, ty = npc.tile_pos
            assert abs((tx + dx) - 5) <= 1
            assert abs((ty + dy) - 5) <= 1
