# Gokemon

A Pokémon-inspired overworld/battle game, built directly on [pygame](https://www.pygame.org/).

This is a fan-made, non-commercial project — see [credits.txt](game/credits.txt) for sprite/asset attribution.

## Setup

Requires Python 3.

```bash
python -m venv venv
venv\Scripts\activate      # on Windows
source venv/bin/activate   # on macOS/Linux
pip install -r game/requirements.txt
```

## Running the game

```bash
python gokemon_game.py
```

Asset and save-data paths are resolved relative to the script's own location, so this works regardless of your current working directory. The game window is a fixed 800x480.

## Controls

**Global** (available on any screen)
| Key | Action |
|---|---|
| R | Rename your player - opens a text-entry overlay |
| N | Reset to a new game - opens a text-entry overlay, type `yes` to confirm |
| Shift (hold) | Fast-forward - speeds up movement, animations, and message/dialogue timers while held |

**Overworld**
| Key | Action |
|---|---|
| Arrow keys | Move |
| Space | Start / advance dialogue |
| P | Open the Gokedex |
| S | Save game |
| Q | Back / quit a screen |
| T | Open the tutorial |
| Esc | Pause - shows this controls list in-game |

**Battle & menu screens**
| Key | Action |
|---|---|
| Arrow keys | Navigate menu |
| Space | Select |
| Q | Quit back |

## Save data

`game/Fight/Files/Save.json`, `PlayerPokemon.json`, and `PlayerPokedex.json` hold your current progress. They're gitignored — not committed to the repo — and get created automatically from the bundled `NewSave.json`/`NewPlayerPokemon.json`/`NewPlayerPokedex.json` templates the first time you run the game (or any time one of them is missing), so a fresh clone works with no setup step. Pressing **N** and typing `yes` resets them from those same templates.

Running out of lives does **not** wipe your save - a "Game Over" screen shows first, and continuing past it fully heals your team, restores your lives, and drops you at the last Pokecenter you visited (or the starting one, if you haven't visited one yet).

## Project structure

- `gokemon_game.py` — main entry point; wires everything in `game/` together and runs the event loop
- `game/` — the game itself:
  - `Fight/` — battle sprite sheets, type-effect sprites, save files, and the fight-screen background
  - `Overworld/` — maps, their matching tilemap JSON files (`maps/`), and player/NPC sprites
  - `Text/` — dialogue and story text
  - `gameplay/` — the overworld: `game.py` (`Game`/`Interaction`/`Keyboard`, the top-level state
    machine), `entities.py` (`Player`/`NPC`/`Wall`/`Interact`), `world.py` (`Background`/map
    loading), `ui.py` (`Pokedex`/`Text`/dialogue), `clock.py` (frame-count timer), `Welcome.py`
    (start/tutorial/credits screen rendering)
  - `battle/` — the fight screen: `fight.py` (`Fight`/`Pokemon`, its own state machine),
    `battle_rules.py` (pure damage/catch/escape/level-up formulas, independent of rendering)
  - `engine/` — generic pygame plumbing shared by both: `canvas.py` (image/text drawing surface),
    `frame.py` (event loop, input dispatch, the R/N text-entry overlay), `image_cache.py`
    (path-keyed image cache), `vector.py` (2D vector math), `balance.py` (named tuning constants),
    `party_grid.py` (the shared party-grid-cursor logic used by both the Gokedex and the fight
    screen's bag/switch menu)
  - `credits.txt`, `requirements.txt`
- `MapBuilder/` — a standalone map-editing tool, independent of the game itself (see its own [README](MapBuilder/README.md))
