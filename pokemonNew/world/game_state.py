"""Live, in-memory view of a save slot: wraps the flat SaveData dataclass with
the convenience objects (StoryFlags/PartyManager/Inventory) scenes actually
interact with. Deserializing real Pokemon requires battle.pokemon +
data.species, which may not exist yet in every environment this runs in
(e.g. before the battle-mechanics workstream lands) — this degrades to an
empty party rather than crashing, since GameState itself must not depend on
the battle package to be importable.
"""

from save.schema import SaveData
from world.story_flags import StoryFlags
from world.party_manager import PartyManager
from world.inventory import Inventory


def _try_import_pokemon():
    try:
        from battle.pokemon import PokemonInstance
        from data.species import SPECIES
        return PokemonInstance, SPECIES
    except ImportError:
        return None, None


class GameState:
    def __init__(self, save_data=None):
        save_data = save_data or SaveData()
        self.player = save_data.player
        self.story_flags = StoryFlags(save_data.story_flags)
        self.inventory = Inventory(save_data.bag)
        self.party_manager = PartyManager(
            party=self._deserialize_mons(save_data.party),
            boxes=[self._deserialize_mons(box) for box in save_data.pc_boxes] or None,
        )
        self.pokedex_seen = set(save_data.pokedex_seen)
        self.pokedex_caught = set(save_data.pokedex_caught)
        self.badges = list(save_data.badges)
        self.defeated_trainers = set(save_data.defeated_trainers)
        self.money = save_data.money

    @staticmethod
    def _deserialize_mons(dicts):
        PokemonInstance, SPECIES = _try_import_pokemon()
        if PokemonInstance is None:
            return []
        return [PokemonInstance.from_dict(d, SPECIES) if d else None for d in dicts]

    def to_save_data(self):
        return SaveData(
            player=self.player,
            party=[mon.to_dict() for mon in self.party_manager.party],
            pc_boxes=[[mon.to_dict() if mon else None for mon in box] for box in self.party_manager.boxes],
            bag=self.inventory.to_dict(),
            pokedex_seen=sorted(self.pokedex_seen),
            pokedex_caught=sorted(self.pokedex_caught),
            badges=self.badges,
            story_flags=self.story_flags.to_dict(),
            defeated_trainers=sorted(self.defeated_trainers),
            money=self.money,
        )
