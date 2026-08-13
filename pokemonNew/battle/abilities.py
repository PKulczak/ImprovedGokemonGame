"""The 22 curated ability hooks.

Each handler is called with an `AbilityContext` and dispatches on
`context.event`. Handlers return a float multiplier for "modify_*" events
(None/omitted means "no change", treated as 1.0 by the caller) or a bool for
"check_*"/"prevent_*" events (True/False), and may append BattleEvent
instances to `context.events` for anything worth surfacing to a UI. State
mutation (inflicting status, dealing damage, changing stages) is done via
the small helper methods on `context.battle` (a `battle_state.Battle`),
duck-typed here (not imported) to avoid a circular import.

Event vocabulary used by battle_state.py:
    "on_switch_in"          -- battler just sent out. other = opposing active.
    "modify_power"          -- value = float multiplier so far (starts 1.0).
                               move = the move being used. battler = attacker.
    "check_immunity"        -- move = incoming move. battler = defender.
                               other = attacker. Return True if immune.
    "on_contact_received"   -- battler = ability owner (defender), other =
                               attacker that made contact. move = the move.
    "prevent_status"        -- battler = ability owner. value = StatusCondition
                               about to be inflicted. Return True to block.
    "on_status_inflicted"   -- battler = ability owner who was just inflicted
                               a status BY THE OPPONENT's move. other =
                               the opponent to reflect the status back onto.
                               value = the StatusCondition inflicted.
    "end_of_turn"           -- battler = ability owner, still on the field.
    "modify_stat"           -- battler = stat owner. extra["stat"] = Stat.
                               value = current computed stat value (int).
                               Return a float multiplier.
    "prevent_stat_stage_change" -- battler = target of a proposed stage
                               change. extra = {"stat": Stat, "stages": int}.
                               Return True to block.
    "check_ignore_evasion" -- battler = attacker. Return True to ignore the
                               defender's positive evasion stage this hit.
"""

from dataclasses import dataclass, field
from typing import Optional

from .pokemon import StatusCondition
from .schemas import Type


@dataclass
class AbilityContext:
    event: str
    battle: object = None
    battler: object = None
    other: object = None
    move: object = None
    value: object = None
    rng: object = None
    events: list = field(default_factory=list)
    extra: dict = field(default_factory=dict)


def _hp_at_or_below_third(battler) -> bool:
    pokemon = battler.pokemon
    return pokemon.current_hp * 3 <= pokemon.get_stats().hp


def _boost_same_type_move(ctx: AbilityContext, boosted_type: Type) -> Optional[float]:
    if ctx.event != "modify_power" or ctx.move is None:
        return None
    if ctx.move.type == boosted_type and _hp_at_or_below_third(ctx.battler):
        return 1.5
    return None


def blaze(ctx: AbilityContext):
    return _boost_same_type_move(ctx, Type.FIRE)


def torrent(ctx: AbilityContext):
    return _boost_same_type_move(ctx, Type.WATER)


def overgrow(ctx: AbilityContext):
    return _boost_same_type_move(ctx, Type.GRASS)


def levitate(ctx: AbilityContext):
    if ctx.event == "check_immunity" and ctx.move is not None:
        return ctx.move.type == Type.GROUND
    return None


def intimidate(ctx: AbilityContext):
    if ctx.event == "on_switch_in" and ctx.other is not None:
        ctx.battle.change_stat_stage(ctx.other, "attack", -1, events=ctx.events)
    return None


def _contact_status_chance(ctx: AbilityContext, status: StatusCondition, chance: float):
    if ctx.event != "on_contact_received" or ctx.other is None:
        return None
    if ctx.move is not None and not ctx.move.makes_contact:
        return None
    if ctx.rng is not None and ctx.rng.random() < chance:
        ctx.battle.try_inflict_status(ctx.other, status, events=ctx.events, source_battler=ctx.battler)
    return None


def static(ctx: AbilityContext):
    return _contact_status_chance(ctx, StatusCondition.PARALYSIS, 0.30)


def flame_body(ctx: AbilityContext):
    return _contact_status_chance(ctx, StatusCondition.BURN, 0.30)


def rough_skin(ctx: AbilityContext):
    if ctx.event != "on_contact_received" or ctx.other is None:
        return None
    if ctx.move is not None and not ctx.move.makes_contact:
        return None
    ctx.battle.deal_fractional_damage(ctx.other, 1, 8, events=ctx.events, source="rough_skin")
    return None


def sturdy(ctx: AbilityContext):
    # Gen-3-accurate: immune to OHKO moves ONLY. Do NOT implement the
    # modern "survive at 1 HP" effect (that's Gen 5+); that niche is
    # deliberately covered by Focus Sash/Focus Band in items.py instead.
    if ctx.event == "check_ohko_immunity":
        return True
    return None


def flash_fire(ctx: AbilityContext):
    if ctx.event == "check_immunity" and ctx.move is not None:
        if ctx.move.type == Type.FIRE:
            ctx.battler.flags["flash_fire_active"] = True
            return True
        return None
    if ctx.event == "modify_power" and ctx.move is not None:
        if ctx.move.type == Type.FIRE and ctx.battler.flags.get("flash_fire_active"):
            return 1.5
    return None


def _status_immunity(ctx: AbilityContext, status: StatusCondition):
    if ctx.event == "prevent_status" and ctx.value == status:
        return True
    return None


def immunity(ctx: AbilityContext):
    return _status_immunity(ctx, StatusCondition.POISON) or _status_immunity(ctx, StatusCondition.TOXIC)


def limber(ctx: AbilityContext):
    return _status_immunity(ctx, StatusCondition.PARALYSIS)


def insomnia(ctx: AbilityContext):
    return _status_immunity(ctx, StatusCondition.SLEEP)


def water_veil(ctx: AbilityContext):
    return _status_immunity(ctx, StatusCondition.BURN)


_SYNC_STATUSES = {StatusCondition.BURN, StatusCondition.PARALYSIS, StatusCondition.POISON, StatusCondition.TOXIC}


def synchronize(ctx: AbilityContext):
    if ctx.event == "on_status_inflicted" and ctx.value in _SYNC_STATUSES and ctx.other is not None:
        reflect = StatusCondition.POISON if ctx.value == StatusCondition.TOXIC else ctx.value
        ctx.battle.try_inflict_status(ctx.other, reflect, events=ctx.events)
    return None


def speed_boost(ctx: AbilityContext):
    if ctx.event == "end_of_turn":
        ctx.battle.change_stat_stage(ctx.battler, "speed", 1, events=ctx.events)
    return None


def shed_skin(ctx: AbilityContext):
    if ctx.event == "end_of_turn" and ctx.battler.pokemon.status != StatusCondition.NONE:
        if ctx.rng is not None and ctx.rng.random() < 0.30:
            ctx.battle.cure_status_event(ctx.battler, events=ctx.events, source="shed_skin")
    return None


def _set_weather_on_switch_in(ctx: AbilityContext, weather):
    if ctx.event == "on_switch_in":
        ctx.battle.set_weather(weather, ctx.battle.ABILITY_WEATHER_DURATION, events=ctx.events)
    return None


def drizzle(ctx: AbilityContext):
    from .status import Weather
    return _set_weather_on_switch_in(ctx, Weather.RAIN)


def drought(ctx: AbilityContext):
    from .status import Weather
    return _set_weather_on_switch_in(ctx, Weather.SUN)


def guts(ctx: AbilityContext):
    if ctx.event == "modify_stat" and ctx.extra.get("stat_name") == "attack":
        if ctx.battler.pokemon.status != StatusCondition.NONE:
            return 1.5
    if ctx.event == "check_burn_halving":
        return False  # negates burn's physical-damage halving
    return None


def marvel_scale(ctx: AbilityContext):
    if ctx.event == "modify_stat" and ctx.extra.get("stat_name") == "defense":
        if ctx.battler.pokemon.status != StatusCondition.NONE:
            return 1.5
    return None


def keen_eye(ctx: AbilityContext):
    if ctx.event == "prevent_stat_stage_change":
        if ctx.extra.get("stat") == "accuracy" and ctx.extra.get("stages", 0) < 0:
            return True
        return None
    if ctx.event == "check_ignore_evasion":
        return True
    return None


ABILITY_HANDLERS = {
    "blaze": blaze,
    "torrent": torrent,
    "overgrow": overgrow,
    "levitate": levitate,
    "intimidate": intimidate,
    "static": static,
    "flame_body": flame_body,
    "rough_skin": rough_skin,
    "sturdy": sturdy,
    "flash_fire": flash_fire,
    "immunity": immunity,
    "limber": limber,
    "insomnia": insomnia,
    "water_veil": water_veil,
    "synchronize": synchronize,
    "speed_boost": speed_boost,
    "shed_skin": shed_skin,
    "drizzle": drizzle,
    "drought": drought,
    "guts": guts,
    "marvel_scale": marvel_scale,
    "keen_eye": keen_eye,
}
