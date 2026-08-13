"""ITEM_HANDLERS: held-item battle hooks AND basic consumable-use hooks.

Two different calling conventions live in this one dict (documented, not a
bug): a caller always knows which item it's invoking and thus which
convention applies.

1. Held-item battle hooks (leftovers, sitrus_berry, lum_berry, choice_band,
   choice_specs, charcoal, mystic_water, miracle_seed, magnet, kings_rock,
   scope_lens, quick_claw, focus_sash, focus_band):
   called as `handler(ItemContext)` by battle_state.py at specific pipeline
   points, dispatching on `context.event` (same pattern as
   `battle.abilities.AbilityContext` -- see that module's docstring for the
   general idea). Event vocabulary used:
       "end_of_turn"            -- leftovers heal. battler = holder.
       "hp_threshold"           -- sitrus_berry. battler = holder, checked
                                    after any HP loss.
       "on_status_or_confusion_inflicted" -- lum_berry. battler = holder,
                                    value = StatusCondition or "confusion".
       "on_move_used"           -- choice_band/specs lock-in. battler =
                                    holder, value = move name just used.
       "modify_stat"            -- choice_band/specs stat boost, extra =
                                    {"stat_name": "attack"|"sp_atk"}.
       "modify_power"           -- charcoal/mystic_water/miracle_seed/magnet.
                                    move = move used, battler = attacker.
       "on_hit_landed"          -- kings_rock. battler = attacker(holder),
                                    other = defender, move = move used.
       "modify_crit_stage"      -- scope_lens. value = current stage (int).
                                    return a stage DELTA to add (int).
       "roll_priority_bonus"    -- quick_claw. battler = holder. Return
                                    True/False (act first in its bracket).
       "check_survive_lethal"   -- focus_sash/focus_band. battler = the
                                    Pokemon about to faint. extra =
                                    {"was_full_hp": bool}. Return True to
                                    survive at 1 HP instead of fainting.

2. Basic consumable-use hooks (potion, super_potion, hyper_potion,
   max_potion, revive, max_revive, full_heal, antidote, paralyze_heal,
   awakening, burn_heal, ice_heal, full_restore): called directly as
   `handler(pokemon)` where `pokemon` is a `battle.pokemon.PokemonInstance`
   (on the field or benched -- these work outside of any `Battle` too, e.g.
   from a bag menu). Returns True if the item had an effect (caller decides
   whether that means "consume the item").
"""

from dataclasses import dataclass, field

from .pokemon import StatusCondition


@dataclass
class ItemContext:
    event: str
    battle: object = None
    battler: object = None
    other: object = None
    move: object = None
    value: object = None
    rng: object = None
    events: list = field(default_factory=list)
    extra: dict = field(default_factory=dict)


# --- held-item battle hooks -------------------------------------------------

def leftovers(ctx: ItemContext):
    if ctx.event == "end_of_turn":
        ctx.battle.heal_fractional(ctx.battler, 1, 16, events=ctx.events, source="leftovers")
    return None


def sitrus_berry(ctx: ItemContext):
    if ctx.event != "hp_threshold":
        return None
    pokemon = ctx.battler.pokemon
    max_hp = pokemon.get_stats().hp
    if pokemon.current_hp * 2 <= max_hp and not pokemon.is_fainted():
        ctx.battle.heal_flat(ctx.battler, 30, events=ctx.events, source="sitrus_berry")
        pokemon.held_item = None  # single-use
    return None


def lum_berry(ctx: ItemContext):
    if ctx.event != "on_status_or_confusion_inflicted":
        return None
    battler = ctx.battler
    if ctx.value == "confusion":
        battler.confusion_turns_remaining = 0
        ctx.battle.note_item_cure(battler, "confusion", events=ctx.events, source="lum_berry")
    else:
        ctx.battle.cure_status_event(battler, events=ctx.events, source="lum_berry")
    battler.pokemon.held_item = None  # single-use
    return None


def _choice_lock(ctx: ItemContext):
    if ctx.event == "on_move_used":
        if ctx.battler.choice_locked_move is None:
            ctx.battler.choice_locked_move = ctx.value
    return None


def choice_band(ctx: ItemContext):
    if ctx.event == "modify_stat" and ctx.extra.get("stat_name") == "attack":
        return 1.5
    return _choice_lock(ctx)


def choice_specs(ctx: ItemContext):
    if ctx.event == "modify_stat" and ctx.extra.get("stat_name") == "sp_atk":
        return 1.5
    return _choice_lock(ctx)


def _boost_same_type(ctx: ItemContext, boosted_type):
    if ctx.event == "modify_power" and ctx.move is not None and ctx.move.type == boosted_type:
        return 1.2
    return None


def charcoal(ctx: ItemContext):
    from .schemas import Type
    return _boost_same_type(ctx, Type.FIRE)


def mystic_water(ctx: ItemContext):
    from .schemas import Type
    return _boost_same_type(ctx, Type.WATER)


def miracle_seed(ctx: ItemContext):
    from .schemas import Type
    return _boost_same_type(ctx, Type.GRASS)


def magnet(ctx: ItemContext):
    from .schemas import Type
    return _boost_same_type(ctx, Type.ELECTRIC)


def kings_rock(ctx: ItemContext):
    if ctx.event == "on_hit_landed" and ctx.other is not None:
        if ctx.rng is not None and ctx.rng.random() < 0.10:
            ctx.battle.set_flinch(ctx.other)
    return None


def scope_lens(ctx: ItemContext):
    if ctx.event == "modify_crit_stage":
        return 1
    return None


def quick_claw(ctx: ItemContext):
    if ctx.event == "roll_priority_bonus":
        return ctx.rng is not None and ctx.rng.random() < 0.20
    return None


def focus_sash(ctx: ItemContext):
    if ctx.event == "check_survive_lethal" and ctx.extra.get("was_full_hp"):
        ctx.battler.pokemon.held_item = None  # single-use
        return True
    return None


def focus_band(ctx: ItemContext):
    if ctx.event == "check_survive_lethal":
        return ctx.rng is not None and ctx.rng.random() < 0.10
    return None


ITEM_HANDLERS = {
    "leftovers": leftovers,
    "sitrus_berry": sitrus_berry,
    "lum_berry": lum_berry,
    "choice_band": choice_band,
    "choice_specs": choice_specs,
    "charcoal": charcoal,
    "mystic_water": mystic_water,
    "miracle_seed": miracle_seed,
    "magnet": magnet,
    "kings_rock": kings_rock,
    "scope_lens": scope_lens,
    "quick_claw": quick_claw,
    "focus_sash": focus_sash,
    "focus_band": focus_band,
}


# --- basic consumables: handler(pokemon) -> bool (had effect?) -------------

def _heal_amount(pokemon, amount) -> bool:
    if pokemon.is_fainted():
        return False
    max_hp = pokemon.get_stats().hp
    if pokemon.current_hp >= max_hp:
        return False
    pokemon.current_hp = min(max_hp, pokemon.current_hp + amount)
    return True


def potion(pokemon) -> bool:
    return _heal_amount(pokemon, 20)


def super_potion(pokemon) -> bool:
    return _heal_amount(pokemon, 50)


def hyper_potion(pokemon) -> bool:
    return _heal_amount(pokemon, 200)


def max_potion(pokemon) -> bool:
    if pokemon.is_fainted():
        return False
    max_hp = pokemon.get_stats().hp
    if pokemon.current_hp >= max_hp:
        return False
    pokemon.current_hp = max_hp
    return True


def revive(pokemon) -> bool:
    if not pokemon.is_fainted():
        return False
    max_hp = pokemon.get_stats().hp
    pokemon.current_hp = max(1, max_hp // 2)
    pokemon.status = StatusCondition.NONE
    pokemon.status_data = {}
    return True


def max_revive(pokemon) -> bool:
    if not pokemon.is_fainted():
        return False
    pokemon.current_hp = pokemon.get_stats().hp
    pokemon.status = StatusCondition.NONE
    pokemon.status_data = {}
    return True


def full_heal(pokemon) -> bool:
    if pokemon.status == StatusCondition.NONE:
        return False
    pokemon.status = StatusCondition.NONE
    pokemon.status_data = {}
    return True


def _cure_specific(pokemon, statuses) -> bool:
    if pokemon.status in statuses:
        pokemon.status = StatusCondition.NONE
        pokemon.status_data = {}
        return True
    return False


def antidote(pokemon) -> bool:
    return _cure_specific(pokemon, {StatusCondition.POISON, StatusCondition.TOXIC})


def paralyze_heal(pokemon) -> bool:
    return _cure_specific(pokemon, {StatusCondition.PARALYSIS})


def awakening(pokemon) -> bool:
    return _cure_specific(pokemon, {StatusCondition.SLEEP})


def burn_heal(pokemon) -> bool:
    return _cure_specific(pokemon, {StatusCondition.BURN})


def ice_heal(pokemon) -> bool:
    return _cure_specific(pokemon, {StatusCondition.FREEZE})


def full_restore(pokemon) -> bool:
    if pokemon.is_fainted():
        return False
    max_hp = pokemon.get_stats().hp
    had_effect = pokemon.current_hp < max_hp or pokemon.status != StatusCondition.NONE
    pokemon.current_hp = max_hp
    pokemon.status = StatusCondition.NONE
    pokemon.status_data = {}
    return had_effect


ITEM_HANDLERS.update({
    "potion": potion,
    "super_potion": super_potion,
    "hyper_potion": hyper_potion,
    "max_potion": max_potion,
    "revive": revive,
    "max_revive": max_revive,
    "full_heal": full_heal,
    "antidote": antidote,
    "paralyze_heal": paralyze_heal,
    "awakening": awakening,
    "burn_heal": burn_heal,
    "ice_heal": ice_heal,
    "full_restore": full_restore,
})
