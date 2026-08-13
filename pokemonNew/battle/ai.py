"""AI heuristics for the three AITier tiers.

`score_move` is shared scoring used by all three tiers. Battler-shaped
objects are duck-typed here (no import of battle_state.Battler) to avoid a
circular import: anything with `.pokemon` and `.stages` works.
"""

from . import damage as _damage
from . import stats as _stats
from .schemas import AITier, MoveCategory
from .type_chart import TYPE_CHART


class _MidRollRng:
    """A tiny stand-in RNG that always returns the midpoint of the 85-100
    damage roll, used so AI scoring is a stable expected-value estimate
    rather than noisy per-call random damage."""

    def randint(self, a, b):
        return (a + b) // 2


_MID_ROLL_RNG = _MidRollRng()


def _type_mult(attacking_type, defending_type):
    if defending_type is None:
        return 1.0
    return TYPE_CHART.get(attacking_type, {}).get(defending_type, 1.0)


def _find_learned(battler, move):
    for lm in battler.pokemon.moves:
        if lm.move is move or lm.move.name == move.name:
            return lm
    return None


def score_move(move, attacker, defender) -> float:
    """0 (or negative) for unusable/no-PP moves. 0.0 for guaranteed-immune
    damaging moves. Otherwise expected_damage_fraction_of_remaining_hp *
    (accuracy/100), plus a flat KO bonus if the move would be lethal.
    Status moves get a smaller flat utility score."""
    learned = _find_learned(attacker, move)
    if learned is not None and learned.current_pp <= 0:
        return -1.0

    if move.category == MoveCategory.STATUS:
        return 0.3

    defender_type1 = defender.pokemon.species.type1
    defender_type2 = defender.pokemon.species.type2
    type1_mult = _type_mult(move.type, defender_type1)
    type2_mult = _type_mult(move.type, defender_type2) if defender_type2 else 1.0
    if type1_mult * type2_mult == 0:
        return 0.0

    atk_stats = attacker.pokemon.get_stats()
    def_stats = defender.pokemon.get_stats()
    is_physical = move.category == MoveCategory.PHYSICAL
    raw_atk = atk_stats.attack if is_physical else atk_stats.sp_atk
    raw_def = def_stats.defense if is_physical else def_stats.sp_def
    atk_stage = attacker.stages.attack if is_physical else attacker.stages.sp_atk
    def_stage = defender.stages.defense if is_physical else defender.stages.sp_def
    atk_value = _stats.apply_stat_stage(raw_atk, atk_stage)
    def_value = _stats.apply_stat_stage(raw_def, def_stage)
    is_stab = move.type in (attacker.pokemon.species.type1, attacker.pokemon.species.type2)

    expected = _damage.calculate_damage(
        level=attacker.pokemon.level, power=move.power or 0, atk_stat=atk_value, def_stat=def_value,
        is_crit=False, is_stab=is_stab, type1_mult=type1_mult, type2_mult=type2_mult,
        is_burn_halved=False, rng=_MID_ROLL_RNG,
    )
    accuracy = move.accuracy if move.accuracy is not None else 100
    remaining = max(1, defender.pokemon.current_hp)
    score = (expected / remaining) * (accuracy / 100)
    if expected >= defender.pokemon.current_hp:
        score += 2.0
    return score


def usable_moves(battler):
    return [lm.move for lm in battler.pokemon.moves if lm.current_pp > 0]


def _scored_moves(battler, defender):
    return [(m, score_move(m, battler, defender)) for m in usable_moves(battler)]


def choose_move_wild(battler, defender, rng):
    moves = usable_moves(battler)
    if not moves:
        return None
    scored = _scored_moves(battler, defender)
    decent = [m for m, s in scored if s > 0] or moves
    return rng.choice(decent)


def choose_move_basic_trainer(battler, defender, rng):
    moves = usable_moves(battler)
    if not moves:
        return None
    scored = sorted(_scored_moves(battler, defender), key=lambda t: -t[1])
    if rng.random() < 0.85:
        return scored[0][0]
    return rng.choice(moves)


def choose_move_expert_trainer(battler, defender, rng):
    moves = usable_moves(battler)
    if not moves:
        return None
    scored = sorted(_scored_moves(battler, defender), key=lambda t: -t[1])
    top = scored[0][0]
    second = scored[1][0] if len(scored) > 1 else top
    return top if rng.random() < 0.70 else second


def should_consider_switch(battler, defender) -> bool:
    """EXPERT_TRAINER: consider switching out when badly type-disadvantaged
    (every usable move scores poorly against the current opponent)."""
    moves = usable_moves(battler)
    if not moves:
        return True
    best = max(score_move(m, battler, defender) for m in moves)
    return best < 0.15


def choose_move(tier: AITier, battler, defender, rng):
    if tier == AITier.WILD:
        return choose_move_wild(battler, defender, rng)
    if tier == AITier.BASIC_TRAINER:
        return choose_move_basic_trainer(battler, defender, rng)
    return choose_move_expert_trainer(battler, defender, rng)
