from save.schema import SaveData, PlayerState, CURRENT_SAVE_VERSION
from save.manager import SaveManager
from world.game_state import GameState


def test_save_data_round_trips_through_dict():
    data = SaveData(
        player=PlayerState(name="Ash", map_id="bramblegate_town", tile_x=3, tile_y=4),
        bag={"Potion": 3},
        badges=["bramblegate"],
        story_flags={"rival_stage": 1},
        defeated_trainers=["rival_1"],
        money=1500,
    )
    restored = SaveData.from_dict(data.to_dict())
    assert restored.player.name == "Ash"
    assert restored.player.map_id == "bramblegate_town"
    assert restored.bag == {"Potion": 3}
    assert restored.badges == ["bramblegate"]
    assert restored.story_flags == {"rival_stage": 1}
    assert restored.defeated_trainers == ["rival_1"]
    assert restored.money == 1500
    assert restored.version == CURRENT_SAVE_VERSION


def test_save_manager_writes_and_reads_json_file(tmp_path):
    manager = SaveManager(str(tmp_path))
    data = SaveData(player=PlayerState(name="Misty"))
    assert manager.has_save(1) is False
    manager.save(data, slot=1)
    assert manager.has_save(1) is True

    loaded = manager.load(slot=1)
    assert loaded.player.name == "Misty"


def test_save_manager_returns_none_for_missing_slot(tmp_path):
    manager = SaveManager(str(tmp_path))
    assert manager.load(slot=2) is None


def test_save_manager_delete(tmp_path):
    manager = SaveManager(str(tmp_path))
    manager.save(SaveData(), slot=1)
    assert manager.has_save(1) is True
    manager.delete(1)
    assert manager.has_save(1) is False


def test_game_state_defaults_to_empty_party_without_battle_package():
    state = GameState()
    assert state.party_manager.party == []
    assert state.money == 0


def test_game_state_round_trips_flags_and_bag():
    data = SaveData(story_flags={"badges": 2}, bag={"Poke Ball": 5}, money=250)
    state = GameState(data)
    assert state.story_flags.get("badges") == 2
    assert state.inventory.has("Poke Ball", 5)
    assert state.money == 250

    exported = state.to_save_data()
    assert exported.story_flags == {"badges": 2}
    assert exported.bag == {"Poke Ball": 5}
    assert exported.money == 250
