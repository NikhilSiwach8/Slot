"""Stake Engine Tile Editor assets from the key-art image (art/source/tile_logo_art.webp).

Writes to art/tile/:
  tile_background.png  bright cave background, no text (Tile Editor "Background" layer)
  tile_foreground.png  the Duke cut out on transparency, no text ("Foreground element" layer)
  tile_logo.png        the full DUMPSTER DUKE logo on transparency (marketing / in-game use)
  provider_logo.png    square provider logo for Team Settings -> Branding
  tile_preview.png     rough mock of the finished tile (not uploaded; the editor adds the title)

Needs: pip install rembg opencv-python-headless  (the cutout model downloads on first run)
Usage: python art/make_tile.py [provider_name]
"""
import os
import sys
import xml.etree.ElementTree as ET

import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
OUT = os.path.join(HERE, "tile")
ART = os.path.join(HERE, "source", "tile_logo_art.webp")
BG = os.path.join(ROOT, "web-sdk/apps/dumpster-duke/static/assets/sprites/dukeBackgrounds/bg_base_portrait.webp")
FONT = os.path.join(ROOT, "web-sdk/apps/dumpster-duke/static/assets/fonts/goldFont/duke_gold.xml")
PROVIDER = (sys.argv[1] if len(sys.argv) > 1 else "nyxhilx").upper()
TILE = (1080, 1440)  # 3:4 portrait


def cutout(img):
    from rembg import new_session, remove

    return remove(img, session=new_session("isnet-general-use"))


def sign_top(x):
    """Top edge of the wooden title sign in the 1254px key art (it arches up in the middle)."""
    return 551 + 52 * ((x - 660) / 510.0) ** 2


def foreground(logo):
    """Everything above the title sign: the Duke, his crown and the trash pile, no lettering."""
    a = np.array(logo)
    h, w = a.shape[:2]
    ys = np.arange(h)[:, None]
    cut = np.array([sign_top(x) for x in range(w)])[None, :]
    fade = np.clip((cut - ys) / 10.0, 0, 1)  # 10px feather into the sign edge
    a[..., 3] = (a[..., 3] * fade).astype(np.uint8)
    out = Image.fromarray(a)
    # drop small leftovers (coin halves) that the cut left floating on the sides
    alpha = np.array(out)[..., 3] > 40
    import cv2

    n, lab, stats, _ = cv2.connectedComponentsWithStats(alpha.astype(np.uint8), 8)
    keep = np.zeros_like(alpha)
    for i in range(1, n):
        if stats[i, cv2.CC_STAT_AREA] > 8000:
            keep |= lab == i
    keep = cv2.dilate(keep.astype(np.uint8), np.ones((5, 5), np.uint8)) > 0
    b = np.array(out)
    b[..., 3] = np.where(keep, b[..., 3], 0)
    out = Image.fromarray(b)
    out = out.crop(out.getbbox())
    # soften the cut so the pile melts into the background instead of ending on a hard arch
    c = np.array(out)
    h = c.shape[0]
    ramp = np.clip((h - np.arange(h)) / (h * 0.14), 0, 1) ** 1.3
    c[..., 3] = (c[..., 3] * ramp[:, None]).astype(np.uint8)
    return Image.fromarray(c)


def background():
    """Our cave background, lifted well above Stake's dark lobby: brighter, warmer, no dark edges."""
    im = Image.open(BG).convert("RGB").resize(TILE, Image.LANCZOS)
    a = np.asarray(im).astype(np.float32) / 255
    a = a ** 0.62  # open the shadows
    w, h = TILE
    yy, xx = np.mgrid[0:h, 0:w]
    # glow behind where the character sits, plus a light lavender rim so the edges never go dark
    d = np.sqrt(((xx - w * 0.5) / (w * 0.55)) ** 2 + ((yy - h * 0.42) / (h * 0.5)) ** 2)
    glow = np.clip(1 - d, 0, 1)[..., None] ** 1.5
    a = a + glow * np.array([0.35, 0.22, 0.05]) * 0.9
    edge = np.clip(d - 0.75, 0, 1)[..., None]
    a = a * (1 - edge * 0.5) + np.array([0.62, 0.48, 0.92]) * edge * 0.5
    im = Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8))
    im = ImageEnhance.Color(im).enhance(1.15)
    return ImageEnhance.Contrast(im).enhance(1.05)


def gold_text(text, height):
    """Render text with the game's gold bitmap font."""
    root = ET.parse(FONT).getroot()
    page = Image.open(os.path.join(os.path.dirname(FONT), root.find("pages/page").get("file"))).convert("RGBA")
    chars = {int(c.get("id")): {k: int(v) for k, v in c.attrib.items() if k != "id"} for c in root.iter("char")}
    line = int(root.find("common").get("lineHeight"))
    width = sum(chars[ord(ch)]["xadvance"] for ch in text) + 20
    canvas = Image.new("RGBA", (width, line + 10), (0, 0, 0, 0))
    x = 10
    for ch in text:
        c = chars[ord(ch)]
        glyph = page.crop((c["x"], c["y"], c["x"] + c["width"], c["y"] + c["height"]))
        canvas.alpha_composite(glyph, (x + c["xoffset"], c["yoffset"] + 5))
        x += c["xadvance"]
    canvas = canvas.crop(canvas.getbbox())
    return canvas.resize((round(canvas.width * height / canvas.height), height), Image.LANCZOS)


def provider_logo():
    size = 1024
    logo = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    word = gold_text(PROVIDER, 220)
    if word.width > size * 0.84:
        word = word.resize((int(size * 0.84), round(word.height * size * 0.84 / word.width)), Image.LANCZOS)
    # soft dark halo so the gold stays legible on light and dark tiles
    halo = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    halo.paste((40, 12, 50, 170), ((size - word.width) // 2, (size - word.height) // 2), word.split()[3])
    halo = halo.filter(ImageFilter.GaussianBlur(18))
    logo.alpha_composite(halo)
    logo.alpha_composite(word, ((size - word.width) // 2, (size - word.height) // 2))
    return logo


def preview(bg, fg):
    tile = bg.convert("RGBA")
    w, h = TILE
    f = fg.copy()
    scale = (w * 0.98) / f.width
    f = f.resize((int(f.width * scale), int(f.height * scale)), Image.LANCZOS)
    tile.alpha_composite(f, ((w - f.width) // 2, int(h * 0.60) - f.height))
    grad = Image.new("RGBA", TILE, (0, 0, 0, 0))
    g = np.zeros((h, w, 4), np.uint8)
    g[..., :3] = (112, 40, 170)
    g[..., 3] = (np.clip((np.arange(h) - h * 0.55) / (h * 0.45), 0, 1) * 210).astype(np.uint8)[:, None]
    tile.alpha_composite(Image.fromarray(g))
    t1, t2 = gold_text("DUMPSTER", 190), gold_text("DUKE", 190)
    for t, y in ((t1, 0.66), (t2, 0.80)):
        t = t.resize((int(w * 0.86), round(t.height * w * 0.86 / t.width)), Image.LANCZOS) if t is t1 else t
        tile.alpha_composite(t, ((w - t.width) // 2, int(h * y)))
    return tile


def main():
    os.makedirs(OUT, exist_ok=True)
    logo = cutout(Image.open(ART).convert("RGB"))
    logo.crop(logo.getbbox()).save(os.path.join(OUT, "tile_logo.png"))
    fg = foreground(logo)
    fg.save(os.path.join(OUT, "tile_foreground.png"))
    bg = background()
    bg.save(os.path.join(OUT, "tile_background.png"))
    provider_logo().save(os.path.join(OUT, "provider_logo.png"))
    preview(bg, fg).convert("RGB").save(os.path.join(OUT, "tile_preview.png"))
    print("wrote", sorted(os.listdir(OUT)))


if __name__ == "__main__":
    main()
