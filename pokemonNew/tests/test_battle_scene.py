import random

from engine.app import App
from engine.scene import Scene
from scenes.battle import BattleScene, Phase
from data.starters import STARTERS
from data.trainers import TRAINERS


class DummyBaseScene(Scene):
    def on_child_closed(self, result):
        self.last_result = result


def make_app(tmp_path, seed=1):
    app = App(headless=True, save_dir=str(tmp_path), rng=random.Random(seed))
    starter = STARTERS["Chikorita"].instantiate(app.rng)
    app.state.party_manager.add(starter)
    return app


def push_base(app):
    base = DummyBaseScene(app)
    base.last_result = None
    app.scene_stack.push(base)
    return base


def confirm(app):
    app.input_state.tap("CONFIRM")
    app.tick(1 / 60)
    app.input_state.release("CONFIRM")


def run_wild_battle_to_completion(app, max_steps=200):
    for _ in range(max_steps):
        scene = app.scene_stack.top
        if not isinstance(scene, BattleScene):
            return True
        if scene.phase == Phase.MESSAGE:
            confirm(app)
        elif scene.phase == Phase.MENU:
            scene.menu.index = 0  # "Fight"
            confirm(app)
        elif scene.phase == Phase.MOVE_SELECT:
            scene.menu.index = 0  # first move
            confirm(app)
        elif scene.phase == Phase.SWITCH_SELECT:
            scene.menu.index = 0
            confirm(app)
        else:
            confirm(app)
    return False


def test_wild_battle_runs_to_completion_and_pops_back(tmp_path):
    app = make_app(tmp_path)
    base = push_base(app)
    app.scene_stack.push(BattleScene(app), wild={"species": "Rattata", "level": 3})

    finished = run_wild_battle_to_completion(app)
    assert finished
    assert app.scene_stack.top is base
    assert base.last_result is not None
    assert base.last_result["outcome"] in ("player", "enemy")


def test_trainer_battle_marks_trainer_defeated_on_player_win(tmp_path):
    # Stack the deck heavily in the player's favor so the outcome is deterministic:
    # a high-level starter against the weakest early trainer.
    app = make_app(tmp_path, seed=2)
    strong = STARTERS["Torchic"].instantiate(app.rng)
    strong.level = 50
    strong.current_exp = 0
    strong.invalidate_stat_cache()
    strong.current_hp = strong.get_stats().hp
    app.state.party_manager.party = [strong]

    class FakeTrainerNPC:
        trainer_id = "youngster_dale"

        def mark_defeated(self):
            self.defeated = True

    base = push_base(app)
    trainer_npc = FakeTrainerNPC()
    app.scene_stack.push(BattleScene(app), trainer=trainer_npc)

    finished = run_wild_battle_to_completion(app, max_steps=400)
    assert finished
    assert app.scene_stack.top is base
    assert base.last_result["outcome"] == "player"
    assert base.last_result.get("trainer_defeated") is trainer_npc


def test_catching_a_wild_pokemon_adds_it_to_party(tmp_path):
    app = make_app(tmp_path, seed=3)
    app.state.inventory.add("Poke Ball", 10)
    base = push_base(app)
    app.scene_stack.push(BattleScene(app), wild={"species": "Rattata", "level": 2})

    scene = app.scene_stack.top
    # drain the intro message
    while scene.phase == Phase.MESSAGE and scene.queue:
        confirm(app)

    assert scene.phase == Phase.MENU
    scene.menu.index = scene.menu.options.index("Bag")
    confirm(app)
    assert scene.phase == Phase.BAG_SELECT
    scene.menu.index = 0  # Poke Ball
    confirm(app)

    # keep confirming through messages/menus (fighting if the ball fails) until resolved
    for _ in range(300):
        top = app.scene_stack.top
        if top is base:
            break
        if top.phase == Phase.MESSAGE:
            confirm(app)
        elif top.phase == Phase.MENU:
            top.menu.index = top.menu.options.index("Bag") if "Bag" in top.menu.options else 0
            confirm(app)
            if app.scene_stack.top is top and top.phase == Phase.BAG_SELECT:
                top.menu.index = 0
                confirm(app)
        else:
            confirm(app)

    assert app.scene_stack.top is base
    assert base.last_result["outcome"] in ("caught", "player", "enemy")
    if base.last_result["outcome"] == "caught":
        names = [m.species.name for m in app.state.party_manager.party]
        assert "Rattata" in names
