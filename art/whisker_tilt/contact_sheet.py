"""Preview every cut asset on a dark background: python art/whisker_tilt/contact_sheet.py"""
import os

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "raw")
CELL, COLS = 260, 7

names = sorted(f[:-4] for f in os.listdir(RAW) if f.endswith(".png"))
order = ["H1", "H2", "H3", "H4", "L1", "L2", "L3", "L4", "S", "C"]
names = [n for n in order if n in names] + [n for n in names if n not in order]
rows = (len(names) + COLS - 1) // COLS
sheet = Image.new("RGBA", (COLS * CELL, rows * CELL), (40, 30, 70, 255))
draw = ImageDraw.Draw(sheet)
for i, name in enumerate(names):
    im = Image.open(os.path.join(RAW, name + ".png"))
    im.thumbnail((CELL - 20, CELL - 30))
    x, y = (i % COLS) * CELL, (i // COLS) * CELL
    sheet.alpha_composite(im, (x + (CELL - im.width) // 2, y + 5 + (CELL - 30 - im.height) // 2))
    draw.text((x + 6, y + CELL - 20), name, fill=(255, 255, 255, 255))
sheet.convert("RGB").save(os.path.join(HERE, "contact_sheet.png"))
print(f"{len(names)} assets -> contact_sheet.png")
