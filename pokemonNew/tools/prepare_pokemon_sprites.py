"""One-off asset-prep tool: builds assets/pokemon/<name>/{front,back}.png
for every species in data/roster_dex_map.ROSTER.

Primary source: a local checkout of PokeAPI/sprites, sparse-checked-out to
    sprites/pokemon/versions/generation-v/black-white/{dex}.png       (front)
    sprites/pokemon/versions/generation-v/black-white/back/{dex}.png  (back)
Fallback: this repo's existing game/Fight/pokemon/<Name>.png (front only;
    back is a horizontal mirror of that same image) for any species the
    primary source doesn't have.

This is dev tooling, never imported by the running game.

Usage:
    python tools/prepare_pokemon_sprites.py --source-dir <path to a PokeAPI/sprites checkout>
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PIL import Image

from data.roster_dex_map import ROSTER

TOOLS_DIR = os.path.dirname(os.path.abspath(__file__))
POKEMON_NEW_DIR = os.path.dirname(TOOLS_DIR)
REPO_ROOT = os.path.dirname(POKEMON_NEW_DIR)
OLD_REPO_SPRITES = os.path.join(REPO_ROOT, "game", "Fight", "pokemon")
OUT_DIR = os.path.join(POKEMON_NEW_DIR, "assets", "pokemon")


def build_fallback_index():
    index = {}
    if os.path.isdir(OLD_REPO_SPRITES):
        for fname in os.listdir(OLD_REPO_SPRITES):
            if fname.lower().endswith(".png"):
                index[fname[:-4].lower()] = os.path.join(OLD_REPO_SPRITES, fname)
    return index


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-dir", required=True, help="path to a PokeAPI/sprites checkout")
    args = parser.parse_args()

    gen5_front_dir = os.path.join(args.source_dir, "sprites", "pokemon", "versions", "generation-v", "black-white")
    gen5_back_dir = os.path.join(gen5_front_dir, "back")

    fallback_index = build_fallback_index()

    made, from_gen5, from_fallback, missing = 0, 0, 0, []

    for name, dex in sorted(ROSTER.items(), key=lambda kv: kv[1]):
        dest_dir = os.path.join(OUT_DIR, name.lower())
        front_src = os.path.join(gen5_front_dir, f"{dex}.png")
        back_src = os.path.join(gen5_back_dir, f"{dex}.png")

        if os.path.isfile(front_src) and os.path.isfile(back_src):
            os.makedirs(dest_dir, exist_ok=True)
            Image.open(front_src).convert("RGBA").save(os.path.join(dest_dir, "front.png"))
            Image.open(back_src).convert("RGBA").save(os.path.join(dest_dir, "back.png"))
            from_gen5 += 1
        elif name.lower() in fallback_index:
            os.makedirs(dest_dir, exist_ok=True)
            img = Image.open(fallback_index[name.lower()]).convert("RGBA")
            img.save(os.path.join(dest_dir, "front.png"))
            img.transpose(Image.FLIP_LEFT_RIGHT).save(os.path.join(dest_dir, "back.png"))
            from_fallback += 1
        else:
            missing.append(f"{name}(#{dex})")
            continue
        made += 1

    print(f"Prepared {made}/{len(ROSTER)} species ({from_gen5} from Gen5 sprites, {from_fallback} from local fallback)")
    if missing:
        print(f"MISSING ({len(missing)}):", ", ".join(missing))


if __name__ == "__main__":
    main()
