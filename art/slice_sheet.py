"""Cut a ChatGPT symbol sheet (tiles on a dark background) into transparent
symbol PNGs in art/raw/, ready for `generate.py --process`.

Usage: python art/slice_sheet.py art/source/symbols_sheet.webp
Tile boxes are for the 4/4/2 layout of the current sheet.
"""
import os
import sys

import numpy as np
from PIL import Image, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "raw")

# key: (left, top, right, bottom) of each tile in the 1536x1024 sheet
TILES = {
    "H1": (38, 30, 376, 342), "H2": (408, 30, 752, 342), "H3": (784, 30, 1128, 342), "H4": (1160, 30, 1498, 342),
    "L1": (38, 370, 376, 666), "L2": (408, 370, 752, 666), "L3": (784, 370, 1128, 666), "L4": (1160, 370, 1498, 666),
    "S": (408, 692, 752, 988), "M": (784, 692, 1128, 988),
}
INSET = 12          # skip the tile's rounded border line
# Colour distance from the background. The fill only travels through pixels closer
# than FLOOD, so it stops at the art's dark outlines instead of leaking into dark
# details (sunglasses, fur); inside the filled area alpha ramps from CLEAR to FLOOD.
# The sheet's purple glow/vignette is also treated as background (dark and clearly
# blue-over-red) and faded out softly up to GLOW_FADE.
# The glow may only be faded within GLOW_BAND pixels of the strict background, so it
# can't creep into dark purple parts of the art (sunglasses, fur).
FLOOD, CLEAR, GLOW_FADE, GLOW_BAND = 20, 7, 90, 10


def grow(mask):
    out = mask.copy()
    out[1:] |= mask[:-1]
    out[:-1] |= mask[1:]
    out[:, 1:] |= mask[:, :-1]
    out[:, :-1] |= mask[:, 1:]
    return out


def flood_from_edges(candidate):
    """Pixels of `candidate` connected to the tile edge."""
    region = np.zeros_like(candidate)
    region[0, :], region[-1, :], region[:, 0], region[:, -1] = (
        candidate[0, :], candidate[-1, :], candidate[:, 0], candidate[:, -1])
    while True:
        grown = grow(region) & candidate
        if (grown == region).all():
            return region
        region = grown


def cut(tile: Image.Image) -> Image.Image:
    rgb = np.asarray(tile.convert("RGB")).astype(np.int16)
    edge = np.concatenate([rgb[0], rgb[-1], rgb[:, 0], rgb[:, -1]])
    bg = np.median(edge, axis=0)
    dist = np.abs(rgb - bg).max(axis=2)

    # background = low-distance pixels connected to the tile edge (keeps dark
    # details inside the art, e.g. the possum's eyes)
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    luminance = 0.3 * r + 0.59 * g + 0.11 * b
    dark_purple = (b - r > 18) & (luminance < 80)
    strict = flood_from_edges(dist < FLOOD)
    band = strict.copy()
    for _ in range(GLOW_BAND):
        band = grow(band)
    region = strict | (flood_from_edges(strict | dark_purple) & band)

    ramp = np.clip((dist - CLEAR) / (GLOW_FADE - CLEAR), 0, 1)
    alpha = np.where(region, ramp * 255, 255).astype(np.uint8)
    alpha_img = Image.fromarray(alpha).filter(ImageFilter.GaussianBlur(0.7))
    out = tile.convert("RGBA")
    out.putalpha(alpha_img)
    return out.crop(out.getchannel("A").point(lambda a: 255 if a > 20 else 0).getbbox())


def main(path):
    sheet = Image.open(path)
    os.makedirs(RAW, exist_ok=True)
    for key, (l, t, r, b) in TILES.items():
        img = cut(sheet.crop((l + INSET, t + INSET, r - INSET, b - INSET)))
        img.save(os.path.join(RAW, f"{key}.png"))
        print(key, img.size)


if __name__ == "__main__":
    main(sys.argv[1])
