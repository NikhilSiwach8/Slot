"""Turn art/whisker_tilt/raw/*.png into the client's assets in
web-sdk/apps/whisker-tilt/static/assets/.

Usage: python art/whisker_tilt/build_web_assets.py

- wtSymbols: the 10 symbols packed into one 256px-cell sheet (frames wt_<key>.png), also
  used by the rules screen.
- wtProps: keepers, Mitten, her paw, frame, gifts, crack overlay, logo plate as webp sprites.
- wtBackgrounds: the six backgrounds as webp.
- wtUi: Dumpster Duke's UI sheet with its purple stone shifted to winter ice blue (the
  layout and frame names are unchanged), until Whisker Tilt gets its own UI sheet.
"""

import colorsys
import json
import os
import shutil

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "raw")
APP = os.path.join(HERE, "..", "..", "web-sdk", "apps", "whisker-tilt")
OUT = os.path.join(APP, "static", "assets")
CELL = 256

SYMBOLS = ["H1", "H2", "H3", "H4", "L1", "L2", "L3", "L4", "S", "C"]
SYMBOL_COLUMNS = 4
# name: longest side in px (sprites are drawn at about half this on a 1080p screen)
PROPS = {
    "keeper_south": 320,
    "keeper_west": 320,
    "keeper_north": 320,
    "keeper_east": 320,
    "mitten": 640,
    "mitten_paw": 512,
    "box_frame": 900,
    "gift_closed": 420,
    "gift_open": 420,
    "crack_overlay": 900,
    "logo_plate": 640,
    "S": 300,  # the Wind-up Key on its own, for the buy menu
}
BACKGROUNDS = {
    "bg_base_landscape": "bg_base",
    "bg_base_portrait": "bg_base_portrait",
    "bg_snowday_landscape": "bg_snowday",
    "bg_snowday_portrait": "bg_snowday_portrait",
    "bg_super_landscape": "bg_super",
    "bg_super_portrait": "bg_super_portrait",
}


def fit(img, longest):
    scale = longest / max(img.size)
    return img.resize((round(img.width * scale), round(img.height * scale)), Image.LANCZOS)


def write_atlas(folder, name, cells, columns, cell):
    os.makedirs(folder, exist_ok=True)
    rows = (len(cells) + columns - 1) // columns
    sheet = Image.new("RGBA", (columns * cell, rows * cell), (0, 0, 0, 0))
    frames = {}
    for i, (frame, img) in enumerate(cells):
        x, y = (i % columns) * cell, (i // columns) * cell
        sheet.paste(img, (x + (cell - img.width) // 2, y + (cell - img.height) // 2), img)
        frames[frame] = {
            "frame": {"x": x, "y": y, "w": cell, "h": cell},
            "rotated": False,
            "trimmed": False,
            "spriteSourceSize": {"x": 0, "y": 0, "w": cell, "h": cell},
            "sourceSize": {"w": cell, "h": cell},
        }
    sheet.save(os.path.join(folder, f"{name}.webp"), quality=90)
    meta = {"app": "art/whisker_tilt/build_web_assets.py", "image": f"{name}.webp", "format": "RGBA8888",
            "size": {"w": sheet.width, "h": sheet.height}, "scale": "1"}
    with open(os.path.join(folder, f"{name}.json"), "w") as f:
        json.dump({"frames": frames, "meta": meta}, f, indent=1)
    with open(os.path.join(folder, "index.ts"), "w") as f:
        f.write("import { createAsset } from 'pixi-svelte';\n\n"
                f"import img from './{name}.webp';\nimport atlas from './{name}.json';\n\n"
                "export default createAsset({ img, atlas });\n")


def winterise(img):
    """Shift purples (the stone and glow of the Dumpster Duke UI) to ice blue; gold stays."""
    arr = np.asarray(img.convert("RGBA")).astype(float) / 255
    rgb = arr[..., :3]
    mx, mn = rgb.max(2), rgb.min(2)
    v = mx
    s = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-6), 0)
    h = np.zeros_like(mx)
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    d = np.maximum(mx - mn, 1e-6)
    h = np.where(mx == r, ((g - b) / d) % 6, h)
    h = np.where(mx == g, (b - r) / d + 2, h)
    h = np.where(mx == b, (r - g) / d + 4, h)
    h = h / 6
    purple = (h > 0.66) & (h < 0.92) & (s > 0.12)
    h2 = np.where(purple, 0.57, h)
    s2 = np.where(purple, s * 0.8, s)
    v2 = np.where(purple, np.minimum(1, v * 1.08), v)
    # back to rgb
    i = np.floor(h2 * 6) % 6
    f = h2 * 6 - np.floor(h2 * 6)
    p, q, t = v2 * (1 - s2), v2 * (1 - f * s2), v2 * (1 - (1 - f) * s2)
    out = np.zeros_like(rgb)
    for k, (a, bb, c) in enumerate([(v2, t, p), (q, v2, p), (p, v2, t), (p, q, v2), (t, p, v2), (v2, p, q)]):
        m = i == k
        out[..., 0] = np.where(m, a, out[..., 0])
        out[..., 1] = np.where(m, bb, out[..., 1])
        out[..., 2] = np.where(m, c, out[..., 2])
    res = np.dstack([out, arr[..., 3:]])
    return Image.fromarray((res * 255).round().astype(np.uint8), "RGBA")


def main():
    sprites = os.path.join(OUT, "sprites")

    cells = []
    for key in SYMBOLS:
        img = Image.open(os.path.join(RAW, f"{key}.png")).convert("RGBA")
        cells.append((f"wt_{key.lower()}.png", fit(img, CELL - 8)))
    write_atlas(os.path.join(sprites, "wtSymbols"), "wtSymbols", cells, SYMBOL_COLUMNS, CELL)
    print(f"wtSymbols: {len(cells)} symbols")

    props = os.path.join(sprites, "wtProps")
    os.makedirs(props, exist_ok=True)
    for name, longest in PROPS.items():
        img = fit(Image.open(os.path.join(RAW, f"{name}.png")).convert("RGBA"), longest)
        img.save(os.path.join(props, f"{name}.webp"), quality=90)
        print(f"wtProps/{name}: {img.width}x{img.height}")

    bgs = os.path.join(sprites, "wtBackgrounds")
    os.makedirs(bgs, exist_ok=True)
    for out_name, src in BACKGROUNDS.items():
        Image.open(os.path.join(RAW, f"{src}.png")).convert("RGB").save(os.path.join(bgs, f"{out_name}.webp"), quality=85)
    print(f"wtBackgrounds: {len(BACKGROUNDS)}")

    # UI: recolour the Dumpster Duke sheet once, from its own source in the dumpster-duke app.
    dd = os.path.join(HERE, "..", "..", "web-sdk", "apps", "dumpster-duke", "static", "assets")
    ui = os.path.join(sprites, "wtUi")
    os.makedirs(ui, exist_ok=True)
    atlas = json.load(open(os.path.join(dd, "sprites", "dukeUi", "dukeUi.json")))
    sheet = winterise(Image.open(os.path.join(dd, "sprites", "dukeUi", "dukeUi.webp")))
    # the Buy Bonus button shows Mitten's gift instead of Dumpster Duke's mine cart
    gift = Image.open(os.path.join(RAW, "gift_closed.png")).convert("RGBA")
    for frame_name in ("ui_icon_cart.png",):
        f = atlas["frames"][frame_name]["frame"]
        sheet.paste((0, 0, 0, 0), (f["x"], f["y"], f["x"] + f["w"], f["y"] + f["h"]))
        icon = fit(gift, min(f["w"], f["h"]) - 6)
        sheet.paste(icon, (f["x"] + (f["w"] - icon.width) // 2, f["y"] + (f["h"] - icon.height) // 2), icon)
    sheet.save(os.path.join(ui, "wtUi.webp"), quality=92)
    atlas["meta"]["image"] = "wtUi.webp"
    json.dump(atlas, open(os.path.join(ui, "wtUi.json"), "w"), indent=1)
    with open(os.path.join(ui, "index.ts"), "w") as f:
        f.write("import { createAsset } from 'pixi-svelte';\n\n"
                "import img from './wtUi.webp';\nimport atlas from './wtUi.json';\n\n"
                "export default createAsset({ img, atlas });\n")
    os.makedirs(os.path.join(OUT, "ui"), exist_ok=True)
    for f in os.listdir(os.path.join(dd, "ui")):
        winterise(Image.open(os.path.join(dd, "ui", f))).save(os.path.join(OUT, "ui", f), quality=92)
    icon = fit(gift, 240)
    canvas = Image.new("RGBA", (256, 256), (0, 0, 0, 0))
    canvas.paste(icon, ((256 - icon.width) // 2, (256 - icon.height) // 2), icon)
    canvas.save(os.path.join(OUT, "ui", "icon_cart.webp"), quality=92)
    print("wtUi + ui/: recoloured from Dumpster Duke")

    for old in ("dukeSymbols", "dukeUi", "dukeBackgrounds"):
        shutil.rmtree(os.path.join(sprites, old), ignore_errors=True)


if __name__ == "__main__":
    main()
