"""Cross-reference checks for the content-authoring workstream's four files:
data/species.py, data/moves.py, data/starters.py, data/trainers.py.

These are pure data-consistency checks (no pygame, no battle simulation):
    - SPECIES keys match roster_dex_map.ROSTER exactly (186 names, no more/fewer).
    - Every move name referenced anywhere (species learnsets, trainer
      movesets, starter movesets) exists in data.moves.MOVES.
    - Every Species.abilities / hidden_ability entry is a non-empty string.
    - Every TrainerPokemonPreset.species is the *same object* as the one in
      SPECIES (not an independently-constructed duplicate with the same
      name), and likewise for STARTERS.
    - Every EvolutionRule.target_dex_number resolves to a real roster entry.
"""

import pytest

from data.roster_dex_map import ROSTER
from data.species import SPECIES
from data.moves import MOVES
from data.starters import STARTERS
from data.trainers import TRAINERS


def test_species_keys_match_roster_exactly():
    assert set(SPECIES.keys()) == set(ROSTER.keys())
    assert len(SPECIES) == 186


def test_species_dex_numbers_match_roster():
    for name, species in SPECIES.items():
        assert species.dex_number == ROSTER[name], name
        assert species.name == name


def test_species_abilities_are_nonempty_strings():
    for name, species in SPECIES.items():
        assert species.abilities, f"{name} has no abilities"
        for ability in species.abilities:
            assert isinstance(ability, str) and ability, f"{name} has a blank ability"
        assert isinstance(species.hidden_ability, str) and species.hidden_ability, (
            f"{name} has a blank/missing hidden_ability"
        )


def test_species_learnset_moves_exist():
    missing = set()
    for name, species in SPECIES.items():
        for level, move_name in species.learnset:
            if move_name not in MOVES:
                missing.add((name, move_name))
    assert not missing, f"Learnset moves missing from MOVES: {sorted(missing)}"


def test_species_learnsets_ascend_by_level():
    for name, species in SPECIES.items():
        levels = [lvl for lvl, _ in species.learnset]
        assert levels == sorted(levels), f"{name} learnset is not ascending: {levels}"


def test_evolution_targets_resolve_to_real_roster_entries():
    dex_to_name = {dex: name for name, dex in ROSTER.items()}
    for name, species in SPECIES.items():
        for rule in species.evolutions:
            assert rule.target_dex_number in dex_to_name, (
                f"{name} has an evolution rule pointing at unknown dex "
                f"number {rule.target_dex_number}"
            )


def test_starters_are_exactly_the_three_from_the_plan():
    assert set(STARTERS.keys()) == {"Chikorita", "Torchic", "Oshawott"}
    for name, preset in STARTERS.items():
        assert preset.species is SPECIES[name]
        assert preset.level == 5
        assert preset.moves and 2 <= len(preset.moves) <= 4
        for mv in preset.moves:
            assert mv in MOVES, f"Starter {name} references unknown move {mv}"


def test_trainer_presets_reference_the_same_species_objects():
    for key, trainer in TRAINERS.items():
        assert trainer.team, f"Trainer {key} has an empty team"
        for preset in trainer.team:
            same_name_species = SPECIES.get(preset.species.name)
            assert same_name_species is not None, (
                f"Trainer {key} uses a species {preset.species.name!r} not in SPECIES"
            )
            assert preset.species is same_name_species, (
                f"Trainer {key}'s preset for {preset.species.name} is a "
                "rebuilt duplicate, not the SPECIES dict's object"
            )


def test_trainer_moves_exist_in_moves_dict():
    missing = set()
    for key, trainer in TRAINERS.items():
        for preset in trainer.team:
            if preset.moves:
                for mv in preset.moves:
                    if mv not in MOVES:
                        missing.add((key, preset.species.name, mv))
    assert not missing, f"Trainer moves missing from MOVES: {sorted(missing)}"


def test_trainers_have_flavor_text():
    for key, trainer in TRAINERS.items():
        assert trainer.pre_battle_text, f"Trainer {key} has no pre_battle_text"
        assert trainer.lose_text, f"Trainer {key} has no lose_text"


def test_expected_trainer_roster_sections_present():
    keys = set(TRAINERS.keys())
    for starter in ("chikorita", "torchic", "oshawott"):
        for stage in (1, 2, 3):
            assert f"rival_{starter}_{stage}" in keys
    for leader in ("wren", "bartle", "talia", "orin", "priscilla", "kade", "garrick", "serath"):
        assert f"gym_leader_{leader}" in keys
    for member in ("ivor", "maren", "zephyra", "draven"):
        assert f"elite_four_{member}" in keys
    assert "champion_astra" in keys
    assert "team_eclipse_nyx" in keys


@pytest.mark.parametrize("key", list(TRAINERS.keys()))
def test_every_trainer_team_nonempty_and_levels_positive(key):
    trainer = TRAINERS[key]
    assert len(trainer.team) >= 1
    for preset in trainer.team:
        assert 1 <= preset.level <= 100
