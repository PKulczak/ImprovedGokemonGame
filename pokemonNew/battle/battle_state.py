"""The turn-resolution engine: StatStages, Battler, BattleSide, Battle.

This is the runtime wrapper around the persisted `PokemonInstance` data --
none of it is saved, it's rebuilt fresh every battle.

Action vocabulary (not specified verbatim by the design doc, so defined
here): a turn's `player_action`/`enemy_action` passed to `run_turn` is one
of `MoveAction`, `SwitchAction`, or `ItemAction`.
"""

from dataclasses import dataclass, field
from typing import Optional

from . import experience as _experience
from . import move_effects as _move_effects
from . import stats as _stats
from . import status as _status
from .abilities import ABILITY_HANDLERS, AbilityContext
from .damage import calculate_damage, crit_chance, effective_crit_stat_stage
from .events import (
    BattleEvent, CriticalHit, DamageDealt, Fainted, HealDealt, ItemConsumed,
    Message, Missed, MoveUsed, StatStageChanged, StatusCured, StatusInflicted,
    SwitchedIn, Thawed, WeatherChanged, WeatherEnded,
)
from .items import ITEM_HANDLERS, ItemContext
from .move_effects import EFFECT_HANDLERS, MoveEffectContext
from .pokemon import StatusCondition
from .schemas import MoveCategory, Target
from .status import Weather
from .type_chart import TYPE_CHART

__all__ = [
    "StatStages", "Battler", "BattleSide", "Battle",
    "MoveAction", "SwitchAction", "ItemAction",
]

_DEFENDER_TARGETED_EFFECTS = {
    "burn", "poison", "toxic", "paralyze", "freeze", "sleep", "confuse",
    "flinch", "stat_change_target",
}


@dataclass
class StatStages:
    attack: int = 0
    defense: int = 0
    sp_atk: int = 0
    sp_def: int = 0
    speed: int = 0
    accuracy: int = 0
    evasion: int = 0


@dataclass
class Battler:
    pokemon: object  # PokemonInstance
    stages: StatStages = field(default_factory=StatStages)
    confusion_turns_remaining: int = 0
    toxic_counter: int = 0
    flinched: bool = False
    choice_locked_move: Optional[str] = None
    # Internal bookkeeping, not part of the spec'd shape -- reset each time a
    # fresh Battler wraps a newly-active Pokemon (i.e. never persisted).
    flags: dict = field(default_factory=dict)


@dataclass
class BattleSide:
    active: Battler
    bench: list  # list[PokemonInstance]


@dataclass
class MoveAction:
    move_index: int


@dataclass
class SwitchAction:
    bench_index: int


@dataclass
class ItemAction:
    item: object  # Item
    bench_index: Optional[int] = None  # None = the side's active Pokemon


def _type_mult(attacking_type, defending_type):
    if defending_type is None:
        return 1.0
    return TYPE_CHART.get(attacking_type, {}).get(defending_type, 1.0)


class Battle:
    """Owns both BattleSides, weather state, turn counter, and run_turn()."""

    ABILITY_WEATHER_DURATION = _status.ABILITY_WEATHER_DURATION
    MOVE_WEATHER_DURATION = _status.MOVE_WEATHER_DURATION

    def __init__(self, player_side: BattleSide, enemy_side: BattleSide, rng, trainer_battle: bool = False):
        self.player_side = player_side
        self.enemy_side = enemy_side
        self.rng = rng
        self.trainer_battle = trainer_battle
        self.weather = Weather.NONE
        self.weather_turns_remaining = 0
        self.turn_count = 0
        self._pending_events = []
        self._fire_switch_in_abilities(self.player_side, "player", self._pending_events)
        self._fire_switch_in_abilities(self.enemy_side, "enemy", self._pending_events)

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #

    def is_over(self) -> bool:
        return self._side_defeated(self.player_side) or self._side_defeated(self.enemy_side)

    def winner(self) -> Optional[str]:
        p_dead = self._side_defeated(self.player_side)
        e_dead = self._side_defeated(self.enemy_side)
        if p_dead and e_dead:
            return None
        if p_dead:
            return "enemy"
        if e_dead:
            return "player"
        return None

    def run_turn(self, player_action, enemy_action) -> list:
        events = list(self._pending_events)
        self._pending_events = []
        self.turn_count += 1

        pending_moves = []
        for side_name, side, action in (
            ("player", self.player_side, player_action),
            ("enemy", self.enemy_side, enemy_action),
        ):
            if isinstance(action, SwitchAction):
                self._perform_switch(side, side_name, action.bench_index, events)
            elif isinstance(action, ItemAction):
                self._perform_item(side, side_name, action, events)
            elif isinstance(action, MoveAction):
                pending_moves.append((side_name, side, action))

        self._check_faint(self.player_side.active, "player", events)
        self._check_faint(self.enemy_side.active, "enemy", events)
        if self.is_over():
            return events

        ordered = self._order_moves(pending_moves)

        for side_name, side, action in ordered:
            battler = side.active
            if battler.pokemon.is_fainted():
                continue
            other_side_name = "enemy" if side_name == "player" else "player"
            other_side = self.enemy_side if side_name == "player" else self.player_side

            can_act, act_events = _status.can_act(battler, side_name, self.rng)
            events.extend(act_events)
            self._check_faint(battler, side_name, events)
            if self.is_over():
                break
            if not can_act:
                continue

            move = self._resolve_move_for_action(battler, action)
            if move is None:
                continue
            self._resolve_move(battler, side_name, move, other_side.active, other_side_name, events)
            self._check_faint(other_side.active, other_side_name, events)
            self._check_faint(battler, side_name, events)
            if self.is_over():
                break

        # Flinch clears at end of every turn regardless of cause.
        self.player_side.active.flinched = False
        self.enemy_side.active.flinched = False

        if not self.is_over():
            self._end_of_turn_phase(events)

        return events

    # ------------------------------------------------------------------ #
    # Switch / item actions
    # ------------------------------------------------------------------ #

    def _perform_switch(self, side: BattleSide, side_name: str, bench_index: int, events: list):
        if bench_index is None or not (0 <= bench_index < len(side.bench)):
            return
        incoming = side.bench[bench_index]
        if incoming.is_fainted():
            return
        outgoing = side.active
        side.bench[bench_index] = outgoing.pokemon
        side.active = Battler(pokemon=incoming)
        events.append(SwitchedIn(side=side_name, pokemon_name=incoming.display_name))
        self._fire_switch_in_abilities(side, side_name, events)

    def _fire_switch_in_abilities(self, side: BattleSide, side_name: str, events: list):
        battler = side.active
        other_side = self.enemy_side if side_name == "player" else self.player_side
        self._call_ability_hook(battler, "on_switch_in", other=other_side.active, events=events)

    def _perform_item(self, side: BattleSide, side_name: str, action: ItemAction, events: list):
        target_pokemon = side.active.pokemon if action.bench_index is None else side.bench[action.bench_index]
        item = action.item
        hook = ITEM_HANDLERS.get(item.effect_hook) if item and item.effect_hook else None
        if hook is None:
            return
        had_effect = hook(target_pokemon)
        if had_effect:
            events.append(ItemConsumed(side=side_name, pokemon_name=target_pokemon.display_name, item_name=item.name))

    def _auto_send_out_if_needed(self, side: BattleSide, side_name: str, events: list):
        if not side.active.pokemon.is_fainted():
            return
        for i, mon in enumerate(side.bench):
            if not mon.is_fainted():
                fainted_mon = side.active.pokemon
                side.bench.pop(i)
                side.bench.append(fainted_mon)
                side.active = Battler(pokemon=mon)
                events.append(SwitchedIn(side=side_name, pokemon_name=mon.display_name))
                self._fire_switch_in_abilities(side, side_name, events)
                return

    # ------------------------------------------------------------------ #
    # Move ordering
    # ------------------------------------------------------------------ #

    def _resolve_move_for_action(self, battler: Battler, action: MoveAction):
        if battler.choice_locked_move is not None:
            for lm in battler.pokemon.moves:
                if lm.move.name == battler.choice_locked_move:
                    return lm.move if lm.current_pp > 0 else None
        if action is None:
            return None
        moves = battler.pokemon.moves
        if 0 <= action.move_index < len(moves):
            return moves[action.move_index].move
        return None

    def _order_moves(self, pending_moves):
        scored = []
        for side_name, side, action in pending_moves:
            battler = side.active
            move = self._resolve_move_for_action(battler, action)
            priority = move.priority if move is not None else -999
            quick = bool(self._call_item_hook(battler, "roll_priority_bonus", events=[]))
            spd = _status.effective_speed(battler)
            tiebreak = self.rng.random()
            scored.append(((-priority, 0 if quick else 1, -spd, tiebreak), side_name, side, action))
        scored.sort(key=lambda t: t[0])
        return [(s[1], s[2], s[3]) for s in scored]

    # ------------------------------------------------------------------ #
    # Move resolution
    # ------------------------------------------------------------------ #

    def _resolve_move(self, attacker: Battler, attacker_side: str, move, defender: Battler, defender_side: str, events: list):
        pokemon = attacker.pokemon
        learned = self._find_learned_move(pokemon, move)
        if learned is not None and learned.current_pp <= 0:
            events.append(Message(text=f"{pokemon.display_name} has no PP left for {move.name}!"))
            return
        if learned is not None:
            learned.current_pp = max(0, learned.current_pp - 1)

        events.append(MoveUsed(side=attacker_side, pokemon_name=pokemon.display_name, move_name=move.name))
        self._call_item_hook(attacker, "on_move_used", value=move.name, events=events)

        if move.target == Target.OPPONENT:
            defender_types = [defender.pokemon.species.type1, defender.pokemon.species.type2]
            type_mult_total = 1.0
            for dt in defender_types:
                type_mult_total *= _type_mult(move.type, dt)
            ability_immune = bool(self._call_ability_hook(
                defender, "check_immunity", move=move, other=attacker, events=events,
            ))
            if type_mult_total == 0 or ability_immune:
                events.append(Message(text=f"It doesn't affect {defender.pokemon.display_name}!"))
                return

        if move.secondary_effect == "ohko":
            hit = move.accuracy is None or self.rng.randint(1, 100) <= move.accuracy
            if not hit:
                events.append(Missed(side=defender_side, pokemon_name=defender.pokemon.display_name, move_name=move.name))
                return
            ctx = MoveEffectContext(battle=self, attacker=attacker, defender=defender, move=move, rng=self.rng, events=events)
            EFFECT_HANDLERS["ohko"](ctx)
            return

        if move.accuracy is not None:
            evasion_stage = defender.stages.evasion
            if self._call_ability_hook(attacker, "check_ignore_evasion", events=events):
                evasion_stage = min(evasion_stage, 0)
            combined_stage = max(-6, min(6, attacker.stages.accuracy - evasion_stage))
            effective_accuracy = _stats.apply_accuracy_stage(move.accuracy, combined_stage)
            hit = self.rng.randint(1, 100) <= effective_accuracy
        else:
            hit = True

        if not hit:
            events.append(Missed(side=defender_side, pokemon_name=defender.pokemon.display_name, move_name=move.name))
            return

        crit_stage = 1 if move.secondary_effect == "high_crit" else 0
        crit_bonus = self._call_item_hook(attacker, "modify_crit_stage", value=crit_stage, events=events)
        if crit_bonus:
            crit_stage += crit_bonus
        is_crit = self.rng.random() < crit_chance(crit_stage)

        damage_dealt = 0
        if move.category != MoveCategory.STATUS and move.power is not None:
            damage_dealt = self._compute_and_apply_damage(attacker, attacker_side, move, defender, defender_side, is_crit, events)

        if move.secondary_effect and move.secondary_effect not in ("ohko", "high_crit"):
            if move.secondary_effect in _DEFENDER_TARGETED_EFFECTS and defender.pokemon.is_fainted():
                pass
            elif self.rng.randint(1, 100) <= move.secondary_effect_chance:
                handler = EFFECT_HANDLERS.get(move.secondary_effect)
                if handler is not None:
                    ctx = MoveEffectContext(
                        battle=self, attacker=attacker, defender=defender, move=move, rng=self.rng,
                        damage_dealt=damage_dealt, params=dict(move.secondary_effect_params), events=events,
                    )
                    handler(ctx)

    def _compute_and_apply_damage(self, attacker: Battler, attacker_side: str, move, defender: Battler, defender_side: str, is_crit: bool, events: list) -> int:
        atk_stats = attacker.pokemon.get_stats()
        def_stats = defender.pokemon.get_stats()
        is_physical = move.category == MoveCategory.PHYSICAL

        if is_physical:
            atk_stage, raw_atk = attacker.stages.attack, atk_stats.attack
            def_stage, raw_def = defender.stages.defense, def_stats.defense
            atk_stat_name, def_stat_name = "attack", "defense"
        else:
            atk_stage, raw_atk = attacker.stages.sp_atk, atk_stats.sp_atk
            def_stage, raw_def = defender.stages.sp_def, def_stats.sp_def
            atk_stat_name, def_stat_name = "sp_atk", "sp_def"

        if is_crit:
            atk_stage = effective_crit_stat_stage(atk_stage, is_attacker=True)
            def_stage = effective_crit_stat_stage(def_stage, is_attacker=False)

        atk_value = _stats.apply_stat_stage(raw_atk, atk_stage)
        def_value = _stats.apply_stat_stage(raw_def, def_stage)
        atk_value = self._apply_modify_stat(attacker, atk_stat_name, atk_value, events)
        def_value = self._apply_modify_stat(defender, def_stat_name, def_value, events)

        power = move.power
        w_num, w_den = _status.weather_power_multiplier(self.weather, move.type)
        power = (power * w_num) // w_den

        power_mult = 1.0
        ability_mult = self._call_ability_hook(attacker, "modify_power", move=move, value=power_mult, events=events)
        if ability_mult is not None:
            power_mult *= ability_mult
        item_mult = self._call_item_hook(attacker, "modify_power", move=move, value=power_mult, events=events)
        if item_mult is not None:
            power_mult *= item_mult
        power = int(power * power_mult)

        is_stab = move.type in (attacker.pokemon.species.type1, attacker.pokemon.species.type2)
        type1_mult = _type_mult(move.type, defender.pokemon.species.type1)
        type2_mult = _type_mult(move.type, defender.pokemon.species.type2) if defender.pokemon.species.type2 else 1.0

        should_halve = is_physical and attacker.pokemon.status == StatusCondition.BURN
        if should_halve:
            halving_check = self._call_ability_hook(attacker, "check_burn_halving", events=events)
            if halving_check is False:
                should_halve = False

        was_full_hp = defender.pokemon.current_hp >= defender.pokemon.get_stats().hp

        damage = calculate_damage(
            level=attacker.pokemon.level, power=power, atk_stat=atk_value, def_stat=def_value,
            is_crit=is_crit, is_stab=is_stab, type1_mult=type1_mult, type2_mult=type2_mult,
            is_burn_halved=should_halve, rng=self.rng,
        )

        if is_crit:
            events.append(CriticalHit(side=attacker_side, pokemon_name=attacker.pokemon.display_name))

        new_hp = defender.pokemon.current_hp - damage
        if new_hp <= 0:
            survive = self._call_item_hook(
                defender, "check_survive_lethal", extra={"was_full_hp": was_full_hp}, events=events,
            )
            new_hp = 1 if survive else 0
        defender.pokemon.current_hp = max(0, new_hp)

        if move.type.value == "fire" and move.category != MoveCategory.STATUS and defender.pokemon.status == StatusCondition.FREEZE:
            _status.cure_status(defender.pokemon)
            events.append(Thawed(side=defender_side, pokemon_name=defender.pokemon.display_name))

        events.append(DamageDealt(
            side=defender_side, pokemon_name=defender.pokemon.display_name, amount=damage,
            remaining_hp=defender.pokemon.current_hp, max_hp=defender.pokemon.get_stats().hp, source="move",
        ))

        if move.makes_contact:
            self._call_ability_hook(defender, "on_contact_received", other=attacker, move=move, events=events)
        self._call_item_hook(attacker, "on_hit_landed", other=defender, move=move, events=events)

        return damage

    def _find_learned_move(self, pokemon, move):
        for lm in pokemon.moves:
            if lm.move is move or lm.move.name == move.name:
                return lm
        return None

    def _apply_modify_stat(self, battler: Battler, stat_name: str, value: int, events: list) -> int:
        mult = 1.0
        a = self._call_ability_hook(battler, "modify_stat", extra={"stat_name": stat_name}, events=events)
        if a is not None:
            mult *= a
        i = self._call_item_hook(battler, "modify_stat", extra={"stat_name": stat_name}, events=events)
        if i is not None:
            mult *= i
        return int(value * mult)

    # ------------------------------------------------------------------ #
    # End of turn
    # ------------------------------------------------------------------ #

    def _end_of_turn_phase(self, events: list):
        order = sorted(
            [self.player_side, self.enemy_side],
            key=lambda s: -_status.effective_speed(s.active),
        )

        for side in order:
            b = side.active
            if b.pokemon.is_fainted():
                continue
            dmg = _status.weather_chip_damage(self.weather, b.pokemon)
            if dmg > 0:
                self.deal_direct_damage(b, dmg, events=events, source="weather")
                self._check_faint(b, self._side_of(b), events)
        if self.is_over():
            return

        for side in order:
            b = side.active
            if b.pokemon.is_fainted():
                continue
            dmg = _status.status_tick_damage(b)
            if dmg > 0:
                source = _status.is_status_damage_source(b.pokemon)
                self.deal_direct_damage(b, dmg, events=events, source=source)
                self._check_faint(b, self._side_of(b), events)
            if b.pokemon.status == StatusCondition.TOXIC and not b.pokemon.is_fainted():
                b.toxic_counter += 1
        if self.is_over():
            return

        for side in order:
            b = side.active
            if b.pokemon.is_fainted():
                continue
            self._call_item_hook(b, "end_of_turn", events=events)
            self._call_item_hook(b, "hp_threshold", events=events)
        if self.is_over():
            return

        for side in order:
            b = side.active
            if b.pokemon.is_fainted():
                continue
            self._call_ability_hook(b, "end_of_turn", events=events)

        if self.weather != Weather.NONE:
            self.weather_turns_remaining -= 1
            if self.weather_turns_remaining <= 0:
                ended = self.weather
                self.weather = Weather.NONE
                events.append(WeatherEnded(weather=ended.value))

        self._check_faint(self.player_side.active, "player", events)
        self._check_faint(self.enemy_side.active, "enemy", events)

    # ------------------------------------------------------------------ #
    # Shared helpers used by ability/item/move-effect handlers
    # ------------------------------------------------------------------ #

    def _side_defeated(self, side: BattleSide) -> bool:
        return side.active.pokemon.is_fainted() and all(mon.is_fainted() for mon in side.bench)

    def _side_of(self, battler: Battler) -> str:
        if battler is self.player_side.active:
            return "player"
        if battler is self.enemy_side.active:
            return "enemy"
        return "unknown"

    def _check_faint(self, battler: Optional[Battler], side_name: str, events: list):
        if battler is None:
            return
        if battler.pokemon.is_fainted() and not battler.flags.get("_faint_processed"):
            battler.flags["_faint_processed"] = True
            events.append(Fainted(side=side_name, pokemon_name=battler.pokemon.display_name))
            other_side = self.enemy_side if side_name == "player" else self.player_side
            other_side_active = other_side.active
            if other_side_active is not None and not other_side_active.pokemon.is_fainted():
                exp_events = _experience.award_exp_and_evs(
                    other_side_active.pokemon, battler.pokemon,
                    trainer_battle=self.trainer_battle, rng=self.rng,
                )
                events.extend(exp_events)
            side = self.player_side if side_name == "player" else self.enemy_side
            self._auto_send_out_if_needed(side, side_name, events)

    def _call_ability_hook(self, battler: Battler, event: str, *, other=None, move=None, value=None, extra=None, events=None):
        if events is None:
            events = []
        ability = battler.pokemon.ability
        hook = ABILITY_HANDLERS.get(ability.effect_hook) if ability and ability.effect_hook else None
        if hook is None:
            return None
        ctx = AbilityContext(
            event=event, battle=self, battler=battler, other=other, move=move,
            value=value, rng=self.rng, extra=extra or {},
        )
        result = hook(ctx)
        events.extend(ctx.events)
        return result

    def _call_item_hook(self, battler: Battler, event: str, *, other=None, move=None, value=None, extra=None, events=None):
        if events is None:
            events = []
        item = battler.pokemon.held_item
        hook = ITEM_HANDLERS.get(item.effect_hook) if item and item.effect_hook else None
        if hook is None:
            return None
        ctx = ItemContext(
            event=event, battle=self, battler=battler, other=other, move=move,
            value=value, rng=self.rng, extra=extra or {},
        )
        result = hook(ctx)
        events.extend(ctx.events)
        return result

    def change_stat_stage(self, battler: Battler, stat: str, stages: int, events=None):
        if events is None:
            events = []
        stat_name = stat.value if hasattr(stat, "value") else stat
        blocked = self._call_ability_hook(
            battler, "prevent_stat_stage_change", extra={"stat": stat_name, "stages": stages}, events=events,
        )
        if blocked:
            return
        current = getattr(battler.stages, stat_name)
        new_val = max(-6, min(6, current + stages))
        delta = new_val - current
        setattr(battler.stages, stat_name, new_val)
        if delta != 0:
            events.append(StatStageChanged(
                side=self._side_of(battler), pokemon_name=battler.pokemon.display_name,
                stat=stat_name, delta=delta, new_stage=new_val,
            ))

    def try_inflict_status(self, target_battler: Battler, status: StatusCondition, events=None, source_battler=None, allow_reflect=True) -> bool:
        if events is None:
            events = []
        if target_battler.pokemon.is_fainted():
            return False
        blocked = self._call_ability_hook(target_battler, "prevent_status", value=status, events=events)
        if blocked:
            return False
        success = _status.inflict_status(target_battler.pokemon, status, rng=self.rng)
        if success:
            if status == StatusCondition.TOXIC:
                target_battler.toxic_counter = 1
            events.append(StatusInflicted(
                side=self._side_of(target_battler), pokemon_name=target_battler.pokemon.display_name, status=status.value,
            ))
            if source_battler is not None and allow_reflect:
                self._call_ability_hook(target_battler, "on_status_inflicted", other=source_battler, value=status, events=events)
        return success

    def try_inflict_confusion(self, target_battler: Battler, events=None) -> bool:
        if events is None:
            events = []
        if target_battler.pokemon.is_fainted():
            return False
        target_battler.confusion_turns_remaining = self.rng.randint(2, 5)
        events.append(StatusInflicted(
            side=self._side_of(target_battler), pokemon_name=target_battler.pokemon.display_name, status="confusion",
        ))
        return True

    def set_flinch(self, target_battler: Battler, events=None):
        target_battler.flinched = True

    def deal_direct_damage(self, battler: Battler, amount: int, events=None, source: str = "") -> int:
        if events is None:
            events = []
        if battler.pokemon.is_fainted() or amount <= 0:
            return 0
        was_full = battler.pokemon.current_hp >= battler.pokemon.get_stats().hp
        new_hp = battler.pokemon.current_hp - amount
        if new_hp <= 0:
            survive = self._call_item_hook(battler, "check_survive_lethal", extra={"was_full_hp": was_full}, events=events)
            new_hp = 1 if survive else 0
        battler.pokemon.current_hp = max(0, new_hp)
        events.append(DamageDealt(
            side=self._side_of(battler), pokemon_name=battler.pokemon.display_name, amount=amount,
            remaining_hp=battler.pokemon.current_hp, max_hp=battler.pokemon.get_stats().hp, source=source,
        ))
        return amount

    def deal_fractional_damage(self, battler: Battler, num: int, den: int, events=None, source: str = "") -> int:
        max_hp = battler.pokemon.get_stats().hp
        amount = max(1, (max_hp * num) // den)
        return self.deal_direct_damage(battler, amount, events=events, source=source)

    def heal_flat(self, battler: Battler, amount: int, events=None, source: str = "") -> int:
        if events is None:
            events = []
        if battler.pokemon.is_fainted() or amount <= 0:
            return 0
        max_hp = battler.pokemon.get_stats().hp
        new_hp = min(max_hp, battler.pokemon.current_hp + amount)
        healed = new_hp - battler.pokemon.current_hp
        battler.pokemon.current_hp = new_hp
        if healed > 0:
            events.append(HealDealt(
                side=self._side_of(battler), pokemon_name=battler.pokemon.display_name, amount=healed,
                remaining_hp=new_hp, max_hp=max_hp, source=source,
            ))
        return healed

    def heal_fractional(self, battler: Battler, num: int, den: int, events=None, source: str = "") -> int:
        max_hp = battler.pokemon.get_stats().hp
        amount = max(1, (max_hp * num) // den)
        return self.heal_flat(battler, amount, events=events, source=source)

    def cure_status_event(self, battler: Battler, events=None, source: str = ""):
        if events is None:
            events = []
        if battler.pokemon.status == StatusCondition.NONE:
            return
        status_name = battler.pokemon.status.value
        _status.cure_status(battler.pokemon)
        events.append(StatusCured(
            side=self._side_of(battler), pokemon_name=battler.pokemon.display_name, status=status_name, source=source,
        ))

    def note_item_cure(self, battler: Battler, status_name: str, events=None, source: str = ""):
        if events is None:
            events = []
        events.append(StatusCured(
            side=self._side_of(battler), pokemon_name=battler.pokemon.display_name, status=status_name, source=source,
        ))

    def set_weather(self, weather: Weather, duration: int, events=None):
        if events is None:
            events = []
        self.weather = weather
        self.weather_turns_remaining = duration
        events.append(WeatherChanged(weather=weather.value, turns=duration))

    def perform_rest(self, battler: Battler, events=None):
        if events is None:
            events = []
        blocked = self._call_ability_hook(battler, "prevent_status", value=StatusCondition.SLEEP, events=events)
        if blocked:
            events.append(Message(text=f"{battler.pokemon.display_name}'s Rest failed!"))
            return
        max_hp = battler.pokemon.get_stats().hp
        healed = max_hp - battler.pokemon.current_hp
        battler.pokemon.current_hp = max_hp
        battler.pokemon.status = StatusCondition.SLEEP
        battler.pokemon.status_data = {"sleep_turns_remaining": 2}
        if healed > 0:
            events.append(HealDealt(
                side=self._side_of(battler), pokemon_name=battler.pokemon.display_name, amount=healed,
                remaining_hp=max_hp, max_hp=max_hp, source="rest",
            ))
        events.append(StatusInflicted(side=self._side_of(battler), pokemon_name=battler.pokemon.display_name, status="sleep"))

    def apply_ohko(self, attacker: Battler, defender: Battler, events=None):
        if events is None:
            events = []
        immune = self._call_ability_hook(defender, "check_ohko_immunity", other=attacker, events=events)
        if immune:
            events.append(Message(text=f"{defender.pokemon.display_name} is unaffected!"))
            return
        old_hp = defender.pokemon.current_hp
        defender.pokemon.current_hp = 0
        events.append(DamageDealt(
            side=self._side_of(defender), pokemon_name=defender.pokemon.display_name, amount=old_hp,
            remaining_hp=0, max_hp=defender.pokemon.get_stats().hp, source="ohko",
        ))

    def apply_extra_multi_hits(self, attacker: Battler, defender: Battler, move, extra_count: int, events=None):
        if events is None:
            events = []
        attacker_side = self._side_of(attacker)
        defender_side = self._side_of(defender)
        for _ in range(max(0, extra_count)):
            if defender.pokemon.is_fainted():
                break
            is_crit = self.rng.random() < crit_chance(0)
            self._compute_and_apply_damage(attacker, attacker_side, move, defender, defender_side, is_crit, events)
            self._check_faint(defender, defender_side, events)
