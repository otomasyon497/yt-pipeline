"""Checks an episode on the PC before anything is rendered: length, wipes, picture holds and photo quality.

    python tools/episode_check.py neom-the-line          # a script.json
    python tools/episode_check.py --words 1650           # an outline's word budget -> estimated minutes

Timings are estimated from the word count (no TTS on the PC): every word takes SEC_PER_WORD, plus the pipeline's own
pauses. Calibrated on neom-the-line (estimate within a few seconds of the rendered 10:10). prepare on GitHub Actions
repeats the length and wipe checks on the real narration and stops the render when they fail.
Exit code 1 when anything must change before rendering.
"""
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "pipeline"))

from config import FPS, LONG_MAX_SEC, LONG_MIN_SEC, WIPE_CLEAR_SEC, WORDS_PER_SEC  # noqa: E402
from schema import load_script, words_of  # noqa: E402
import timeline as tl  # noqa: E402

SEC_PER_WORD = 0.425  # speaking time per word at the episode pace (pauses come from timeline.layout)
HOLD_LIMIT = 6.5  # seconds without a new picture (stricter than prepare's 8 s note)
REPEAT_GAP = 60.0  # seconds before the same photo or map view may come back
PHOTO_MAX_USES = 3  # times one photo may appear in an episode
VIEW_MAX_USES = 4  # times one map view may appear in an episode
STAT_MIN_SEC = 2.5  # a stat card shorter than this is a flash: the label never becomes readable


def fake_timings(script):
    durations, words = [], []
    for ch in script.chapters:
        d_ch, w_ch = [], []
        for p in ch.paragraphs:
            ws = words_of(p.text)
            w_ch.append([{"t": w, "s": i * SEC_PER_WORD, "e": (i + 1) * SEC_PER_WORD} for i, w in enumerate(ws)])
            d_ch.append(len(ws) * SEC_PER_WORD)
        durations.append(d_ch)
        words.append(w_ch)
    return durations, words


def holds(script) -> list[str]:
    out = []
    for ci, ch in enumerate(script.chapters, 1):
        for pi, p in enumerate(ch.paragraphs, 1):
            n = len(words_of(p.text))
            marks = set(p.anchor_indices())
            for idxs in p.step_indices():
                marks |= set(idxs)
            if p.ask_index() is not None:
                marks.add(p.ask_index())
            m = sorted(marks) + [n]
            for a, b in zip(m, m[1:]):
                sec = (b - a) * SEC_PER_WORD
                if sec > HOLD_LIMIT:
                    out.append(f"c{ci:02d}p{pi:02d} words {a}-{b}: {sec:.1f}s on one picture")
    return out


def _picture_keys(shot) -> list[tuple]:
    """What a shot puts on screen, as comparable keys: the photo file, or each map step's camera."""
    if shot.type == "photo" and shot.photo:
        return [("photo", shot.photo)]
    if shot.type == "map" and shot.map:
        keys = []
        for st in shot.map.steps:
            if st.view:
                keys.append(("view", round(st.view.lon, 2), round(st.view.lat, 2), round(st.view.span, 2)))
            elif st.focus:
                keys.append(("focus", tuple(sorted(str(f) for f in st.focus))))
        return keys
    return []


def repeats(lay: dict) -> list[str]:
    """Photos and map views that come back too often or too soon, pictures held too long across shots, and stat
    cards too short to read. Ep 10-11 audits: one photo 8 times, five photos cycling 8-12 times each, the same map
    crop back within a minute, the same view held 10-23 s over several shots, a 1.5-s stat card."""
    out, last_seen, count = [], {}, {}
    shots = [s for s in lay["shots"] if s["src"] is not None]
    for s in shots:
        name = s["src"].photo or "map view"
        for key in _picture_keys(s["src"]):
            t = s["start"]
            count[key] = count.get(key, 0) + 1
            if key in last_seen and last_seen[key][1] != s["id"] and t - last_seen[key][0] < REPEAT_GAP:
                what = name if key[0] == "photo" else f"map view {key[1:]}"
                out.append(f"{s['id']}: {what} again after {t - last_seen[key][0]:.0f}s (shown in {last_seen[key][1]}; "
                           f"keep {REPEAT_GAP:.0f}s between repeats)")
            last_seen[key] = (t, s["id"])
    for key, n in count.items():
        limit = PHOTO_MAX_USES if key[0] == "photo" else VIEW_MAX_USES
        if n > limit:
            out.append(f"{key[1] if key[0] == 'photo' else 'map view ' + str(key[1:])} used {n} times (max {limit})")
    # One picture across consecutive shots: a photo followed by the same photo, or a map shot whose first camera is
    # the previous map shot's last one, is still the same picture on screen.
    run_start, prev_last = 0.0, None
    for i, s in enumerate(shots):
        keys = _picture_keys(s["src"])
        end = shots[i + 1]["start"] if i + 1 < len(shots) else lay["total_frames"] / FPS
        if not keys or keys[0] != prev_last:
            run_start = s["start"]  # a new picture
        if len(keys) > 1:  # the last camera of a multi-step map starts at its own step
            run_start = s["steps"][-1] if s["steps"] else s["start"]
        if keys and i + 1 < len(shots) and _picture_keys(shots[i + 1]["src"])[:1] == keys[-1:]:
            pass  # the next shot continues this picture: judge the run where it ends
        elif keys and end - run_start > HOLD_LIMIT + 1.5:
            out.append(f"{s['id']}: the same picture for {end - run_start:.1f}s across shots (vary the view or cut away)")
        prev_last = keys[-1] if keys else None
        if s["src"].type == "stat" and end - s["start"] < STAT_MIN_SEC:
            out.append(f"{s['id']}: stat card on screen {end - s['start']:.1f}s (min {STAT_MIN_SEC}s to read it)")
    return out


def compares(script) -> list[str]:
    """Landsat before/after pairs: seasons must match (a summer 'before' against a winter 'after' shows a colour
    change, not the coast), and mid-latitude winter scenes render dormant marsh maroon (ep 11, 'March 2026')."""
    out = []
    for ci, ch in enumerate(script.chapters, 1):
        for pi, p in enumerate(ch.paragraphs, 1):
            for k, sh in enumerate(p.shots, 1):
                if sh.type != "map" or not sh.map:
                    continue
                for st in sh.map.steps:
                    c = st.compare
                    if not c or c.source == "modis":
                        continue
                    months = [int(d.split("/")[0][5:7]) for d in (c.before, c.after)]
                    gap = abs(months[0] - months[1])
                    if min(gap, 12 - gap) > 2:
                        out.append(f"c{ci:02d}p{pi:02d}s{k:02d}: compare {c.before} vs {c.after}: seasons differ "
                                   f"by {min(gap, 12 - gap)} months (keep within 2)")
                    if c.source == "landsat" and abs(st.view.lat) > 25:
                        winter = {11, 12, 1, 2, 3} if st.view.lat > 0 else {5, 6, 7, 8, 9}
                        for d, m in zip((c.before, c.after), months):
                            if m in winter:
                                out.append(f"c{ci:02d}p{pi:02d}s{k:02d}: Landsat {d} is a winter scene "
                                           f"(dormant vegetation turns maroon); pick a growing-season day")
    return out


def photos(script) -> list[str]:
    import commons
    import nasa_media
    from PIL import Image
    out, seen = [], set()
    for ch in script.chapters:
        for p in ch.paragraphs:
            for s in p.shots:
                if s.type != "photo" or s.photo in seen:
                    continue
                seen.add(s.photo)
                try:
                    path, _ = (nasa_media.fetch if s.photo.lower().startswith("nasa:") else commons.fetch)(s.photo)
                    q = commons.check_quality(Image.open(path).convert("RGB"), s.photo)
                    hazy = " (hazy: levels will be stretched)" if q["contrast"] < commons.HAZY else ""
                    print(f"  photo ok: {s.photo[:60]} detail {q['detail']:.2f}{hazy}")
                except Exception as exc:  # report every photo, not just the first failure
                    out.append(str(exc))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("slug", nargs="?")
    ap.add_argument("--words", type=int, help="estimate the length of an outline's word budget")
    ap.add_argument("--no-photos", action="store_true", help="skip downloading photos for the quality check")
    a = ap.parse_args()
    lo, hi = LONG_MIN_SEC / 60, LONG_MAX_SEC / 60
    if a.words:
        minutes = a.words / WORDS_PER_SEC / 60
        need_lo, need_hi = round(LONG_MIN_SEC * WORDS_PER_SEC, -1), round(LONG_MAX_SEC * WORDS_PER_SEC, -1)
        ok = lo <= minutes <= hi
        print(f"{a.words} words -> about {minutes:.1f} min. 15-20 min needs {need_lo:.0f}-{need_hi:.0f} words: "
              f"{'OK' if ok else 'CHANGE THE BUDGET'}")
        sys.exit(0 if ok else 1)
    if not a.slug:
        ap.error("give an episode slug or --words N")
    script = load_script(ROOT / "episodes" / a.slug / "script.json")
    problems = []
    n_words = sum(len(words_of(p.text)) for ch in script.chapters for p in ch.paragraphs)
    durations, words = fake_timings(script)
    lay = tl.layout(script, durations, words)
    minutes = lay["total_frames"] / FPS / 60
    print(f"{a.slug}: {n_words} words, {len(script.chapters)} chapters -> about {minutes:.1f} min")
    if script.format == "long" and not lo <= minutes <= hi:
        msg = f"length {minutes:.1f} min is outside {lo:.0f}-{hi:.0f} min ({n_words} words; aim for " \
              f"{LONG_MIN_SEC * WORDS_PER_SEC:.0f}-{LONG_MAX_SEC * WORDS_PER_SEC:.0f})"
        (print("  legacy episode, not enforced: " + msg) if script.legacy_length else problems.append(msg))
    wipes = tl.wipe_problems(lay, WIPE_CLEAR_SEC)
    if script.legacy_length:
        for w in wipes:
            print("  legacy episode, not enforced: " + w)
    else:
        problems += wipes
    problems += holds(script)
    problems += repeats(lay)
    problems += compares(script)
    if not a.no_photos:
        problems += photos(script)
    for pr in problems:
        print("  FIX: " + pr)
    print("OK, ready to render" if not problems else f"{len(problems)} thing(s) to fix before rendering")
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
