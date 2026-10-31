"""Procedural documentary background music - prototype ("music lab").

Every sound is synthesised from scratch with numpy: wavetable pads, Karplus-Strong plucks, FM bells,
noise ticks, synthetic low booms and a synthetic convolution reverb. No samples or third-party
recordings are used, so the output carries no licence terms and cannot match a Content ID reference.

  python tools/music_lab.py --out DIR [--mood calm|curious|tension|all] [--seconds 75] [--seed 7]
                            [--narration narration.wav]

Writes NN_<mood>.wav (48 kHz stereo), an analysis PNG per track (spectrogram + loudness curve),
report.json, and with --narration a demo of the calm bed ducked under the voice.
"""
from __future__ import annotations

import argparse
import json
import math
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import soundfile as sf

SR = 48000
TAU = 2.0 * np.pi

SCALES = {
    "aeolian": [0, 2, 3, 5, 7, 8, 10],
    "major": [0, 2, 4, 5, 7, 9, 11],
    "harmonic_minor": [0, 2, 3, 5, 7, 8, 11],
}


def midi_hz(m: float) -> float:
    return 440.0 * 2.0 ** ((m - 69.0) / 12.0)


@dataclass
class Mood:
    scale: str
    key: int  # MIDI note of the tonic in the bass register
    bpm: float
    beats_per_chord: int
    chords: list  # (scale degree, degree offsets); (0, [0, 2, 4, 8]) = tonic triad + 9th
    gains: dict  # layer -> linear gain
    brightness: float  # pad brightness 0..1 (crossfade dark -> bright wavetable)
    wet: float  # reverb return level
    bell_prob: float = 0.0  # chance of a bell note on each beat


MOODS = {
    # A minor: Am(add9) - Fmaj7 - C(add9) - Gsus2, slow and spacious.
    "calm": Mood("aeolian", 45, 66, 8,
                 [(0, [0, 2, 4, 8]), (5, [0, 2, 4, 6]), (2, [0, 2, 4, 8]), (6, [0, 1, 4])],
                 {"pad": 1.0, "sub": 0.32, "bells": 0.45}, 0.5, 0.42, bell_prob=0.38),
    # D major: D(add9) - Gmaj7 - Bm7 - Asus2 with a rolling plucked arpeggio.
    "curious": Mood("major", 38, 100, 8,
                    [(0, [0, 2, 4, 8]), (3, [0, 2, 4, 6]), (5, [0, 2, 4, 6]), (4, [0, 1, 4])],
                    {"pad": 0.6, "sub": 0.3, "pluck": 0.8, "bells": 0.16}, 0.62, 0.30, bell_prob=0.12),
    # D harmonic minor: D5(add9) - Dm - Bb - A, pulsing low ostinato, clock ticks, booms, risers.
    "tension": Mood("harmonic_minor", 38, 84, 8,
                    [(0, [0, 4, 8]), (0, [0, 2, 4]), (5, [0, 2, 4]), (4, [0, 2, 4])],
                    {"pad": 0.6, "sub": 0.42, "ostinato": 0.7, "ticks": 0.22, "boom": 0.5, "riser": 0.2},
                    0.32, 0.32),
}

RHYTHMIC = {"pluck", "ostinato", "ticks", "boom", "riser", "bells"}


# ---------------------------------------------------------------- music theory
def chord_semis(scale: list[int], degree: int, offsets: list[int]) -> list[int]:
    """Semitones above the key tonic for each chord tone (offsets are scale steps above `degree`)."""
    return [scale[(degree + o) % 7] + 12 * ((degree + o) // 7) for o in offsets]


def stack_voicing(key: int, semis: list[int], low: int = 53, high: int = 64, min_gap: int = 3) -> list[int]:
    """Open voicing: chord root placed in [low, high], each next tone at least `min_gap` semitones above."""
    root = key + semis[0]
    while root < low:
        root += 12
    while root > high:
        root -= 12
    notes = [root]
    for s in semis[1:]:
        m = key + s
        while m < notes[-1] + min_gap:
            m += 12
        while m - 12 >= notes[-1] + min_gap:
            m -= 12
        notes.append(m)
    return notes


def bass_note(key: int, semi: int) -> int:
    m = key + semi
    while m > 47:
        m -= 12
    while m < 36:
        m += 12
    return m


def section_gain(layer: str, i: int, n: int) -> float:
    """Simple arrangement: pads from the start, rhythm layers enter later and leave before the end."""
    if layer in ("pad", "sub") or layer not in RHYTHMIC or n <= 4:
        return 1.0
    if i == 0:
        return 0.0
    if i == 1:
        return 0.6
    if i == n - 1:
        return 0.0 if layer in ("ostinato", "ticks", "boom", "riser") else 0.5
    if i == n - 2:
        return 0.7
    if n >= 8 and i == n // 2:  # short breakdown in the middle for variety
        return 0.45
    return 1.0


# ---------------------------------------------------------------- building blocks
_TABLES: dict = {}


def wavetable(n_harm: int, slope: float, seed: int) -> np.ndarray:
    """Band-limited single-cycle table (harmonics 1..n_harm, amplitude 1/k^slope), unit RMS."""
    key = (n_harm, slope, seed)
    if key not in _TABLES:
        rng = np.random.default_rng(seed)
        x = np.arange(4096) / 4096
        t = np.zeros(4096)
        for k in range(1, n_harm + 1):
            t += np.sin(TAU * k * x + rng.uniform(0, TAU)) / k ** slope
        _TABLES[key] = t / np.sqrt(np.mean(t ** 2))
    return _TABLES[key]


def phase_track(f: float, n: int, rng, vib_cents: float = 4.0) -> np.ndarray:
    t = np.arange(n) / SR
    rate = rng.uniform(0.12, 0.3)
    inst = f * 2.0 ** (vib_cents * np.sin(TAU * rate * t + rng.uniform(0, TAU)) / 1200.0)
    return rng.uniform() + np.cumsum(inst) / SR


def lookup(table: np.ndarray, phase: np.ndarray) -> np.ndarray:
    pos = (phase % 1.0) * len(table)
    i0 = pos.astype(np.int64)
    frac = pos - i0
    return table[i0] + frac * (table[(i0 + 1) % len(table)] - table[i0])


def raised_cos(n: int) -> np.ndarray:
    return 0.5 - 0.5 * np.cos(np.pi * np.arange(n) / max(n, 1))


def env_asr(n: int, attack: float, sustain: float, release: float) -> np.ndarray:
    t = np.arange(n) / SR
    e = np.ones(n)
    a = t < attack
    e[a] = 0.5 - 0.5 * np.cos(np.pi * t[a] / attack)
    r = t > sustain
    e[r] = np.cos(0.5 * np.pi * np.clip((t[r] - sustain) / release, 0, 1))
    return e


def fade_tail(sig: np.ndarray, seconds: float = 0.03) -> np.ndarray:
    k = min(len(sig), int(seconds * SR))
    sig[-k:] *= np.linspace(1.0, 0.0, k)
    return sig


def smoothstep(x, a, b):
    t = np.clip((x - a) / (b - a), 0.0, 1.0)
    return t * t * (3 - 2 * t)


def band_noise(n: int, lo: float, hi: float, rng) -> np.ndarray:
    spec = np.fft.rfft(rng.standard_normal(n))
    f = np.fft.rfftfreq(n, 1 / SR)
    return np.fft.irfft(spec * ((f >= lo) & (f < hi)), n)


def place(dry, send, sig, start_s, pan=0.0, gain=1.0, send_amt=0.5):
    s0 = int(round(max(start_s, 0.0) * SR))
    n = min(len(sig), dry.shape[1] - s0)
    if n <= 0 or gain <= 0:
        return
    left, right = math.cos((pan + 1) * math.pi / 4), math.sin((pan + 1) * math.pi / 4)
    seg = sig[:n] * gain
    dry[0, s0:s0 + n] += seg * left
    dry[1, s0:s0 + n] += seg * right
    if send_amt:
        send[0, s0:s0 + n] += seg * left * send_amt
        send[1, s0:s0 + n] += seg * right * send_amt


# ---------------------------------------------------------------- instruments
def pad_chord(dry, send, start, dur, notes, mood, gain, rng):
    release = 2.8
    s0 = int(start * SR)
    n = min(int((dur + release) * SR), dry.shape[1] - s0)
    if n <= 0:
        return
    env = env_asr(n, attack=min(2.2, dur * 0.35), sustain=dur, release=release)
    tt = (s0 + np.arange(n)) / SR
    bright = np.clip(mood.brightness + 0.18 * np.sin(TAU * tt / 27.0), 0.0, 1.0)  # slow timbre drift
    for m in notes:
        f = midi_hz(m)
        dark_t = wavetable(max(1, min(8, int(6000 / f))), 1.8, seed=1)
        bright_t = wavetable(max(1, min(40, int(12000 / f))), 1.0, seed=2)
        level = gain / math.sqrt(len(notes)) * 0.5 ** max(0.0, (m - 64) / 12) / math.sqrt(3)
        for cents, pan in ((-7.0, -0.55), (0.0, 0.0), (7.0, 0.55)):
            ph = phase_track(f * 2.0 ** ((cents + rng.normal(0, 1.5)) / 1200.0), n, rng)
            sig = (lookup(dark_t, ph) * (1 - bright) + lookup(bright_t, ph) * bright) * env
            place(dry, send, sig, start, pan, level, send_amt=0.6)


def sub_note(dry, send, start, dur, m, gain):
    n = int((dur + 1.5) * SR)
    t = np.arange(n) / SR
    f = midi_hz(m)
    sig = (np.sin(TAU * f * t) + 0.25 * np.sin(TAU * 2 * f * t)) * env_asr(n, 0.8, dur, 1.5)
    place(dry, send, sig, start, 0.0, gain, send_amt=0.0)


def bell(f: float, dur: float = 3.2) -> np.ndarray:
    """Soft celesta-like tone: harmonic FM body (1:1) plus a short inharmonic strike (1:3.5)."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    body = np.sin(TAU * f * t + (1.2 * np.exp(-t / 0.5) + 0.08) * np.sin(TAU * f * t)) * np.exp(-t / 1.6)
    strike = np.sin(TAU * f * t + 1.5 * np.exp(-t / 0.08) * np.sin(TAU * 3.5 * f * t)) * np.exp(-t / 0.3)
    sig = (0.78 * body + 0.22 * strike) * (1 - np.exp(-t / 0.004))
    return fade_tail(sig, 0.05)


def ks_pluck(f: float, dur: float, t60: float, rng, soft: int = 2) -> np.ndarray:
    """Karplus-Strong plucked string, computed one period per numpy step."""
    N = max(2, int(round(SR / f - 0.5)))
    total = int(dur * SR)
    g = 10 ** (-3.0 / (f * t60))
    y = np.zeros(total + N + 1)
    exc = rng.uniform(-1, 1, N)
    if soft > 1:
        exc = np.convolve(exc, np.ones(soft) / soft, mode="same")
    y[1:N + 1] = exc - exc.mean()
    s = N + 1
    while s < len(y):
        e = min(s + N, len(y))
        k = e - s
        y[s:e] = g * 0.5 * (y[s - N:s - N + k] + y[s - N - 1:s - N - 1 + k])
        s = e
    out = fade_tail(y[1:total + 1].copy(), 0.03)
    return out / (np.max(np.abs(out)) + 1e-9)


def pulse_note(f: float, dur: float, rng) -> np.ndarray:
    n = int(dur * SR)
    t = np.arange(n) / SR
    table = wavetable(max(1, min(10, int(5000 / f))), 1.5, seed=3)
    sig = lookup(table, phase_track(f, n, rng, vib_cents=2.0))
    sig *= (1 - np.exp(-t / 0.004)) * np.exp(-t / 0.11)
    return fade_tail(sig, 0.02)


def tick(rng) -> np.ndarray:
    n = int(0.03 * SR)
    t = np.arange(n) / SR
    sig = band_noise(n, 2500, 9000, rng) * (1 - np.exp(-t / 0.0005)) * np.exp(-t / 0.004)
    return sig / (np.max(np.abs(sig)) + 1e-9)


def boom(rng) -> np.ndarray:
    n = int(2.4 * SR)
    t = np.arange(n) / SR
    f = 36 + 34 * np.exp(-t / 0.09)
    body = np.sin(TAU * np.cumsum(f) / SR) * (1 - np.exp(-t / 0.003)) * np.exp(-t / 0.65)
    thump = band_noise(n, 20, 180, rng) * np.exp(-t / 0.03)
    sig = body + 0.3 * thump / (np.max(np.abs(thump)) + 1e-9)
    return fade_tail(sig / (np.max(np.abs(sig)) + 1e-9), 0.05)


def riser(dur: float, rng) -> np.ndarray:
    n = int(dur * SR)
    x = np.arange(n) / n
    sig = (band_noise(n, 200, 1500, rng) * (1 - x) + band_noise(n, 2500, 12000, rng) * x) * x ** 2.5
    return fade_tail(sig / (np.max(np.abs(sig)) + 1e-9), 0.04)


# ---------------------------------------------------------------- reverb + mastering
def make_ir(rng, seconds: float = 3.2, predelay: float = 0.018) -> np.ndarray:
    """Synthetic stereo hall: band-dependent exponential decay + a few early reflections."""
    n, pre = int(seconds * SR), int(predelay * SR)
    t = np.arange(n) / SR
    lf = np.log2(np.maximum(np.fft.rfftfreq(n, 1 / SR), 1.0))
    w_low = 1 - smoothstep(lf, math.log2(300), math.log2(900))
    w_high = smoothstep(lf, math.log2(3000), math.log2(8000))
    w_mid = np.clip(1 - w_low - w_high, 0, 1)
    hp = smoothstep(lf, math.log2(120), math.log2(250))  # keep the reverb out of the low end
    ir = np.zeros((2, pre + n))
    for ch in range(2):
        spec = np.fft.rfft(rng.standard_normal(n))
        tail = sum(np.fft.irfft(spec * w * hp, n) * 10 ** (-3 * t / t60)
                   for w, t60 in ((w_low, 2.7), (w_mid, 1.9), (w_high, 1.0)))
        tail *= 1 - np.exp(-t / 0.012)
        ir[ch, pre:] = tail
        for k in range(7):
            ir[ch, pre + int(rng.uniform(0.006, 0.06) * SR)] += rng.choice([-1, 1]) * 0.5 * 0.8 ** k
        ir[ch, -int(0.05 * SR):] *= np.linspace(1, 0, int(0.05 * SR))
    return ir / math.sqrt(np.sum(ir ** 2) / 2)


def fft_convolve(x: np.ndarray, h: np.ndarray) -> np.ndarray:
    n = len(x) + len(h) - 1
    nfft = 1 << (n - 1).bit_length()
    return np.fft.irfft(np.fft.rfft(x, nfft) * np.fft.rfft(h, nfft), nfft)[:n]


def eq_curve_db(freqs: np.ndarray) -> np.ndarray:
    lf = np.log2(np.maximum(freqs, 1.0))
    g = 18.0 * np.clip(lf - math.log2(35.0), -4, 0)  # high-pass: -18 dB/oct below 35 Hz
    x = lf - math.log2(300.0)  # low-mid scoop: this is where a male narrator's voice has its body
    g += np.where(np.abs(x) < 1, -3.0 * 0.5 * (1 + np.cos(np.pi * x)), 0.0)
    x = lf - math.log2(2200.0)  # gentle dip where speech intelligibility lives
    g += np.where(np.abs(x) < 1, -2.0 * 0.5 * (1 + np.cos(np.pi * x)), 0.0)
    g += 2.5 * smoothstep(lf, math.log2(5000.0), math.log2(10000.0))  # a little air on top
    return g


def master(mix: np.ndarray, fade_in: float = 2.5, fade_out: float = 4.0, target_rms_db: float = -19.0) -> np.ndarray:
    n = mix.shape[1]
    nfft = 1 << (n - 1).bit_length()
    gain = 10 ** (eq_curve_db(np.fft.rfftfreq(nfft, 1 / SR)) / 20)
    out = np.stack([np.fft.irfft(np.fft.rfft(mix[c], nfft) * gain, nfft)[:n] for c in range(2)])
    fi, fo = int(fade_in * SR), int(fade_out * SR)
    out[:, :fi] *= raised_cos(fi)
    out[:, -fo:] *= raised_cos(fo)[::-1]
    out /= np.max(np.abs(out)) + 1e-12
    out = np.tanh(1.4 * out) / np.tanh(1.4)  # gentle glue / soft saturation
    out *= 10 ** ((target_rms_db - 20 * math.log10(np.sqrt(np.mean(out ** 2)) + 1e-12)) / 20)
    peak = np.max(np.abs(out))
    if peak > 0.891:  # -1 dBFS ceiling
        out *= 0.891 / peak
    return out


# ---------------------------------------------------------------- arrangement
def render(mood_name: str, seconds: float, seed: int) -> np.ndarray:
    mood = MOODS[mood_name]
    rng = np.random.default_rng(seed)
    total = int(seconds * SR)
    dry, send = np.zeros((2, total)), np.zeros((2, total))
    scale = SCALES[mood.scale]
    beat = 60.0 / mood.bpm
    eighth = beat / 2
    chord_len = beat * mood.beats_per_chord
    n_chords = max(2, math.ceil(seconds / chord_len))
    tick_sig, boom_sig = tick(rng), boom(rng)
    bell_idx = None

    for i in range(n_chords):
        degree, offsets = mood.chords[0] if i == n_chords - 1 else mood.chords[i % len(mood.chords)]
        semis = chord_semis(scale, degree, offsets)
        start = i * chord_len

        def G(layer: str) -> float:
            return mood.gains.get(layer, 0.0) * section_gain(layer, i, n_chords)

        if G("pad"):
            pad_chord(dry, send, start, chord_len, stack_voicing(mood.key, semis), mood, G("pad"), rng)
        if G("sub"):
            sub_note(dry, send, start, chord_len, bass_note(mood.key, semis[0]), G("sub"))
        if G("bells"):
            pcs = {s % 12 for s in semis} | {scale[(degree + 1) % 7]}
            cands = [m for m in range(69, 85) if (m - mood.key) % 12 in pcs]
            bell_idx = len(cands) // 2 if bell_idx is None else min(bell_idx, len(cands) - 1)
            for j in range(mood.beats_per_chord):
                if rng.random() < mood.bell_prob:
                    bell_idx = int(np.clip(bell_idx + rng.choice([-2, -1, -1, 0, 1, 1, 2]), 0, len(cands) - 1))
                    place(dry, send, bell(midi_hz(cands[bell_idx])), start + j * beat + rng.normal(0, 0.008),
                          rng.uniform(-0.35, 0.35), G("bells") * rng.uniform(0.55, 1.0), send_amt=0.9)
        if G("pluck"):
            arp = stack_voicing(mood.key, semis, low=60, high=69)
            pattern = [0, 2, 1, 3, 2, 1, 3, 2]
            for j in range(mood.beats_per_chord * 2):
                idx = pattern[j % 8] % len(arp)
                if j % 16 >= 14:
                    idx = len(arp) - 1 - (j % 2)
                vel = (1.0 if j % 8 == 0 else 0.8 if j % 2 == 0 else 0.62) * rng.uniform(0.92, 1.05)
                place(dry, send, ks_pluck(midi_hz(arp[idx]), 1.5, 1.1, rng), start + j * eighth + rng.normal(0, 0.005),
                      0.25 if j % 2 == 0 else -0.25, G("pluck") * vel * 0.5, send_amt=0.55)
        if G("ostinato"):
            root3 = bass_note(mood.key, semis[0]) + 12
            for j in range(mood.beats_per_chord * 2):
                m = root3 + (7 if j % 8 in (3, 6) else 0)
                place(dry, send, pulse_note(midi_hz(m), 0.34, rng), start + j * eighth, 0.0,
                      G("ostinato") * (1.0 if j % 2 == 0 else 0.72) * 0.55, send_amt=0.3)
        if G("ticks"):
            for j in range(mood.beats_per_chord * 2):
                place(dry, send, tick_sig, start + j * eighth, -0.15 if j % 2 == 0 else 0.15,
                      G("ticks") * (1.0 if j % 2 == 0 else 0.55) * 0.4, send_amt=0.35)
        if G("boom") and i % 2 == 0 and i > 0:
            place(dry, send, boom_sig, start, 0.0, G("boom"), send_amt=0.25)
        if G("riser") and i % 4 == 3 and i < n_chords - 1:
            place(dry, send, riser(chord_len, rng), start, 0.0, G("riser") * 0.5, send_amt=0.4)

    ir = make_ir(rng)
    wet = np.stack([fft_convolve(send[c], ir[c])[:total] for c in range(2)])
    return master(dry + mood.wet * wet)


# ---------------------------------------------------------------- analysis (I cannot listen, so I measure and look)
def analyse(x: np.ndarray) -> dict:
    mono = x.mean(axis=0)
    p = np.abs(np.fft.rfft(mono)) ** 2
    f = np.fft.rfftfreq(len(mono), 1 / SR)
    bands = [(20, 80), (80, 250), (250, 1000), (1000, 4000), (4000, 12000), (12000, 24000)]
    w = int(0.4 * SR)
    k = len(mono) // w
    st = 20 * np.log10(np.sqrt(np.mean(mono[:k * w].reshape(k, w) ** 2, axis=1)) + 1e-12)
    body = st[int(3 / 0.4):-int(5 / 0.4)] if k > 20 else st  # ignore the fades
    return {
        "seconds": round(x.shape[1] / SR, 1),
        "peak_dbfs": round(20 * math.log10(np.max(np.abs(x)) + 1e-12), 1),
        "rms_dbfs": round(20 * math.log10(np.sqrt(np.mean(x ** 2)) + 1e-12), 1),
        "band_energy_pct": {f"{a}-{b}Hz": round(100 * p[(f >= a) & (f < b)].sum() / p.sum(), 1) for a, b in bands},
        "stereo_correlation": round(float(np.corrcoef(x[0], x[1])[0, 1]), 2),
        "max_sample_jump": round(float(np.max(np.abs(np.diff(x, axis=1)))), 3),
        "loudness_range_db": round(float(np.percentile(body, 95) - np.percentile(body, 10)), 1),
    }


def spectrogram_png(x: np.ndarray, path: Path, title: str) -> None:
    from PIL import Image, ImageDraw

    mono = x.mean(axis=0)
    win, cols, rows, strip = 4096, 1100, 320, 90
    starts = np.linspace(0, len(mono) - win, cols).astype(int)
    hann = np.hanning(win)
    spec = np.array([np.abs(np.fft.rfft(mono[s:s + win] * hann)) for s in starts]).T
    db = 20 * np.log10(spec + 1e-9)
    freqs = np.fft.rfftfreq(win, 1 / SR)
    grid = np.geomspace(30, 16000, rows)[::-1]
    img = db[np.clip(np.searchsorted(freqs, grid), 0, len(freqs) - 1), :]
    top = np.percentile(img, 99.5)
    c = np.clip((img - (top - 75)) / 75, 0, 1)
    rgb = np.stack([np.clip(1.6 * c, 0, 1), np.clip(1.6 * c - 0.6, 0, 1), np.clip(0.35 + 0.9 * c - 1.2 * c * c, 0, 1) * (c > 0.02)], -1)
    canvas = np.zeros((rows + strip + 20, cols, 3), dtype=np.uint8)
    canvas[20:20 + rows] = (rgb * 255).astype(np.uint8)
    im = Image.fromarray(canvas)
    d = ImageDraw.Draw(im)
    d.text((4, 3), title, fill=(255, 255, 255))
    for hz, label in ((100, "100 Hz"), (1000, "1 kHz"), (10000, "10 kHz")):
        y = 20 + int(np.argmin(np.abs(grid - hz)))
        d.line([(0, y), (cols, y)], fill=(90, 90, 90))
        d.text((4, y - 12), label, fill=(200, 200, 200))
    # loudness strip (400 ms RMS), -50..0 dBFS
    w = int(0.4 * SR)
    k = len(mono) // w
    st = 20 * np.log10(np.sqrt(np.mean(mono[:k * w].reshape(k, w) ** 2, axis=1)) + 1e-12)
    pts = [(int(i * (cols - 1) / max(k - 1, 1)), 20 + rows + strip - 5 - int(np.clip((v + 50) / 50, 0, 1) * (strip - 10))) for i, v in enumerate(st)]
    d.line(pts, fill=(80, 200, 255), width=2)
    d.text((4, 20 + rows + 2), "loudness (400 ms RMS, -50..0 dBFS)", fill=(160, 160, 160))
    im.save(path)


# ---------------------------------------------------------------- narration demo
def duck_under(narration: Path, bed: np.ndarray, out_path: Path, under_db: float = 15.0, duck_db: float = 9.0) -> None:
    """Approximation of the pipeline's sidechain ducking, for listening tests only."""
    v, sr = sf.read(narration, dtype="float64", always_2d=True)
    assert sr == SR, f"narration must be {SR} Hz"
    v = v.mean(axis=1)
    n = min(len(v), bed.shape[1])
    v, m = v[:n], bed[:, :n].copy()
    hop = int(0.01 * SR)
    k = n // hop
    frames = v[:k * hop].reshape(k, hop)
    speech = 20 * np.log10(np.sqrt(np.mean(frames ** 2, axis=1)) + 1e-9) > -42
    a_att, a_rel = 1 - math.exp(-0.01 / 0.05), 1 - math.exp(-0.01 / 0.7)
    g, cur = np.zeros(k), 0.0
    for i in range(k):
        target = -duck_db if speech[i] else 0.0
        cur += (a_att if target < cur else a_rel) * (target - cur)
        g[i] = cur
    gain = 10 ** (np.interp(np.arange(n), (np.arange(k) + 0.5) * hop, g) / 20)
    voice_rms = np.sqrt(np.mean(frames[speech] ** 2))
    m *= voice_rms * 10 ** (-under_db / 20) / (np.sqrt(np.mean(m ** 2)) + 1e-12)
    out = np.stack([v, v]) + m * gain
    out *= 0.891 / (np.max(np.abs(out)) + 1e-12)
    sf.write(out_path, out.T, SR, subtype="PCM_16")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--mood", default="all", choices=["all", *MOODS])
    ap.add_argument("--seconds", type=float, default=75.0)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--narration", type=Path)
    a = ap.parse_args()
    a.out.mkdir(parents=True, exist_ok=True)
    (a.out / "_analysis").mkdir(exist_ok=True)
    report = {}
    moods = list(MOODS) if a.mood == "all" else [a.mood]
    for i, mood in enumerate(moods, 1):
        x = render(mood, a.seconds, a.seed + i)
        name = f"{i:02d}_{mood}"
        sf.write(a.out / f"{name}.wav", x.T, SR, subtype="PCM_16")
        spectrogram_png(x, a.out / "_analysis" / f"{name}.png", name)
        report[name] = analyse(x)
        print(name, json.dumps(report[name]))
    if a.narration:
        info = sf.info(a.narration)
        bed = render("calm", info.frames / info.samplerate + 0.5, a.seed + 100)
        demo = a.out / f"{len(moods) + 1:02d}_demo_calm_under_narration.wav"
        duck_under(a.narration, bed, demo)
        print("demo:", demo.name)
    (a.out / "_analysis" / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
