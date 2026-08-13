"""Pluggable NPC movement controllers: decide(npc_entity, tilemap, dt) -> Optional[(dx, dy)].
Pure decision logic — callable/testable with a fake entity/tilemap, no rendering."""


class StaticNPC:
    def decide(self, npc_entity, tilemap, dt):
        return None


class PatrolNPC:
    def __init__(self, waypoints):
        self.waypoints = list(waypoints)
        self.target_index = 0

    def decide(self, npc_entity, tilemap, dt):
        if npc_entity.moving or not self.waypoints:
            return None
        tx, ty = npc_entity.tile_pos
        wx, wy = self.waypoints[self.target_index]
        if (tx, ty) == (wx, wy):
            self.target_index = (self.target_index + 1) % len(self.waypoints)
            wx, wy = self.waypoints[self.target_index]
        dx = (wx > tx) - (wx < tx)
        dy = (wy > ty) - (wy < ty)
        if dx != 0:
            return (dx, 0)
        if dy != 0:
            return (0, dy)
        return None


class WanderNPC:
    def __init__(self, home, radius, rng):
        self.home = home
        self.radius = radius
        self.rng = rng
        self._cooldown = 0.0

    def decide(self, npc_entity, tilemap, dt):
        self._cooldown -= dt
        if npc_entity.moving or self._cooldown > 0:
            return None
        self._cooldown = self.rng.uniform(1.0, 2.5)
        if self.rng.random() > 0.4:
            return None
        dx, dy = self.rng.choice([(0, 1), (0, -1), (1, 0), (-1, 0)])
        tx, ty = npc_entity.tile_pos
        hx, hy = self.home
        if abs((tx + dx) - hx) > self.radius or abs((ty + dy) - hy) > self.radius:
            return None
        return (dx, dy)
