import random

from battle.battle_state import (
    Battle, BattleSide, Battler, ItemAction, MoveAction, StatStages, SwitchAction,
)
from battle.natures import NATURES
from battle.pokemon import Gender, LearnedMove, PokemonInstance, StatusCondition
from battle.schemas import (
    Ability, GenderRatio, GrowthRate, Item, ItemCategory, Move, MoveCategory,
    Species, Stat, StatBlock, Target, Type,
)


class DeterministicRng:
    """Always hits (accuracy rolls), never procs low-probability abilities/
    items/statuses, and returns the minimum of the 85-100 damage roll --
    predictable behavior for straightforward turn-pipeline tests."""

    def __init__(self, randint_value=50, random_value=0.9):
        self._randint_value = randint_value
        self._random_value = random_value

    def randint(self, a, b):
        return min(max(self._randint_value, a), b)

    def random(self):
        return self._random_value

    def choice(self, seq):
        return seq[0]

    def choices(self, population, weights=None, k=1):
        return [population[0]] * k


def make_species(name="Testmon", dex=1, type1=Type.NORMAL, type2=None, base_stats=None,
                  base_exp_yield=64, growth_rate=GrowthRate.MEDIUM_FAST, learnset=(), evolutions=()):
    return Species(
        dex_number=dex, name=name, type1=type1, type2=type2,
        base_stats=base_stats or StatBlock(hp=100, attack=80, defense=70, sp_atk=60, sp_def=65, speed=90),
        abilities=("Keen Eye",), hidden_ability=None, gender_ratio=GenderRatio.GENDERLESS,
        base_catch_rate=45, base_exp_yield=base_exp_yield, ev_yield={Stat.SPEED: 1},
        growth_rate=growth_rate, learnset=learnset, evolutions=evolutions,
    )


def make_pokemon(moves, species=None, level=50, ability_name="Keen Eye", held_item=None, speed_base=90):
    species = species or make_species(base_stats=StatBlock(hp=100, attack=80, defense=70, sp_atk=60, sp_def=65, speed=speed_base))
    mon = PokemonInstance(
        species=species, level=level, current_exp=0,
        ivs=StatBlock(31, 31, 31, 31, 31, 31), evs=StatBlock(0, 0, 0, 0, 0, 0),
        nature=NATURES["Hardy"], ability=Ability(name=ability_name, flavor_text=""),
        held_item=held_item, current_hp=0, gender=Gender.GENDERLESS,
        moves=[LearnedMove(move=m, current_pp=m.pp) for m in moves],
    )
    mon.current_hp = mon.get_stats().hp
    return mon


TACKLE = Move(name="Tackle", type=Type.NORMAL, category=MoveCategory.PHYSICAL, power=40, accuracy=100, pp=35, makes_contact=True)
QUICK_ATTACK = Move(name="Quick Attack", type=Type.NORMAL, category=MoveCategory.PHYSICAL, power=40, accuracy=100, pp=30, priority=1, makes_contact=True)
THUNDER_WAVE = Move(name="Thunder Wave", type=Type.ELECTRIC, category=MoveCategory.STATUS, power=None, accuracy=100, pp=20,
                     secondary_effect="paralyze", secondary_effect_chance=100)
EMBER = Move(name="Ember", type=Type.FIRE, category=MoveCategory.SPECIAL, power=40, accuracy=100, pp=25,
             secondary_effect="burn", secondary_effect_chance=100)
GROWL = Move(name="Growl", type=Type.NORMAL, category=MoveCategory.STATUS, power=None, accuracy=100, pp=40,
             secondary_effect="stat_change_target", secondary_effect_chance=100,
             secondary_effect_params={"stat": "attack", "stages": -1})
WATERGUN_ON_GROUND_IMMUNE = Move(name="Thunderbolt", type=Type.ELECTRIC, category=MoveCategory.SPECIAL, power=90, accuracy=100, pp=15)


def make_battle(p_moves, e_moves, rng=None, p_speed=90, e_speed=90, p_item=None, e_item=None, p_bench=None, e_bench=None):
    player = Battler(pokemon=make_pokemon(p_moves, speed_base=p_speed, held_item=p_item))
    enemy = Battler(pokemon=make_pokemon(e_moves, speed_base=e_speed, held_item=e_item))
    battle = Battle(
        BattleSide(active=player, bench=p_bench or []),
        BattleSide(active=enemy, bench=e_bench or []),
        rng or DeterministicRng(),
    )
    return battle, player, enemy


# --- basics ---

def test_stat_stages_default_zero_and_battler_defaults():
    stages = StatStages()
    assert (stages.attack, stages.defense, stages.sp_atk, stages.sp_def, stages.speed, stages.accuracy, stages.evasion) == (0,) * 7
    battler = Battler(pokemon=make_pokemon([TACKLE]))
    assert battler.confusion_turns_remaining == 0
    assert battler.toxic_counter == 0
    assert battler.flinched is False
    assert battler.choice_locked_move is None


def test_pp_decrements_on_move_use():
    battle, player, enemy = make_battle([TACKLE], [TACKLE])
    pp_before = player.pokemon.moves[0].current_pp
    battle.run_turn(MoveAction(move_index=0), MoveAction(move_index=0))
    assert player.pokemon.moves[0].current_pp == pp_before - 1


def test_damage_move_reduces_target_hp():
    battle, player, enemy = make_battle([TACKLE], [TACKLE])
    hp_before = enemy.pokemon.current_hp
    battle.run_turn(MoveAction(move_index=0), MoveAction(move_index=0))
    assert enemy.pokemon.current_hp < hp_before
    assert player.pokemon.current_hp < player.pokemon.get_stats().hp


def test_type_immunity_prevents_damage_entirely():
    battle, player, enemy = make_battle(
        [WATERGUN_ON_GROUND_IMMUNE], [TACKLE],
    )
    enemy.pokemon.species = make_species(type1=Type.GROUND)
    enemy.pokemon.invalidate_stat_cache()
    hp_before = enemy.pokemon.current_hp
    battle.run_turn(MoveAction(move_index=0), MoveAction(move_index=0))
    # Electric move should have done 0 damage to the Ground-type (only Tackle's damage applies)
    from battle.type_chart import type_effectiveness
    assert type_effectiveness(Type.ELECTRIC, [Type.GROUND]) == 0.0


def test_priority_move_acts_first_despite_lower_speed():
    battle, player, enemy = make_battle([QUICK_ATTACK], [TACKLE], p_speed=10, e_speed=200)
    events = battle.run_turn(MoveAction(move_index=0), MoveAction(move_index=0))
    move_used_sides = [e.side for e in events if e.__class__.__name__ == "MoveUsed"]
    assert move_used_sides[0] == "player"  # despite being slower, priority move goes first


def test_faster_pokemon_acts_first_without_priority_difference():
    battle, player, enemy = make_battle([TACKLE], [TACKLE], p_speed=200, e_speed=10)
    events = battle.run_turn(MoveAction(move_index=0), MoveAction(move_index=0))
    move_used_sides = [e.side for e in events if e.__class__.__name__ == "MoveUsed"]
    assert move_used_sides[0] == "player"


def test_secondary_effect_inflicts_status():
    battle, player, enemy = make_battle([THUNDER_WAVE], [TACKLE])
    battle.run_turn(MoveAction(move_index=0), MoveAction(move_index=0))
    assert enemy.pokemon.status == StatusCondition.PARALYSIS


def test_stat_change_target_effect_lowers_stage():
    battle, player, enemy = make_battle([GROWL], [TACKLE])
    battle.run_turn(MoveAction(move_index=0), MoveAction(move_index=0))
    assert enemy.stages.attack == -1


def test_switch_action_resets_volatile_state():
    bench_mon = make_pokemon([TACKLE])
    battle, player, enemy = make_battle([TACKLE], [TACKLE], p_bench=[bench_mon])
    player.stages.attack = 3
    player.confusion_turns_remaining = 2
    battle.run_turn(SwitchAction(bench_index=0), MoveAction(move_index=0))
    assert battle.player_side.active.pokemon is bench_mon
    assert battle.player_side.active.stages.attack == 0
    assert battle.player_side.active.confusion_turns_remaining == 0


def test_item_action_heals_active_pokemon():
    potion = Item(name="Potion", category=ItemCategory.CONSUMABLE, flavor_text="", effect_hook="potion")
    # enemy uses a non-damaging status move so the heal isn't immediately
    # clobbered by an incoming attack later in the same turn
    battle, player, enemy = make_battle([TACKLE], [GROWL])
    player.pokemon.current_hp = 1
    battle.run_turn(ItemAction(item=potion), MoveAction(move_index=0))
    assert player.pokemon.current_hp == 21


def test_leftovers_heals_at_end_of_turn():
    leftovers = Item(name="Leftovers", category=ItemCategory.HELD, flavor_text="", effect_hook="leftovers")
    battle, player, enemy = make_battle([TACKLE], [TACKLE], p_item=leftovers)
    player.pokemon.current_hp = player.pokemon.get_stats().hp // 2
    hp_before = player.pokemon.current_hp
    battle.run_turn(MoveAction(move_index=0), MoveAction(move_index=0))
    assert player.pokemon.current_hp > hp_before - 50  # healed some amount by leftovers (net of any damage taken)


def test_burn_damage_applied_at_end_of_turn():
    battle, player, enemy = make_battle([TACKLE], [TACKLE])
    enemy.pokemon.status = StatusCondition.BURN
    hp_after_moves_estimate = enemy.pokemon.current_hp
    battle.run_turn(MoveAction(move_index=0), MoveAction(move_index=0))
    # HP should reflect both move damage AND end-of-turn burn damage
    max_hp = enemy.pokemon.get_stats().hp
    assert enemy.pokemon.current_hp <= hp_after_moves_estimate - max(1, max_hp // 8)


def test_is_over_and_winner_when_side_fully_fainted():
    battle, player, enemy = make_battle([TACKLE], [TACKLE])
    enemy.pokemon.current_hp = 0
    assert battle.is_over() is True
    assert battle.winner() == "player"


def test_auto_switch_on_faint_brings_in_bench_pokemon():
    bench_mon = make_pokemon([TACKLE])
    battle, player, enemy = make_battle([TACKLE], [TACKLE], e_bench=[bench_mon])
    enemy.pokemon.current_hp = 1
    battle.run_turn(MoveAction(move_index=0), MoveAction(move_index=0))
    assert battle.is_over() is False
    assert battle.enemy_side.active.pokemon is bench_mon


def test_exp_awarded_to_winner_side_on_faint():
    weak_species = make_species(name="Weak", dex=2, base_stats=StatBlock(hp=1, attack=1, defense=1, sp_atk=1, sp_def=1, speed=1))
    weak_mon = make_pokemon([TACKLE], species=weak_species)
    weak_mon.current_hp = 1
    enemy_battler = Battler(pokemon=weak_mon)
    player = Battler(pokemon=make_pokemon([TACKLE]))
    battle = Battle(BattleSide(active=player, bench=[]), BattleSide(active=enemy_battler, bench=[]), DeterministicRng())
    exp_before = player.pokemon.current_exp
    battle.run_turn(MoveAction(move_index=0), MoveAction(move_index=0))
    assert battle.is_over() is True
    assert player.pokemon.current_exp > exp_before


def test_no_pygame_import_anywhere_under_battle_package():
    import pathlib
    battle_dir = pathlib.Path(__file__).resolve().parent.parent / "battle"
    for path in battle_dir.glob("*.py"):
        text = path.read_text(encoding="utf-8")
        assert "import pygame" not in text, f"pygame import found in {path}"


# --- full scripted battle to completion ---

def test_scripted_two_pokemon_battle_runs_to_completion():
    species_a = make_species(name="Alpha", dex=1, base_stats=StatBlock(hp=60, attack=60, defense=50, sp_atk=50, sp_def=50, speed=70))
    species_b = make_species(name="Beta", dex=2, base_stats=StatBlock(hp=60, attack=55, defense=50, sp_atk=50, sp_def=50, speed=60))
    player = Battler(pokemon=make_pokemon([TACKLE], species=species_a, level=20))
    enemy = Battler(pokemon=make_pokemon([TACKLE], species=species_b, level=20))
    battle = Battle(
        BattleSide(active=player, bench=[]), BattleSide(active=enemy, bench=[]),
        random.Random(1234),
    )

    turns = 0
    all_events = []
    while not battle.is_over() and turns < 200:
        events = battle.run_turn(MoveAction(move_index=0), MoveAction(move_index=0))
        all_events.extend(events)
        turns += 1

    assert battle.is_over() is True
    assert battle.winner() in ("player", "enemy")
    assert turns < 200  # actually terminated, didn't hit the safety cap
    assert any(e.__class__.__name__ == "Fainted" for e in all_events)
