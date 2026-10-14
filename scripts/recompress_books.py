"""Recompress published books with stronger zstd settings (same data, ~2.5x smaller upload).

Window stays at 2^27 (the default decoder limit), so any standard zstd reader can open them.
Verifies the decompressed bytes match the original before replacing a file.
Usage: python scripts/recompress_books.py dist/math
"""
import hashlib
import os
import sys

import zstandard

CHUNK = 1 << 24


def digest(path):
    h = hashlib.sha256()
    with open(path, "rb") as f, zstandard.ZstdDecompressor().stream_reader(f) as r:
        while chunk := r.read(CHUNK):
            h.update(chunk)
    return h.hexdigest()


def recompress(path):
    params = zstandard.ZstdCompressionParameters.from_level(19, window_log=27, enable_ldm=True, threads=-1)
    tmp = path + ".tmp"
    with open(path, "rb") as src, zstandard.ZstdDecompressor().stream_reader(src) as r, open(tmp, "wb") as dst:
        with zstandard.ZstdCompressor(compression_params=params).stream_writer(dst, closefd=False) as w:
            while chunk := r.read(CHUNK):
                w.write(chunk)
    if digest(tmp) != digest(path):
        os.remove(tmp)
        raise SystemExit(f"{path}: recompressed data differs, kept original")
    before, after = os.path.getsize(path), os.path.getsize(tmp)
    os.replace(tmp, path)
    print(f"{os.path.basename(path)}: {before / 1e6:.1f} MB -> {after / 1e6:.1f} MB")


for name in sorted(os.listdir(sys.argv[1])):
    if name.endswith(".jsonl.zst"):
        recompress(os.path.join(sys.argv[1], name))
