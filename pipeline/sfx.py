"""Procedural sound effects (numpy only: no samples, so no licence terms and no Content ID matches).

Kinds: whoosh (camera flights), whoosh_long (globe dive), swoosh (lines drawing), pop (markers),
thump (highlights), hit (chapter / title cards), ticks (numbers counting up).
build_track() places them on one mono track that media.mix_audio() lays under the narration.
"""
from functools import lru_cache

import numpy as np
import soundfile as sf

from config import SFX_LEVEL_DB

SR = 48000
# Peak level of each kind relative to SFX_LEVEL_DB (dB).
BASE_DB = {"whoosh": -1.0, "whoosh_long": 0.0, "swoosh": -4.0, "pop": -5.0, "thump": -2.0, "hit": 2.0, "ticks": -7.0}
MIN_GAP = {"pop": 0.12, "whoosh": 0.5, "swoosh": 0.4, "thump": 0.3, "hit": 1.0, "whoosh_long": 1.0, "ticks": 0.5}


def _band_noise(n: int, centers: np.ndarray, width_oct: float, seed: int) -> np.ndarray:
    """White noise through a moving band-pass (Gaussian in log-frequency), done in the STFT domain."""
    rng = np.random.default_rng(seed)
    size, hop = 2048, 512
    x = np.concatenate([np.zeros(size), rng.standard_normal(n), np.zeros(size)])
    win = np.hanning(size)
    freqs = np.maximum(np.fft.rfftfreq(size, 1 / SR), 1.0)
    out = np.zeros_like(x)
    for i in range(0, len(x) - size, hop):
        fc = centers[min(max(i + size // 2 - size, 0), n - 1)]
        gain = np.exp(-0.5 * (np.log2(freqs / fc) / width_oct) ** 2)
        out[i:i + size] += np.fft.irfft(np.fft.rfft(x[i:i + size] * win) * gain) * win
    return out[size:size + n]


def _sweep(n: int, points: list[tuple[float, float]]) -> np.ndarray:
    """Piecewise log-linear frequency curve through (time fraction, Hz) points."""
    t = np.linspace(0, 1, n)
    xs, ys = zip(*points)
    return np.exp(np.interp(t, xs, np.log(ys)))


def _norm(x: np.ndarray) -> np.ndarray:
    return x / (np.max(np.abs(x)) + 1e-12)


def _whoosh(seconds: float, peak: float, lo: float, hi: float, end: float, seed: int, width: float = 0.9) -> np.ndarray:
    n = int(seconds * SR)
    t = np.linspace(0, 1, n)
    centers = _sweep(n, [(0, lo), (peak, hi), (1, end)])
    env = np.where(t < peak, np.sin(0.5 * np.pi * t / peak) ** 2, np.exp(-4.5 * (t - peak) / (1 - peak)))
    return _norm(_band_noise(n, centers, width, seed) * env)


def _tone(seconds: float, f0: float, f1: float, tau: float) -> np.ndarray:
    n = int(seconds * SR)
    t = np.arange(n) / SR
    freq = f1 + (f0 - f1) * np.exp(-t / (tau * 0.6))
    phase = 2 * np.pi * np.cumsum(freq) / SR
    env = np.exp(-t / tau) * np.minimum(1.0, t / 0.002)
    return np.sin(phase) * env


@lru_cache(maxsize=None)
def sound(kind: str) -> np.ndarray:
    if kind == "whoosh":
        return _whoosh(0.85, 0.55, 260, 1900, 650, seed=1)
    if kind == "whoosh_long":
        return _whoosh(2.6, 0.72, 140, 2400, 420, seed=2, width=1.1)
    if kind == "swoosh":
        return _whoosh(1.1, 0.4, 900, 3200, 1500, seed=3, width=0.7)
    if kind == "pop":
        body = _tone(0.12, 1500, 620, 0.028)
        click = _band_noise(int(0.12 * SR), np.full(int(0.12 * SR), 4000.0), 1.0, 4) * np.exp(-np.arange(int(0.12 * SR)) / (0.002 * SR))
        return _norm(body + 0.25 * _norm(click))
    if kind == "thump":
        n = int(0.45 * SR)
        low = _tone(0.45, 120, 52, 0.11)
        air = _band_noise(n, np.full(n, 260.0), 1.0, 5) * np.exp(-np.arange(n) / (0.03 * SR))
        return _norm(low + 0.35 * _norm(air))
    if kind == "hit":
        n = int(1.8 * SR)
        boom = _tone(1.8, 70, 36, 0.42)
        crack = _band_noise(n, np.full(n, 900.0), 1.2, 6) * np.exp(-np.arange(n) / (0.025 * SR))
        tail = _band_noise(n, np.full(n, 320.0), 1.4, 7) * np.exp(-np.arange(n) / (0.55 * SR))
        return _norm(boom + 0.45 * _norm(crack) + 0.12 * _norm(tail))
    if kind == "ticks":  # a counter rolling and slowing down (0.9 s)
        n = int(0.9 * SR)
        out = np.zeros(n)
        click = _band_noise(int(0.006 * SR), np.full(int(0.006 * SR), 4200.0), 0.8, 8)
        click = _norm(click * np.exp(-np.arange(len(click)) / (0.0012 * SR)))
        t, k = 0.0, 0
        while t < 0.9 - 0.01:
            i = int(t * SR)
            seg = click[: n - i]
            out[i:i + len(seg)] += seg * (1.0 - 0.45 * t / 0.9)
            t += 1.0 / (30.0 - 22.0 * (t / 0.9))
            k += 1
        return _norm(out)
    raise ValueError(f"unknown sound effect {kind!r}")


def build_track(events: list[tuple[float, str, float]], total_sec: float, out_wav) -> int:
    """events: (seconds, kind, extra gain dB). Returns how many effects were placed."""
    track = np.zeros(int(total_sec * SR) + 1, dtype=np.float64)
    last: dict[str, float] = {}
    placed = 0
    for t, kind, gain in sorted(events):
        if t < 0 or t >= total_sec or t - last.get(kind, -1e9) < MIN_GAP.get(kind, 0.2):
            continue
        last[kind] = t
        s = sound(kind) * 10 ** ((SFX_LEVEL_DB + BASE_DB[kind] + gain) / 20)
        i = int(t * SR)
        seg = s[: len(track) - i]
        track[i:i + len(seg)] += seg
        placed += 1
    peak = np.max(np.abs(track)) if placed else 0
    if peak > 0.9:  # many overlaps: keep the bed below clipping
        track *= 0.9 / peak
    sf.write(out_wav, track.astype(np.float32), SR, subtype="PCM_16")
    return placed
