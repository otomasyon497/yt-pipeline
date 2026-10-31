"""Build the frame-accurate timeline consumed by Remotion (all timing comes from the narration audio)."""
import math

import numpy as np
import soundfile as sf

from config import END_PAD_FRAMES, FPS, HEIGHT, TAIL_FRAMES, TRANSITION_FRAMES, TTS_SAMPLE_RATE, WIDTH

# Deterministic Ken Burns variations: (zoom_from, zoom_to, pan_x_from, pan_x_to, pan_y_from, pan_y_to) in % of frame.
_KB = [
    (1.00, 1.14, 0, -2, 0, -1),
    (1.14, 1.00, -2, 2, -1, 1),
    (1.02, 1.12, 2, -2, 1, -1),
    (1.12, 1.02, -2, 0, 1, 0),
]


def build(scenes, durations: list[float], words: list[list[dict]], media: list[str | None]) -> dict:
    """scenes: validated Scene objects; durations: narration seconds; words: aligned word timings (seconds)."""
    items, cursor = [], 0
    for i, sc in enumerate(scenes):
        narr_frames = math.ceil(durations[i] * FPS)
        base = TRANSITION_FRAMES + narr_frames + TAIL_FRAMES + (END_PAD_FRAMES if i == len(scenes) - 1 else 0)
        draw = base + (TRANSITION_FRAMES if i < len(scenes) - 1 else 0)  # overlap with next scene's dissolve
        kb = _KB[i % len(_KB)]
        items.append({
            "id": sc.id,
            "visual": sc.visual,
            "startFrame": cursor,
            "durationFrames": draw,
            "narrationStartFrame": cursor + TRANSITION_FRAMES,
            "media": media[i],
            "onScreenText": sc.on_screen_text,
            "subtitle": sc.subtitle,
            "chart": sc.chart.model_dump() if sc.chart else None,
            "map": sc.map.model_dump() if sc.map else None,
            "quote": sc.quote,
            "author": sc.author,
            "showCaptions": sc.captions,
            "kenBurns": {"z0": kb[0], "z1": kb[1], "x0": kb[2], "x1": kb[3], "y0": kb[4], "y1": kb[5]},
            # Frames are relative to the scene's own Sequence (which starts at startFrame).
            "words": [
                {"text": w["t"], "start": TRANSITION_FRAMES + round(w["s"] * FPS), "end": TRANSITION_FRAMES + max(round(w["e"] * FPS), round(w["s"] * FPS) + 1)}
                for w in words[i]
            ],
        })
        cursor += base
    return {"fps": FPS, "width": WIDTH, "height": HEIGHT, "totalFrames": cursor, "transitionFrames": TRANSITION_FRAMES, "scenes": items}


def build_narration_track(wavs: list, timeline: dict, out_wav) -> float:
    """Place each scene's narration at its narrationStartFrame on one continuous mono track."""
    total_sec = timeline["totalFrames"] / FPS
    track = np.zeros(int(total_sec * TTS_SAMPLE_RATE) + 1, dtype=np.float32)
    for wav, sc in zip(wavs, timeline["scenes"]):
        data, sr = sf.read(wav, dtype="float32")
        assert sr == TTS_SAMPLE_RATE
        start = int(sc["narrationStartFrame"] / FPS * sr)
        track[start:start + len(data)] += data[: len(track) - start]
    sf.write(out_wav, track, TTS_SAMPLE_RATE, subtype="PCM_16")
    return total_sec
