"""Battle event log entries.

`Battle.run_turn()` returns/accumulates a list of these. This is the ONLY
thing a future Pygame battle scene consumes to drive animation/text, so
these must stay data-only (no pygame, no behavior).
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class BattleEvent:
    """Base class. All concrete events are dataclasses with plain data fields."""


@dataclass
class MoveUsed(BattleEvent):
    side: str          # "player" | "enemy"
    pokemon_name: str
    move_name: str


@dataclass
class Missed(BattleEvent):
    side: str
    pokemon_name: str
    move_name: str


@dataclass
class CriticalHit(BattleEvent):
    side: str
    pokemon_name: str


@dataclass
class DamageDealt(BattleEvent):
    side: str           # side of the POKEMON TAKING damage
    pokemon_name: str
    amount: int
    remaining_hp: int
    max_hp: int
    source: str = ""    # e.g. "move", "burn", "poison", "weather", "recoil", "confusion"


@dataclass
class HealDealt(BattleEvent):
    side: str
    pokemon_name: str
    amount: int
    remaining_hp: int
    max_hp: int
    source: str = ""


@dataclass
class StatusInflicted(BattleEvent):
    side: str
    pokemon_name: str
    status: str


@dataclass
class StatusCured(BattleEvent):
    side: str
    pokemon_name: str
    status: str
    source: str = ""


@dataclass
class StatStageChanged(BattleEvent):
    side: str
    pokemon_name: str
    stat: str
    delta: int
    new_stage: int


@dataclass
class Fainted(BattleEvent):
    side: str
    pokemon_name: str


@dataclass
class SwitchedIn(BattleEvent):
    side: str
    pokemon_name: str


@dataclass
class WeatherChanged(BattleEvent):
    weather: str
    turns: Optional[int] = None


@dataclass
class WeatherEnded(BattleEvent):
    weather: str


@dataclass
class AbilityTriggered(BattleEvent):
    side: str
    pokemon_name: str
    ability_name: str
    detail: str = ""


@dataclass
class ItemTriggered(BattleEvent):
    side: str
    pokemon_name: str
    item_name: str
    detail: str = ""


@dataclass
class ItemConsumed(BattleEvent):
    side: str
    pokemon_name: str
    item_name: str


@dataclass
class Flinched(BattleEvent):
    side: str
    pokemon_name: str


@dataclass
class ConfusionSelfHit(BattleEvent):
    side: str
    pokemon_name: str
    amount: int
    remaining_hp: int


@dataclass
class FullyParalyzed(BattleEvent):
    side: str
    pokemon_name: str


@dataclass
class WokeUp(BattleEvent):
    side: str
    pokemon_name: str


@dataclass
class Thawed(BattleEvent):
    side: str
    pokemon_name: str


@dataclass
class Message(BattleEvent):
    """Free-form fallback for flavor text a future UI might want to show."""
    text: str
