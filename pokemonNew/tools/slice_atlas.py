"""One-off dev tool: detects sprite "islands" in a freeform/bin-packed tileset
sheet (alpha-channel connected-component labeling) and writes a committed
`<name>.atlas.json` manifest + a labeled preview PNG for a quick visual sanity
check. No detection logic ships in the runtime game — it just reads the
manifest this tool produces.

Usage:
    python tools/slice_atlas.py <image_path> [--min-area 4] [--out-dir assets/tilesets]
"""
import argparse
import json
import os
import sys

from PIL import Image, ImageDraw


def find_components(mask, min_area=4):
    h = len(mask)
    w = len(mask[0]) if h else 0
    seen = [[False] * w for _ in range(h)]
    boxes = []
    for y in range(h):
        row = mask[y]
        for x in range(w):
            if row[x] and not seen[y][x]:
                stack = [(x, y)]
                seen[y][x] = True
                minx = maxx = x
                miny = maxy = y
                area = 0
                while stack:
                    cx, cy = stack.pop()
                    area += 1
                    if cx < minx:
                        minx = cx
                    if cx > maxx:
                        maxx = cx
                    if cy < miny:
                        miny = cy
                    if cy > maxy:
                        maxy = cy
                    for nx, ny in ((cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)):
                        if 0 <= nx < w and 0 <= ny < h and mask[ny][nx] and not seen[ny][nx]:
                            seen[ny][nx] = True
                            stack.append((nx, ny))
                if area >= min_area:
                    boxes.append((minx, miny, maxx - minx + 1, maxy - miny + 1))
    return boxes


def build_mask(img, alpha_threshold=10):
    img = img.convert("RGBA")
    w, h = img.size
    alpha = img.split()[3]
    px = alpha.load()
    return [[px[x, y] >= alpha_threshold for x in range(w)] for y in range(h)]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("image_path")
    parser.add_argument("--min-area", type=int, default=4)
    parser.add_argument("--out-dir", default=None)
    args = parser.parse_args()

    img = Image.open(args.image_path)
    name = os.path.splitext(os.path.basename(args.image_path))[0]
    out_dir = args.out_dir or os.path.dirname(os.path.abspath(args.image_path))

    print(f"Scanning {args.image_path} ({img.size[0]}x{img.size[1]})...", file=sys.stderr)
    mask = build_mask(img)
    boxes = find_components(mask, min_area=args.min_area)
    boxes.sort(key=lambda b: (b[1], b[0]))

    manifest = [
        {"id": i, "x": x, "y": y, "w": w, "h": h}
        for i, (x, y, w, h) in enumerate(boxes)
    ]
    manifest_path = os.path.join(out_dir, f"{name}.atlas.json")
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)

    preview = img.convert("RGBA").copy()
    draw = ImageDraw.Draw(preview)
    for entry in manifest:
        x, y, w, h = entry["x"], entry["y"], entry["w"], entry["h"]
        draw.rectangle([x, y, x + w - 1, y + h - 1], outline=(255, 0, 255, 255))
    preview_path = os.path.join(out_dir, f"{name}.atlas_preview.png")
    preview.save(preview_path)

    print(f"{len(manifest)} components found -> {manifest_path}")
    print(f"Preview -> {preview_path}")


if __name__ == "__main__":
    main()
