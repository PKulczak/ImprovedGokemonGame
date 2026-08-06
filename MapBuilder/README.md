# Gokemon Map Builder

A standalone tool for building maps for the main game using real tileset art, instead of hand-typing `Overworld/maps/*.json` by hand. Uses plain `pygame` (already a project dependency) - no extra install needed.

Tileset art in `tilesets/` is vendored from [icyethics/PokemonAssets](https://github.com/icyethics/PokemonAssets/tree/main/Tilesets) (non-commercial use, credit to IcyEthics - see [credits.txt](../credits.txt)).

## Running it

```bash
python MapBuilder/map_builder.py <project_name>
```

If `<project_name>` doesn't exist yet under `projects/`, a blank one is created. Omit the name to use `untitled`.

## How maps are built

The tool works in two layers:

- **Ground layer** - the floor/terrain (grass, dirt, paths, water). Stamped freely, no grid snapping, and flattened into one image on save/export - it's always drawn beneath everything else, so it never needs to be individually sorted.
- **Object layer** - anything that should be able to occlude (or be occluded by) the player: trees, bushes, building pieces, decorations. Each one stays a separate object all the way into the exported map, so the game can draw the player, NPCs, and objects in the correct front-to-back order based on position - this is what fixes the old flat-image system always drawing the player on top of everything.

Any placed object can also be marked as **collision** - a type from the same vocabulary the game already understands (`tree`, `wall_up_a`, `wall_up_b`, `wall_left_a`, `wall_left_b`, `fight`, `heal`, `interact`, `boss_gate`, `npc`, `yacht`). A collision marker doesn't need a visual stamp - e.g. a `fight` (wild encounter) trigger is usually invisible.

The tileset sheets in `tilesets/` are **not** clean uniform grids - they're loose reference sheets mixing small icons with big irregular multi-tile art and placeholder cells. So tile selection is a freeform rectangle drag over the sheet, not a fixed-size grid pick - drag over exactly the art you want, any size.

`npc` and `yacht` markers are placement-only: the game resolves the actual NPC sprite/species itself (via `Background.load_npc()` in `gokemon_game.py`, keyed by map name), so these never carry a decorative stamp even if one is selected in the palette.

## Controls

| Input | Action |
|---|---|
| Left-click drag (tileset panel, right side) | Select a region of the current tileset as a new palette stamp |
| `[` / `]` | Switch to the previous/next tileset sheet |
| Mouse wheel (over tileset panel) | Scroll the sheet |
| Left-click (palette panel) | Pick a saved stamp as the active one |
| `Tab` | Switch between Ground layer and Object layer |
| Left-click (canvas) | Paint the active stamp (ground layer) / place an object (object layer) |
| Right-click (canvas) | Erase - clears a ground patch, or removes the topmost object under the cursor |
| `G` | Toggle grid snapping for object placement |
| `0`-`9`, `n`, `y` | Set the active collision brush (see bottom bar for the legend; `0` = none/decoration only) |
| `F5` / `Ctrl+S` | Save the project (own editable format, under `projects/`) |
| `F9` | Save, then export to `output/<name>/` |
| `Esc` | Quit |

`interact`/`boss_gate` brushes prompt for a one-line comma-separated field (`target_map,x,y` or `target_map,x,y,requires_defeated`) right after you place them.

## Using an exported map in the game

`F9` writes a self-contained bundle to `MapBuilder/output/<name>/`:

```
output/<name>/
  <name>.json              -> copy into Overworld/maps/
  map_img/<name>_ground.png -> copy into Overworld/map_img/
  objects/<name>/*.png      -> copy into Overworld/objects/<name>/
```

Copy those three pieces into the matching folders under `Overworld/` (the internal paths already match, so it's a straight merge) and the map is playable - `gokemon_game.py` detects the new format automatically (existing hand-authored maps are untouched and keep working exactly as before).

Two things the tool doesn't automate for a brand-new map:
- `npc` markers need one manual entry in the `load_npc()` dict in `gokemon_game.py` (which species appears on this map).
- Nothing currently transitions *into* a new map unless some other map's `interact`/`boss_gate` object targets it (`target_map` + `target_pos`).

## Not in v1

Undo/redo, autotiling, tileset animation, and migrating the 14 existing hand-authored maps to this format.
