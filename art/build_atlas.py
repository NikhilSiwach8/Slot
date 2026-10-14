"""Pack symbol art into a Pixi spritesheet for the game client.

Uses art/final/<KEY>.webp when it exists (finished ChatGPT art), otherwise draws
a clearly-labelled placeholder so the game runs before the real art arrives.
Usage: python art/build_atlas.py
"""

import json
import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
FINAL = os.path.join(HERE, "final")
OUT = os.path.join(HERE, "..", "web-sdk", "apps", "dumpster-duke", "static", "assets", "sprites", "dukeSymbols")
CELL = 256

SYMBOLS = {
    # key: (placeholder colour, label)
    "H1": ((120, 120, 140), "DUKE"),
    "H2": ((150, 150, 165), "POSSUM"),
    "H3": ((120, 90, 170), "PIGEON"),
    "H4": ((240, 180, 40), "PIZZA"),
    "L1": ((240, 70, 150), "SODA"),
    "L2": ((120, 210, 210), "FISH"),
    "L3": ((250, 220, 60), "BANANA"),
    "L4": ((150, 220, 60), "APPLE"),
    "S": ((255, 200, 30), "TRASH\nCAN"),
    "M": ((220, 40, 40), ""),
}
OUTLINE = (45, 25, 20)


def font(size):
    for path in ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",):
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def placeholder(key):
    colour, label = SYMBOLS[key]
    img = Image.new("RGBA", (CELL, CELL), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    pad = 18
    if key == "M":
        # bottle cap: crimped circle
        import math

        cx = cy = CELL / 2
        pts = []
        for i in range(48):
            a = i / 48 * 2 * math.pi
            r = (CELL / 2 - pad) * (1.0 if i % 2 == 0 else 0.9)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
        d.polygon(pts, fill=colour, outline=OUTLINE, width=10)
        d.ellipse([60, 60, CELL - 60, CELL - 60], fill=(250, 210, 80), outline=OUTLINE, width=8)
    elif key == "S":
        d.rounded_rectangle([pad + 20, pad + 50, CELL - pad - 20, CELL - pad], 18, fill=colour, outline=OUTLINE, width=12)
        d.rounded_rectangle([pad, pad + 20, CELL - pad, pad + 60], 14, fill=(255, 230, 120), outline=OUTLINE, width=12)
    else:
        d.ellipse([pad, pad, CELL - pad, CELL - pad], fill=colour, outline=OUTLINE, width=12)
        d.ellipse([pad + 40, pad + 30, pad + 90, pad + 60], fill=(255, 255, 255, 170))
    if label:
        f = font(30 if "\n" not in label else 30)
        d.multiline_text((CELL / 2, CELL / 2 + (25 if key == "S" else 0)), label, font=f, fill="white",
                         anchor="mm", align="center", stroke_width=5, stroke_fill=OUTLINE)
    return img


def load(key):
    path = os.path.join(FINAL, f"{key}.webp")
    if not os.path.exists(path):
        return placeholder(key), False
    src = Image.open(path).convert("RGBA")
    src.thumbnail((CELL, CELL), Image.LANCZOS)
    img = Image.new("RGBA", (CELL, CELL), (0, 0, 0, 0))
    img.paste(src, ((CELL - src.width) // 2, (CELL - src.height) // 2), src)
    return img, True


def main():
    os.makedirs(OUT, exist_ok=True)
    keys = list(SYMBOLS)
    cols = 4
    rows = (len(keys) + cols - 1) // cols
    sheet = Image.new("RGBA", (cols * CELL, rows * CELL), (0, 0, 0, 0))
    frames = {}
    for i, key in enumerate(keys):
        img, real = load(key)
        x, y = (i % cols) * CELL, (i // cols) * CELL
        sheet.paste(img, (x, y))
        frames[f"duke_{key.lower()}.png"] = {
            "frame": {"x": x, "y": y, "w": CELL, "h": CELL},
            "rotated": False,
            "trimmed": False,
            "spriteSourceSize": {"x": 0, "y": 0, "w": CELL, "h": CELL},
            "sourceSize": {"w": CELL, "h": CELL},
        }
        print(f"{key}: {'final art' if real else 'placeholder'}")
    sheet.save(os.path.join(OUT, "dukeSymbols.webp"), quality=92)
    meta = {"app": "art/build_atlas.py", "image": "dukeSymbols.webp", "format": "RGBA8888",
            "size": {"w": sheet.width, "h": sheet.height}, "scale": "1"}
    with open(os.path.join(OUT, "dukeSymbols.json"), "w") as f:
        json.dump({"frames": frames, "meta": meta}, f, indent=1)
    with open(os.path.join(OUT, "index.ts"), "w") as f:
        f.write("import { createAsset } from 'pixi-svelte';\n\n"
                "import img from './dukeSymbols.webp';\nimport atlas from './dukeSymbols.json';\n\n"
                "export default createAsset({ img, atlas });\n")


if __name__ == "__main__":
    main()
