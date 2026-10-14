"""Render sample strings with the generated BMFont to check spacing/baselines."""
import os
import re
import sys

from PIL import Image

D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "web-sdk", "apps", "dumpster-duke", "static", "assets", "fonts", "goldFont")
xml = open(os.path.join(D, "duke_gold.xml"), encoding="utf-8").read()
page = Image.open(os.path.join(D, "duke_gold.webp")).convert("RGBA")
line = int(re.search(r'lineHeight="(\d+)"', xml).group(1))
chars = {int(m["id"]): {k: int(v) for k, v in m.groupdict().items() if k != "id"} for m in re.finditer(
    r'<char id="(?P<id>\d+)" x="(?P<x>-?\d+)" y="(?P<y>-?\d+)" width="(?P<w>\d+)" height="(?P<h>\d+)" xoffset="(?P<xo>-?\d+)" yoffset="(?P<yo>-?\d+)" xadvance="(?P<adv>-?\d+)"', xml)}
lines = sys.argv[2:] or ["BIG WIN $1,234.50", "10x 38x LOOT BAG", "FREE SPIN 3 OF 10", "€9.99 ₹100 ¥5 ZŁ"]
out = Image.new("RGBA", (1400, line * len(lines) + 20), (40, 24, 50, 255))
for i, text in enumerate(lines):
    x, y = 10, 10 + i * line
    for ch in text:
        c = chars.get(ord(ch))
        if not c:
            print("missing", repr(ch)); continue
        g = page.crop((c["x"], c["y"], c["x"] + c["w"], c["y"] + c["h"]))
        out.alpha_composite(g, (x + c["xo"], y + c["yo"]))
        x += c["adv"]
out.convert("RGB").save(sys.argv[1])
