import os

import pytest

import scenes.overworld as overworld_module
from engine.app import App
from scenes.overworld import OverworldScene
from scenes.dialogue_overlay import DialogueScene
from scenes.battle import BattleScene

FIXTURES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures")


@pytest.fixture(autouse=True)
def patch_maps_dir(monkeypatch):
    monkeypatch.setattr(overworld_module, "MAPS_DIR", FIXTURES_DIR)


@pytest.fixture
def app(tmp_path):
    application = App(headless=True, save_dir=str(tmp_path))
    application.dialogue_text = {"test_villager": ["Hello there!", "Nice weather today."]}
    from data.starters import STARTERS
    starter = STARTERS["Chikorita"].instantiate(application.rng)
    application.state.party_manager.add(starter)
    return application


def push_overworld(app, spawn=(5, 5), facing="DOWN"):
    scene = OverworldScene(app)
    app.scene_stack.push(scene, map_id="test_room", spawn=spawn, facing=facing)
    return scene


def run_ticks(app, n, dt=1 / 60):
    for _ in range(n):
        app.tick(dt)


def test_player_spawns_at_requested_position(app):
    scene = push_overworld(app)
    assert scene.player.tile_pos == (5, 5)


def test_player_walks_one_tile_and_arrives(app):
    scene = push_overworld(app)
    app.input_state.press("UP")
    run_ticks(app, 9)  # a 0.15s step at 60 ticks/sec, released before a 2nd step could start
    app.input_state.release("UP")
    run_ticks(app, 2)  # let the first step finish settling regardless of float rounding
    assert scene.player.tile_pos == (5, 4)
    assert scene.player.moving is False


def test_walking_into_wall_turns_but_does_not_move(app):
    scene = push_overworld(app, spawn=(1, 1))
    app.input_state.press("UP")  # (1,0) is border rock
    run_ticks(app, 20)
    assert scene.player.tile_pos == (1, 1)
    assert scene.player.facing == "UP"


def test_dialogue_triggers_on_interact_and_pages_through(app):
    scene = push_overworld(app, spawn=(3, 3), facing="UP")
    app.input_state.tap("CONFIRM")
    run_ticks(app, 1)
    assert isinstance(app.scene_stack.top, DialogueScene)
    assert app.scene_stack.top.box.current_text == "Hello there!"

    app.input_state.release("CONFIRM")
    run_ticks(app, 30)  # let the typewriter fully reveal page 1
    app.input_state.tap("CONFIRM")  # already fully revealed -> advance to page 2
    run_ticks(app, 1)
    assert app.scene_stack.top.box.current_text == "Nice weather today."

    app.input_state.release("CONFIRM")
    run_ticks(app, 30)  # let the typewriter fully reveal page 2
    app.input_state.tap("CONFIRM")  # already fully revealed -> finish dialogue, pop back
    run_ticks(app, 1)
    assert app.scene_stack.top is scene


def test_warp_reloads_map_and_repositions_player(app):
    scene = push_overworld(app, spawn=(1, 2))
    app.input_state.press("UP")  # steps onto (1,1) which has a self-loop warp
    for _ in range(50):
        app.tick(1 / 60)
        if scene.fade.active:
            break
    app.input_state.release("UP")  # stop holding before the fade completes and repositions us
    for _ in range(60):
        app.tick(1 / 60)
        if not scene.fade.active:
            break
    assert scene.player.tile_pos == (8, 5)


def test_trainer_sightline_triggers_battle(app):
    scene = push_overworld(app, spawn=(6, 6), facing="UP")

    triggered = False
    for _ in range(6):
        app.input_state.press("UP")
        run_ticks(app, 20)
        app.input_state.release("UP")
        if isinstance(app.scene_stack.top, BattleScene):
            triggered = True
            break
    assert triggered
    assert app.scene_stack.top.trainer_npc is not None
    assert app.scene_stack.top.trainer_npc.trainer_id == "youngster_dale"


def test_trainer_marked_defeated_after_battle_resolves(app):
    # Stack the deck heavily in the player's favor so the win is deterministic.
    strong = app.state.party_manager.party[0]
    strong.level = 50
    strong.invalidate_stat_cache()
    strong.current_hp = strong.get_stats().hp

    scene = push_overworld(app, spawn=(6, 3), facing="DOWN")
    trainer_npc = next(n["trainer"] for n in scene.npcs if n["trainer"] is not None)
    assert trainer_npc.defeated is False

    for _ in range(6):
        app.input_state.press("DOWN")
        run_ticks(app, 20)
        app.input_state.release("DOWN")
        if isinstance(app.scene_stack.top, BattleScene):
            break
    assert isinstance(app.scene_stack.top, BattleScene)

    from scenes.battle import Phase

    def confirm():
        app.input_state.tap("CONFIRM")
        run_ticks(app, 1)
        app.input_state.release("CONFIRM")

    for _ in range(300):
        top = app.scene_stack.top
        if top is scene:
            break
        if top.phase in (Phase.MENU, Phase.MOVE_SELECT):
            top.menu.index = 0  # "Fight" from the menu, first move from the move list
        confirm()

    assert app.scene_stack.top is scene
    assert trainer_npc.defeated is True
    assert "youngster_dale" in app.state.defeated_trainers


def test_wild_encounter_triggers_battle(app, monkeypatch):
    import world.encounters as encounters_module

    monkeypatch.setattr(
        encounters_module,
        "_load_tables",
        lambda path=None: {
            "test_room_grass": {
                "entries": [{"species": "Rattata", "min_level": 2, "max_level": 4, "weight": 1}]
            }
        },
    )
    scene = push_overworld(app, spawn=(4, 3))

    def step(direction):
        app.input_state.press(direction)
        for _ in range(20):
            app.tick(1 / 60)
            if isinstance(app.scene_stack.top, BattleScene):
                return True
        app.input_state.release(direction)
        return False

    triggered = False
    for _ in range(200):
        if step("DOWN") or step("UP"):
            triggered = True
            break
    assert triggered
    assert app.scene_stack.top.wild["species"] == "Rattata"
    assert 2 <= app.scene_stack.top.wild["level"] <= 4


def test_healer_npc_restores_party_on_interact(app):
    from battle.pokemon import StatusCondition

    app.dialogue_text["test_nurse_heal"] = ["All better!"]
    mon = app.state.party_manager.party[0]
    mon.current_hp = 1
    mon.status = StatusCondition.POISON
    for lm in mon.moves:
        lm.current_pp = 0

    scene = push_overworld(app, spawn=(3, 5), facing="DOWN")
    app.input_state.tap("CONFIRM")
    run_ticks(app, 1)

    assert isinstance(app.scene_stack.top, DialogueScene)
    assert mon.current_hp == mon.get_stats().hp
    assert mon.status == StatusCondition.NONE
    assert all(lm.current_pp == lm.move.pp for lm in mon.moves)
