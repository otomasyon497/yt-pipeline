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
    if not a.no_photos:
        problems += photos(script)
    for pr in problems:
        print("  FIX: " + pr)
    print("OK, ready to render" if not problems else f"{len(problems)} thing(s) to fix before rendering")
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
