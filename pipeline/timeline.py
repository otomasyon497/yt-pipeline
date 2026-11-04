"""Frame-accurate long-form timeline: chapters -> paragraphs (narration) -> shots cut on anchor words.

All timing comes from the narration audio (paragraph durations + word timestamps). Consecutive map shots are
grouped into one map block ("unit") so the camera flies continuously from one paragraph to the next.
"""
import re

import numpy as np
import soundfile as sf

from config import (CARD_SEC, CARD_TRANSITION_FRAMES, CHAPTER_PAUSE, CUT_LEAD, END_PAD, FPS, HEIGHT, LEAD_IN,
                    MIN_SHOT, PARA_PAUSE, SHORT, TRANSITION_FRAMES, TTS_SAMPLE_RATE, UI_SCALE, WIDTH)

# Deterministic Ken Burns variations: (zoom_from, zoom_to, pan_x_from, pan_x_to, pan_y_from, pan_y_to) in % of frame.
_KB = [
    (1.00, 1.14, 0, -2, 0, -1),
    (1.14, 1.00, -2, 2, -1, 1),
    (1.02, 1.12, 2, -2, 1, -1),
    (1.12, 1.02, -2, 0, 1, 0),
]
TEXT_DELAY = 6  # frames after the transition before an on-screen label slides in
# Seconds without a cut, a map step or a question card before prepare warns. Similar channels change the picture in
# 89-98 % of 10-s steps, ours did in 71-83 % (docs/channel-analysis-2026-11.md), so the bar is 8 s (was 12).
LONG_HOLD = 8.0

_NUM = re.compile(r"^(?P<pre>.*?)(?P<cur>[$€£]?)(?P<num>\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+(?:\.\d+)?)(?P<post>.*)$")
_UNIT = re.compile(r"^\s?(%|percent|per cent|billion|million|trillion|thousand|bn|km|kilomet|mile|metre|meter|m\b|"
                   r"tons?|tonnes?|ships?|people|times|x\b)", re.IGNORECASE)


def count_up(text: str | None, any_unit: bool = False) -> dict | None:
    """Animate a number in an on-screen label ("About $9.6 billion" counts up), but never a bare year.

    Labels count only with a currency or a known unit after the number; a stat card (`any_unit`) counts any
    number except a year on its own ("1963").
    """
    if not text:
        return None
    m = _NUM.match(text)
    if not m:
        return None
    num, cur, post = m["num"], m["cur"], m["post"]
    value = float(num.replace(",", ""))
    if any_unit:
        year = not cur and "," not in num and value.is_integer() and 1000 <= value <= 2100
        if year and not post.strip(" .,;:!?"):  # "1963", "since 1963": a year, not an amount
            return None
    elif not cur and not _UNIT.match(post):
        return None
    if value <= 0:
        return None
    decimals = len(num.split(".")[1]) if "." in num else 0
    return {"prefix": m["pre"] + cur, "value": value, "decimals": decimals, "commas": "," in num, "suffix": post}


def layout(script, durations: list[list[float]], words: list[list[list[dict]]]) -> dict:
    """durations[c][p]: narration seconds; words[c][p]: aligned words ({t, s, e} in paragraph seconds).

    Returns shots (with `src` = the script Shot, None for chapter cards), units (what is drawn: single shots or
    map blocks), paragraphs, words and chapters, all positioned in seconds and frames.
    """
    t, last_end = 0.0, 0.0
    shots, paras, all_words, chapters, asks = [], [], [], [], []
    for ci, ch in enumerate(script.chapters):
        chapters.append({"title": ch.title, "mood": ch.mood, "start": t})
        if script.has_card(ci):
            shots.append({"id": f"c{ci + 1:02d}card", "src": None, "kind": "chapter_card",
                          "title": ch.title, "chapter": ci + 1, "start": t, "steps": []})
            t += CARD_SEC
        elif ci == 0:
            t += LEAD_IN
        for pi, para in enumerate(ch.paragraphs):
            start, ws = t, words[ci][pi]
            paras.append({"start": start, "chapter": ci})
            p_index = len(paras) - 1
            all_words += [{"text": w["t"], "s": start + w["s"], "e": start + w["e"], "p": p_index} for w in ws]
            step_idx = para.step_indices()
            for k, (shot, idx) in enumerate(zip(para.shots, para.anchor_indices())):
                shots.append({"id": f"c{ci + 1:02d}p{pi + 1:02d}s{k + 1:02d}", "src": shot, "kind": shot.type,
                              "start": start + ws[idx]["s"] - CUT_LEAD,
                              "steps": [start + ws[j]["s"] - CUT_LEAD for j in step_idx[k]]})
            if para.ask is not None:
                asks.append({"t": start + ws[para.ask_index()]["s"], "end": start + durations[ci][pi] + 1.2,
                             "text": para.ask.text})
            last_end = start + durations[ci][pi]
            t = last_end + PARA_PAUSE
        t += CHAPTER_PAUSE

    shots.sort(key=lambda s: s["start"])
    shots[0]["start"] = 0.0
    for prev, cur in zip(shots, shots[1:]):
        if cur["start"] < prev["start"] + MIN_SHOT:
            print(f"  note: {cur['id']} moved {prev['start'] + MIN_SHOT - cur['start']:.2f}s later (min shot {MIN_SHOT}s)")
            cur["start"] = prev["start"] + MIN_SHOT
    for s in shots:
        s["steps"] = [max(x, s["start"]) for x in s["steps"]]

    total_frames = round((last_end + END_PAD) * FPS)
    for s in shots:
        s["startFrame"] = round(s["start"] * FPS)
    for i, s in enumerate(shots):
        s["frames"] = max(1, (total_frames if i + 1 == len(shots) else shots[i + 1]["startFrame"]) - s["startFrame"])
    units = group_units(shots, total_frames, [round(a["t"] * FPS) for a in asks])
    return {"shots": shots, "units": units, "paragraphs": paras, "words": all_words, "chapters": chapters,
            "total_frames": total_frames, "asks": asks}


def group_units(shots: list[dict], total_frames: int, beats: list[int] | None = None) -> list[dict]:
    """Consecutive map shots -> one map block (a new block starts on `globe`). Adds transitions and draw lengths.

    `beats`: extra frames where the picture changes inside a unit (question cards), for the hold check.
    """
    units: list[dict] = []
    for s in shots:
        if s["kind"] == "map" and units and units[-1]["kind"] == "map" and not s["src"].map.globe:
            units[-1]["subs"].append(s)
            continue
        units.append({"id": ("m" + s["id"]) if s["kind"] == "map" else s["id"], "kind": s["kind"], "subs": [s],
                      "startFrame": s["startFrame"]})
    for i, u in enumerate(units):
        u["frames"] = (units[i + 1]["startFrame"] if i + 1 < len(units) else total_frames) - u["startFrame"]
        u["transitionIn"] = 0 if i == 0 else CARD_TRANSITION_FRAMES if u["kind"] == "chapter_card" else TRANSITION_FRAMES
    long_holds = 0
    for i, u in enumerate(units):
        u["drawFrames"] = u["frames"] + (units[i + 1]["transitionIn"] if i + 1 < len(units) else 0)
        # Longest stretch without a cut, a map step or a question card.
        end = u["startFrame"] + u["frames"]
        marks = sorted({u["startFrame"]} | {round(x * FPS) for s in u["subs"] for x in s["steps"]} |
                       {s["startFrame"] for s in u["subs"]} | {b for b in beats or [] if u["startFrame"] < b < end}) + [end]
        hold = max(b - a for a, b in zip(marks, marks[1:])) / FPS
        if hold > LONG_HOLD:
            long_holds += 1
            print(f"  note: {u['id']} holds {hold:.1f}s without a cut, map step or question (add a beat by {LONG_HOLD:.0f}s)")
    if long_holds:
        print(f"  note: {long_holds} unit(s) hold one picture longer than {LONG_HOLD:.0f}s")
    return units


def to_timeline(lay: dict, script, media: dict, map_style: str, photo_fit: dict | None = None,
                locs: dict | None = None, card_bg: dict | None = None, docs: dict | None = None) -> dict:
    """JSON props for the Remotion `Episode` composition."""
    shots = []
    for i, u in enumerate(lay["units"]):
        first = u["subs"][0]
        src, kb = first["src"], _KB[i % len(_KB)]
        texts = []
        for s in u["subs"]:
            text = s["src"].on_screen_text if s["src"] is not None and s["kind"] in ("stock", "film", "ai_image", "photo", "map") else None
            if text:
                offset = s["startFrame"] - u["startFrame"]
                if SHORT and i == 0 and offset == 0:  # a Short's hook line is on screen from the very first frame
                    texts.append({"text": text, "from": 0, "countUp": None, "instant": True})
                    continue
                texts.append({"text": text, "from": offset + (u["transitionIn"] if offset == 0 else 0) + TEXT_DELAY,
                              "countUp": count_up(text)})
        for a in lay.get("asks", []):
            f = round(a["t"] * FPS)
            if u["startFrame"] <= f < u["startFrame"] + u["frames"]:
                texts.append({"text": a["text"], "from": f - u["startFrame"], "countUp": None, "kind": "question",
                              "hold": max(48, round(a["end"] * FPS) - f)})
        texts.sort(key=lambda x: x["from"])
        shots.append({
            "id": u["id"],
            "visual": u["kind"],
            "startFrame": u["startFrame"],
            "durationFrames": u["drawFrames"],
            "transitionIn": u["transitionIn"],
            "media": media.get(u["id"]),
            "texts": texts,
            "onScreenText": first["title"] if src is None else src.on_screen_text,
            "subtitle": None if src is None else src.subtitle,
            "chart": ({**src.chart.model_dump(), "reveal": [round(x * FPS) - u["startFrame"] for x in first["steps"]]}
                      if src is not None and src.chart else None),
            "stat": ({**src.stat.model_dump(), "countUp": count_up(src.stat.value, any_unit=True)}
                     if src is not None and src.stat else None),
            "document": (docs or {}).get(u["id"]),
            "quote": None if src is None else src.quote,
            "author": None if src is None else src.author,
            "kenBurns": {"z0": kb[0], "z1": kb[1], "x0": kb[2], "x1": kb[3], "y0": kb[4], "y1": kb[5]},
            "chapterNumber": first.get("chapter"),
            "photoFit": (photo_fit or {}).get(u["id"]),
            "where": (locs or {}).get(u["id"]),
            "cardBg": (card_bg or {}).get(u["id"]),
        })
    words = []
    for w in lay["words"]:
        start = round(w["s"] * FPS)
        words.append({"text": w["text"], "start": start, "end": max(round(w["e"] * FPS), start + 1), "p": w["p"]})
    return {
        "fps": FPS, "width": WIDTH, "height": HEIGHT, "uiScale": UI_SCALE,
        "totalFrames": lay["total_frames"],
        "showCaptions": script.captions,
        "mapStyle": map_style,
        "look": getattr(script, "look", "none"),
        "shots": shots,
        "words": words,
        "chapters": [{"title": c["title"], "startFrame": round(c["start"] * FPS), "mood": c["mood"]} for c in lay["chapters"]],
    }


def card_sfx(timeline: dict) -> list[tuple[float, str, float]]:
    """Sound effects for cards and counting numbers (map effects come from maps.build_block)."""
    events = []
    for s in timeline["shots"]:
        t = s["startFrame"] / FPS
        if s["visual"] == "chapter_card":
            events += [(max(0.0, t - 0.3), "whoosh", -2.0), (t + 0.05, "hit", 0.0)]
        elif s["visual"] == "title_card":
            events.append((t + 0.1, "hit", -3.0))
        elif s["visual"] == "document":  # the page slides in, the marker sweeps once the camera has closed in
            events += [(t + 0.05, "whoosh", -6.0), (t + 2.1, "swoosh", -6.0)]
        elif s["visual"] == "stat":
            events.append((t + 0.15, "hit", -3.0))
            if s["stat"] and s["stat"]["countUp"]:
                events.append((t + 0.45, "ticks", 0.0))
        elif s["visual"] == "chart" and s["chart"]:  # each item revealed with the narration grows with a soft pop
            events += [(t + f / FPS + 0.1, "pop", -6.0) for f in s["chart"]["reveal"]]
        for text in s["texts"]:
            if text.get("kind") == "question":
                events.append(((s["startFrame"] + text["from"]) / FPS, "pop", -1.0))
            if text["countUp"]:
                events.append(((s["startFrame"] + text["from"]) / FPS + 0.3, "ticks", 0.0))
    return events


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
