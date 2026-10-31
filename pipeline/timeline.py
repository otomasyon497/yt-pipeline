"""Frame-accurate long-form timeline: chapters -> paragraphs (narration) -> shots cut on anchor words.

All timing comes from the narration audio (paragraph durations + word timestamps).
"""
import numpy as np
import soundfile as sf

from config import (CARD_SEC, CHAPTER_PAUSE, CUT_LEAD, END_PAD, FPS, HEIGHT, LEAD_IN, MIN_SHOT, PARA_PAUSE,
                    TRANSITION_FRAMES, TTS_SAMPLE_RATE, WIDTH)

# Deterministic Ken Burns variations: (zoom_from, zoom_to, pan_x_from, pan_x_to, pan_y_from, pan_y_to) in % of frame.
_KB = [
    (1.00, 1.14, 0, -2, 0, -1),
    (1.14, 1.00, -2, 2, -1, 1),
    (1.02, 1.12, 2, -2, 1, -1),
    (1.12, 1.02, -2, 0, 1, 0),
]


def layout(script, durations: list[list[float]], words: list[list[list[dict]]]) -> dict:
    """durations[c][p]: narration seconds; words[c][p]: aligned words ({t, s, e} in paragraph seconds).

    Returns shots (with `src` = the script Shot, None for chapter cards), paragraphs, words and chapters,
    all positioned in seconds and frames.
    """
    t, last_end = 0.0, 0.0
    shots, paras, all_words, chapters = [], [], [], []
    for ci, ch in enumerate(script.chapters):
        chapters.append({"title": ch.title, "mood": ch.mood, "start": t})
        if script.has_card(ci):
            shots.append({"id": f"c{ci + 1:02d}card", "src": None, "kind": "chapter_card",
                          "title": ch.title, "chapter": ci + 1, "start": t})
            t += CARD_SEC
        elif ci == 0:
            t += LEAD_IN
        for pi, para in enumerate(ch.paragraphs):
            start, ws = t, words[ci][pi]
            paras.append({"start": start, "chapter": ci})
            p_index = len(paras) - 1
            all_words += [{"text": w["t"], "s": start + w["s"], "e": start + w["e"], "p": p_index} for w in ws]
            for k, (shot, idx) in enumerate(zip(para.shots, para.anchor_indices())):
                shots.append({"id": f"c{ci + 1:02d}p{pi + 1:02d}s{k + 1:02d}", "src": shot, "kind": shot.type,
                              "start": start + ws[idx]["s"] - CUT_LEAD})
            last_end = start + durations[ci][pi]
            t = last_end + PARA_PAUSE
        t += CHAPTER_PAUSE

    shots.sort(key=lambda s: s["start"])
    shots[0]["start"] = 0.0
    for prev, cur in zip(shots, shots[1:]):
        if cur["start"] < prev["start"] + MIN_SHOT:
            print(f"  note: {cur['id']} moved {prev['start'] + MIN_SHOT - cur['start']:.2f}s later (min shot {MIN_SHOT}s)")
            cur["start"] = prev["start"] + MIN_SHOT

    total_frames = round((last_end + END_PAD) * FPS)
    for s in shots:
        s["startFrame"] = round(s["start"] * FPS)
    for i, s in enumerate(shots):
        last = i + 1 == len(shots)
        s["frames"] = max(1, (total_frames if last else shots[i + 1]["startFrame"]) - s["startFrame"])
        s["drawFrames"] = s["frames"] + (0 if last else TRANSITION_FRAMES)  # overlap for the next dissolve
        if s["frames"] > 12 * FPS:
            print(f"  note: {s['id']} stays on screen {s['frames'] / FPS:.1f}s (consider another cut)")
    return {"shots": shots, "paragraphs": paras, "words": all_words, "chapters": chapters, "total_frames": total_frames}


def to_timeline(lay: dict, script, media: dict) -> dict:
    """JSON props for the Remotion `Episode` composition."""
    shots = []
    for i, s in enumerate(lay["shots"]):
        src, kb = s["src"], _KB[i % len(_KB)]
        shots.append({
            "id": s["id"],
            "visual": s["kind"],
            "startFrame": s["startFrame"],
            "durationFrames": s["drawFrames"],
            "media": media.get(s["id"]),
            "onScreenText": s["title"] if src is None else src.on_screen_text,
            "subtitle": None if src is None else src.subtitle,
            "chart": src.chart.model_dump() if src is not None and src.chart else None,
            "map": src.map.model_dump() if src is not None and src.map else None,
            "quote": None if src is None else src.quote,
            "author": None if src is None else src.author,
            "kenBurns": {"z0": kb[0], "z1": kb[1], "x0": kb[2], "x1": kb[3], "y0": kb[4], "y1": kb[5]},
            "chapterNumber": s.get("chapter"),
        })
    words = []
    for w in lay["words"]:
        start = round(w["s"] * FPS)
        words.append({"text": w["text"], "start": start, "end": max(round(w["e"] * FPS), start + 1), "p": w["p"]})
    return {
        "fps": FPS, "width": WIDTH, "height": HEIGHT,
        "totalFrames": lay["total_frames"], "transitionFrames": TRANSITION_FRAMES,
        "showCaptions": script.captions,
        "shots": shots,
        "words": words,
        "chapters": [{"title": c["title"], "startFrame": round(c["start"] * FPS), "mood": c["mood"]} for c in lay["chapters"]],
    }


def build_narration_track(wavs: list, lay: dict, out_wav) -> float:
    """Place every paragraph's narration at its start time on one continuous mono track."""
    total_sec = lay["total_frames"] / FPS
    track = np.zeros(int(total_sec * TTS_SAMPLE_RATE) + 1, dtype=np.float32)
    for wav, para in zip(wavs, lay["paragraphs"]):
        data, sr = sf.read(wav, dtype="float32")
        assert sr == TTS_SAMPLE_RATE
        start = int(round(para["start"] * sr))
        end = min(len(track), start + len(data))
        track[start:end] += data[: end - start]
    sf.write(out_wav, track, TTS_SAMPLE_RATE, subtype="PCM_16")
    return total_sec
