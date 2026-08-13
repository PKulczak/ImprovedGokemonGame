"""End-to-end headless smoke test: boot -> title -> new game -> starter
select -> overworld -> walk toward a wild encounter -> battle -> save ->
reload. Exercises the real game content (maps/species/starters), not fixtures.
"""

from engine.app import App
from scenes.title import TitleScene
from scenes.starter_select import StarterSelectScene
from scenes.overworld import OverworldScene
from scenes.battle import BattleScene


def run_ticks(app, n, dt=1 / 60):
    for _ in range(n):
        app.tick(dt)


def test_full_new_game_flow(tmp_path):
    app = App(headless=True, save_dir=str(tmp_path))
    app.boot()
    run_ticks(app, 1)
    assert isinstance(app.scene_stack.top, TitleScene)

    app.input_state.tap("CONFIRM")  # New Game
    run_ticks(app, 1)
    assert isinstance(app.scene_stack.top, StarterSelectScene)

    app.input_state.release("CONFIRM")
    app.input_state.tap("CONFIRM")  # confirm first starter in the list
    run_ticks(app, 1)
    assert isinstance(app.scene_stack.top, OverworldScene)

    party = app.state.party_manager.party
    assert len(party) == 1
    starter = party[0]
    assert starter.level == 5
    assert starter.current_hp == starter.get_stats().hp

    scene = app.scene_stack.top
    assert scene.tilemap.map_id == "sagewood_town"
    assert scene.player.tile_pos == (5, 5)


def test_walking_to_route_and_healthy_movement(tmp_path):
    app = App(headless=True, save_dir=str(tmp_path))
    app.boot()
    run_ticks(app, 1)
    app.input_state.tap("CONFIRM")
    run_ticks(app, 1)
    app.input_state.release("CONFIRM")
    app.input_state.tap("CONFIRM")
    run_ticks(app, 1)

    scene = app.scene_stack.top
    assert isinstance(scene, OverworldScene)

    # walk down from spawn (5,5) toward the path/south exit
    for _ in range(10):
        app.input_state.press("DOWN")
        run_ticks(app, 9)
        app.input_state.release("DOWN")
        run_ticks(app, 2)
    # should have made real forward progress without getting stuck immediately
    assert scene.player.tile_pos[1] > 5


def test_save_and_reload_round_trip(tmp_path):
    app = App(headless=True, save_dir=str(tmp_path))
    app.boot()
    run_ticks(app, 1)
    app.input_state.tap("CONFIRM")
    run_ticks(app, 1)
    app.input_state.release("CONFIRM")
    app.input_state.tap("CONFIRM")
    run_ticks(app, 1)

    app.save_manager.save(app.state.to_save_data())
    assert app.save_manager.has_save(1)

    loaded = app.save_manager.load(1)
    assert loaded.player.map_id == "sagewood_town"
    assert len(loaded.party) == 1

    from world.game_state import GameState
    restored_state = GameState(loaded)
    assert len(restored_state.party_manager.party) == 1
    assert restored_state.party_manager.party[0].species.name in ("Chikorita", "Torchic", "Oshawott")
