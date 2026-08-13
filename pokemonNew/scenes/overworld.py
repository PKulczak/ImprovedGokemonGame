import os

from engine.scene import Scene
from engine.camera import Camera
from engine.tileset import TilesetRegistry
from engine.tilemap import TileMap
from engine.entity import Entity, Direction
from engine.animation import load_character_sheet
from engine.assets import DATA_DIR
from engine.fade import FadeTransition
from world.encounters import roll_encounter
from world.trainers import TrainerNPC
from world.npc_behavior import StaticNPC, PatrolNPC
from world.story_flags import evaluate_condition

MAPS_DIR = os.path.join(DATA_DIR, "maps")
TILESETS_CONFIG = os.path.join(DATA_DIR, "tilesets.json")


class OverworldScene(Scene):
    """The persistent overworld: owns the current TileMap/Camera/player/NPCs.
    Warping between maps swaps internal state rather than pushing a new
    scene, so there's exactly one OverworldScene instance for the whole game."""

    def __init__(self, app):
        super().__init__(app)
        self.assets = app.assets
        self.tileset_registry = TilesetRegistry(self.assets, TILESETS_CONFIG)
        self.camera = Camera()
        self.fade = FadeTransition()
        self.tilemap = None
        self.player = None
        self.npcs = []

    def on_enter(self, map_id=None, spawn=(5, 5), facing=Direction.DOWN, **kwargs):
        self.load_map(map_id, spawn, facing)

    def load_map(self, map_id, spawn, facing=Direction.DOWN):
        self.tilemap = TileMap.load(map_id, MAPS_DIR, self.tileset_registry)
        px, py = spawn
        if self.player is None:
            anim = load_character_sheet(self.assets, "player/player.png")
            self.player = Entity(px, py, animation=anim, facing=facing)
        else:
            self.player.mover.tile_x, self.player.mover.tile_y = px, py
            self.player.mover.facing = facing
            self.player.mover.moving = False
        self.app.state.player.map_id = map_id
        self.app.state.player.tile_x = px
        self.app.state.player.tile_y = py
        self.app.state.player.facing = facing
        self._spawn_npcs()

    def _spawn_npcs(self):
        self.npcs = []
        flags = self.app.state.story_flags
        for npc_data in self.tilemap.npcs:
            if not evaluate_condition(npc_data.get("condition"), flags):
                continue
            sheet_name = npc_data.get("sprite", "boss1")
            anim = load_character_sheet(self.assets, f"npc/{sheet_name}.png", single_row=True)
            entity = Entity(
                npc_data["x"], npc_data["y"], animation=anim, facing=npc_data.get("facing", "DOWN")
            )
            behavior = StaticNPC()
            if npc_data.get("patrol"):
                behavior = PatrolNPC(npc_data["patrol"])
            trainer = None
            if npc_data.get("type") == "trainer":
                trainer_id = npc_data["trainer_ref"]
                defeated = trainer_id in self.app.state.defeated_trainers
                trainer = TrainerNPC(
                    npc_data["id"], entity, trainer_id,
                    vision_range=npc_data.get("vision_range", 4), defeated=defeated,
                )
            self.npcs.append({"entity": entity, "behavior": behavior, "trainer": trainer, "data": npc_data})

    def occupancy_map(self):
        occ = {npc["entity"].tile_pos: npc["entity"] for npc in self.npcs}
        occ[self.player.tile_pos] = self.player
        return occ

    def handle_input(self, input_state):
        if self.fade.active or self.player is None:
            return
        if input_state.was_pressed("START"):
            from scenes.pause_menu import PauseMenuScene
            self.app.scene_stack.push(PauseMenuScene(self.app))
            return
        if self.player.moving:
            return
        occ = self.occupancy_map()
        if input_state.is_held("UP"):
            self.player.mover.try_move(0, -1, self.tilemap, occ)
        elif input_state.is_held("DOWN"):
            self.player.mover.try_move(0, 1, self.tilemap, occ)
        elif input_state.is_held("LEFT"):
            self.player.mover.try_move(-1, 0, self.tilemap, occ)
        elif input_state.is_held("RIGHT"):
            self.player.mover.try_move(1, 0, self.tilemap, occ)
        elif input_state.was_pressed("CONFIRM"):
            self._interact()

    def _interact(self):
        dx, dy = Direction.to_delta(self.player.facing)
        px, py = self.player.tile_pos
        target = (px + dx, py + dy)
        for npc in self.npcs:
            if npc["entity"].tile_pos == target:
                if npc["data"].get("type") == "healer":
                    self._heal_party()
                self._start_dialogue(npc["data"].get("dialogue_id"))
                return

    def _heal_party(self):
        from battle.pokemon import StatusCondition
        for mon in self.app.state.party_manager.party:
            mon.current_hp = mon.get_stats().hp
            mon.status = StatusCondition.NONE
            mon.status_data = {}
            for lm in mon.moves:
                lm.current_pp = lm.move.pp

    def _start_dialogue(self, dialogue_id):
        if not dialogue_id:
            return
        from scenes.dialogue_overlay import DialogueScene
        pages = self.app.dialogue_text.get(dialogue_id, ["..."])
        self.app.scene_stack.push(DialogueScene(self.app), pages=pages)

    def update(self, dt):
        self.fade.update(dt)
        if self.fade.active or self.player is None:
            return
        arrived = self.player.update(dt)
        occ = self.occupancy_map()
        for npc in self.npcs:
            if not npc["entity"].moving:
                move = npc["behavior"].decide(npc["entity"], self.tilemap, dt)
                if move:
                    npc["entity"].mover.try_move(move[0], move[1], self.tilemap, occ)
            npc["entity"].update(dt)

        if arrived is not None:
            self._on_player_arrived(arrived)

    def _on_player_arrived(self, tile_pos):
        warp = self.tilemap.warp_at(tile_pos)
        if warp is not None:
            self._do_warp(warp)
            return

        table_id = self.tilemap.encounter_table_for(tile_pos)
        if table_id is not None:
            encounter = roll_encounter(table_id, self.app.rng)
            if encounter is not None:
                self._start_wild_battle(encounter)
                return

        for npc in self.npcs:
            trainer = npc["trainer"]
            if trainer and trainer.sees_player(self.player.tile_pos, self.tilemap):
                self._start_trainer_battle(trainer)
                return

    def _do_warp(self, warp):
        def midpoint():
            self.load_map(warp["to_map"], (warp["to_x"], warp["to_y"]), warp.get("to_facing", "DOWN"))

        self.fade.start(on_midpoint=midpoint)

    def _start_wild_battle(self, encounter):
        from scenes.battle import BattleScene
        self.app.scene_stack.push(BattleScene(self.app), wild=encounter)

    def _start_trainer_battle(self, trainer):
        from scenes.battle import BattleScene
        self.app.scene_stack.push(BattleScene(self.app), trainer=trainer)

    def on_child_closed(self, result):
        if isinstance(result, dict) and result.get("trainer_defeated") is not None:
            trainer = result["trainer_defeated"]
            trainer.mark_defeated()
            self.app.state.defeated_trainers.add(trainer.trainer_id)

    def draw(self, surface):
        if self.tilemap is None or self.player is None:
            return
        target_px = self.player.mover.pixel_pos
        map_px_w, map_px_h = self.tilemap.pixel_size()
        self.camera.follow(target_px, map_px_w, map_px_h)

        self.tilemap.draw(surface, self.camera)
        drawables = self.npcs + [{"entity": self.player}]
        for n in sorted(drawables, key=lambda item: item["entity"].tile_pos[1]):
            n["entity"].draw(surface, self.camera)
        self.tilemap.draw_above(surface, self.camera)
        self.fade.draw(surface)
