"""Core data schemas for the battle engine.

Pure dataclasses/enums, zero pygame dependency, zero dependency on any other
`battle/*` module except where noted. Other workstreams (species/moves/
trainers content authoring, and the eventual Pygame battle scene) import
these classes by these exact names, so field names/shapes must not change.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Mapping, Optional


class Type(Enum):
    NORMAL = "normal"
    FIRE = "fire"
    WATER = "water"
    ELECTRIC = "electric"
    GRASS = "grass"
    ICE = "ice"
    FIGHTING = "fighting"
    POISON = "poison"
    GROUND = "ground"
    FLYING = "flying"
    PSYCHIC = "psychic"
    BUG = "bug"
    ROCK = "rock"
    GHOST = "ghost"
    DRAGON = "dragon"
    DARK = "dark"
    STEEL = "steel"
    # 17 types total. Deliberately NO FAIRY -- it doesn't exist pre-Gen-6 and
    # our whole roster is Gen 1-5. Confirmed correct, not an oversight.


# Gen 3 physical/special split is BY MOVE TYPE, not per-move (that's Gen 4+).
PHYSICAL_TYPES = frozenset({
    Type.NORMAL, Type.FIGHTING, Type.FLYING, Type.GROUND, Type.ROCK,
    Type.BUG, Type.GHOST, Type.POISON, Type.STEEL,
})
SPECIAL_TYPES = frozenset({
    Type.FIRE, Type.WATER, Type.GRASS, Type.ELECTRIC, Type.ICE,
    Type.PSYCHIC, Type.DRAGON, Type.DARK,
})


class MoveCategory(Enum):
    PHYSICAL = "physical"
    SPECIAL = "special"
    STATUS = "status"


class Stat(Enum):
    HP = "hp"
    ATTACK = "attack"
    DEFENSE = "defense"
    SP_ATK = "sp_atk"
    SP_DEF = "sp_def"
    SPEED = "speed"


@dataclass(frozen=True)
class StatBlock:
    hp: int
    attack: int
    defense: int
    sp_atk: int
    sp_def: int
    speed: int

    def get(self, stat: Stat) -> int:
        return getattr(self, stat.value)


class GenderRatio(Enum):
    ALWAYS_MALE = "always_male"
    MOSTLY_MALE = "mostly_male"
    EVEN = "even"
    MOSTLY_FEMALE = "mostly_female"
    ALWAYS_FEMALE = "always_female"
    GENDERLESS = "genderless"


class GrowthRate(Enum):
    FAST = "fast"
    MEDIUM_FAST = "medium_fast"
    MEDIUM_SLOW = "medium_slow"
    SLOW = "slow"


class EvolutionTrigger(Enum):
    LEVEL_UP = "level_up"
    ITEM = "item"
    OTHER = "other"


@dataclass(frozen=True)
class EvolutionRule:
    trigger: EvolutionTrigger
    target_dex_number: int
    min_level: Optional[int] = None
    item_name: Optional[str] = None
    note: str = ""


@dataclass(frozen=True)
class Species:
    dex_number: int
    name: str
    type1: Type
    type2: Optional[Type]
    base_stats: StatBlock
    abilities: tuple  # tuple[str, ...] -- 1-2 normal-slot ability names
    hidden_ability: Optional[str]
    gender_ratio: GenderRatio
    base_catch_rate: int
    base_exp_yield: int
    ev_yield: Mapping  # Mapping[Stat, int]
    growth_rate: GrowthRate
    learnset: tuple  # tuple[tuple[int, str], ...], sorted ascending by level
    evolutions: tuple  # tuple[EvolutionRule, ...]
    flavor_text: str = ""


class Target(Enum):
    USER = "user"
    OPPONENT = "opponent"


@dataclass(frozen=True)
class Move:
    name: str
    type: Type
    category: MoveCategory
    power: Optional[int]
    accuracy: Optional[int]  # None = never misses
    pp: int
    priority: int = 0
    target: Target = Target.OPPONENT
    makes_contact: bool = False
    secondary_effect: Optional[str] = None
    secondary_effect_chance: int = 100
    secondary_effect_params: Mapping = field(default_factory=dict)
    flavor_text: str = ""

    def __post_init__(self):
        if self.category == MoveCategory.STATUS or self.power is None:
            return
        if self.type in PHYSICAL_TYPES:
            expected = MoveCategory.PHYSICAL
        elif self.type in SPECIAL_TYPES:
            expected = MoveCategory.SPECIAL
        else:
            expected = None
        if expected is not None and self.category != expected:
            raise ValueError(
                f"Move {self.name!r}: type {self.type} requires category "
                f"{expected} under the Gen-3 type-based physical/special "
                f"split, got {self.category}"
            )


@dataclass(frozen=True)
class Ability:
    name: str
    flavor_text: str
    effect_hook: Optional[str] = None


class ItemCategory(Enum):
    HELD = "held"
    CONSUMABLE = "consumable"
    BALL = "ball"
    TM = "tm"
    KEY = "key"


@dataclass(frozen=True)
class Item:
    name: str
    category: ItemCategory
    flavor_text: str
    effect_hook: Optional[str] = None
    catch_multiplier: Optional[float] = None
    teaches_move: Optional[str] = None


@dataclass(frozen=True)
class Nature:
    name: str
    increased_stat: Optional[Stat]
    decreased_stat: Optional[Stat]


class AITier(Enum):
    WILD = "wild"
    BASIC_TRAINER = "basic_trainer"
    EXPERT_TRAINER = "expert_trainer"


@dataclass
class TrainerPokemonPreset:
    species: Species
    level: int
    moves: Optional[tuple] = None
    nature: Optional[str] = None
    ability_slot: Optional[object] = None
    ivs: Optional[object] = None
    evs: Optional[StatBlock] = None
    held_item: Optional[str] = None

    def instantiate(self, rng):
        """Factory: builds a fresh, full-HP, unstatused PokemonInstance.

        Resolves ability_slot/ivs/evs/nature/moves/held_item into concrete
        objects. Move objects and Item objects are resolved via
        ``data.moves.MOVES`` / ``data.items.ITEMS`` looked up lazily (at call
        time, not import time) to avoid a circular import between the
        `battle` and `data` packages. `data/moves.py` is owned by the
        content-authoring workstream and may not exist yet; if so, moves
        can only be resolved when this preset supplies explicit Move objects
        via a pre-resolved lookup (see battle/schemas.py docstring in repo
        history / final report for details).
        """
        # Local imports: deferred on purpose (see docstring above).
        from . import natures as _natures
        from .pokemon import Gender, LearnedMove, PokemonInstance, StatusCondition

        try:
            from data.moves import MOVES as _MOVES
        except ImportError:
            _MOVES = {}
        try:
            from data.items import ITEMS as _ITEMS
        except ImportError:
            _ITEMS = {}
        try:
            from data.abilities import ABILITIES as _ABILITIES
        except ImportError:
            _ABILITIES = {}

        # Nature
        if self.nature is not None:
            nature = _natures.NATURES[self.nature]
        else:
            nature = rng.choice(list(_natures.NATURES.values()))

        # Ability
        if self.ability_slot == "hidden" and self.species.hidden_ability:
            ability_name = self.species.hidden_ability
        elif isinstance(self.ability_slot, int):
            ability_name = self.species.abilities[self.ability_slot]
        elif self.ability_slot is None:
            ability_name = rng.choice(list(self.species.abilities))
        else:
            ability_name = self.species.abilities[0]
        ability = _ABILITIES.get(ability_name, Ability(name=ability_name, flavor_text=""))

        # IVs
        if self.ivs == "perfect":
            ivs = StatBlock(31, 31, 31, 31, 31, 31)
        elif isinstance(self.ivs, StatBlock):
            ivs = self.ivs
        else:
            ivs = StatBlock(*(rng.randint(0, 31) for _ in range(6)))

        # EVs
        evs = self.evs if self.evs is not None else StatBlock(0, 0, 0, 0, 0, 0)

        # Held item
        held_item = _ITEMS.get(self.held_item) if self.held_item else None

        # Moves: explicit names, or auto-pick best (highest-level) 4 from
        # the learnset at-or-below this preset's level.
        if self.moves is not None:
            move_names = list(self.moves)
        else:
            learnable = [name for lvl, name in self.species.learnset if lvl <= self.level]
            move_names = learnable[-4:]

        learned_moves = []
        for name in move_names:
            move_obj = _MOVES.get(name)
            if move_obj is None:
                continue
            learned_moves.append(LearnedMove(move=move_obj, current_pp=move_obj.pp))

        stats = None
        # Gender
        if self.species.gender_ratio == GenderRatio.GENDERLESS:
            gender = Gender.GENDERLESS
        elif self.species.gender_ratio == GenderRatio.ALWAYS_MALE:
            gender = Gender.MALE
        elif self.species.gender_ratio == GenderRatio.ALWAYS_FEMALE:
            gender = Gender.FEMALE
        else:
            female_chance = {
                GenderRatio.MOSTLY_MALE: 0.125,
                GenderRatio.EVEN: 0.5,
                GenderRatio.MOSTLY_FEMALE: 0.875,
            }[self.species.gender_ratio]
            gender = Gender.FEMALE if rng.random() < female_chance else Gender.MALE

        pokemon = PokemonInstance(
            species=self.species,
            level=self.level,
            current_exp=0,
            ivs=ivs,
            evs=evs,
            nature=nature,
            ability=ability,
            held_item=held_item,
            current_hp=0,
            status=StatusCondition.NONE,
            moves=learned_moves,
            gender=gender,
        )
        pokemon.current_hp = pokemon.get_stats().hp
        return pokemon


@dataclass
class Trainer:
    name: str
    trainer_class: str
    team: tuple  # tuple[TrainerPokemonPreset, ...]
    ai_tier: AITier
    prize_money: int
    pre_battle_text: tuple = ()
    win_text: tuple = ()
    lose_text: tuple = ()
