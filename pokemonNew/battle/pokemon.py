"""PokemonInstance: the persisted, per-Pokemon runtime data (save-game shape).

Distinct from `battle_state.Battler`, which wraps a PokemonInstance with
battle-only, non-persisted state (stat stages, confusion, etc).
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from . import stats as _stats
from .schemas import Ability, Item, Move, Nature, Species, StatBlock


class StatusCondition(Enum):
    NONE = "none"
    BURN = "burn"
    FREEZE = "freeze"
    PARALYSIS = "paralysis"
    POISON = "poison"
    TOXIC = "toxic"
    SLEEP = "sleep"


class Gender(Enum):
    MALE = "male"
    FEMALE = "female"
    GENDERLESS = "genderless"


@dataclass
class LearnedMove:
    move: Move
    current_pp: int


@dataclass
class PokemonInstance:
    species: Species
    level: int
    current_exp: int
    ivs: StatBlock
    evs: StatBlock
    nature: Nature
    ability: Ability
    held_item: Optional[Item]
    current_hp: int
    status: StatusCondition = StatusCondition.NONE
    status_data: dict = field(default_factory=dict)
    moves: list = field(default_factory=list)  # list[LearnedMove]
    gender: Gender = Gender.GENDERLESS
    nickname: Optional[str] = None

    # Internal cache, not part of the persisted shape / equality.
    _stat_cache: Optional[StatBlock] = field(default=None, repr=False, compare=False)

    def get_stats(self) -> StatBlock:
        if self._stat_cache is None:
            self._stat_cache = _stats.calc_all_stats(
                self.species.base_stats, self.ivs, self.evs, self.level, self.nature
            )
        return self._stat_cache

    def invalidate_stat_cache(self) -> None:
        self._stat_cache = None

    def is_fainted(self) -> bool:
        return self.current_hp <= 0

    @property
    def display_name(self) -> str:
        return self.nickname or self.species.name

    def to_dict(self) -> dict:
        return {
            "species": self.species.name,
            "level": self.level,
            "current_exp": self.current_exp,
            "ivs": _statblock_to_dict(self.ivs),
            "evs": _statblock_to_dict(self.evs),
            "nature": self.nature.name,
            "ability": self.ability.name,
            "held_item": self.held_item.name if self.held_item else None,
            "current_hp": self.current_hp,
            "status": self.status.value,
            "status_data": dict(self.status_data),
            "moves": [
                {"move": lm.move.name, "current_pp": lm.current_pp}
                for lm in self.moves
            ],
            "gender": self.gender.value,
            "nickname": self.nickname,
        }

    @classmethod
    def from_dict(cls, data: dict, species_lookup: dict) -> "PokemonInstance":
        """Rebuild a PokemonInstance from a save dict.

        `species_lookup` must be a dict[str, Species] (e.g. data.species.SPECIES).
        Moves/abilities/items are resolved the same way, lazily, from
        data.moves.MOVES / data.abilities.ABILITIES / data.items.ITEMS so this
        module has no hard import-time dependency on the content packages.
        """
        try:
            from data.moves import MOVES
        except ImportError:
            MOVES = {}
        try:
            from data.abilities import ABILITIES
        except ImportError:
            ABILITIES = {}
        try:
            from data.items import ITEMS
        except ImportError:
            ITEMS = {}
        from . import natures as _natures

        species = species_lookup[data["species"]]
        ability_name = data["ability"]
        ability = ABILITIES.get(ability_name, Ability(name=ability_name, flavor_text=""))
        held_item_name = data.get("held_item")
        held_item = ITEMS.get(held_item_name) if held_item_name else None

        moves = []
        for entry in data.get("moves", []):
            move_obj = MOVES.get(entry["move"])
            if move_obj is None:
                continue
            moves.append(LearnedMove(move=move_obj, current_pp=entry["current_pp"]))

        instance = cls(
            species=species,
            level=data["level"],
            current_exp=data["current_exp"],
            ivs=_statblock_from_dict(data["ivs"]),
            evs=_statblock_from_dict(data["evs"]),
            nature=_natures.NATURES[data["nature"]],
            ability=ability,
            held_item=held_item,
            current_hp=data["current_hp"],
            status=StatusCondition(data.get("status", "none")),
            status_data=dict(data.get("status_data", {})),
            moves=moves,
            gender=Gender(data.get("gender", "genderless")),
            nickname=data.get("nickname"),
        )
        return instance


def _statblock_to_dict(sb: StatBlock) -> dict:
    return {
        "hp": sb.hp, "attack": sb.attack, "defense": sb.defense,
        "sp_atk": sb.sp_atk, "sp_def": sb.sp_def, "speed": sb.speed,
    }


def _statblock_from_dict(d: dict) -> StatBlock:
    return StatBlock(
        hp=d["hp"], attack=d["attack"], defense=d["defense"],
        sp_atk=d["sp_atk"], sp_def=d["sp_def"], speed=d["speed"],
    )
