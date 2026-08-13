"""Headless integration test walking through the REAL authored world (not
fixtures): new game -> Sagewood Town -> Route 101 -> Bramblegate Town.
Exercises the real maps/species/trainers content end to end.
"""

from engine.app import App
from scenes.overworld import OverworldScene


def run_ticks(app, n, dt=1 / 60):
    for _ in range(n):
        app.tick(dt)


def start_new_game(app):
    app.boot()
    run_ticks(app, 1)
    app.input_state.tap("CONFIRM")  # New Game
    run_ticks(app, 1)
    app.input_state.release("CONFIRM")
    app.input_state.tap("CONFIRM")  # confirm first starter
    run_ticks(app, 1)
    app.input_state.release("CONFIRM")
    return app.scene_stack.top


def walk(app, scene, direction, steps=1):
    for _ in range(steps):
        app.input_state.press(direction)
        run_ticks(app, 9)
        app.input_state.release(direction)
        run_ticks(app, 2)


def test_new_game_spawns_in_sagewood_town(tmp_path):
    app = App(headless=True, save_dir=str(tmp_path))
    scene = start_new_game(app)
    assert isinstance(scene, OverworldScene)
    assert scene.tilemap.map_id == "sagewood_town"
    assert scene.player.tile_pos == (5, 5)


def test_walking_south_out_of_sagewood_reaches_route_101(tmp_path):
    app = App(headless=True, save_dir=str(tmp_path))
    scene = start_new_game(app)

    # walk down to the south exit gap (8, 13) from spawn (5, 5)
    walk(app, scene, "DOWN", steps=1)  # onto the path spine at y=6
    walk(app, scene, "RIGHT", steps=3)  # toward x=8
    for _ in range(20):
        if scene.tilemap.map_id == "route_101":
            break
        walk(app, scene, "DOWN", steps=1)

    assert scene.tilemap.map_id == "route_101"


def test_full_route_101_to_bramblegate_town(tmp_path):
    app = App(headless=True, save_dir=str(tmp_path))
    scene = start_new_game(app)

    # Proven path out of Sagewood: onto the path spine, then across to the south exit column.
    walk(app, scene, "DOWN", steps=1)
    walk(app, scene, "RIGHT", steps=3)
    for _ in range(20):
        if scene.tilemap.map_id == "route_101":
            break
        walk(app, scene, "DOWN", steps=1)
    assert scene.tilemap.map_id == "route_101"

    # The warp lands the player already on Route 101's own path spine, so a
    # straight walk south should reach the next town.
    reached_bramblegate = False
    for _ in range(80):
        if scene.tilemap.map_id == "bramblegate_town":
            reached_bramblegate = True
            break
        walk(app, scene, "DOWN", steps=1)

    assert reached_bramblegate
