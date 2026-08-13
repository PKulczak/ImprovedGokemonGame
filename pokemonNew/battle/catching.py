"""The exact Gen 3/4 catch formula.

Master Ball bypasses the formula entirely (always succeeds) -- handled as a
special case here (checking `item.catch_multiplier`) rather than trying to
route the 255 sentinel through the ball_bonus multiplication.
"""

from .pokemon import StatusCondition

STATUS_BONUS = {
    StatusCondition.SLEEP: 20,
    StatusCondition.FREEZE: 20,
    StatusCondition.PARALYSIS: 15,
    StatusCondition.POISON: 15,
    StatusCondition.TOXIC: 15,
    StatusCondition.BURN: 15,
    StatusCondition.NONE: 10,
}

MASTER_BALL_SENTINEL = 255.0


def modified_catch_value(hp_max, hp_current, species_catch_rate, ball_bonus, status_bonus) -> int:
    a = (3 * hp_max - 2 * hp_current) * species_catch_rate * ball_bonus
    a //= (3 * hp_max)
    a = (a * status_bonus) // 10
    return min(int(a), 255)


def attempt_catch(a, rng) -> bool:
    if a >= 255:
        return True
    b = int(1048560 / ((16711680 / a) ** 0.25))
    for _ in range(4):
        if rng.randint(0, 65535) >= b:
            return False
    return True


def attempt_catch_with_item(pokemon, item, rng) -> bool:
    """High-level convenience wrapper tying the ball item + target Pokemon's
    current state together into a single catch attempt."""
    if item.catch_multiplier is not None and item.catch_multiplier >= MASTER_BALL_SENTINEL:
        return True
    hp_max = pokemon.get_stats().hp
    status_bonus = STATUS_BONUS.get(pokemon.status, 10)
    ball_bonus = item.catch_multiplier if item.catch_multiplier is not None else 1.0
    a = modified_catch_value(
        hp_max, pokemon.current_hp, pokemon.species.base_catch_rate, ball_bonus, status_bonus,
    )
    return attempt_catch(a, rng)
