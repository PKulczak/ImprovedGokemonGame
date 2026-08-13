from battle.schemas import Stat, StatBlock
from battle.stats import (
    apply_stat_stage, accuracy_stage_multiplier, calc_all_stats, calc_hp,
    calc_stat, clamp_ev_gain, hidden_power, nature_modifier, stat_stage_multiplier,
)
from battle.natures import NATURES


def test_hp_formula_hand_computed():
    # base=100, iv=31, ev=0, level=50
    # HP = floor((2*100+31+0)*50/100) + 50 + 10
    #    = floor(231*50/100) + 60 = floor(115.5) + 60 = 115 + 60 = 175
    assert calc_hp(base=100, iv=31, ev=0, level=50) == 175


def test_non_hp_stat_formula_hand_computed_raised():
    # base=100, iv=31, ev=0, level=50, Adamant raises Attack (x1.10)
    # pre_nature = floor((2*100+31+0)*50/100) + 5 = floor(11550/100) + 5 = 115+5=120
    # final = floor(120 * 110 / 100) = floor(13200/100) = 132
    adamant = NATURES["Adamant"]
    assert calc_stat(base=100, iv=31, ev=0, level=50, nature=adamant, stat=Stat.ATTACK) == 132


def test_non_hp_stat_formula_hand_computed_lowered_with_evs():
    # base=100, iv=31, ev=252, level=100, Modest LOWERS Attack (x0.90)
    # pre_nature = floor((2*100+31+63)*100/100) + 5 = 294 + 5 = 299
    # final = floor(299 * 90 / 100) = floor(26910/100) = 269
    modest = NATURES["Modest"]
    assert calc_stat(base=100, iv=31, ev=252, level=100, nature=modest, stat=Stat.ATTACK) == 269


def test_neutral_nature_no_change():
    hardy = NATURES["Hardy"]
    # pre_nature = floor((2*100+31+0)*50/100)+5 = 120, neutral nature -> unchanged
    assert calc_stat(base=100, iv=31, ev=0, level=50, nature=hardy, stat=Stat.ATTACK) == 120


def test_nature_modifier_table():
    adamant = NATURES["Adamant"]
    assert nature_modifier(Stat.ATTACK, adamant) == (110, 100)
    assert nature_modifier(Stat.SP_ATK, adamant) == (90, 100)
    assert nature_modifier(Stat.SPEED, adamant) == (100, 100)


def test_calc_all_stats_matches_individual_calls():
    base = StatBlock(hp=100, attack=100, defense=80, sp_atk=90, sp_def=85, speed=95)
    ivs = StatBlock(31, 31, 31, 31, 31, 31)
    evs = StatBlock(0, 0, 0, 0, 0, 0)
    nature = NATURES["Adamant"]
    result = calc_all_stats(base, ivs, evs, 50, nature)
    assert result.hp == calc_hp(100, 31, 0, 50)
    assert result.attack == calc_stat(100, 31, 0, 50, nature, Stat.ATTACK)
    assert result.speed == calc_stat(95, 31, 0, 50, nature, Stat.SPEED)


def test_ev_clamp_per_stat_and_total():
    evs = StatBlock(0, 0, 0, 0, 0, 0)
    evs = clamp_ev_gain(evs, Stat.ATTACK, 300)  # over the 252-per-stat cap
    assert evs.attack == 252
    evs = clamp_ev_gain(evs, Stat.DEFENSE, 300)  # also clamped to 252 (504 total so far)
    assert evs.defense == 252
    assert evs.attack + evs.defense == 504
    evs = clamp_ev_gain(evs, Stat.SPEED, 300)  # only 6 EVs of "room" left under the 510 total cap
    assert evs.speed == 6
    assert evs.attack + evs.defense + evs.speed == 510


def test_stat_stage_multipliers_gen3_table():
    assert stat_stage_multiplier(0) == (2, 2)
    assert stat_stage_multiplier(1) == (3, 2)
    assert stat_stage_multiplier(-1) == (2, 3)
    assert stat_stage_multiplier(6) == (8, 2)
    assert stat_stage_multiplier(-6) == (2, 8)
    assert apply_stat_stage(100, 1) == 150
    assert apply_stat_stage(100, -1) == 66


def test_accuracy_stage_multiplier_uses_thirds():
    assert accuracy_stage_multiplier(0) == (3, 3)
    assert accuracy_stage_multiplier(1) == (4, 3)
    assert accuracy_stage_multiplier(-1) == (3, 4)


def test_hidden_power_returns_type_and_power_in_range():
    ivs = StatBlock(hp=31, attack=31, defense=31, sp_atk=31, sp_def=31, speed=31)
    htype, power = hidden_power(ivs)
    assert 30 <= power <= 70
    assert htype is not None
