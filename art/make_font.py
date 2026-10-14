"""Build the game's bitmap font ("gold") from the ChatGPT UI sheet.

A-Z and 0-9 are cut from the sheet. Signs the sheet doesn't have ($ , . x and
currency symbols) are rendered from DejaVu Sans Bold with the same gold gradient
and dark outline. Output is a BMFont (.xml + .webp) that replaces the template's
"gold" font, so every existing use of fontFamily 'gold' switches over.

Usage: python art/make_font.py art/source/ui_sheet.webp
"""
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from slice_sheet import cut  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "web-sdk", "apps", "dumpster-duke", "static", "assets", "fonts", "goldFont")
FACE = "gold"
LINE, BASE = 110, 96  # line height and baseline in the font's pixels
ROWS = [  # (top, bottom, characters) of each glyph row on the sheet; x from 30 to 640
    (60, 155, "ABCDEFGHI"),
    (158, 250, "JKLMNOPQR"),
    (252, 345, "STUVWXYZ"),
    (355, 450, "0123456789"),
]
RENDERED = " !\"$%&'()+,-./:;=?€₹₩₱₽₺₫¥łŁz×"
DEJAVU = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
OUTLINE_PX = 7  # outline width around the gold fill on the sheet
GOLD_TOP, GOLD_BOTTOM, OUTLINE = (255, 226, 92), (244, 146, 20), (58, 20, 36)


def gold_runs(row_rgb):
    """Column ranges of the gold letter fills in one row."""
    a = row_rgb.astype(int)
    gold = (a[..., 0] > 170) & (a[..., 1] > 110) & (a[..., 2] < 120)
    col = gold.sum(axis=0) > 1
    runs, start = [], None
    for x, on in enumerate(col):
        if on and start is None:
            start = x
        elif not on and start is not None:
            runs.append((start, x))
            start = None
    if start is not None:
        runs.append((start, len(col)))
    return [r for r in runs if r[1] - r[0] > 4]


def sheet_glyphs(sheet):
    glyphs = {}
    for top, bottom, chars in ROWS:
        row = sheet.crop((30, top, 640, bottom))
        runs = gold_runs(np.asarray(row))
        assert len(runs) == len(chars), f"row {chars}: found {len(runs)} glyphs"
        # each letter = its gold fill plus the dark outline around it (not the glow)
        cut_glyphs = [
            cut(row.crop((max(0, a - OUTLINE_PX), 0, min(row.width, b + OUTLINE_PX), row.height)))
            for a, b in runs
        ]
        # common height so all letters in a row share a baseline; scale to the font size
        height = max(g.height for g in cut_glyphs)
        scale = (BASE - 8) / height
        for ch, g in zip(chars, cut_glyphs):
            glyphs[ch] = g.resize((max(1, round(g.width * scale)), max(1, round(g.height * scale))), Image.LANCZOS)
    return glyphs


def rendered_glyph(ch, cap_height):
    font = ImageFont.truetype(DEJAVU, 100)
    probe = font.getbbox("H")
    font = ImageFont.truetype(DEJAVU, round(100 * cap_height / (probe[3] - probe[1])))
    stroke = 8
    l, t, r, b = font.getbbox(ch, stroke_width=stroke)
    w, h = max(1, r - l), max(1, b - t)
    mask = Image.new("L", (w, h))
    ImageDraw.Draw(mask).text((-l, -t), ch, font=font, fill=255)
    outline = Image.new("L", (w, h))
    ImageDraw.Draw(outline).text((-l, -t), ch, font=font, fill=255, stroke_width=stroke, stroke_fill=255)
    ramp = np.linspace(0, 1, h)[:, None, None]
    fill = (np.array(GOLD_TOP) * (1 - ramp) + np.array(GOLD_BOTTOM) * ramp).repeat(w, axis=1)
    img = Image.new("RGBA", (w, h), OUTLINE + (0,))
    img.putalpha(outline)
    img.paste(Image.fromarray(fill.astype(np.uint8)), (0, 0), mask)
    # where the glyph sits relative to the baseline: font top offset from the cap top
    return img, t - font.getbbox("H")[1]


def main(path):
    sheet = Image.open(path).convert("RGB")
    glyphs = {ch: (img, None) for ch, img in sheet_glyphs(sheet).items()}
    cap = glyphs["H"][0].height
    # lowercase x / multiplication sign: a smaller sheet X, so "10x" matches the art
    small_x = glyphs["X"][0].resize((round(glyphs["X"][0].width * 0.72), round(cap * 0.72)), Image.LANCZOS)
    glyphs["x"] = (small_x, None)
    for ch in RENDERED:
        if ch == " ":
            continue
        img, top_from_cap = rendered_glyph(ch, cap - 12)
        glyphs[ch] = (img, top_from_cap)
    if "×" in glyphs:
        glyphs["×"] = (small_x, None)

    # shelf-pack into one page
    page_w, pad = 1024, 2
    x = y = shelf = 0
    placed = {}
    for ch, (img, _) in sorted(glyphs.items(), key=lambda kv: -kv[1][0].height):
        if x + img.width + pad > page_w:
            x, y, shelf = 0, y + shelf + pad, 0
        placed[ch] = (x, y)
        x += img.width + pad
        shelf = max(shelf, img.height)
    page_h = y + shelf
    page = Image.new("RGBA", (page_w, page_h))
    chars_xml = [f'    <char id="32" x="0" y="0" width="1" height="1" xoffset="0" yoffset="0" xadvance="{round(cap * 0.35)}" page="0"/>']
    for ch, (img, top_from_cap) in glyphs.items():
        px, py = placed[ch]
        page.paste(img, (px, py))
        if top_from_cap is None:  # sheet glyph: bottom on the baseline
            yoffset = BASE - img.height
        else:  # rendered glyph: positioned relative to the cap top
            yoffset = BASE - (cap - 12) + top_from_cap - 6
        chars_xml.append(
            f'    <char id="{ord(ch)}" x="{px}" y="{py}" width="{img.width}" height="{img.height}" '
            f'xoffset="0" yoffset="{yoffset}" xadvance="{img.width - (10 if top_from_cap is not None else 2)}" page="0"/>'
        )
    os.makedirs(OUT, exist_ok=True)
    page.save(os.path.join(OUT, "duke_gold.webp"), quality=92)
    with open(os.path.join(OUT, "duke_gold.xml"), "w", encoding="utf-8") as f:
        f.write(f'''<?xml version="1.0" encoding="UTF-8"?>
<font>
  <info face="{FACE}" size="{LINE}" bold="0" italic="0" charset="" unicode="1" stretchH="100" smooth="1" aa="1" padding="0,0,0,0" spacing="1,1" outline="0"/>
  <common lineHeight="{LINE}" base="{BASE}" scaleW="{page_w}" scaleH="{page_h}" pages="1" packed="0"/>
  <pages>
    <page id="0" file="duke_gold.webp"/>
  </pages>
  <chars count="{len(chars_xml)}">
{chr(10).join(chars_xml)}
  </chars>
</font>
''')
    print(f"{len(chars_xml)} glyphs, page {page_w}x{page_h}")


if __name__ == "__main__":
    main(sys.argv[1])
