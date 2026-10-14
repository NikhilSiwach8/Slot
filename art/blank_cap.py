"""Paint out the star in the middle of the bottle-cap symbol (art/raw/M.png) so the
game can print the multiplier value there. Re-run after re-slicing the sheet."""
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "raw", "M.png")
CENTER_COLOUR = np.array([236, 52, 92])
EDGE_COLOUR = np.array([176, 8, 58])

img = Image.open(PATH).convert("RGBA")
px = np.asarray(img).astype(int)
r, g, b = px[..., 0], px[..., 1], px[..., 2]
h, w = r.shape
# The gold ring (an ellipse, the cap is slightly tilted) and the star share a strict
# gold colour; percentiles of those pixels give the ring's extent while ignoring
# stray highlights. The painted disc sits just inside the ring.
yy, xx = np.mgrid[0:h, 0:w]
gold = (r > 220) & (g > 150) & (g < 240) & (b < 110) & (px[..., 3] > 200)
cy, cx = np.nonzero(gold)
x0, x1 = np.percentile(cx, [0.5, 99.5])
y0, y1 = np.percentile(cy, [0.5, 99.5])
centre = ((x0 + x1) / 2, (y0 + y1) / 2)
rx, ry = (x1 - x0) / 2 * 0.86, (y1 - y0) / 2 * 0.86

# radial red gradient disc with a soft top-left highlight, blended in with a feathered mask
dist = np.hypot((xx - centre[0]) / rx, (yy - centre[1]) / ry)
t = np.clip(dist, 0, 1)[..., None]
disc = CENTER_COLOUR * (1 - t) + EDGE_COLOUR * t
highlight = np.clip(1 - np.hypot((xx - (centre[0] - rx * 0.35)) / rx, (yy - (centre[1] - ry * 0.4)) / ry) / 0.55, 0, 1)
disc = disc + highlight[..., None] * 60
fill = Image.fromarray(np.clip(disc, 0, 255).astype(np.uint8), "RGB").convert("RGBA")
mask = Image.new("L", (w, h), 0)
ImageDraw.Draw(mask).ellipse([centre[0] - rx, centre[1] - ry, centre[0] + rx, centre[1] + ry], fill=255)
mask = mask.filter(ImageFilter.GaussianBlur(3))
img.paste(fill, (0, 0), mask)
img.save(PATH)
print(f"blanked star at {centre[0]:.0f},{centre[1]:.0f} rx={rx:.0f} ry={ry:.0f}")
