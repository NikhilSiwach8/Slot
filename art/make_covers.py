"""Finished key art: a 3:4 game tile and a 16:9 cover, both with the full DUMPSTER DUKE logo.

Run art/make_tile.py first (it cuts art/tile/tile_logo.png from the key art).
Writes art/tile/game_tile_3x4.png (1080x1440) and art/tile/cover_16x9.png (1920x1080).
Usage: python art/make_covers.py
"""
import os

import numpy as np
from PIL import Image, ImageEnhance, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "tile")
BGS = os.path.join(HERE, "..", "web-sdk/apps/dumpster-duke/static/assets/sprites/dukeBackgrounds")
SYMBOLS = os.path.join(HERE, "final")


def bright_background(name, size, focus):
    """The game's cave art, lifted well above Stake's dark lobby, with a warm glow at `focus`."""
    im = Image.open(os.path.join(BGS, name)).convert("RGB")
    scale = max(size[0] / im.width, size[1] / im.height)
    im = im.resize((round(im.width * scale), round(im.height * scale)), Image.LANCZOS)
    left, top = (im.width - size[0]) // 2, (im.height - size[1]) // 2
    im = im.crop((left, top, left + size[0], top + size[1]))
    a = (np.asarray(im).astype(np.float32) / 255) ** 0.62
    w, h = size
    yy, xx = np.mgrid[0:h, 0:w]
    d = np.sqrt(((xx - w * focus[0]) / (w * 0.55)) ** 2 + ((yy - h * focus[1]) / (h * 0.55)) ** 2)
    a = a + (np.clip(1 - d, 0, 1)[..., None] ** 1.5) * np.array([0.32, 0.20, 0.05])
    edge = np.clip(d - 0.8, 0, 1)[..., None]
    a = a * (1 - edge * 0.45) + np.array([0.62, 0.48, 0.92]) * edge * 0.45
    im = Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8))
    return ImageEnhance.Color(im).enhance(1.15).convert("RGBA")


def with_shadow(layer, blur=22, alpha=150):
    """Soft dark halo behind a cut-out so it separates from the busy background."""
    pad = blur * 3
    canvas = Image.new("RGBA", (layer.width + pad * 2, layer.height + pad * 2), (0, 0, 0, 0))
    shadow = Image.new("RGBA", layer.size, (30, 8, 45, alpha))
    canvas.paste(shadow, (pad, pad + blur // 2), layer.split()[3])
    canvas = canvas.filter(ImageFilter.GaussianBlur(blur))
    canvas.alpha_composite(layer, (pad, pad))
    return canvas


def place(base, layer, width, cx, cy, angle=0):
    layer = layer.resize((round(width), round(layer.height * width / layer.width)), Image.LANCZOS)
    if angle:
        layer = layer.rotate(angle, Image.BICUBIC, expand=True)
    layer = with_shadow(layer, blur=max(8, round(width / 40)))
    base.alpha_composite(layer, (round(cx - layer.width / 2), round(cy - layer.height / 2)))


def logo():
    im = Image.open(os.path.join(OUT, "tile_logo.png")).convert("RGBA")
    return im.crop(im.getbbox())


def symbol(name):
    im = Image.open(os.path.join(SYMBOLS, f"{name}.webp")).convert("RGBA")
    return im.crop(im.getbbox())


def game_tile():
    w, h = 1080, 1440
    tile = bright_background("bg_base_portrait.webp", (w, h), (0.5, 0.45))
    place(tile, symbol("S"), 300, w * 0.17, h * 0.85, angle=12)
    place(tile, symbol("M"), 260, w * 0.84, h * 0.86, angle=-10)
    place(tile, logo(), w * 0.96, w * 0.5, h * 0.47)
    return tile


def cover():
    w, h = 1920, 1080
    art = bright_background("bg_base_landscape.webp", (w, h), (0.5, 0.48))
    place(art, symbol("H1"), 330, w * 0.15, h * 0.30, angle=-10)
    place(art, symbol("S"), 360, w * 0.13, h * 0.74, angle=8)
    place(art, symbol("M"), 320, w * 0.86, h * 0.30, angle=10)
    place(art, symbol("H2"), 330, w * 0.87, h * 0.73, angle=-8)
    place(art, logo(), h * 0.98, w * 0.5, h * 0.5)
    return art


if __name__ == "__main__":
    game_tile().convert("RGB").save(os.path.join(OUT, "game_tile_3x4.png"))
    cover().convert("RGB").save(os.path.join(OUT, "cover_16x9.png"))
    print("wrote game_tile_3x4.png, cover_16x9.png")
