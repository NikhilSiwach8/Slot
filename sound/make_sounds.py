"""Synthesize every Dumpster Duke sound (original, no samples) into one audio sprite.

Writes web-sdk/apps/dumpster-duke/static/assets/audio/sounds.{ogg,m4a,mp3} and
sounds.json (Howler sprite format, same sound names the game already uses).
Usage: python sound/make_sounds.py        (needs numpy and ffmpeg)
"""
import json
import os
import subprocess
import tempfile
import wave

import numpy as np

SR = 44100
RNG = np.random.default_rng(7)
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "web-sdk", "apps", "dumpster-duke",
                   "static", "assets", "audio")


# ---------------------------------------------------------------- building blocks
def t(sec):
    return np.arange(int(sec * SR)) / SR


def env(n, a=0.005, d=0.1, s=0.0, r=0.05, sustain_time=None):
    """ADSR envelope of length n samples."""
    a_n, d_n, r_n = int(a * SR), int(d * SR), int(r * SR)
    s_n = max(0, n - a_n - d_n - r_n) if sustain_time is None else int(sustain_time * SR)
    e = np.concatenate([np.linspace(0, 1, a_n, endpoint=False), np.linspace(1, s, d_n, endpoint=False),
                        np.full(s_n, s), np.linspace(s, 0, r_n)])
    return np.pad(e, (0, max(0, n - len(e))))[:n]


def exp_decay(n, tau):
    return np.exp(-np.arange(n) / (tau * SR))


def sine(freq, sec, phase=0.0):
    f = np.broadcast_to(np.asarray(freq, dtype=float), (int(sec * SR),))
    return np.sin(2 * np.pi * np.cumsum(f) / SR + phase)


def saw(freq, sec):
    f = np.broadcast_to(np.asarray(freq, dtype=float), (int(sec * SR),))
    ph = np.cumsum(f) / SR
    return 2 * (ph - np.floor(ph + 0.5))


def square(freq, sec, duty=0.5):
    f = np.broadcast_to(np.asarray(freq, dtype=float), (int(sec * SR),))
    ph = (np.cumsum(f) / SR) % 1
    return np.where(ph < duty, 1.0, -1.0)


def noise(sec):
    return RNG.uniform(-1, 1, int(sec * SR))


def lowpass(x, cutoff):
    """One-pole low-pass; cutoff may be an array (sweeps)."""
    c = np.broadcast_to(np.asarray(cutoff, dtype=float), x.shape)
    alpha = 1 - np.exp(-2 * np.pi * c / SR)
    y = np.empty_like(x)
    acc = 0.0
    for i in range(len(x)):
        acc += alpha[i] * (x[i] - acc)
        y[i] = acc
    return y


def highpass(x, cutoff):
    return x - lowpass(x, cutoff)


def bandpass(x, lo, hi):
    return highpass(lowpass(x, hi), lo)


def fm_bell(freq, sec, ratio=3.5, index=4.0, tau=0.35):
    n = int(sec * SR)
    tt = np.arange(n) / SR
    mod_env = exp_decay(n, tau * 0.6)
    return np.sin(2 * np.pi * freq * tt + index * mod_env * np.sin(2 * np.pi * freq * ratio * tt)) * exp_decay(n, tau)


def pluck(freq, sec, tau=0.18, bright=3000):
    n = int(sec * SR)
    tone = saw(freq, sec) * 0.6 + square(freq, sec, 0.3) * 0.25
    return lowpass(tone, bright * exp_decay(n, tau) + 200) * exp_decay(n, tau)


def kick(sec=0.35):
    n = int(sec * SR)
    f = 50 + 110 * exp_decay(n, 0.04)
    return sine(f, sec) * exp_decay(n, 0.12)


def snare(sec=0.25):
    n = int(sec * SR)
    return (bandpass(noise(sec), 900, 6000) * 0.8 + sine(190, sec) * 0.4) * exp_decay(n, 0.07)


def hat(sec=0.08):
    n = int(sec * SR)
    return highpass(noise(sec), 6000) * exp_decay(n, 0.02)


def place(dst, src, at, gain=1.0):
    i = int(at * SR)
    if i >= len(dst):
        return dst
    end = min(len(dst), i + len(src))
    dst[i:end] += src[: end - i] * gain
    return dst


def silence(sec):
    return np.zeros(int(sec * SR))


def echo(x, delay=0.18, feedback=0.35, mix=0.35, tail=0.6):
    out = np.concatenate([x, np.zeros(int(tail * SR))])
    d = int(delay * SR)
    wet = np.zeros_like(out)
    wet[: len(x)] = x
    for i in range(d, len(out)):
        wet[i] += wet[i - d] * feedback
    return out * (1 - mix) + wet * mix


def norm(x, peak=0.8):
    m = np.max(np.abs(x)) or 1
    return x / m * peak


def midi(n):
    return 440 * 2 ** ((n - 69) / 12)


# A minor pentatonic-ish palette (playful, a bit mischievous)
SCALE = [57, 60, 62, 64, 67, 69, 72, 74, 76, 79, 81]


# ---------------------------------------------------------------- music
def groove(bpm, bars, bass_line, melody, bright=False, arp=False):
    beat = 60 / bpm
    total = bars * 4 * beat
    out = silence(total + 0.01)
    for b in range(bars * 4):
        at = b * beat
        place(out, kick(), at, 0.9 if b % 2 == 0 else 0.55)
        if b % 4 in (1, 3):
            place(out, snare(), at, 0.45)
        for half in (0, 0.5):
            place(out, hat(), at + half * beat, 0.22 if half else 0.14)
        note = bass_line[b % len(bass_line)]
        place(out, pluck(midi(note - 24), beat * 0.9, tau=0.16, bright=900), at, 0.55)
        if arp:
            for k, step in enumerate((0, 7, 12, 7)):
                place(out, fm_bell(midi(note + step), 0.25, ratio=2, index=1.5, tau=0.12), at + k * beat / 4, 0.12)
    for i, (beat_at, note, length) in enumerate(melody):
        place(out, fm_bell(midi(note), length * beat + 0.4, ratio=3.01 if bright else 4.0, index=2.5, tau=0.25 + length * 0.08),
              beat_at * beat, 0.32)
    # seamless loop: fold the tail back onto the start
    loop_n = int(total * SR)
    tail = out[loop_n:]
    out = out[:loop_n]
    out[: len(tail)] += tail
    return norm(out, 0.62)


def melody_line(bars, seed, density=0.55, low=0, high=9):
    rng = np.random.default_rng(seed)
    notes = []
    pos = 0.0
    idx = 4
    while pos < bars * 4:
        length = rng.choice([0.5, 0.5, 1, 1, 1.5, 2])
        if rng.random() < density:
            idx = int(np.clip(idx + rng.choice([-2, -1, -1, 1, 1, 2]), low, high))
            notes.append((pos, SCALE[idx], length))
        pos += length
    return notes


# Base-game music: "Silly Intro" by Alexander Nakarada (serpentsoundstudios.com), CC BY 4.0,
# taken from sound/source/. Falls back to the synthesized groove if the file is missing.
BGM_MAIN_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "source", "bgm_main_silly_intro.mp3")


def load_track(path, level=0.85):
    """Decode a music file to stereo float32 and make it loop cleanly: trim the near-silent
    head and tail, add short fades so the loop point never clicks, and set its peak."""
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", path, "-f", "s16le", "-ac", "2", "-ar", str(SR), "-"],
                         check=True, capture_output=True).stdout
    x = np.frombuffer(raw, dtype=np.int16).reshape(-1, 2).astype(np.float32) / 32768
    loud = np.sqrt(np.convolve((x ** 2).mean(axis=1), np.ones(441) / 441, mode="same")) > 0.004
    first, last = int(np.argmax(loud)), len(loud) - int(np.argmax(loud[::-1]))
    x = x[max(0, first - 220): min(len(x), last + 2205)]
    fade = int(0.03 * SR)
    ramp = np.linspace(0, 1, fade)[:, None]
    x[:fade] *= ramp
    x[-fade:] *= ramp[::-1]
    return x / np.abs(x).max() * level


# Recorded sound effects supplied for the game (sound/source/): bonus start, tumble
# collect and the spin-win sound. Trimmed to their audible part and levelled.
SOURCE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "source")
RECORDED_SFX = {
    # sprite name: (file, peak level, max seconds)
    "jng_intro_fs": ("sfx_bonus_start.mp3", 0.85, 1.2),
    "sfx_tumble_collect": ("sfx_tumble_collect.wav", 0.75, 1.4),
    "sfx_win": ("sfx_win.mp3", 0.8, 3.2),
}


def load_sfx(file, level, max_sec):
    x = load_track(os.path.join(SOURCE, file), level)
    if len(x) > max_sec * SR:
        x = x[: int(max_sec * SR)]
        fade = int(0.25 * SR)
        x[-fade:] *= np.linspace(1, 0, fade)[:, None]
    return x


def bgm_main():
    if os.path.exists(BGM_MAIN_FILE):
        return load_track(BGM_MAIN_FILE)
    bass = [45, 45, 48, 48, 50, 50, 43, 43]
    return groove(104, 16, bass, melody_line(16, 3, 0.5))


def bgm_freespin():
    bass = [45, 52, 50, 48, 45, 52, 55, 53]
    return groove(126, 16, bass, melody_line(16, 11, 0.65, 3, 10), bright=True, arp=True)


def bgm_win(tier):
    bpm = 120 + tier * 6
    beat = 60 / bpm
    total = 8.0
    out = silence(total + 1)
    roots = [57, 60, 62, 64, 65][tier] if tier < 5 else 57
    chord = [0, 4, 7, 12]
    for b in range(int(total / beat)):
        at = b * beat
        place(out, kick(), at, 0.7)
        place(out, hat(), at + beat / 2, 0.25)
        if b % 2 == 0:
            for c in chord:
                place(out, fm_bell(midi(roots + c + 12 * (b % 4 == 0)), beat * 2, ratio=2.0, index=2, tau=0.35), at, 0.16)
        for k in range(2 + tier):
            place(out, fm_bell(midi(roots + 24 + chord[(b + k) % 4]), 0.2, ratio=3.5, index=1, tau=0.08),
                  at + k * beat / (2 + tier), 0.08)
    loop_n = int(total * SR)
    tail = out[loop_n:]
    out = out[:loop_n]
    out[: len(tail)] += tail
    return norm(out, 0.62)


# ---------------------------------------------------------------- effects
def click():
    x = highpass(noise(0.06), 2000) * exp_decay(int(0.06 * SR), 0.006) + sine(1800, 0.06) * exp_decay(int(0.06 * SR), 0.01) * 0.6
    return norm(x, 0.6)


def spin_button():
    n = int(0.6 * SR)
    sweep = lowpass(noise(0.6), np.linspace(300, 5000, n)) * np.sin(np.linspace(0, np.pi, n)) * 0.8
    clunk = place(silence(0.6), kick(0.3) * 0.7 + bandpass(noise(0.3), 300, 1500) * exp_decay(int(0.3 * SR), 0.03), 0.0)
    return norm(sweep + clunk, 0.75)


def reel_stop(variant):
    sec = 0.25
    n = int(sec * SR)
    thud = sine(70 + variant * 6 + 60 * exp_decay(n, 0.02), sec) * exp_decay(n, 0.07)
    knock = bandpass(noise(sec), 400 + variant * 80, 2500) * exp_decay(n, 0.02) * 0.6
    tick = sine(2400 + variant * 120, sec) * exp_decay(n, 0.006) * 0.2
    return norm(thud + knock + tick, 0.8)


def cap_ting(pitch=0):
    return norm(fm_bell(midi(84 + pitch), 0.9, ratio=5.1, index=3, tau=0.18) + click() [:1] * 0, 0.7)


def crate_clang(step):
    base = midi(64 + step * 3)
    x = fm_bell(base, 1.0, ratio=1.41, index=5, tau=0.3) * 0.7 + fm_bell(base * 2, 1.0, ratio=2.76, index=2, tau=0.2) * 0.3
    x[: int(0.25 * SR)] += kick(0.25) * 0.5
    return norm(echo(x, 0.12, 0.25, 0.2, 0.3), 0.8)


def arpeggio(notes, step, tau=0.3, ratio=3.5, gain=0.4, tail=0.8):
    out = silence(len(notes) * step + tail)
    for i, n in enumerate(notes):
        place(out, fm_bell(midi(n), tail + 0.2, ratio=ratio, index=2.5, tau=tau), i * step, gain)
    return out


def shimmer(sec, gain=0.15):
    out = silence(sec)
    for k in range(int(sec * 14)):
        place(out, fm_bell(midi(int(RNG.choice([88, 91, 93, 96, 98, 100]))), 0.4, ratio=4.2, index=1, tau=0.07),
              RNG.uniform(0, sec - 0.3), gain)
    return out


def riser(sec, start=200, end=1600):
    n = int(sec * SR)
    f = np.geomspace(start, end, n)
    tone = (saw(f, sec) * 0.3 + saw(f * 1.01, sec) * 0.3)
    swell = lowpass(noise(sec), np.geomspace(400, 8000, n)) * 0.4
    return (lowpass(tone, f * 3) + swell) * np.linspace(0.05, 1, n) ** 2


def boom(sec=1.2, crackle=True):
    n = int(sec * SR)
    x = sine(40 + 90 * exp_decay(n, 0.05), sec) * exp_decay(n, 0.35)
    x += lowpass(noise(sec), 1200 * exp_decay(n, 0.2) + 100) * exp_decay(n, 0.25) * 0.8
    if crackle:
        x += shimmer(sec, 0.1)
    return norm(x, 0.85)


def coin_loop(sec=8.0):
    out = silence(sec + 0.6)
    for _ in range(int(sec * 9)):
        place(out, fm_bell(midi(int(RNG.choice([86, 88, 91, 93, 95]))), 0.35, ratio=5.6, index=2, tau=0.06),
              RNG.uniform(0, sec), 0.25)
    loop_n = int(sec * SR)
    tail = out[loop_n:]
    out = out[:loop_n]
    out[: len(tail)] += tail
    return norm(out, 0.6)


def jingle(notes, step, chord_at_end=True, gain=0.5):
    out = arpeggio(notes, step, tau=0.25, gain=gain, tail=1.2)
    if chord_at_end:
        end = len(notes) * step
        for c in (0, 4, 7, 12):
            place(out, fm_bell(midi(notes[-1] - 12 + c), 1.4, ratio=2, index=2, tau=0.5), end, 0.18)
    return norm(echo(out, 0.16, 0.3, 0.25, 0.6), 0.8)


def tumble_pop(step):
    sec = 0.6
    n = int(sec * SR)
    pop = sine(300 + step * 80 + 500 * exp_decay(n, 0.02), sec) * exp_decay(n, 0.05) * 0.6
    return norm(pop + fm_bell(midi(76 + step * 2), sec, ratio=3, index=2, tau=0.15) * 0.6, 0.75)


def whoosh(sec=1.0, up=True):
    n = int(sec * SR)
    cut = np.geomspace(300, 6000, n) if up else np.geomspace(6000, 300, n)
    return norm(lowpass(noise(sec), cut) * np.sin(np.linspace(0, np.pi, n)) ** 1.5, 0.7)


def anticipation_loop(sec=7.5):
    n = int(sec * SR)
    f = 110 * (1 + 0.5 * np.arange(n) / n)
    trem = 0.6 + 0.4 * np.sin(2 * np.pi * 8 * np.arange(n) / SR)
    x = lowpass(saw(f, sec) + saw(f * 1.5, sec) * 0.5, 1200) * trem * 0.6 + shimmer(sec, 0.06)
    fade = np.minimum(1, np.minimum(np.arange(n), n - np.arange(n)) / (0.05 * SR))
    return norm(x * fade, 0.6)


def build():
    sounds = {}
    sounds["bgm_main"] = (bgm_main(), True)
    sounds["bgm_freespin"] = (bgm_freespin(), True)
    for tier, name in enumerate(["big", "superwin", "mega", "epic", "max"]):
        sounds[f"bgm_winlevel_{name}"] = (bgm_win(tier), True)
    sounds["jng_intro_fs"] = (jingle([69, 72, 76, 79, 81], 0.12), False)
    sounds["sfx_anticipation"] = (anticipation_loop(), False)
    sounds["sfx_anticipation_start"] = (norm(riser(1.0), 0.6), False)
    sounds["sfx_bigwin_coinloop"] = (coin_loop(), True)
    sounds["sfx_btn_general"] = (click(), False)
    sounds["sfx_btn_spin"] = (spin_button(), False)
    sounds["sfx_fs_respins"] = (jingle([72, 76, 79, 84, 88], 0.14), False)
    sounds["sfx_multiplier_combine_a"] = (whoosh(1.0, True), False)
    sounds["sfx_multiplier_combine_b"] = (whoosh(0.9, False), False)
    sounds["sfx_multiplier_explosion_a"] = (boom(0.8), False)
    sounds["sfx_multiplier_explosion_b"] = (boom(1.8), False)
    sounds["sfx_multiplier_explosion_c"] = (boom(1.2, False), False)
    sounds["sfx_multiplier_landing"] = (cap_ting(0), False)
    sounds["sfx_multiplier_reset"] = (norm(arpeggio([79, 74, 69], 0.08, tau=0.12, gain=0.5, tail=0.3), 0.6), False)
    sounds["sfx_multiplier_up"] = (norm(arpeggio([72, 76, 79, 84], 0.07, gain=0.5, tail=0.6), 0.7), False)
    sounds["sfx_multiplier_update"] = (norm(arpeggio([79, 84, 88, 91], 0.06, ratio=5.1, gain=0.5, tail=0.8), 0.75), False)
    x = arpeggio([69, 76, 81, 84, 88], 0.09, gain=0.45, tail=2.5)
    sounds["sfx_multiplier_win"] = (norm(echo(x + place(silence(len(x) / SR), shimmer(3.0), 0.3), 0.2, 0.3, 0.25, 0.3), 0.8), False)
    for i in range(1, 6):
        sounds[f"sfx_reel_stop_{i}"] = (reel_stop(i), False)
        sounds[f"sfx_scatter_stop_{i}"] = (crate_clang(i), False)
        sounds[f"tumble_win_{i}"] = (tumble_pop(i), False)
    sounds["sfx_royals_landing"] = (norm(reel_stop(2) * 0.6 + cap_ting(-12)[: len(reel_stop(2))] * 0.2, 0.6), False)
    sounds["sfx_scatter_reveal"] = (norm(shimmer(1.5, 0.3) + whoosh(1.5) * 0.4, 0.7), False)
    sounds["sfx_scatter_win"] = (jingle([64, 67, 71, 76], 0.15), False)
    sounds["sfx_scatter_win_v2"] = (norm(jingle([64, 67, 71, 76, 79, 83], 0.13) , 0.8), False)
    x = norm(riser(2.5, 120, 1200), 0.6)
    x = np.concatenate([x, jingle([69, 72, 76, 81, 84], 0.11)])
    sounds["sfx_superfreespin"] = (norm(x, 0.8), False)
    sounds["sfx_symbols_landing"] = (norm(reel_stop(1) * 0.5, 0.5), False)
    sounds["sfx_wild_explode"] = (boom(1.3), False)
    sounds["sfx_winlevel_small"] = (jingle([76, 79], 0.1, False, 0.5), False)
    sounds["sfx_winlevel_standard"] = (jingle([72, 76, 79], 0.1, False, 0.5), False)
    sounds["sfx_winlevel_nice"] = (jingle([72, 76, 79, 84], 0.1), False)
    sounds["sfx_winlevel_substantial"] = (jingle([69, 72, 76, 79, 84, 88], 0.11), False)
    sounds["sfx_winlevel_end"] = (jingle([84, 79, 84, 88], 0.13), False)
    sounds["sfx_youwon_panel"] = (norm(jingle([67, 72, 76, 79, 84, 88, 91], 0.12) + 0, 0.85), False)
    for name, (file, level, max_sec) in RECORDED_SFX.items():
        if os.path.exists(os.path.join(SOURCE, file)):
            sounds[name] = (load_sfx(file, level, max_sec), False)
    return sounds


# the recorded base-game track is mastered louder than the synth tracks
BGM_VOLUME = {"bgm_main": 0.5}


def main():
    sounds = build()
    gap = 1.0
    sprite, chunks, cursor = {}, [], 0.0
    for name in sorted(sounds):
        data, loop = sounds[name]
        data = np.clip(data, -1, 1)
        if data.ndim == 1:  # synthesized sounds are mono; music files keep their stereo
            data = np.stack([data, data], axis=1)
        start = cursor
        length_ms = len(data) / SR * 1000
        sprite[name] = [round(start * 1000), length_ms, True] if loop else [round(start * 1000), length_ms]
        padded = np.concatenate([data, np.zeros((int(gap * SR), 2))])
        chunks.append(padded)
        cursor += len(padded) / SR
    stereo = np.concatenate(chunks)
    os.makedirs(OUT, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        wav_path = os.path.join(tmp, "sounds.wav")
        with wave.open(wav_path, "wb") as w:
            w.setnchannels(2)
            w.setsampwidth(2)
            w.setframerate(SR)
            w.writeframes((stereo * 32767).astype(np.int16).tobytes())
        for ext, args in {"ogg": ["-c:a", "libvorbis", "-q:a", "4"], "m4a": ["-c:a", "aac", "-b:a", "128k"],
                          "mp3": ["-c:a", "libmp3lame", "-b:a", "128k"]}.items():
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", wav_path, *args, os.path.join(OUT, f"sounds.{ext}")],
                           check=True)
    for stale in ("sounds.ac3",):
        path = os.path.join(OUT, stale)
        if os.path.exists(path):
            os.remove(path)
    manifest = {
        "sprite": sprite,
        "src": ["./assets/audio/sounds.ogg", "./assets/audio/sounds.m4a", "./assets/audio/sounds.mp3"],
        "config": {name: {"volume": BGM_VOLUME.get(name, 0.55) if name.startswith("bgm_") else 1} for name in sprite},
    }
    with open(os.path.join(OUT, "sounds.json"), "w") as f:
        json.dump(manifest, f, indent="\t")
    print(f"{len(sprite)} sounds, {cursor:.0f}s sprite")


if __name__ == "__main__":
    main()
