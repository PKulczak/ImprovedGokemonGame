import random

from battle.damage import (
    PHYSICAL_TYPES, SPECIAL_TYPES, calculate_damage, crit_chance,
    effective_crit_stat_stage,
)


class _FixedRng:
    """Stand-in RNG that always returns a fixed value for randint."""

    def __init__(self, value):
        self.value = value

    def randint(self, a, b):
        return self.value


def test_physical_special_type_split_totals_seventeen_with_status_excluded():
    assert len(PHYSICAL_TYPES) == 9
    assert len(SPECIAL_TYPES) == 8
    assert not (PHYSICAL_TYPES & SPECIAL_TYPES)


def test_hand_computed_neutral_stab_no_crit_min_roll():
    # level=50, power=80, atk=100, def=100, STAB, neutral type, roll=85 (min)
    # base = (2*50)//5+2 = 22
    # base = 22*80 = 1760
    # base = 1760*100 = 176000
    # base //= 100 -> 1760
    # base //= 50 -> 35
    # base += 2 -> 37
    # STAB: (37*3)//2 = 55
    # type mults neutral: unchanged -> 55
    # roll=85: (55*85)//100 = 46
    dmg = calculate_damage(
        level=50, power=80, atk_stat=100, def_stat=100, is_crit=False, is_stab=True,
        type1_mult=1.0, type2_mult=1.0, is_burn_halved=False, rng=_FixedRng(85),
    )
    assert dmg == 46


def test_hand_computed_neutral_stab_no_crit_max_roll():
    # same as above but roll=100: (55*100)//100 = 55
    dmg = calculate_damage(
        level=50, power=80, atk_stat=100, def_stat=100, is_crit=False, is_stab=True,
        type1_mult=1.0, type2_mult=1.0, is_burn_halved=False, rng=_FixedRng(100),
    )
    assert dmg == 55


def test_damage_falls_in_expected_range_across_rolls():
    for roll in range(85, 101):
        dmg = calculate_damage(
            level=50, power=80, atk_stat=100, def_stat=100, is_crit=False, is_stab=True,
            type1_mult=1.0, type2_mult=1.0, is_burn_halved=False, rng=_FixedRng(roll),
        )
        assert 46 <= dmg <= 55


def test_crit_doubles_pre_stab_base_gen3_style():
    no_crit = calculate_damage(
        level=50, power=80, atk_stat=100, def_stat=100, is_crit=False, is_stab=False,
        type1_mult=1.0, type2_mult=1.0, is_burn_halved=False, rng=_FixedRng(100),
    )
    crit = calculate_damage(
        level=50, power=80, atk_stat=100, def_stat=100, is_crit=True, is_stab=False,
        type1_mult=1.0, type2_mult=1.0, is_burn_halved=False, rng=_FixedRng(100),
    )
    # base (pre-roll) = 37; no crit -> 37; crit -> 74. Both scaled by roll=100/100=1.
    assert no_crit == 37
    assert crit == 74


def test_immunity_returns_zero_no_minimum_one():
    dmg = calculate_damage(
        level=50, power=80, atk_stat=100, def_stat=100, is_crit=False, is_stab=False,
        type1_mult=0.0, type2_mult=1.0, is_burn_halved=False, rng=_FixedRng(100),
    )
    assert dmg == 0


def test_super_effective_dual_type_applies_each_step():
    # 2x then 2x again = 4x
    dmg_4x = calculate_damage(
        level=50, power=80, atk_stat=100, def_stat=100, is_crit=False, is_stab=False,
        type1_mult=2.0, type2_mult=2.0, is_burn_halved=False, rng=_FixedRng(100),
    )
    dmg_1x = calculate_damage(
        level=50, power=80, atk_stat=100, def_stat=100, is_crit=False, is_stab=False,
        type1_mult=1.0, type2_mult=1.0, is_burn_halved=False, rng=_FixedRng(100),
    )
    assert dmg_4x == dmg_1x * 4


def test_burn_halves_final_damage():
    normal = calculate_damage(
        level=50, power=80, atk_stat=100, def_stat=100, is_crit=False, is_stab=False,
        type1_mult=1.0, type2_mult=1.0, is_burn_halved=False, rng=_FixedRng(100),
    )
    burned = calculate_damage(
        level=50, power=80, atk_stat=100, def_stat=100, is_crit=False, is_stab=False,
        type1_mult=1.0, type2_mult=1.0, is_burn_halved=True, rng=_FixedRng(100),
    )
    assert burned == normal // 2


def test_minimum_one_damage_floor():
    dmg = calculate_damage(
        level=1, power=1, atk_stat=1, def_stat=999, is_crit=False, is_stab=False,
        type1_mult=0.5, type2_mult=0.5, is_burn_halved=True, rng=_FixedRng(85),
    )
    assert dmg == 1


def test_crit_chance_table():
    assert crit_chance(0) == 1 / 16
    assert crit_chance(1) == 1 / 8
    assert crit_chance(2) == 1 / 4
    assert crit_chance(3) == 1 / 3
    assert crit_chance(10) == 1 / 3


def test_effective_crit_stat_stage_ignores_unfavorable():
    # Attacker with -2 Attack: crit ignores the drop (treated as 0)
    assert effective_crit_stat_stage(-2, is_attacker=True) == 0
    # Attacker with +3 Attack: crit still benefits from the boost
    assert effective_crit_stat_stage(3, is_attacker=True) == 3
    # Defender with +2 Defense: crit ignores the boost (treated as 0)
    assert effective_crit_stat_stage(2, is_attacker=False) == 0
    # Defender with -3 Defense: crit still benefits attacker from the drop
    assert effective_crit_stat_stage(-3, is_attacker=False) == -3


def test_random_roll_is_discrete_integer_in_range():
    rng = random.Random(42)
    seen = set()
    for _ in range(500):
        seen.add(rng.randint(85, 100))
    assert seen <= set(range(85, 101))
    assert min(seen) >= 85 and max(seen) <= 100
