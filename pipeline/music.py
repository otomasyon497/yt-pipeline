"""Procedural background music per chapter (generator: tools/music_lab.py, numpy only).

Each chapter gets a bed in its mood (calm / curious / tension) that overlaps the next one by CROSSFADE
seconds; music_lab's master already fades every bed in and out, so the overlaps play as crossfades.
No samples are used, so there are no licence terms and nothing for Content ID to match.
"""
import importlib.util
import sys
from functools import lru_cache
from pathlib import Path

import numpy as np
import soundfile as sf

from config import ROOT

CROSSFADE = 2.0  # seconds two chapter beds overlap
BED_UNDER_VOICE_DB = 10.0  # bed loudness below the narration (sidechain ducking takes ~9 dB more while speaking)


@lru_cache(maxsize=1)
def _lab():
    spec = importlib.util.spec_from_file_location("music_lab", ROOT / "tools" / "music_lab.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod  # dataclasses look the module up while the file executes
    spec.loader.exec_module(mod)
    return mod


def build(chapters: list[tuple[float, str]], total_sec: float, out_wav: Path, seed: int) -> None:
    """chapters: (start second, mood) in order. Writes one stereo 48 kHz bed for the whole video."""
    lab = _lab()
    sr = lab.SR
    track = np.zeros((2, int(total_sec * sr) + 1))
    for i, (start, mood) in enumerate(chapters):
        end = chapters[i + 1][0] if i + 1 < len(chapters) else total_sec
        a, b = max(0.0, start - CROSSFADE / 2), min(total_sec, end + CROSSFADE / 2)
        if b - a < 4.0:
            continue
        bed = lab.render(mood, b - a, seed + i)
        i0 = int(a * sr)
        n = min(bed.shape[1], track.shape[1] - i0)
        track[:, i0:i0 + n] += bed[:, :n]
        print(f"  music: chapter {i + 1} '{mood}' {b - a:.1f}s")
    peak = np.max(np.abs(track))
    if peak > 0.95:
        track *= 0.95 / peak
    sf.write(out_wav, track.T.astype(np.float32), sr, subtype="PCM_16")


LIBRARY = ROOT / "music" / "library"  # <mood>/*.ogg|flac|wav: beds made with tools/music_gen.py (ACE-Step 1.5, MIT)
LIB_EXT = {".ogg", ".flac", ".wav"}


def _load_bed(path: Path, sr: int) -> np.ndarray:
    """A library track as (2, n) float at `sr`, peak-normalised to 0.9."""
    y, r = sf.read(path, always_2d=True)
    y = y.T.astype(np.float64)
    if y.shape[0] == 1:
        y = np.vstack([y, y])
    if r != sr:
        import soxr
        y = soxr.resample(y.T, r, sr).T
    return y * (0.9 / (np.max(np.abs(y)) + 1e-12))


def build_library(chapters: list[tuple[float, str]], total_sec: float, out_wav: Path, seed: int, sr: int = 48000) -> None:
    """Like build(), from music/library/<mood>/ tracks instead of the procedural beds (script.music = "library").

    Each chapter takes the next track of its mood (episodes start at a slug-dependent offset, so neighbours differ),
    looped with 3-s crossfades when the chapter is longer than the track, faded in and out at the chapter edges.
    """
    track = np.zeros((2, int(total_sec * sr) + 1))
    used: dict[str, int] = {}
    for i, (start, mood) in enumerate(chapters):
        files = sorted(p for p in (LIBRARY / mood).glob("*") if p.suffix.lower() in LIB_EXT)
        if not files:
            raise RuntimeError(f"music library has no '{mood}' tracks ({LIBRARY / mood})")
        k = used.get(mood, 0)
        used[mood] = k + 1
        path = files[(seed + k) % len(files)]
        end = chapters[i + 1][0] if i + 1 < len(chapters) else total_sec
        a, b = max(0.0, start - CROSSFADE / 2), min(total_sec, end + CROSSFADE / 2)
        n = int((b - a) * sr)
        if n < 4 * sr:
            continue
        src = _load_bed(path, sr)
        xf = int(3.0 * sr)
        bed = src.copy()
        while bed.shape[1] < n:  # loop with an equal-power crossfade
            ramp = np.linspace(0, 1, xf)
            tail = bed[:, -xf:] * np.cos(ramp * np.pi / 2) + src[:, :xf] * np.sin(ramp * np.pi / 2)
            bed = np.concatenate([bed[:, :-xf], tail, src[:, xf:]], axis=1)
        bed = bed[:, :n]
        fade = int(min(CROSSFADE, (b - a) / 4) * sr)
        env = np.ones(n)
        env[:fade] = np.linspace(0, 1, fade)
        env[-fade:] = np.linspace(1, 0, fade)
        i0 = int(a * sr)
        m = min(n, track.shape[1] - i0)
        track[:, i0:i0 + m] += (bed * env)[:, :m]
        print(f"  music: chapter {i + 1} '{mood}' {b - a:.1f}s <- library/{mood}/{path.name}")
    peak = np.max(np.abs(track))
    if peak > 0.95:
        track *= 0.95 / peak
    sf.write(out_wav, track.T.astype(np.float32), sr, subtype="PCM_16")
