"""Build the full-screen bonus splashes from the portrait (2:3) ChatGPT art in art/source.

Each image is placed full height over a blurred, darkened copy of itself, giving a
1920x1080 landscape and a 1080x1440 portrait version with nothing cropped. The art's
blank plaque is left empty: the game draws the spin count / total win on it (plaque
positions live in web-sdk/apps/dumpster-duke/src/game/splashes.ts).

Usage: python art/make_fs_splashes.py
"""
import os

from PIL import Image

from make_backgrounds import LANDSCAPE, PORTRAIT, save, widen

HERE = os.path.dirname(os.path.abspath(__file__))
SPLASHES = ["raid", "super", "mystery", "outro"]


def main():
    for name in SPLASHES:
        art = Image.open(os.path.join(HERE, "source", f"fs_{name}.webp")).convert("RGB")
        save(widen(art, LANDSCAPE), f"fs_{name}_landscape")
        save(widen(art, PORTRAIT), f"fs_{name}_portrait")


if __name__ == "__main__":
    main()
