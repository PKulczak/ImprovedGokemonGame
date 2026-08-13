import random

from world.encounters import roll_encounter

TABLES = {
    "grass": {
        "entries": [
            {"species": "Rattata", "min_level": 2, "max_level": 4, "weight": 80},
            {"species": "Zigzagoon", "min_level": 2, "max_level": 4, "weight": 20},
        ]
    },
    "empty": {"entries": []},
}


def test_no_encounter_below_roll_threshold():
    rng = random.Random(1)
    # base_chance=0.0 means the gate roll can never succeed
    assert roll_encounter("grass", rng, base_chance=0.0, tables=TABLES) is None


def test_encounter_returns_species_and_level_in_range():
    rng = random.Random(1)
    result = roll_encounter("grass", rng, base_chance=1.0, tables=TABLES)
    assert result is not None
    assert result["species"] in ("Rattata", "Zigzagoon")
    assert 2 <= result["level"] <= 4


def test_unknown_table_returns_none():
    rng = random.Random(1)
    assert roll_encounter("nonexistent", rng, base_chance=1.0, tables=TABLES) is None


def test_empty_table_returns_none():
    rng = random.Random(1)
    assert roll_encounter("empty", rng, base_chance=1.0, tables=TABLES) is None


def test_deterministic_with_seeded_rng():
    result_a = roll_encounter("grass", random.Random(42), base_chance=1.0, tables=TABLES)
    result_b = roll_encounter("grass", random.Random(42), base_chance=1.0, tables=TABLES)
    assert result_a == result_b
