"""STARTERS: dict[str, TrainerPokemonPreset] -- the 3 new-game starter choices.

Each value is a ready-to-instantiate `battle.schemas.TrainerPokemonPreset` (not
a raw Species) so `scenes/starter_select.py` can hand the player's choice
straight to `preset.instantiate(rng)` to get a fresh, full-HP level-5
`PokemonInstance` with no extra plumbing needed.

Per the design doc, the three starters deliberately span three different
generations: Chikorita (Gen 2, Grass), Torchic (Gen 3, Fire), Oshawott
(Gen 5, Water). Rival Corin always picks whichever starter is
type-advantaged over the player's choice (Torchic beats Chikorita, Oshawott
beats Torchic, Chikorita beats Oshawott) -- see data/trainers.py for the
three parallel rival lines this implies.
"""

from battle.schemas import TrainerPokemonPreset
from data.species import SPECIES

STARTERS: dict[str, TrainerPokemonPreset] = {
    "Chikorita": TrainerPokemonPreset(
        species=SPECIES["Chikorita"], level=5,
        moves=("Tackle", "Growl", "Vine Whip"),
    ),
    "Torchic": TrainerPokemonPreset(
        species=SPECIES["Torchic"], level=5,
        moves=("Scratch", "Growl", "Ember"),
    ),
    "Oshawott": TrainerPokemonPreset(
        species=SPECIES["Oshawott"], level=5,
        moves=("Tackle", "Tail Whip", "Water Gun"),
    ),
}
