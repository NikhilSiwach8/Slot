"""Cut the UI pieces out of the ChatGPT UI sheet and pack them into a sprite sheet.

Baked-in text that doesn't fit our game is painted out:
  bar_panel / bar_frame - "BET $1.00" (we draw live labels and amounts)
  btn_blank             - the TURBO bolt, giving a plain round button for AUTO etc.
  panel                 - the rows (ante/wild are not features of this game)
  card                  - "3+ SCATTERS TRIGGER FREE SPINS" (this game needs 4+)

Usage: python art/slice_ui.py art/source/ui_sheet.webp
"""
import json
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from slice_sheet import cut  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "web-sdk", "apps", "dumpster-duke", "static", "assets", "sprites", "dukeUi")
HTML_OUT = os.path.join(HERE, "..", "web-sdk", "apps", "dumpster-duke", "static", "assets", "ui")

BOXES = {
    "btn_menu": (185, 705, 310, 830),
    "btn_spin": (335, 700, 460, 830),
    "btn_turbo": (485, 705, 610, 830),
    "icon_bonus": (35, 530, 160, 645),
    "icon_cart": (185, 530, 310, 645),
    "bar_minus": (806, 128, 882, 204),
    "bar_plus": (1054, 128, 1128, 204),
    "bar_frame": (792, 100, 1160, 230),
    "btn_back": (50, 880, 235, 960),
    "btn_info": (262, 880, 440, 960),
    "panel": (660, 318, 1218, 955),
    "card": (1228, 340, 1508, 885),
}
PANEL_IN_FRAME = (885 - 792, 115 - 100, 1048 - 792, 205 - 100)  # bet panel inside bar_frame


def paint(img, box, shape="rect", radius=12, feather=3, colour=None):
    """Cover `box` with a flat colour sampled from just inside its edge."""
    rgb = np.asarray(img.convert("RGB")).astype(int)
    l, t, r, b = (int(v) for v in box)
    box = (l, t, r, b)
    if colour is None:
        ring = np.concatenate([rgb[t + 2, l:r], rgb[b - 3, l:r], rgb[t:b, l + 2], rgb[t:b, r - 3]])
        colour = tuple(int(c) for c in np.median(ring, axis=0))
    mask = Image.new("L", img.size, 0)
    draw = ImageDraw.Draw(mask)
    if shape == "ellipse":
        draw.ellipse(box, fill=255)
    else:
        draw.rounded_rectangle(box, radius, fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(feather))
    flat = Image.new("RGBA", img.size, colour + (255,))
    out = img.copy()
    out.paste(flat, (0, 0), mask)
    return out


def erase_icon(img):
    """Remove the yellow icon from a round button: paint the yellow pixels (grown a
    little) with the button's inner colour."""
    rgb = np.asarray(img.convert("RGB")).astype(int)
    h, w = rgb.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w]
    inner = np.hypot((xx - w / 2) / (w / 2), (yy - h / 2) / (h / 2)) < 0.62
    yellow = (rgb[..., 0] > 110) & (rgb[..., 1] > 70) & (rgb[..., 2] < 110) & inner
    colour = tuple(int(c) for c in np.median(rgb[inner & ~yellow], axis=0))
    mask = Image.fromarray((yellow * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(9))
    mask = mask.filter(ImageFilter.GaussianBlur(2.5))
    out = img.copy()
    out.paste(Image.new("RGB", img.size, colour), (0, 0), mask)
    return out


def main(path):
    sheet = Image.open(path).convert("RGB")
    raw = {k: sheet.crop(b) for k, b in BOXES.items()}

    # paint out baked text before cutting the background away
    pl, pt, pr, pb = PANEL_IN_FRAME
    raw["bar_frame"] = paint(raw["bar_frame"], (pl + 8, pt + 8, pr - 8, pb - 8))
    raw["bar_panel"] = raw["bar_frame"].crop(PANEL_IN_FRAME)
    raw["btn_blank"] = erase_icon(raw["btn_turbo"])
    raw["panel"] = paint(raw["panel"], (722 - 660, 418 - 318, 1146 - 660, 902 - 318), radius=14)
    raw["card"] = paint(raw["card"], (1262 - 1228, 732 - 340, 1475 - 1228, 785 - 340), radius=6)

    pieces = {}
    for key, img in raw.items():
        # the bet panel is already cut from inside the frame: keep it solid
        pieces[key] = img.convert("RGBA") if key == "bar_panel" else cut(img)

    # pack (simple shelf packer) into one Pixi sprite sheet
    os.makedirs(OUT, exist_ok=True)
    page_w, pad = 1024, 2
    x = y = shelf = 0
    frames = {}
    for key, img in sorted(pieces.items(), key=lambda kv: -kv[1].height):
        if x + img.width + pad > page_w:
            x, y, shelf = 0, y + shelf + pad, 0
        frames[key] = (x, y, img)
        x += img.width + pad
        shelf = max(shelf, img.height)
    page = Image.new("RGBA", (page_w, y + shelf))
    atlas = {"frames": {}, "meta": {"app": "art/slice_ui.py", "image": "dukeUi.webp", "format": "RGBA8888",
                                      "size": {"w": page.width, "h": page.height}, "scale": "1"}}
    for key, (fx, fy, img) in frames.items():
        page.paste(img, (fx, fy))
        atlas["frames"][f"ui_{key}.png"] = {
            "frame": {"x": fx, "y": fy, "w": img.width, "h": img.height}, "rotated": False, "trimmed": False,
            "spriteSourceSize": {"x": 0, "y": 0, "w": img.width, "h": img.height},
            "sourceSize": {"w": img.width, "h": img.height},
        }
        print(f"ui_{key}.png", img.size)
    page.save(os.path.join(OUT, "dukeUi.webp"), quality=92)
    with open(os.path.join(OUT, "dukeUi.json"), "w") as f:
        json.dump(atlas, f, indent=1)
    with open(os.path.join(OUT, "index.ts"), "w") as f:
        f.write("import { createAsset } from 'pixi-svelte';\n\nimport img from './dukeUi.webp';\n"
                "import atlas from './dukeUi.json';\n\nexport default createAsset({ img, atlas });\n")
    # pieces the HTML menus use as plain images
    os.makedirs(HTML_OUT, exist_ok=True)
    for key in ("panel", "card", "icon_cart", "btn_back", "bar_panel"):
        pieces[key].save(os.path.join(HTML_OUT, f"{key}.webp"), quality=90)
    # natural sizes, so the client can fit art without distorting it
    sizes_path = os.path.join(HERE, "..", "web-sdk", "apps", "dumpster-duke", "src", "ui", "artSizes.json")
    with open(sizes_path, "w") as f:
        json.dump({k: {"width": v.width, "height": v.height} for k, v in sorted(pieces.items())}, f, indent=1)


if __name__ == "__main__":
    main(sys.argv[1])
