"""EFFECT_HANDLERS: secondary move-effect hooks.

Fixed vocabulary (the roster-content workstream references these exact
string ids from `data/moves.py`): burn, poison, toxic, paralyze, freeze,
sleep, confuse, flinch, stat_change_self, stat_change_target, heal_self,
recoil, drain, rest, ohko, multi_hit, high_crit.

Handlers are called as `handler(MoveEffectContext)` by `battle_state.py`
AFTER the primary damage (if any) has already been applied and its faint
check performed, with one exception documented below.

Two effects are special-cased directly in battle_state.py because their
timing requirement can't be "after the primary hit":
  - "high_crit": crit stage must be decided BEFORE damage is computed, so
    battle_state reads `move.secondary_effect == "high_crit"` up front to
    seed the crit stage at >=1. The registered handler here is a documented
    no-op kept only so every id in the fixed vocabulary has a callable.
  - "ohko": bypasses the normal damage pipeline entirely (no power/type/crit
    math) so battle_state special-cases it before the usual damage call;
    the registered handler here performs the actual "set HP to 0" effect
    once battle_state has already done the accuracy/Sturdy-immunity check.
"""

import math
from dataclasses import dataclass, field

from .pokemon import StatusCondition


@dataclass
class MoveEffectContext:
    battle: object
    attacker: object
    defender: object
    move: object
    rng: object
    damage_dealt: int = 0
    params: dict = field(default_factory=dict)
    events: list = field(default_factory=list)


_STATUS_MAP = {
    "burn": StatusCondition.BURN,
    "poison": StatusCondition.POISON,
    "toxic": StatusCondition.TOXIC,
    "paralyze": StatusCondition.PARALYSIS,
    "freeze": StatusCondition.FREEZE,
    "sleep": StatusCondition.SLEEP,
}


def _make_status_handler(status: StatusCondition):
    def handler(ctx: MoveEffectContext):
        ctx.battle.try_inflict_status(ctx.defender, status, events=ctx.events, source_battler=ctx.attacker)
    return handler


burn = _make_status_handler(StatusCondition.BURN)
poison = _make_status_handler(StatusCondition.POISON)
toxic = _make_status_handler(StatusCondition.TOXIC)
paralyze = _make_status_handler(StatusCondition.PARALYSIS)
freeze = _make_status_handler(StatusCondition.FREEZE)
sleep = _make_status_handler(StatusCondition.SLEEP)


def confuse(ctx: MoveEffectContext):
    ctx.battle.try_inflict_confusion(ctx.defender, events=ctx.events)


def flinch(ctx: MoveEffectContext):
    ctx.battle.set_flinch(ctx.defender, events=ctx.events)


def stat_change_self(ctx: MoveEffectContext):
    stat = ctx.params["stat"]
    stages = ctx.params["stages"]
    ctx.battle.change_stat_stage(ctx.attacker, stat, stages, events=ctx.events)


def stat_change_target(ctx: MoveEffectContext):
    stat = ctx.params["stat"]
    stages = ctx.params["stages"]
    ctx.battle.change_stat_stage(ctx.defender, stat, stages, events=ctx.events)


def heal_self(ctx: MoveEffectContext):
    fraction = ctx.params.get("fraction", 0.5)
    max_hp = ctx.attacker.pokemon.get_stats().hp
    amount = math.floor(max_hp * fraction)
    ctx.battle.heal_flat(ctx.attacker, amount, events=ctx.events, source="heal_self")


def recoil(ctx: MoveEffectContext):
    fraction = ctx.params.get("fraction", 0.25)
    amount = max(1, math.floor(ctx.damage_dealt * fraction))
    ctx.battle.deal_direct_damage(ctx.attacker, amount, events=ctx.events, source="recoil")


def drain(ctx: MoveEffectContext):
    fraction = ctx.params.get("fraction", 0.5)
    amount = max(1, math.floor(ctx.damage_dealt * fraction))
    ctx.battle.heal_flat(ctx.attacker, amount, events=ctx.events, source="drain")


def rest(ctx: MoveEffectContext):
    ctx.battle.perform_rest(ctx.attacker, events=ctx.events)


def ohko(ctx: MoveEffectContext):
    ctx.battle.apply_ohko(ctx.attacker, ctx.defender, events=ctx.events)


_MULTI_HIT_COUNTS = [2, 3, 4, 5]
_MULTI_HIT_WEIGHTS = [3, 3, 1, 1]  # standard Gen 3 2/3/4/5 hit distribution (37.5/37.5/12.5/12.5)


def multi_hit(ctx: MoveEffectContext):
    min_hits = ctx.params.get("min_hits", 2)
    max_hits = ctx.params.get("max_hits", 5)
    if (min_hits, max_hits) == (2, 5):
        total_hits = ctx.rng.choices(_MULTI_HIT_COUNTS, weights=_MULTI_HIT_WEIGHTS, k=1)[0]
    else:
        total_hits = ctx.rng.randint(min_hits, max_hits)
    # The primary hit (already applied by battle_state before this handler
    # ran) counts as hit #1; apply (total_hits - 1) more.
    ctx.battle.apply_extra_multi_hits(ctx.attacker, ctx.defender, ctx.move, total_hits - 1, events=ctx.events)


def high_crit(ctx: MoveEffectContext):
    # No-op here: battle_state.py reads move.secondary_effect == "high_crit"
    # up front (before damage) to seed the crit stage. See module docstring.
    return None


_WEATHER_NAME_MAP = {
    "rain": "rain", "sun": "sun", "sandstorm": "sandstorm", "hail": "hail",
}


def weather(ctx: MoveEffectContext):
    """Set move-triggered weather (Rain Dance/Sunny Day/Sandstorm/Hail),
    params: {"weather": "rain"|"sun"|"sandstorm"|"hail"}. Lasts exactly 5
    turns and refreshes (doesn't stack) on reuse.

    NOT part of the originally-specified fixed EFFECT_HANDLERS vocabulary --
    added because that vocabulary had no id for "this move sets weather",
    which the Status/Weather section of the spec otherwise requires
    (move-set weather with a 5-turn duration, distinct from the 8-turn
    ability-set house rule). Flagged explicitly in the final report.
    """
    from .status import MOVE_WEATHER_DURATION
    from .status import Weather as _Weather
    name = ctx.params.get("weather")
    mapping = {
        "rain": _Weather.RAIN, "sun": _Weather.SUN,
        "sandstorm": _Weather.SANDSTORM, "hail": _Weather.HAIL,
    }
    w = mapping.get(name)
    if w is not None:
        ctx.battle.set_weather(w, MOVE_WEATHER_DURATION, events=ctx.events)


EFFECT_HANDLERS = {
    "burn": burn,
    "poison": poison,
    "toxic": toxic,
    "paralyze": paralyze,
    "freeze": freeze,
    "sleep": sleep,
    "confuse": confuse,
    "flinch": flinch,
    "stat_change_self": stat_change_self,
    "stat_change_target": stat_change_target,
    "heal_self": heal_self,
    "recoil": recoil,
    "drain": drain,
    "rest": rest,
    "ohko": ohko,
    "multi_hit": multi_hit,
    "high_crit": high_crit,
    "weather": weather,
}
