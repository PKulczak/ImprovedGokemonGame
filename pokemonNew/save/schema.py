"""SaveData: the one dataclass that fully describes a save slot. Party/PC-box
Pokemon are stored as plain dicts (produced by battle.pokemon.PokemonInstance.to_dict())
so this module has zero dependency on the battle package."""

from dataclasses import dataclass, field, asdict

CURRENT_SAVE_VERSION = 1


@dataclass
class PlayerState:
    name: str = "Red"
    map_id: str = "sagewood_town"
    tile_x: int = 5
    tile_y: int = 5
    facing: str = "DOWN"
    playtime_seconds: float = 0.0


@dataclass
class SaveData:
    version: int = CURRENT_SAVE_VERSION
    player: PlayerState = field(default_factory=PlayerState)
    party: list = field(default_factory=list)             # list[dict]
    pc_boxes: list = field(default_factory=list)            # list[list[Optional[dict]]]
    bag: dict = field(default_factory=dict)
    pokedex_seen: list = field(default_factory=list)
    pokedex_caught: list = field(default_factory=list)
    badges: list = field(default_factory=list)
    story_flags: dict = field(default_factory=dict)
    defeated_trainers: list = field(default_factory=list)
    money: int = 0

    def to_dict(self):
        return {
            "version": self.version,
            "player": asdict(self.player),
            "party": self.party,
            "pc_boxes": self.pc_boxes,
            "bag": dict(self.bag),
            "pokedex_seen": list(self.pokedex_seen),
            "pokedex_caught": list(self.pokedex_caught),
            "badges": list(self.badges),
            "story_flags": dict(self.story_flags),
            "defeated_trainers": list(self.defeated_trainers),
            "money": self.money,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            version=data.get("version", CURRENT_SAVE_VERSION),
            player=PlayerState(**data.get("player", {})),
            party=data.get("party", []),
            pc_boxes=data.get("pc_boxes", []),
            bag=data.get("bag", {}),
            pokedex_seen=data.get("pokedex_seen", []),
            pokedex_caught=data.get("pokedex_caught", []),
            badges=data.get("badges", []),
            story_flags=data.get("story_flags", {}),
            defeated_trainers=data.get("defeated_trainers", []),
            money=data.get("money", 0),
        )
