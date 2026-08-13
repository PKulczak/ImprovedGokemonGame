"""Period-accurate Gen 3 status/weather effects.

Deliberately does NOT implement later-gen rules: no Fire-type burn immunity
change, no Electric-type paralysis immunity, no Grass-type powder immunity,
no half-HP paralysis speed, no "sturdy survives at 1hp" -- see the module
docstrings in abilities.py/items.py for where those authentic-period
niches actually live.

Functions here take Battler-shaped objects duck-typed (no import of
battle_state.Battler, to avoid a circular import): any object with
`.pokemon` (a PokemonInstance), `.stages` (has .attack/.defense/.speed etc),
`.confusion_turns_remaining` (int) and `.flinched` (bool) will work.
"""

from enum import Enum

from . import damage as _damage
from . import stats as _stats
from .events import (
    ConfusionSelfHit, Flinched, FullyParalyzed, StatusCured, Thawed, WokeUp,
)
from .pokemon import StatusCondition
from .schemas import Type

MOVE_WEATHER_DURATION = 5      # move-set weather (Rain Dance/Sunny Day/etc)
ABILITY_WEATHER_DURATION = 8   # house-rule fixed duration for Drizzle/Drought


class Weather(Enum):
    NONE = "none"
    RAIN = "rain"
    SUN = "sun"
    SANDSTORM = "sandstorm"
    HAIL = "hail"


# --- status infliction / immunity ---

def can_be_statused(pokemon, status: StatusCondition) -> bool:
    types = {pokemon.species.type1, pokemon.species.type2}
    if status == StatusCondition.BURN and Type.FIRE in types:
        return False
    if status == StatusCondition.FREEZE and Type.ICE in types:
        return False
    if status in (StatusCondition.POISON, StatusCondition.TOXIC) and \
            (Type.POISON in types or Type.STEEL in types):
        return False
    return True


def inflict_status(pokemon, status: StatusCondition, rng=None) -> bool:
    """Attempt to set a major status on `pokemon`. Returns False if blocked by
    an existing status or an intrinsic type immunity (does NOT check
    ability immunities -- those are handled by ABILITY_HANDLERS before this
    is called)."""
    if pokemon.status != StatusCondition.NONE:
        return False
    if not can_be_statused(pokemon, status):
        return False
    pokemon.status = status
    pokemon.status_data = {}
    if status == StatusCondition.SLEEP:
        turns = rng.randint(1, 4) if rng is not None else 3
        pokemon.status_data["sleep_turns_remaining"] = turns
    return True


def cure_status(pokemon) -> None:
    pokemon.status = StatusCondition.NONE
    pokemon.status_data = {}


# --- effective speed (paralysis quarters speed; stat stages already applied) ---

def effective_speed(battler) -> int:
    base = battler.pokemon.get_stats().speed
    spd = _stats.apply_stat_stage(base, battler.stages.speed)
    if battler.pokemon.status == StatusCondition.PARALYSIS:
        spd = spd // 4
    return max(1, spd)


# --- per-turn ability to act ---

def can_act(battler, side: str, rng) -> tuple:
    """Run the full pre-move gate: sleep/freeze -> flinch -> confusion ->
    paralysis. Returns (can_act: bool, events: list[BattleEvent])."""
    events = []
    pokemon = battler.pokemon
    name = pokemon.display_name

    if pokemon.status == StatusCondition.SLEEP:
        remaining = pokemon.status_data.get("sleep_turns_remaining", 1) - 1
        if remaining <= 0:
            cure_status(pokemon)
            events.append(WokeUp(side=side, pokemon_name=name))
            # falls through -- may still act this same turn
        else:
            pokemon.status_data["sleep_turns_remaining"] = remaining
            return False, events

    if pokemon.status == StatusCondition.FREEZE:
        if rng.random() < 0.20:
            cure_status(pokemon)
            events.append(Thawed(side=side, pokemon_name=name))
        else:
            return False, events

    if battler.flinched:
        events.append(Flinched(side=side, pokemon_name=name))
        return False, events

    if battler.confusion_turns_remaining > 0:
        battler.confusion_turns_remaining -= 1
        if battler.confusion_turns_remaining == 0:
            events.append(StatusCured(side=side, pokemon_name=name, status="confusion"))
        else:
            if rng.random() < (1 / 3):
                dmg = _confusion_self_hit_damage(battler, rng)
                pokemon.current_hp = max(0, pokemon.current_hp - dmg)
                events.append(ConfusionSelfHit(
                    side=side, pokemon_name=name, amount=dmg,
                    remaining_hp=pokemon.current_hp,
                ))
                return False, events

    if pokemon.status == StatusCondition.PARALYSIS:
        if rng.random() < 0.25:
            events.append(FullyParalyzed(side=side, pokemon_name=name))
            return False, events

    return True, events


def _confusion_self_hit_damage(battler, rng) -> int:
    pokemon = battler.pokemon
    stats_ = pokemon.get_stats()
    atk = _stats.apply_stat_stage(stats_.attack, battler.stages.attack)
    dfn = _stats.apply_stat_stage(stats_.defense, battler.stages.defense)
    return _damage.calculate_damage(
        level=pokemon.level, power=40, atk_stat=atk, def_stat=dfn,
        is_crit=False, is_stab=False, type1_mult=1.0, type2_mult=1.0,
        is_burn_halved=(pokemon.status == StatusCondition.BURN), rng=rng,
    )


# --- end-of-turn status damage ---

def status_tick_damage(battler) -> int:
    pokemon = battler.pokemon
    max_hp = pokemon.get_stats().hp
    if pokemon.status in (StatusCondition.BURN, StatusCondition.POISON):
        return max(1, max_hp // 8)
    if pokemon.status == StatusCondition.TOXIC:
        return max(1, (max_hp * max(1, battler.toxic_counter)) // 16)
    return 0


def is_status_damage_source(pokemon) -> str:
    return {
        StatusCondition.BURN: "burn",
        StatusCondition.POISON: "poison",
        StatusCondition.TOXIC: "toxic",
    }.get(pokemon.status, "")


# --- weather ---

def weather_power_multiplier(weather: Weather, move_type: Type):
    """(numerator, denominator) power multiplier for Rain/Sun vs Water/Fire moves."""
    if weather == Weather.RAIN:
        if move_type == Type.WATER:
            return (3, 2)
        if move_type == Type.FIRE:
            return (1, 2)
    elif weather == Weather.SUN:
        if move_type == Type.FIRE:
            return (3, 2)
        if move_type == Type.WATER:
            return (1, 2)
    return (1, 1)


_SANDSTORM_IMMUNE = {Type.ROCK, Type.GROUND, Type.STEEL}
_HAIL_IMMUNE = {Type.ICE}


def weather_chip_damage(weather: Weather, pokemon) -> int:
    types = {pokemon.species.type1, pokemon.species.type2}
    if weather == Weather.SANDSTORM and not (types & _SANDSTORM_IMMUNE):
        return max(1, pokemon.get_stats().hp // 16)
    if weather == Weather.HAIL and not (types & _HAIL_IMMUNE):
        return max(1, pokemon.get_stats().hp // 16)
    return 0
