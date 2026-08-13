# Pokemon Virelia

A from-scratch Pokemon Emerald-style 2D RPG, built entirely new in this `pokemonNew/` folder — no code or design from the rest of this repository was reused, only some vendored art assets plus freely available Pokemon battle sprites.

Explore the region of **Virelia**, catch and train Pokemon spanning five generations, take on 8 gym leaders with distinct type themes, foil the schemes of **Team Eclipse**, and challenge the Elite Four and Champion.

## Running the game

```
cd pokemonNew
pip install -r requirements.txt
python main.py
```

Requires Python 3.10+ and Pygame 2.5+.

## Controls

| Key | Action |
|---|---|
| Arrow keys / WASD | Move / navigate menus |
| Z, Enter, or Space | Confirm / interact / advance text |
| X or Backspace | Cancel / back |
| Escape | Pause menu (Party / Bag / Pokedex / Save) |

## Development

```
pip install -r requirements-dev.txt
python -m pytest tests/ -v
```

Tests run entirely headless (`SDL_VIDEODRIVER=dummy`, set automatically by `tests/conftest.py`) — no display is required in CI or a remote shell. A few offline dev tools live in `tools/`:

- `tools/prepare_pokemon_sprites.py` — one-off script that populated `assets/pokemon/<name>/{front,back}.png` from a sparse clone of `PokeAPI/sprites` (Gen 5 Black/White style, chosen for one consistent art style across a roster that spans Gen 1–5), falling back to this repo's existing `game/Fight/pokemon/*.png` art for any species that wasn't available there.
- `tools/generate_base_tiles.py` — procedurally paints the small set of clean terrain tiles (`assets/tilesets/base_tiles.png`) used for every map's ground layer.
- `tools/slice_atlas.py` — connected-component detector that turns the irregular, bin-packed `MapBuilder/tilesets/padded_*.png` sheets into usable decoration-prop manifests (`assets/tilesets/*.atlas.json`) without any manual pixel-hunting.
- `tools/map_builder.py` — the small authoring helper (`MapBuilder`) every map under `data/maps/*.json` was built with; see any of those files' generating one-liners in the class's docstring for the pattern.
- `tools/render_preview.py <map_id>` — renders a single map to a PNG for a quick visual check.

## Architecture

```
pokemonNew/
├── main.py, settings.py            # entry point + pure constants
├── engine/                          # generic Pygame plumbing (scene stack, tilemap, camera, entities, dialogue, menus)
├── scenes/                          # concrete screens: title, starter select, overworld, battle, party/bag/pokedex/pause
├── world/                           # Pokemon-specific glue: encounters, trainers, NPC behavior, save-state wrapper
├── battle/                          # pure-Python, zero-pygame battle engine (stats/damage/status/abilities/items/AI/catching/EXP)
├── data/                            # content: species, moves, trainers, items, abilities, natures, maps, dialogue
├── assets/                          # sprites, tilesets, UI art (see Asset credits below)
├── save/                            # SaveData schema + JSON save/load (own save/ folder, isolated from the rest of the repo)
└── tests/                           # pytest suite — unit tests for battle math + headless integration tests for the whole game loop
```

The engine and battle system are fully decoupled: `battle/` has no `pygame` import anywhere and can be (and is) unit-tested in complete isolation. `Battle.run_turn()` returns a flat list of `BattleEvent` objects that `scenes/battle.py` translates into on-screen text/HP bars — the battle scene never reaches into battle-engine internals.

## Scope notes — what's deliberately simplified

This is a complete, playable game, not a byte-for-byte recreation of a commercial Pokemon title. Some things were deliberately scoped down or simplified to keep the whole thing buildable and correct in one focused effort:

- **Battle mechanics** are "full Gen 3 depth" — real Abilities, Natures, EVs/IVs, held items, weather, and all major status conditions — but a curated subset (~22 abilities, ~27 items) get real mechanical effects; every other ability/item name is authentic (real Gen 1-5 names) but flavor-only. Every basic bag item (Potions, status healers, Poke Balls, Revives) is fully implemented.
- **No double battles, no breeding/daycare.** Every evolution that would normally require trading (including trade-with-item and friendship-based evolutions) was converted to a plain level-up or direct-item-use trigger, so nothing is ever permanently unobtainable.
- **No music or sound effects** — a deliberate omission given the scope, not an oversight.
- **Gym/route "puzzles"** are maze-style layouts and trainer gauntlets rather than special movement mechanics (no ice-sliding, conveyor belts, etc.) — the engine doesn't have bespoke movement-mechanic support, and adding it was out of scope.
- **Building exteriors** are simple, clean rectangular shapes rather than detailed multi-tile facades, in favor of a fast, consistent, fully-controlled authoring pipeline (see `tools/map_builder.py`).

## Asset credits

- Pokemon battle sprites: fetched from the community `PokeAPI/sprites` repository (Gen 5 Black/White style), used here purely for local, non-distributed testing purposes.
- Overworld tileset (`assets/tilesets/nikouu_*.png`), player/NPC walk-cycle sheets, and dialogue box art: vendored from this repository's pre-existing `MapBuilder/`/`game/` art assets (not code).
- Base terrain tiles: procedurally generated for this project (`tools/generate_base_tiles.py`).
