"""Generate Dumpster Duke art with OpenAI's image model, then 'humanise' it.

Needs OPENAI_API_KEY (env var or network secret) and network access to api.openai.com.
Usage: python art/generate.py [--only H1,S] [--model gpt-image-1]
Outputs: art/raw/<key>.png (as generated) and art/final/<key>.webp (processed).
"""

import argparse
import base64
import json
import os
import random

import requests
from PIL import Image, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
RAW, FINAL = os.path.join(HERE, "raw"), os.path.join(HERE, "final")


def generate(prompt, size, model, transparent):
    resp = requests.post(
        "https://api.openai.com/v1/images/generations",
        # The key may be injected by the environment's network proxy instead of the shell.
        headers={"Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}"} if os.environ.get("OPENAI_API_KEY") else {},
        json={
            "model": model,
            "prompt": prompt,
            "size": size,
            "quality": "high",
            "background": "transparent" if transparent else "opaque",
            "n": 1,
        },
        timeout=300,
    )
    if not resp.ok:
        raise SystemExit(f"OpenAI error {resp.status_code}: {resp.text[:500]}")
    return base64.b64decode(resp.json()["data"][0]["b64_json"])


def humanise(img, seed):
    """Light post-pass so assets read as hand-finished rather than machine-smooth:
    trim, subtle paper grain inside the art, and a tiny warm colour grade."""
    rng = random.Random(seed)
    img = img.convert("RGBA")
    bbox = img.getchannel("A").getbbox()
    if bbox:
        img = img.crop(bbox)
    grain = Image.effect_noise(img.size, 18).convert("L").filter(ImageFilter.GaussianBlur(0.6))
    r, g, b, a = img.split()
    r, g, b = (Image.blend(c, grain, 0.04) for c in (r, g, b))
    warm = 1.0 + rng.uniform(0.01, 0.03)
    r = r.point(lambda v: min(255, int(v * warm)))
    return Image.merge("RGBA", (r, g, b, a))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="")
    ap.add_argument("--model", default="gpt-image-2")
    ap.add_argument("--process", action="store_true")
    args = ap.parse_args()
    spec = json.load(open(os.path.join(HERE, "prompts.json")))
    os.makedirs(RAW, exist_ok=True)
    os.makedirs(FINAL, exist_ok=True)
    jobs = [(k, f"{v} {spec['style']}", "1024x1024", True) for k, v in spec["symbols"].items()]
    for k, v in spec["backgrounds"].items():
        transparent = k == "logo_plate"
        jobs.append((k, v, "1536x1024", transparent))
    only = set(filter(None, args.only.split(",")))
    for i, (key, prompt, size, transparent) in enumerate(jobs):
        if only and key not in only:
            continue
        raw_path = os.path.join(RAW, f"{key}.png")
        if args.process:
            if not os.path.exists(raw_path):
                print("missing", raw_path)
                continue
        else:
            print("generating", key)
            data = generate(prompt, size, args.model, transparent)
            with open(raw_path, "wb") as f:
                f.write(data)
        print("processing", key)
        img = humanise(Image.open(raw_path), seed=i)
        if key in spec["symbols"]:
            img.thumbnail((300, 300), Image.LANCZOS)
        img.save(os.path.join(FINAL, f"{key}.webp"), quality=90)


if __name__ == "__main__":
    main()
