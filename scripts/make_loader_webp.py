"""Re-encode Stake Engine's intro loader (stake-engine-loader.gif from the web-sdk template,
1080x1080, 1.3 MB) as an 800x800 animated WebP: same 52 frames and 2.08 s timing, about a
third of the size, so the "Powered by Stake Engine" intro shows straight away instead of
building up while the GIF downloads. It is shown at most 400 px wide (LoaderStakeEngine).

Usage: python3 scripts/make_loader_webp.py path/to/stake-engine-loader.gif
"""
import os
import sys

from PIL import Image

OUT = os.path.join(os.path.dirname(__file__), "..", "web-sdk", "apps", "dumpster-duke", "static", "stake-engine-loader.webp")
SIZE = 800

src = Image.open(sys.argv[1])
frames, durations = [], []
try:
    while True:
        frames.append(src.convert("RGB").resize((SIZE, SIZE), Image.LANCZOS))
        durations.append(src.info.get("duration", 40))
        src.seek(src.tell() + 1)
except EOFError:
    pass
frames[0].save(OUT, save_all=True, append_images=frames[1:], duration=durations, loop=0, quality=75, method=6)
print(f"{len(frames)} frames, {sum(durations)} ms, {os.path.getsize(OUT) // 1024} KB -> {OUT}")
