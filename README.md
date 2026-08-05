# Gokemon

A Pokémon-inspired overworld/battle game, built on [CodeSkulptor's](https://py3.codeskulptor.org/) `simplegui` module with a desktop fallback via [`SimpleGUICS2Pygame`](https://simpleguics2pygame.readthedocs.io/en/latest/).

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

Run from the **repo root** — the game builds its file paths (save data, sprites, maps) relative to the current working directory, so it won't find its assets if launched from elsewhere:

```bash
python gokemon_game.py
```

## Controls

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

`Fight/Files/Save.txt`, `PlayerPokemon.txt`, and `PlayerPokedex.txt` hold your current progress and are overwritten as you play — expect them to show as changed in `git status` after a session. `NewSave.txt`, `NewPlayerPokemon.txt`, and `NewPlayerPokedex.txt` are the fresh-start templates used when starting a new game.

## Project structure

- `Fight/` — battle sprite sheets, type-effect sprites, save files, and the fight-screen background
- `Overworld/` — maps, their matching collision/NPC text files, and player/NPC sprites
- `Text/` — dialogue and story text
- `gokemon_game.py` — main entry point / game loop
- `fight.py` — battle logic
- `Welcome.py` — start/tutorial/credits screen rendering
- `vector.py` — 2D vector math helper
