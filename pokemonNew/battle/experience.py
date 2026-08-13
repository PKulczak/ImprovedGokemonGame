"""EXP yield, the 4 Gen 3 growth-rate curves, level-up move learning, and
evolution triggering.

All EXP/EVs go 100% to the single active Pokemon at the moment of a KO --
single battles only, no participant-splitting logic (explicit simplification
agreed for this project).
"""

import math

from . import stats as _stats
from .events import Message
from .schemas import EvolutionTrigger, GrowthRate

MAX_LEVEL = 100


def exp_threshold(growth_rate: GrowthRate, level: int) -> int:
    """Total EXP required to BE at `level` under the given growth rate."""
    n = level
    if growth_rate == GrowthRate.FAST:
        return math.floor(0.8 * n ** 3)
    if growth_rate == GrowthRate.MEDIUM_FAST:
        return n ** 3
    if growth_rate == GrowthRate.MEDIUM_SLOW:
        if n <= 1:
            return 0  # the polynomial is negative at n=1 -- a known real
                      # quirk of this curve, clamped explicitly per spec.
        return max(0, math.floor(1.2 * n ** 3 - 15 * n ** 2 + 100 * n - 140))
    if growth_rate == GrowthRate.SLOW:
        return math.floor(1.25 * n ** 3)
    raise ValueError(f"Unknown growth rate: {growth_rate}")


def exp_yield(base_exp_yield: int, fainted_level: int, trainer_battle: bool = False) -> int:
    val = base_exp_yield * fainted_level / 7
    if trainer_battle:
        val *= 1.5
    return math.floor(val)


def moves_to_learn(species, old_level: int, new_level: int):
    """Move names that become available strictly after `old_level` and at or
    before `new_level` (ascending learnset order)."""
    return [name for lvl, name in species.learnset if old_level < lvl <= new_level]


def apply_exp_gain(pokemon, amount: int) -> dict:
    """Add EXP to `pokemon`, leveling up as many times as warranted (capped
    at level 100). Mutates `pokemon` in place (level, current_exp,
    current_hp, stat cache). Returns a summary dict; does NOT force-replace
    any of the 4 current moves -- it only surfaces which move names *want*
    to be learned so a caller (UI/AI) can decide.
    """
    old_level = pokemon.level
    old_max_hp = pokemon.get_stats().hp
    pokemon.current_exp += amount
    new_level = old_level
    while new_level < MAX_LEVEL and pokemon.current_exp >= exp_threshold(pokemon.species.growth_rate, new_level + 1):
        new_level += 1
    leveled_up = new_level > old_level
    learnable = []
    if leveled_up:
        pokemon.level = new_level
        pokemon.invalidate_stat_cache()
        new_max_hp = pokemon.get_stats().hp
        pokemon.current_hp = min(new_max_hp, pokemon.current_hp + max(0, new_max_hp - old_max_hp))
        learnable = moves_to_learn(pokemon.species, old_level, new_level)
    return {
        "exp_gained": amount,
        "leveled_up": leveled_up,
        "old_level": old_level,
        "new_level": new_level,
        "learnable_moves": learnable,
    }


def award_exp_and_evs(receiver, fainted, trainer_battle: bool = False, rng=None) -> list:
    """Award EXP + EVs to `receiver` (a PokemonInstance) for `fainted` (the
    PokemonInstance that just fainted). Returns a list of BattleEvent-ish
    Message events describing what happened."""
    events = []
    if receiver is None or receiver.is_fainted():
        return events

    gained = exp_yield(fainted.species.base_exp_yield, fainted.level, trainer_battle)
    result = apply_exp_gain(receiver, gained)
    events.append(Message(text=f"{receiver.display_name} gained {gained} EXP. Points!"))
    if result["leveled_up"]:
        events.append(Message(text=f"{receiver.display_name} grew to level {result['new_level']}!"))
        for move_name in result["learnable_moves"]:
            events.append(Message(text=f"{receiver.display_name} wants to learn {move_name}!"))

    new_evs = receiver.evs
    for stat, amount in fainted.species.ev_yield.items():
        new_evs = _stats.clamp_ev_gain(new_evs, stat, amount)
    receiver.evs = new_evs
    receiver.invalidate_stat_cache()

    return events


def check_level_up_evolution(pokemon):
    """Return the first applicable LEVEL_UP EvolutionRule for `pokemon`'s
    current level, or None."""
    for rule in pokemon.species.evolutions:
        if rule.trigger == EvolutionTrigger.LEVEL_UP and rule.min_level is not None:
            if pokemon.level >= rule.min_level:
                return rule
    return None


def apply_evolution(pokemon, rule, species_lookup) -> object:
    """Apply an EvolutionRule to `pokemon`, mutating its species in place.

    `species_lookup`: dict[int, Species] keyed by dex_number (caller-supplied,
    same pattern as PokemonInstance.from_dict's species_lookup, to avoid a
    hard import-time dependency on data/species.py which isn't ours).
    Returns the new Species.
    """
    old_max_hp = pokemon.get_stats().hp
    new_species = species_lookup[rule.target_dex_number]
    pokemon.species = new_species
    pokemon.invalidate_stat_cache()
    new_max_hp = pokemon.get_stats().hp
    pokemon.current_hp = min(new_max_hp, pokemon.current_hp + max(0, new_max_hp - old_max_hp))
    return new_species


def try_item_evolution(pokemon, item_name: str, species_lookup):
    """Apply an ITEM-triggered EvolutionRule matching `item_name`, if any
    (covers former trade-with-item evolutions too -- 'use the item on the
    Pokemon' per this project's agreed simplification). Returns the new
    Species, or None if no matching rule exists."""
    for rule in pokemon.species.evolutions:
        if rule.trigger == EvolutionTrigger.ITEM and rule.item_name == item_name:
            if rule.target_dex_number in species_lookup:
                return apply_evolution(pokemon, rule, species_lookup)
    return None
