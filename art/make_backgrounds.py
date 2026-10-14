"""Build the game backgrounds from the ChatGPT backgrounds sheet.

The sheet holds two portrait images side by side:
  left  - the mine tunnel   -> base game and (purple-graded) free-spins backgrounds
  right - the FREE SPINS cart -> full-screen splash when free spins trigger

The landscape backgrounds behind the reels fill the screen (cropping top and
bottom); the splash, which has its sign in the middle, is instead widened by
placing it full height over a blurred, darkened copy of itself.

Usage: python art/make_backgrounds.py art/source/backgrounds_sheet.webp
"""
import os
import sys

import numpy as np
from PIL import Image, ImageEnhance, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "web-sdk", "apps", "dumpster-duke", "static", "assets", "sprites", "dukeBackgrounds")
LEFT, RIGHT = (0, 766), (771, 1536)  # the sheet's halves, skipping the seam
LANDSCAPE = (1920, 1080)
PORTRAIT = (1080, 1440)
FEATHER = 90  # px of soft edge where the sharp art meets the blurred fill


def cover(img, size):
    scale = max(size[0] / img.width, size[1] / img.height)
    resized = img.resize((round(img.width * scale), round(img.height * scale)), Image.LANCZOS)
    left, top = (resized.width - size[0]) // 2, (resized.height - size[1]) // 2
    return resized.crop((left, top, left + size[0], top + size[1]))


def cover_sharp(img, size, focus_y=0.5):
    """Fill the screen with the art itself (cropping top/bottom), lightly sharpened
    to offset the upscale. Used where the reels would hide a centred image."""
    scale = max(size[0] / img.width, size[1] / img.height)
    resized = img.resize((round(img.width * scale), round(img.height * scale)), Image.LANCZOS)
    left = (resized.width - size[0]) // 2
    top = round((resized.height - size[1]) * focus_y)
    out = resized.crop((left, top, left + size[0], top + size[1]))
    return out.filter(ImageFilter.UnsharpMask(radius=2, percent=60, threshold=2))


def widen(img, size):
    fill = cover(img, size).filter(ImageFilter.GaussianBlur(28))
    fill = ImageEnhance.Brightness(fill).enhance(0.55)
    sharp = img.resize((round(img.width * size[1] / img.height), size[1]), Image.LANCZOS)
    ramp = np.minimum(np.arange(sharp.width), np.arange(sharp.width)[::-1]) / FEATHER
    mask = Image.fromarray((np.clip(ramp, 0, 1)[None, :].repeat(sharp.height, 0) * 255).astype(np.uint8))
    fill.paste(sharp, ((size[0] - sharp.width) // 2, 0), mask)
    return fill


def raid_grade(img):
    """Darker, purple-heavy 'midnight raid' version of the tunnel."""
    arr = np.asarray(img.convert("RGB")).astype(float)
    arr = arr * np.array([0.78, 0.62, 1.05])
    h, w = arr.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w]
    vignette = 1 - 0.45 * np.clip(np.hypot((xx - w / 2) / (w / 2), (yy - h / 2) / (h / 2)) - 0.35, 0, 1)
    return Image.fromarray(np.clip(arr * vignette[..., None], 0, 255).astype(np.uint8))


def save(img, name):
    path = os.path.join(OUT, f"{name}.webp")
    img.convert("RGB").save(path, quality=86)
    print(name, img.size, f"{os.path.getsize(path) // 1024} KB")


def main(path):
    os.makedirs(OUT, exist_ok=True)
    sheet = Image.open(path).convert("RGB")
    tunnel = sheet.crop((LEFT[0], 0, LEFT[1], sheet.height))
    splash = sheet.crop((RIGHT[0], 0, RIGHT[1], sheet.height))
    # Behind the reels: fill the screen so the tunnel stays visible around the board.
    save(cover_sharp(tunnel, LANDSCAPE, 0.45), "bg_base_landscape")
    save(cover(tunnel, PORTRAIT), "bg_base_portrait")
    save(raid_grade(cover_sharp(tunnel, LANDSCAPE, 0.45)), "bg_raid_landscape")
    save(raid_grade(cover(tunnel, PORTRAIT)), "bg_raid_portrait")
    save(widen(splash, LANDSCAPE), "fs_splash_landscape")
    save(cover(splash, PORTRAIT), "fs_splash_portrait")


if __name__ == "__main__":
    main(sys.argv[1])
