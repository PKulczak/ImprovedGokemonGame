"""The Gen 3 damage formula, exact integer pipeline.

Physical/special split is BY MOVE TYPE (Gen 3 rule): re-exported here from
schemas.py, which is the canonical definition (Move.__post_init__ needs it
too, so it lives there to avoid a circular import).
"""

from .schemas import PHYSICAL_TYPES, SPECIAL_TYPES  # re-exported, see docstring
from .type_chart import type_effectiveness_components

__all__ = [
    "PHYSICAL_TYPES", "SPECIAL_TYPES", "calculate_damage", "crit_chance",
    "effective_crit_stat_stage",
]


def crit_chance(stage: int) -> float:
    """Gen 3 crit rate table. stage 0 -> 1/16, +1 -> 1/8, +2 -> 1/4, +3+ -> 1/3."""
    if stage <= 0:
        return 1 / 16
    if stage == 1:
        return 1 / 8
    if stage == 2:
        return 1 / 4
    return 1 / 3


def effective_crit_stat_stage(actual_stage: int, *, is_attacker: bool) -> int:
    """On a crit, ignore the attacker's unfavorable (negative) offensive stage,
    and the defender's unfavorable (positive, defense-boosting) stage."""
    if is_attacker:
        return max(actual_stage, 0)
    return min(actual_stage, 0)


def calculate_damage(level, power, atk_stat, def_stat, *, is_crit, is_stab,
                      type1_mult, type2_mult, is_burn_halved, rng,
                      type1=None, type2=None, defending_type1=None, defending_type2=None):
    """Full Gen 3 damage pipeline, integer truncated division throughout.

    `type1_mult`/`type2_mult` are the plain float multipliers (e.g. 2.0, 0.5,
    1.0) for up to two defending types; if a Pokemon has only one type, pass
    1.0 (neutral) for the second. Immunity (product == 0) short-circuits to 0
    damage with no minimum-1 override.
    """
    if type1_mult * type2_mult == 0:
        return 0

    base = (2 * level) // 5 + 2
    base = base * power
    base = base * atk_stat
    base = base // def_stat
    base = base // 50
    base = base + 2

    if is_crit:
        base = base * 2  # Gen 3 crit = 2x, not 1.5x (that's Gen 6+)

    if is_stab:
        base = (base * 3) // 2

    t1_num, t1_den = _mult_to_fraction(type1_mult)
    base = (base * t1_num) // t1_den
    t2_num, t2_den = _mult_to_fraction(type2_mult)
    base = (base * t2_num) // t2_den

    roll = rng.randint(85, 100)
    base = (base * roll) // 100

    if is_burn_halved:
        base = base // 2

    return max(1, base)


def _mult_to_fraction(mult: float):
    _TABLE = {0.0: (0, 1), 0.5: (1, 2), 1.0: (1, 1), 2.0: (2, 1)}
    if mult in _TABLE:
        return _TABLE[mult]
    # Fallback for unexpected combined multipliers -- shouldn't normally
    # happen since calculate_damage applies each defending type separately.
    from fractions import Fraction
    frac = Fraction(mult).limit_denominator(4)
    return frac.numerator, frac.denominator
