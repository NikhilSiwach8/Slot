"""Cut ChatGPT art sheets into transparent PNGs in art/whisker_tilt/raw/.

Usage: python art/whisker_tilt/slice_sheet.py art/whisker_tilt/source/<sheet>.webp ...
Each sheet has its own boxes in SHEETS. Later sheets replace earlier cuts of the same name,
so run them in order: sheet_1, sheet_2, paw.

sheet_2 and paw come with real transparency: they are only cropped and their alpha cleaned.
sheet_1's "transparent" background is a painted grey/white checkerboard instead:

How the background is removed:
- checker-like pixels (near-neutral and bright) connected to the sheet edge are background;
- closed pockets of checker inside an object (the frame's window, gaps between sleigh
  runners) are found by their two-tone pattern, so white snow is never mistaken for them;
- the crack overlay is pale lines with checker showing through everywhere, so it is keyed
  per pixel instead.

Fix-ups for this sheet (see FIXES): the red star becomes pine green so it doesn't read as
the red bauble, and the wide frame is narrowed to the square board.
"""

import colorsys
import os
import sys
from collections import deque

import numpy as np
from PIL import Image, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "raw")

# name: (left, top, right, bottom) on the 1536x1024 sheet_1
SHEET_1 = {
    "H1": (4, 60, 280, 345),
    "H2": (279, 60, 518, 342),
    "H3": (518, 8, 655, 358),
    "H4": (656, 60, 846, 346),
    "L1": (840, 115, 958, 330),
    "L2": (946, 115, 1030, 330),
    "L3": (1008, 115, 1126, 330),
    "L4": (1110, 115, 1240, 330),
    "S": (1210, 92, 1402, 332),
    "C": (1376, 145, 1536, 325),
    "keeper_south": (426, 370, 676, 710),
    "keeper_west": (716, 362, 980, 705),
    "keeper_north": (1012, 356, 1242, 708),
    "keeper_east": (1258, 368, 1506, 706),
    "box_frame": (0, 706, 420, 1004),
    "gift_closed": (418, 736, 650, 995),
    "gift_open": (646, 698, 892, 995),
    "crack_overlay": (896, 724, 1214, 1012),
    "logo_plate": (1216, 722, 1536, 986),
}
# sheet_2 (1125x750, real alpha): the props again, with a squarer frame. These replace sheet_1's.
SHEET_2 = {
    "box_frame": (0, 40, 470, 424),
    "gift_closed": (450, 60, 776, 430),
    "gift_open": (778, 0, 1102, 440),
    "crack_overlay": (10, 415, 562, 750),
    "logo_plate": (565, 405, 1088, 742),
}
SHEETS = {
    "sheet_1": ("checker", SHEET_1),
    "sheet_2": ("alpha", SHEET_2),
    "paw": ("alpha", {"mitten_paw": (395, 135, 1126, 1222)}),
    "mitten": ("alpha", {"mitten": (0, 0, 1024, 1536)}),
    # Full-size backgrounds, one file each, used as they are.
    "bg_base": ("opaque", {"bg_base": (0, 0, 1536, 1024)}),
    "bg_base_portrait": ("opaque", {"bg_base_portrait": (0, 0, 1024, 1536)}),
    "bg_snowday": ("opaque", {"bg_snowday": (0, 0, 1536, 1024)}),
    "bg_snowday_portrait": ("opaque", {"bg_snowday_portrait": (0, 0, 1024, 1536)}),
    "bg_super": ("opaque", {"bg_super": (0, 0, 1536, 1024)}),
    "bg_super_portrait": ("opaque", {"bg_super_portrait": (0, 0, 1024, 1536)}),
}
PER_PIXEL = {"crack_overlay"}
# The three baubles touch on the sheet: drop the neighbour's colour from each crop
# (L2 has no red, L1 and L3 have no blue).
PURGE = {"L1": "blue", "L2": "red", "L3": "blue"}
FIXES = {"L3": "recolour_green", "box_frame": "make_square"}


def checker_like(rgb):
    mx, mn = rgb.max(2), rgb.min(2)
    return (mx - mn < 16) & (mn > 222)


def flood(mask, seeds):
    h, w = mask.shape
    out = np.zeros_like(mask)
    q = deque()
    for y, x in seeds:
        if mask[y, x] and not out[y, x]:
            out[y, x] = True
            q.append((y, x))
    while q:
        y, x = q.popleft()
        for ny, nx in ((y + 1, x), (y - 1, x), (y, x + 1), (y, x - 1)):
            if 0 <= ny < h and 0 <= nx < w and mask[ny, nx] and not out[ny, nx]:
                out[ny, nx] = True
                q.append((ny, nx))
    return out


def regions(mask):
    """Connected regions of a boolean mask, as lists of (y, x)."""
    seen = np.zeros_like(mask)
    h, w = mask.shape
    for y in range(h):
        for x in range(w):
            if mask[y, x] and not seen[y, x]:
                part = flood(mask & ~seen, [(y, x)])
                seen |= part
                yield np.argwhere(part)


def is_checker(rgb, cells):
    """The painted checker alternates ~234 and ~254 greys in equal parts; snow does not."""
    vals = rgb[cells[:, 0], cells[:, 1]].mean(1)
    dark = np.mean((vals > 226) & (vals < 243))
    light = np.mean(vals >= 248)
    return dark > 0.25 and light > 0.25


def cut_object(rgb):
    h, w, _ = rgb.shape
    like = checker_like(rgb)
    edge = [(y, x) for y in range(h) for x in (0, w - 1)] + [(y, x) for x in range(w) for y in (0, h - 1)]
    bg = flood(like, edge)
    for cells in regions(like & ~bg):
        if len(cells) > 250 and is_checker(rgb, cells):
            bg[cells[:, 0], cells[:, 1]] = True
    alpha = Image.fromarray(np.where(bg, 0, 255).astype(np.uint8))
    # Eat the light fringe left by the checker, then soften the edge.
    alpha = alpha.filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(0.7))
    return np.asarray(alpha)


def clean_alpha(alpha):
    """Real-alpha sheets keep the background at 0-16 and the art at ~252: snap both ends."""
    return (np.clip((alpha.astype(float) - 24) / (250 - 24), 0, 1) * 255).astype(np.uint8)


def cut_per_pixel(rgb):
    mx, mn = rgb.max(2), rgb.min(2)
    blue = rgb[..., 2] - rgb[..., 0]
    a = np.clip((mx - mn - 10) / 30, 0, 1) + np.clip((222 - mn) / 50, 0, 1) + np.clip((blue - 6) / 25, 0, 1)
    return (np.clip(a, 0, 1) * 255).astype(np.uint8)


def recolour_green(img):
    """Shift reds to pine green, leaving the gold snowflake and cap alone."""
    arr = np.asarray(img).astype(float) / 255
    out = arr.copy()
    for y in range(arr.shape[0]):
        for x in range(arr.shape[1]):
            r, g, b, a = arr[y, x]
            hh, ss, vv = colorsys.rgb_to_hsv(r, g, b)
            if a > 0 and ss > 0.35 and (hh < 0.04 or hh > 0.93):
                out[y, x, :3] = colorsys.hsv_to_rgb(0.37, ss * 0.85, vv * 0.85)
    return Image.fromarray((out * 255).astype(np.uint8), "RGBA")


def make_square(img, blend=24):
    """Drop a vertical band from the middle of the frame; the top and bottom rails are plain
    there, so the join is hidden by a short cross-fade."""
    w, h = img.size
    if w <= h:
        return img
    cut = w - h
    left_w = (w - cut) // 2
    arr = np.asarray(img).astype(float)
    left = arr[:, : left_w + blend]
    right = arr[:, left_w + cut - blend :]
    out = np.zeros((h, h, 4))
    out[:, :left_w] = left[:, :left_w]
    out[:, left_w + blend :] = right[:, 2 * blend : 2 * blend + h - left_w - blend]
    t = np.linspace(0, 1, blend)[None, :, None]
    out[:, left_w : left_w + blend] = left[:, left_w:] * (1 - t) + right[:, :blend] * t
    return Image.fromarray(out.astype(np.uint8), "RGBA")


def purge_colour(rgb, alpha, colour):
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    if colour == "blue":
        hit = (b > r + 30) & (b > g + 10)
    else:
        hit = (r > 120) & (r > g + 70) & (r > b + 40)
    # Also take the dark outline right next to the purged colour.
    near = np.asarray(Image.fromarray(hit.astype(np.uint8) * 255).filter(ImageFilter.MaxFilter(9))) > 0
    dark = rgb.max(2) < 90
    out = alpha.copy()
    out[hit | (near & dark)] = 0
    return out


def tidy_bauble(img, mirror_fill=False):
    """After a purge: drop thin scraps of the neighbour's outline beside the body (the cap and
    hook at the top are left alone), and optionally rebuild an occluded side of a symmetric
    bauble from its mirror image."""
    a = np.asarray(img).copy()
    if mirror_fill:
        cols = np.where((a[..., 3] > 128).any(0))[0]
        mid = (cols.min() + cols.max()) / 2
        flipped = a[:, ::-1]
        shift = int(round(2 * mid - (a.shape[1] - 1)))
        flipped = np.roll(flipped, shift, axis=1)
        hole = (a[..., 3] < 200) & (flipped[..., 3] > 200)
        hole[:, : int(mid)] = False
        a[hole] = flipped[hole]
    solid = Image.fromarray(((a[..., 3] > 128) * 255).astype(np.uint8))
    body = solid.filter(ImageFilter.MinFilter(9)).filter(ImageFilter.MaxFilter(9)).filter(ImageFilter.MaxFilter(5))
    keep = np.asarray(body) > 0
    keep[: int(a.shape[0] * 0.3)] = True  # cap and hook
    w = a.shape[1]
    keep[:, int(w * 0.38) : int(w * 0.62)] = True  # the pointed tips sit on the centre line
    a[~keep, 3] = 0
    return Image.fromarray(a, "RGBA")


def drop_neighbours(img):
    """Crops can catch the edge of the next object on the sheet: keep the biggest shape and
    anything that doesn't touch the crop border."""
    a = np.asarray(img).copy()
    solid = a[..., 3] > 8
    parts = sorted(regions(solid), key=len, reverse=True)
    h, w = solid.shape
    for cells in parts[1:]:
        ys, xs = cells[:, 0], cells[:, 1]
        if ys.min() == 0 or xs.min() == 0 or ys.max() == h - 1 or xs.max() == w - 1:
            a[ys, xs, 3] = 0
    return Image.fromarray(a, "RGBA")


def trim(img, pad=6):
    box = img.getchannel("A").point(lambda v: 255 if v > 8 else 0).getbbox()
    if not box:
        return img
    l, t, r, b = box
    return img.crop((max(0, l - pad), max(0, t - pad), min(img.width, r + pad), min(img.height, b + pad)))


def cut_sheet(path):
    stem = os.path.splitext(os.path.basename(path))[0]
    kind, boxes = SHEETS[stem]
    sheet = Image.open(path).convert("RGBA")
    for name, box in boxes.items():
        if kind == "opaque":
            img = sheet.crop(box).convert("RGB")
            if name.endswith("_portrait") and img.size != (1024, 1536):
                img = img.resize((1024, 1536), Image.LANCZOS)
            img.save(os.path.join(RAW, f"{name}.png"))
            print(f"{stem:8} {name:20} {img.size[0]}x{img.size[1]}")
            continue
        crop = np.asarray(sheet.crop(box)).astype(int)
        rgb = crop[..., :3]
        if kind == "alpha":
            alpha = clean_alpha(crop[..., 3])
        elif name in PER_PIXEL:
            alpha = cut_per_pixel(rgb)
        else:
            alpha = cut_object(rgb)
        if name in PURGE and kind == "checker":
            alpha = purge_colour(rgb, alpha, PURGE[name])
        img = Image.fromarray(np.dstack([rgb, alpha]).astype(np.uint8), "RGBA")
        if name not in PER_PIXEL:
            img = drop_neighbours(img)
        img = trim(img)
        if name in PURGE and kind == "checker":
            img = trim(tidy_bauble(img, mirror_fill=name == "L1"))
        fix = FIXES.get(name)
        if fix and (kind == "checker" or fix == "make_square"):
            img = globals()[fix](img)
        img.save(os.path.join(RAW, f"{name}.png"))
        print(f"{stem:8} {name:14} {img.size[0]}x{img.size[1]}" + (f"  ({fix})" if fix else ""))


def main():
    os.makedirs(RAW, exist_ok=True)
    for path in sys.argv[1:]:
        cut_sheet(path)


if __name__ == "__main__":
    main()
