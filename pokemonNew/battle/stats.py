"""Stat calculation: the exact Gen 3 formulas, integer math throughout.

    HP         = floor((2*Base + IV + floor(EV/4)) * Level / 100) + Level + 10
    Other stat = floor( (floor((2*Base + IV + floor(EV/4)) * Level / 100) + 5)
                          * NatureModifier )

IVs: 0-31 per stat. EVs: 0-252 per stat, 510 total cap.
"""

from .schemas import Nature, Stat, StatBlock, Type

MAX_IV = 31
MAX_EV_PER_STAT = 252
MAX_EV_TOTAL = 510

_NON_HP_STATS = (Stat.ATTACK, Stat.DEFENSE, Stat.SP_ATK, Stat.SP_DEF, Stat.SPEED)


def calc_hp(base: int, iv: int, ev: int, level: int) -> int:
    return (2 * base + iv + ev // 4) * level // 100 + level + 10


def nature_modifier(stat: Stat, nature: Nature):
    """Return (numerator, denominator) nature multiplier for `stat`."""
    if nature.increased_stat == stat and nature.decreased_stat == stat:
        return (100, 100)
    if nature.increased_stat == stat:
        return (110, 100)
    if nature.decreased_stat == stat:
        return (90, 100)
    return (100, 100)


def calc_stat(base: int, iv: int, ev: int, level: int, nature: Nature, stat: Stat) -> int:
    pre_nature = (2 * base + iv + ev // 4) * level // 100 + 5
    num, den = nature_modifier(stat, nature)
    return (pre_nature * num) // den


def apply_nature(value: int, stat: Stat, nature: Nature) -> int:
    """Apply just the nature multiplier step to an already-computed pre-nature value."""
    num, den = nature_modifier(stat, nature)
    return (value * num) // den


def calc_all_stats(base_stats: StatBlock, ivs: StatBlock, evs: StatBlock, level: int, nature: Nature) -> StatBlock:
    hp = calc_hp(base_stats.hp, ivs.hp, evs.hp, level)
    values = {}
    for stat in _NON_HP_STATS:
        values[stat] = calc_stat(base_stats.get(stat), ivs.get(stat), evs.get(stat), level, nature, stat)
    return StatBlock(
        hp=hp,
        attack=values[Stat.ATTACK],
        defense=values[Stat.DEFENSE],
        sp_atk=values[Stat.SP_ATK],
        sp_def=values[Stat.SP_DEF],
        speed=values[Stat.SPEED],
    )


def clamp_ev_gain(evs: StatBlock, stat: Stat, amount: int) -> StatBlock:
    """Return a new StatBlock with `amount` EVs added to `stat`, respecting the
    252-per-stat and 510-total caps."""
    values = {
        Stat.HP: evs.hp, Stat.ATTACK: evs.attack, Stat.DEFENSE: evs.defense,
        Stat.SP_ATK: evs.sp_atk, Stat.SP_DEF: evs.sp_def, Stat.SPEED: evs.speed,
    }
    total = sum(values.values())
    room_total = MAX_EV_TOTAL - total
    room_stat = MAX_EV_PER_STAT - values[stat]
    actual = max(0, min(amount, room_total, room_stat))
    values[stat] += actual
    return StatBlock(
        hp=values[Stat.HP], attack=values[Stat.ATTACK], defense=values[Stat.DEFENSE],
        sp_atk=values[Stat.SP_ATK], sp_def=values[Stat.SP_DEF], speed=values[Stat.SPEED],
    )


# --- Battle stat stages (Gen 3 rule: main stats step by halves of 2, accuracy/evasion by thirds of 3) ---

def stat_stage_multiplier(stage: int):
    stage = max(-6, min(6, stage))
    if stage >= 0:
        return (2 + stage, 2)
    return (2, 2 - stage)


def accuracy_stage_multiplier(stage: int):
    stage = max(-6, min(6, stage))
    if stage >= 0:
        return (3 + stage, 3)
    return (3, 3 - stage)


def apply_stat_stage(value: int, stage: int) -> int:
    num, den = stat_stage_multiplier(stage)
    return (value * num) // den


def apply_accuracy_stage(value: int, stage: int) -> int:
    num, den = accuracy_stage_multiplier(stage)
    return (value * num) // den


# --- Optional: Hidden Power (Gen 3+ formula) ---

_HIDDEN_POWER_TYPES = [
    Type.FIGHTING, Type.FLYING, Type.POISON, Type.GROUND, Type.ROCK, Type.BUG,
    Type.GHOST, Type.STEEL, Type.FIRE, Type.WATER, Type.GRASS, Type.ELECTRIC,
    Type.PSYCHIC, Type.ICE, Type.DRAGON, Type.DARK,
]


def hidden_power(ivs: StatBlock):
    """Return (Type, power) for Hidden Power, Gen 3+ formula.

    Bit order for both type and power indices is HP, Atk, Def, Spe, SpA, SpD.
    """
    order = [ivs.hp, ivs.attack, ivs.defense, ivs.speed, ivs.sp_atk, ivs.sp_def]
    u = sum((iv & 1) << i for i, iv in enumerate(order))
    v = sum(((iv >> 1) & 1) << i for i, iv in enumerate(order))
    type_index = (u * 15) // 63
    power = (v * 40) // 63 + 30
    return _HIDDEN_POWER_TYPES[type_index], power
