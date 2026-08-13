import random

from battle.battle_state import Battler
from battle.natures import NATURES
from battle.pokemon import Gender, PokemonInstance, StatusCondition
from battle.schemas import (
    Ability, GenderRatio, GrowthRate, Species, Stat, StatBlock, Type,
)
from battle.status import (
    Weather, can_act, can_be_statused, cure_status, effective_speed,
    inflict_status, status_tick_damage, weather_chip_damage,
    weather_power_multiplier,
)


def make_species(name="Testmon", type1=Type.NORMAL, type2=None, **overrides):
    base_stats = overrides.pop("base_stats", StatBlock(hp=100, attack=80, defense=70, sp_atk=60, sp_def=65, speed=90))
    return Species(
        dex_number=1, name=name, type1=type1, type2=type2, base_stats=base_stats,
        abilities=("Keen Eye",), hidden_ability=None, gender_ratio=GenderRatio.GENDERLESS,
        base_catch_rate=45, base_exp_yield=64, ev_yield={Stat.SPEED: 1}, growth_rate=GrowthRate.MEDIUM_FAST,
        learnset=(), evolutions=(), **overrides,
    )


def make_pokemon(species=None, level=50, ability_name="Keen Eye", **overrides):
    species = species or make_species()
    pokemon = PokemonInstance(
        species=species, level=level, current_exp=0,
        ivs=StatBlock(31, 31, 31, 31, 31, 31), evs=StatBlock(0, 0, 0, 0, 0, 0),
        nature=NATURES["Hardy"], ability=Ability(name=ability_name, flavor_text=""),
        held_item=None, current_hp=0, gender=Gender.GENDERLESS,
    )
    for k, v in overrides.items():
        setattr(pokemon, k, v)
    pokemon.current_hp = pokemon.get_stats().hp
    return pokemon


def test_fire_cannot_be_burned():
    mon = make_pokemon(species=make_species(type1=Type.FIRE))
    assert can_be_statused(mon, StatusCondition.BURN) is False
    assert inflict_status(mon, StatusCondition.BURN) is False
    assert mon.status == StatusCondition.NONE


def test_ice_cannot_be_frozen():
    mon = make_pokemon(species=make_species(type1=Type.ICE))
    assert can_be_statused(mon, StatusCondition.FREEZE) is False


def test_poison_and_steel_cannot_be_poisoned():
    mon = make_pokemon(species=make_species(type1=Type.POISON))
    assert can_be_statused(mon, StatusCondition.POISON) is False
    assert can_be_statused(mon, StatusCondition.TOXIC) is False
    mon2 = make_pokemon(species=make_species(type1=Type.STEEL))
    assert can_be_statused(mon2, StatusCondition.POISON) is False


def test_electric_can_be_paralyzed_no_gen6_immunity():
    mon = make_pokemon(species=make_species(type1=Type.ELECTRIC))
    assert can_be_statused(mon, StatusCondition.PARALYSIS) is True
    assert inflict_status(mon, StatusCondition.PARALYSIS, rng=random.Random(1)) is True


def test_grass_can_be_hit_by_powder_no_gen6_immunity():
    mon = make_pokemon(species=make_species(type1=Type.GRASS))
    assert can_be_statused(mon, StatusCondition.SLEEP) is True


def test_sleep_turns_are_1_to_4_and_wakes_and_can_act_same_turn():
    mon = make_pokemon()
    rng = random.Random(7)
    assert inflict_status(mon, StatusCondition.SLEEP, rng=rng) is True
    turns = mon.status_data["sleep_turns_remaining"]
    assert 1 <= turns <= 4

    battler = Battler(pokemon=mon)
    woke = False
    for _ in range(10):
        acted, events = can_act(battler, "player", rng)
        if mon.status == StatusCondition.NONE:
            woke = True
            assert acted is True  # wakes AND can act same turn
            break
    assert woke


def test_paralysis_quarters_speed_gen3_not_half():
    mon = make_pokemon()
    mon.status = StatusCondition.PARALYSIS
    battler = Battler(pokemon=mon)
    base_speed = mon.get_stats().speed
    assert effective_speed(battler) == max(1, base_speed // 4)


def test_full_paralysis_roll_blocks_action():
    mon = make_pokemon()
    mon.status = StatusCondition.PARALYSIS
    battler = Battler(pokemon=mon)

    class AlwaysFullPara:
        def random(self):
            return 0.0  # < 0.25 => full paralysis

        def randint(self, a, b):
            return a

    acted, events = can_act(battler, "player", AlwaysFullPara())
    assert acted is False


def test_confusion_self_hit_blocks_action_and_damages_self():
    mon = make_pokemon()
    battler = Battler(pokemon=mon)
    battler.confusion_turns_remaining = 3

    class AlwaysConfuseHit:
        def random(self):
            return 0.0  # < 1/3 => self-hit

        def randint(self, a, b):
            return a

    hp_before = mon.current_hp
    acted, events = can_act(battler, "player", AlwaysConfuseHit())
    assert acted is False
    assert mon.current_hp < hp_before
    assert battler.confusion_turns_remaining == 2


def test_confusion_wearing_off_skips_self_hit_roll():
    mon = make_pokemon()
    battler = Battler(pokemon=mon)
    battler.confusion_turns_remaining = 1  # will hit 0 this turn -> wears off

    class NeverConfuseHit:
        def random(self):
            return 0.999

        def randint(self, a, b):
            return a

    hp_before = mon.current_hp
    acted, events = can_act(battler, "player", NeverConfuseHit())
    assert battler.confusion_turns_remaining == 0
    assert mon.current_hp == hp_before
    assert acted is True


def test_cure_status_clears_status_and_data():
    mon = make_pokemon()
    mon.status = StatusCondition.POISON
    mon.status_data = {"foo": "bar"}
    cure_status(mon)
    assert mon.status == StatusCondition.NONE
    assert mon.status_data == {}


def test_status_tick_damage_burn_poison_are_eighth():
    mon = make_pokemon()
    battler = Battler(pokemon=mon)
    mon.status = StatusCondition.BURN
    assert status_tick_damage(battler) == max(1, mon.get_stats().hp // 8)
    mon.status = StatusCondition.POISON
    assert status_tick_damage(battler) == max(1, mon.get_stats().hp // 8)


def test_toxic_damage_scales_with_counter():
    mon = make_pokemon()
    battler = Battler(pokemon=mon)
    mon.status = StatusCondition.TOXIC
    battler.toxic_counter = 1
    dmg1 = status_tick_damage(battler)
    battler.toxic_counter = 2
    dmg2 = status_tick_damage(battler)
    max_hp = mon.get_stats().hp
    assert dmg1 == max(1, (max_hp * 1) // 16)
    assert dmg2 == max(1, (max_hp * 2) // 16)
    assert dmg2 >= dmg1


def test_weather_power_multiplier_rain_and_sun():
    assert weather_power_multiplier(Weather.RAIN, Type.WATER) == (3, 2)
    assert weather_power_multiplier(Weather.RAIN, Type.FIRE) == (1, 2)
    assert weather_power_multiplier(Weather.SUN, Type.FIRE) == (3, 2)
    assert weather_power_multiplier(Weather.SUN, Type.WATER) == (1, 2)
    assert weather_power_multiplier(Weather.NONE, Type.FIRE) == (1, 1)


def test_sandstorm_spares_rock_ground_steel():
    rock_mon = make_pokemon(species=make_species(type1=Type.ROCK))
    assert weather_chip_damage(Weather.SANDSTORM, rock_mon) == 0
    normal_mon = make_pokemon(species=make_species(type1=Type.NORMAL))
    assert weather_chip_damage(Weather.SANDSTORM, normal_mon) == max(1, normal_mon.get_stats().hp // 16)


def test_hail_spares_ice():
    ice_mon = make_pokemon(species=make_species(type1=Type.ICE))
    assert weather_chip_damage(Weather.HAIL, ice_mon) == 0
    normal_mon = make_pokemon(species=make_species(type1=Type.NORMAL))
    assert weather_chip_damage(Weather.HAIL, normal_mon) == max(1, normal_mon.get_stats().hp // 16)


def test_flinch_blocks_action_and_is_reported():
    mon = make_pokemon()
    battler = Battler(pokemon=mon)
    battler.flinched = True
    acted, events = can_act(battler, "player", random.Random(1))
    assert acted is False
