from world.story_flags import StoryFlags, evaluate_condition


def test_get_set_default():
    flags = StoryFlags()
    assert flags.get("badges") is None
    assert flags.get("badges", 0) == 0
    flags.set("badges", 3)
    assert flags.get("badges") == 3


def test_increment():
    flags = StoryFlags()
    assert flags.increment("rival_stage") == 1
    assert flags.increment("rival_stage") == 2


def test_round_trip_dict():
    flags = StoryFlags({"badges": 2, "met_rival": True})
    data = flags.to_dict()
    restored = StoryFlags.from_dict(data)
    assert restored.get("badges") == 2
    assert restored.get("met_rival") is True


def test_condition_none_is_always_true():
    assert evaluate_condition(None, StoryFlags()) is True


def test_condition_comparisons():
    flags = StoryFlags({"badges": 3})
    assert evaluate_condition({"flag": "badges", "op": ">=", "value": 3}, flags) is True
    assert evaluate_condition({"flag": "badges", "op": ">=", "value": 4}, flags) is False
    assert evaluate_condition({"flag": "badges", "op": "==", "value": 3}, flags) is True
    assert evaluate_condition({"flag": "badges", "op": "!=", "value": 3}, flags) is False


def test_condition_in_operator():
    flags = StoryFlags({"story_stage": "eclipse_intro"})
    cond = {"flag": "story_stage", "op": "in", "value": ["eclipse_intro", "eclipse_mid"]}
    assert evaluate_condition(cond, flags) is True
