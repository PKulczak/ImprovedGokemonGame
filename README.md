# Gokemon

A Pokémon-inspired overworld/battle game, built directly on [pygame](https://www.pygame.org/).

This is a fan-made, non-commercial project — see [credits.txt](credits.txt) for sprite/asset attribution.

## Setup

Requires Python 3.

```bash
python -m venv venv
venv\Scripts\activate      # on Windows
source venv/bin/activate   # on macOS/Linux
pip install -r requirements.txt
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

**Overworld**
| Key | Action |
|---|---|
| Arrow keys | Move |
| Space | Start / advance dialogue |
| P | Open the Gokedex |
| S | Save game |
| Q | Back / quit a screen |
| T | Open the tutorial |

**Battle & menu screens**
| Key | Action |
|---|---|
| Arrow keys | Navigate menu |
| Space | Select |
| Q | Quit back |

## Save data

`Fight/Files/Save.json`, `PlayerPokemon.json`, and `PlayerPokedex.json` hold your current progress. They're gitignored — not committed to the repo — and get created automatically from the bundled `NewSave.json`/`NewPlayerPokemon.json`/`NewPlayerPokedex.json` templates the first time you run the game (or any time one of them is missing), so a fresh clone works with no setup step. Pressing **N** and typing `yes` resets them from those same templates.

## Project structure

- `Fight/` — battle sprite sheets, type-effect sprites, save files, and the fight-screen background
- `Overworld/` — maps, their matching tilemap JSON files (`maps/`), and player/NPC sprites
- `Text/` — dialogue and story text
- `gokemon_game.py` — main entry point / game loop
- `fight.py` — battle logic
- `Welcome.py` — start/tutorial/credits screen rendering
- `vector.py` — 2D vector math helper
- `canvas.py` — drop-in image/text drawing surface (crop, scale, and center images; render named-color text)
- `frame.py` — the main event loop/window (input dispatch, the R/N text-entry overlay)
- `image_cache.py` — path-keyed cache so repeated image loads decode from disk once
