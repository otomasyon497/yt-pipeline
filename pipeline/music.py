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
