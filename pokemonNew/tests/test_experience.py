from battle.experience import (
    apply_exp_gain, apply_evolution, award_exp_and_evs, check_level_up_evolution,
    exp_threshold, exp_yield, moves_to_learn, try_item_evolution,
)
from battle.natures import NATURES
from battle.pokemon import Gender, PokemonInstance
from battle.schemas import (
    Ability, EvolutionRule, EvolutionTrigger, GenderRatio, GrowthRate, Species,
    Stat, StatBlock, Type,
)


def make_species(name="Testmon", dex=1, growth_rate=GrowthRate.MEDIUM_FAST, learnset=(), evolutions=(), base_exp_yield=64, ev_yield=None):
    return Species(
        dex_number=dex, name=name, type1=Type.NORMAL, type2=None,
        base_stats=StatBlock(hp=100, attack=80, defense=70, sp_atk=60, sp_def=65, speed=90),
        abilities=("Keen Eye",), hidden_ability=None, gender_ratio=GenderRatio.GENDERLESS,
        base_catch_rate=45, base_exp_yield=base_exp_yield, ev_yield=ev_yield or {Stat.SPEED: 2},
        growth_rate=growth_rate, learnset=learnset, evolutions=evolutions,
    )


def make_pokemon(species, level=10):
    mon = PokemonInstance(
        species=species, level=level, current_exp=0,
        ivs=StatBlock(31, 31, 31, 31, 31, 31), evs=StatBlock(0, 0, 0, 0, 0, 0),
        nature=NATURES["Hardy"], ability=Ability(name="Keen Eye", flavor_text=""),
        held_item=None, current_hp=0, gender=Gender.GENDERLESS,
    )
    mon.current_hp = mon.get_stats().hp
    return mon


def test_fast_growth_curve_hand_computed():
    # floor(0.8 * 10^3) = floor(800) = 800
    assert exp_threshold(GrowthRate.FAST, 10) == 800


def test_medium_fast_growth_curve_hand_computed():
    assert exp_threshold(GrowthRate.MEDIUM_FAST, 10) == 1000


def test_medium_slow_growth_curve_hand_computed():
    # 1.2*1000 - 15*100 + 100*10 - 140 = 1200-1500+1000-140 = 560
    assert exp_threshold(GrowthRate.MEDIUM_SLOW, 10) == 560


def test_medium_slow_clamps_negative_at_level_1():
    # 1.2 - 15 + 100 - 140 = -53.8, must clamp to 0 (documented real quirk)
    assert exp_threshold(GrowthRate.MEDIUM_SLOW, 1) == 0


def test_slow_growth_curve_hand_computed():
    # floor(1.25 * 1000) = 1250
    assert exp_threshold(GrowthRate.SLOW, 10) == 1250


def test_exp_yield_wild_and_trainer_hand_computed():
    # floor(64 * 50 / 7) = floor(457.142857) = 457
    assert exp_yield(64, 50, trainer_battle=False) == 457
    # floor(457.142857 * 1.5) = floor(685.714) = 685
    assert exp_yield(64, 50, trainer_battle=True) == 685


def test_moves_to_learn_returns_only_newly_crossed_levels():
    species = make_species(learnset=((5, "Tackle"), (10, "Growl"), (15, "Ember")))
    assert moves_to_learn(species, old_level=4, new_level=10) == ["Tackle", "Growl"]
    assert moves_to_learn(species, old_level=10, new_level=10) == []
    assert moves_to_learn(species, old_level=9, new_level=20) == ["Growl", "Ember"]


def test_apply_exp_gain_levels_up_and_scales_current_hp():
    species = make_species(growth_rate=GrowthRate.MEDIUM_FAST)
    mon = make_pokemon(species, level=9)
    old_max_hp = mon.get_stats().hp
    mon.current_hp = old_max_hp  # full HP before leveling
    needed = exp_threshold(GrowthRate.MEDIUM_FAST, 10) - mon.current_exp
    result = apply_exp_gain(mon, needed)
    assert result["leveled_up"] is True
    assert mon.level == 10
    new_max_hp = mon.get_stats().hp
    assert new_max_hp > old_max_hp
    assert mon.current_hp == new_max_hp  # was full before, stays full


def test_apply_exp_gain_no_level_up_for_small_amount():
    species = make_species(growth_rate=GrowthRate.MEDIUM_FAST)
    mon = make_pokemon(species, level=10)
    result = apply_exp_gain(mon, 1)
    assert result["leveled_up"] is False
    assert mon.level == 10


def test_apply_exp_gain_surfaces_learnable_moves_without_forcing():
    species = make_species(growth_rate=GrowthRate.MEDIUM_FAST, learnset=((11, "Quick Attack"),))
    mon = make_pokemon(species, level=10)
    needed = exp_threshold(GrowthRate.MEDIUM_FAST, 11) - mon.current_exp
    result = apply_exp_gain(mon, needed)
    assert result["new_level"] == 11
    assert "Quick Attack" in result["learnable_moves"]
    assert len(mon.moves) == 0  # NOT force-added; caller decides


def test_award_exp_and_evs_applies_ev_yield_and_exp():
    winner_species = make_species(name="Winner", dex=1)
    loser_species = make_species(name="Loser", dex=2, base_exp_yield=64, ev_yield={Stat.SPEED: 2})
    winner = make_pokemon(winner_species, level=10)
    loser = make_pokemon(loser_species, level=10)
    loser.current_hp = 0

    old_evs_speed = winner.evs.speed
    events = award_exp_and_evs(winner, loser, trainer_battle=False, rng=None)
    assert winner.evs.speed == old_evs_speed + 2
    assert len(events) >= 1


def test_award_exp_and_evs_skips_fainted_receiver():
    winner_species = make_species(name="Winner", dex=1)
    loser_species = make_species(name="Loser", dex=2)
    winner = make_pokemon(winner_species, level=10)
    winner.current_hp = 0
    loser = make_pokemon(loser_species, level=10)
    events = award_exp_and_evs(winner, loser, trainer_battle=False, rng=None)
    assert events == []


def test_level_up_evolution_rule_triggers_at_min_level():
    evo_rule = EvolutionRule(trigger=EvolutionTrigger.LEVEL_UP, target_dex_number=2, min_level=16)
    species = make_species(dex=1, evolutions=(evo_rule,))
    mon = make_pokemon(species, level=15)
    assert check_level_up_evolution(mon) is None
    mon.level = 16
    assert check_level_up_evolution(mon) is evo_rule


def test_apply_evolution_swaps_species_and_scales_hp():
    evolved_species = make_species(name="Evolved", dex=2)
    evo_rule = EvolutionRule(trigger=EvolutionTrigger.LEVEL_UP, target_dex_number=2, min_level=16)
    base_species = make_species(dex=1, evolutions=(evo_rule,))
    mon = make_pokemon(base_species, level=16)
    mon.current_hp = mon.get_stats().hp  # full
    lookup = {2: evolved_species}
    new_species = apply_evolution(mon, evo_rule, lookup)
    assert new_species is evolved_species
    assert mon.species is evolved_species
    assert mon.current_hp == mon.get_stats().hp  # stayed full through evolution


def test_item_evolution_covers_former_trade_evolutions():
    evolved_species = make_species(name="Evolved", dex=2)
    evo_rule = EvolutionRule(
        trigger=EvolutionTrigger.ITEM, target_dex_number=2, item_name="Metal Coat",
        note="formerly trade-with-Metal-Coat",
    )
    base_species = make_species(dex=1, evolutions=(evo_rule,))
    mon = make_pokemon(base_species, level=20)
    lookup = {2: evolved_species}
    result = try_item_evolution(mon, "Metal Coat", lookup)
    assert result is evolved_species
    assert mon.species is evolved_species

    # wrong item name -> no evolution
    mon2 = make_pokemon(base_species, level=20)
    assert try_item_evolution(mon2, "Fire Stone", lookup) is None
