from battle.catching import (
    STATUS_BONUS, attempt_catch, attempt_catch_with_item, modified_catch_value,
)
from battle.natures import NATURES
from battle.pokemon import Gender, PokemonInstance, StatusCondition
from battle.schemas import (
    Ability, GenderRatio, GrowthRate, Item, ItemCategory, Species, Stat,
    StatBlock, Type,
)


def make_species(catch_rate=45):
    return Species(
        dex_number=1, name="Testmon", type1=Type.NORMAL, type2=None,
        base_stats=StatBlock(hp=100, attack=80, defense=70, sp_atk=60, sp_def=65, speed=90),
        abilities=("Keen Eye",), hidden_ability=None, gender_ratio=GenderRatio.GENDERLESS,
        base_catch_rate=catch_rate, base_exp_yield=64, ev_yield={Stat.SPEED: 1},
        growth_rate=GrowthRate.MEDIUM_FAST, learnset=(), evolutions=(),
    )


def make_pokemon(catch_rate=45, hp_fraction=1.0, status=StatusCondition.NONE):
    species = make_species(catch_rate=catch_rate)
    mon = PokemonInstance(
        species=species, level=50, current_exp=0,
        ivs=StatBlock(31, 31, 31, 31, 31, 31), evs=StatBlock(0, 0, 0, 0, 0, 0),
        nature=NATURES["Hardy"], ability=Ability(name="Keen Eye", flavor_text=""),
        held_item=None, current_hp=0, gender=Gender.GENDERLESS, status=status,
    )
    max_hp = mon.get_stats().hp
    mon.current_hp = max(1, int(max_hp * hp_fraction))
    return mon


class _FixedRng:
    def __init__(self, value):
        self.value = value

    def randint(self, a, b):
        return self.value


def test_hand_computed_modified_catch_value_full_hp_no_status():
    # hp_max=100, hp_current=100, catch_rate=255, Poke Ball (1.0), no status (10)
    # a = (300-200)*255*1.0 // 300 = 100*255 // 300 = 25500 // 300 = 85
    # a = (85*10)//10 = 85
    a = modified_catch_value(hp_max=100, hp_current=100, species_catch_rate=255, ball_bonus=1.0, status_bonus=10)
    assert a == 85


def test_hand_computed_modified_catch_value_low_hp_with_status_and_great_ball():
    # hp_max=100, hp_current=1, catch_rate=45, Great Ball (1.5), asleep (20)
    # a = (300-2)*45*1.5 // 300 = 298*67.5 // 300 = 20115 // 300 = 67
    # a = (67*20)//10 = 134
    a = modified_catch_value(hp_max=100, hp_current=1, species_catch_rate=45, ball_bonus=1.5, status_bonus=20)
    assert a == 134


def test_catch_value_capped_at_255():
    a = modified_catch_value(hp_max=100, hp_current=1, species_catch_rate=255, ball_bonus=2.0, status_bonus=20)
    assert a == 255


def test_attempt_catch_always_succeeds_at_or_above_255():
    hostile_rng = _FixedRng(65535)  # would fail every shake if the formula were actually evaluated
    assert attempt_catch(255, hostile_rng) is True
    assert attempt_catch(300, hostile_rng) is True


def test_attempt_catch_fails_when_any_shake_roll_meets_or_exceeds_b():
    # a=85 -> b is well under 65535, so a roll of 65535 always fails the first shake
    assert attempt_catch(85, _FixedRng(65535)) is False


def test_attempt_catch_succeeds_when_all_shake_rolls_are_zero():
    assert attempt_catch(85, _FixedRng(0)) is True


def test_status_bonus_table():
    assert STATUS_BONUS[StatusCondition.SLEEP] == 20
    assert STATUS_BONUS[StatusCondition.FREEZE] == 20
    assert STATUS_BONUS[StatusCondition.PARALYSIS] == 15
    assert STATUS_BONUS[StatusCondition.POISON] == 15
    assert STATUS_BONUS[StatusCondition.TOXIC] == 15
    assert STATUS_BONUS[StatusCondition.BURN] == 15
    assert STATUS_BONUS[StatusCondition.NONE] == 10


def test_master_ball_always_succeeds_bypassing_formula():
    master_ball = Item(name="Master Ball", category=ItemCategory.BALL, flavor_text="", catch_multiplier=255.0)
    mon = make_pokemon(catch_rate=3, hp_fraction=1.0)  # a legendary-tier low catch rate at full HP
    hostile_rng = _FixedRng(65535)
    assert attempt_catch_with_item(mon, master_ball, hostile_rng) is True


def test_poke_ball_low_catch_rate_full_hp_can_fail():
    poke_ball = Item(name="Poke Ball", category=ItemCategory.BALL, flavor_text="", catch_multiplier=1.0)
    mon = make_pokemon(catch_rate=3, hp_fraction=1.0)
    hostile_rng = _FixedRng(65535)
    assert attempt_catch_with_item(mon, poke_ball, hostile_rng) is False


def test_ball_bonus_improves_catch_value():
    mon = make_pokemon(catch_rate=45, hp_fraction=0.5)
    max_hp = mon.get_stats().hp
    a_poke = modified_catch_value(max_hp, mon.current_hp, 45, 1.0, 10)
    a_ultra = modified_catch_value(max_hp, mon.current_hp, 45, 2.0, 10)
    assert a_ultra > a_poke
