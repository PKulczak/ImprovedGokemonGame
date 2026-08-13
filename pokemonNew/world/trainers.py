"""Trainer NPCs: a sightline-triggered battle, on top of the generic Entity/vision plumbing."""

from engine.vision import can_see_player


class TrainerNPC:
    def __init__(self, npc_id, entity, trainer_id, vision_range=4, defeated=False):
        self.npc_id = npc_id
        self.entity = entity
        self.trainer_id = trainer_id
        self.vision_range = vision_range
        self.defeated = defeated

    def sees_player(self, player_tile_pos, tilemap):
        if self.defeated:
            return False
        return can_see_player(
            self.entity.tile_pos, self.entity.facing, self.vision_range, player_tile_pos, tilemap
        )

    def mark_defeated(self):
        self.defeated = True
