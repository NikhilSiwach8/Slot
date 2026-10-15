"""Pack dist/ into release/ zips that GitHub accepts (each file under 100 MB).

    python3 scripts/make_release_zips.py

release/dumpster_duke_frontend.zip   the static frontend
release/dumpster_duke_math_<i>of<n>.zip   the math files, grouped so each zip stays under
                                     LIMIT; unzip every part into one folder before uploading.
"""
import os
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIST = os.path.join(ROOT, "dist")
OUT = os.path.join(ROOT, "release")
LIMIT = 95_000_000


def main():
    os.makedirs(OUT, exist_ok=True)
    for name in os.listdir(OUT):
        if name.endswith(".zip"):
            os.remove(os.path.join(OUT, name))

    front = os.path.join(DIST, "frontend")
    with zipfile.ZipFile(os.path.join(OUT, "dumpster_duke_frontend.zip"), "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for folder, _, files in os.walk(front):
            for f in files:
                path = os.path.join(folder, f)
                z.write(path, os.path.relpath(path, front))

    math = os.path.join(DIST, "math")
    files = sorted(os.listdir(math), key=lambda f: -os.path.getsize(os.path.join(math, f)))
    groups: list[list[str]] = []
    for f in files:  # first-fit decreasing
        size = os.path.getsize(os.path.join(math, f))
        assert size < LIMIT, f"{f} alone is over the limit"
        for g in groups:
            if sum(os.path.getsize(os.path.join(math, x)) for x in g) + size < LIMIT:
                g.append(f)
                break
        else:
            groups.append([f])
    groups.sort(key=lambda g: "index.json" not in g)  # part 1 carries index.json
    for i, g in enumerate(groups, 1):
        name = f"dumpster_duke_math_{i}of{len(groups)}.zip"
        with zipfile.ZipFile(os.path.join(OUT, name), "w", zipfile.ZIP_DEFLATED, compresslevel=6) as z:
            for f in sorted(g):
                z.write(os.path.join(math, f), f)
        print(name, f"{os.path.getsize(os.path.join(OUT, name)) / 1e6:.1f} MB", sorted(g))
    print("dumpster_duke_frontend.zip", f"{os.path.getsize(os.path.join(OUT, 'dumpster_duke_frontend.zip')) / 1e6:.1f} MB")


if __name__ == "__main__":
    main()
