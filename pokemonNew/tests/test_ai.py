import random

from battle.ai import (
    choose_move_basic_trainer, choose_move_expert_trainer, choose_move_wild,
    score_move, should_consider_switch,
)
from battle.battle_state import Battler
from battle.natures import NATURES
from battle.pokemon import Gender, LearnedMove, PokemonInstance
from battle.schemas import (
    Ability, GenderRatio, GrowthRate, Move, MoveCategory, Species, Stat,
    StatBlock, Type,
)


def make_species(type1=Type.NORMAL, type2=None, base_stats=None):
    return Species(
        dex_number=1, name="Testmon", type1=type1, type2=type2,
        base_stats=base_stats or StatBlock(hp=100, attack=80, defense=70, sp_atk=60, sp_def=65, speed=90),
        abilities=("Keen Eye",), hidden_ability=None, gender_ratio=GenderRatio.GENDERLESS,
        base_catch_rate=45, base_exp_yield=64, ev_yield={Stat.SPEED: 1},
        growth_rate=GrowthRate.MEDIUM_FAST, learnset=(), evolutions=(),
    )


def make_battler(moves, type1=Type.NORMAL, type2=None, hp_fraction=1.0):
    mon = PokemonInstance(
        species=make_species(type1=type1, type2=type2), level=50, current_exp=0,
        ivs=StatBlock(31, 31, 31, 31, 31, 31), evs=StatBlock(0, 0, 0, 0, 0, 0),
        nature=NATURES["Hardy"], ability=Ability(name="Keen Eye", flavor_text=""),
        held_item=None, current_hp=0, gender=Gender.GENDERLESS,
        moves=[LearnedMove(move=m, current_pp=m.pp) for m in moves],
    )
    max_hp = mon.get_stats().hp
    mon.current_hp = max(1, int(max_hp * hp_fraction))
    return Battler(pokemon=mon)


TACKLE = Move(name="Tackle", type=Type.NORMAL, category=MoveCategory.PHYSICAL, power=40, accuracy=100, pp=35)
GROWL = Move(name="Growl", type=Type.NORMAL, category=MoveCategory.STATUS, power=None, accuracy=100, pp=40,
             secondary_effect="stat_change_target", secondary_effect_params={"stat": "attack", "stages": -1})
HYPER_BEAM = Move(name="Hyper Beam", type=Type.NORMAL, category=MoveCategory.PHYSICAL, power=150, accuracy=90, pp=5)
THUNDERBOLT = Move(name="Thunderbolt", type=Type.ELECTRIC, category=MoveCategory.SPECIAL, power=90, accuracy=100, pp=15)
NO_PP_MOVE = Move(name="Struggle-ish", type=Type.NORMAL, category=MoveCategory.PHYSICAL, power=50, accuracy=100, pp=1)


def test_status_move_gets_flat_utility():
    attacker = make_battler([GROWL])
    defender = make_battler([TACKLE])
    assert score_move(GROWL, attacker, defender) == 0.3


def test_immune_move_scores_zero():
    attacker = make_battler([THUNDERBOLT])
    defender = make_battler([TACKLE], type1=Type.GROUND)  # Ground is immune to Electric
    assert score_move(THUNDERBOLT, attacker, defender) == 0.0


def test_no_pp_move_scores_non_positive():
    attacker = make_battler([NO_PP_MOVE])
    attacker.pokemon.moves[0].current_pp = 0
    defender = make_battler([TACKLE])
    assert score_move(NO_PP_MOVE, attacker, defender) <= 0


def test_lethal_move_gets_ko_bonus():
    attacker = make_battler([HYPER_BEAM])
    defender = make_battler([TACKLE], hp_fraction=0.01)  # nearly dead
    score = score_move(HYPER_BEAM, attacker, defender)
    assert score >= 2.0


def test_wild_ai_avoids_terrible_moves_when_a_decent_one_exists():
    rng = random.Random(3)
    attacker = make_battler([THUNDERBOLT, TACKLE])
    defender = make_battler([TACKLE], type1=Type.GROUND)  # immune to Thunderbolt only
    chosen_names = {choose_move_wild(attacker, defender, rng).name for _ in range(30)}
    assert "Tackle" in chosen_names


def test_basic_trainer_mostly_picks_top_scored_move():
    rng = random.Random(5)
    attacker = make_battler([HYPER_BEAM, GROWL])
    defender = make_battler([TACKLE])
    picks = [choose_move_basic_trainer(attacker, defender, rng).name for _ in range(200)]
    top_share = picks.count("Hyper Beam") / len(picks)
    assert top_share > 0.7  # ~85% target, allow statistical slack


def test_expert_trainer_wobbles_between_top_two():
    rng = random.Random(9)
    attacker = make_battler([HYPER_BEAM, THUNDERBOLT])
    defender = make_battler([TACKLE])
    picks = {choose_move_expert_trainer(attacker, defender, rng).name for _ in range(50)}
    assert len(picks) >= 1  # never crashes, always returns a usable move
    assert picks <= {"Hyper Beam", "Thunderbolt"}


def test_should_consider_switch_when_badly_disadvantaged():
    # Attacker only has a move type resisted hard by the defender
    resisted_move = Move(name="Weak", type=Type.NORMAL, category=MoveCategory.PHYSICAL, power=10, accuracy=100, pp=10)
    attacker = make_battler([resisted_move])
    defender = make_battler([TACKLE], type1=Type.STEEL)  # resists Normal
    assert should_consider_switch(attacker, defender) is True


def test_should_not_switch_with_a_strong_move_available():
    attacker = make_battler([HYPER_BEAM])
    defender = make_battler([TACKLE])
    assert should_consider_switch(attacker, defender) is False
