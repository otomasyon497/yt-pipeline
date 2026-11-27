"""Hook check for Ink & Orbit long videos (known-place "why" documentaries), calibrated 2026-11-27.

    python tools/hook_check.py --text "first ~75 words of narration" --place Wyoming
    python tools/hook_check.py --file hooks.txt --place Wyoming     # several hooks, one per paragraph (blank line between)
    python tools/hook_check.py --calibrate                          # re-run the calibration on youtube-transcript/

Why not the generic hookscore (.claude/skills/yt-script/hookscore.py): it was built on Shorts hooks of 9-24 words and
rewards "you" and loss words. On 19 rival long videos in our niche its score did not follow views/subscribers
(Spearman 0.06 on the first 15 s, 0.22 on the first sentence). This checker scores the things the outliers share,
and docs/script-rules.md's own retention rules:

  PLACE      the place is named in the first two sentences (the title's promise confirmed)
  SCALE      a scale anchor the viewer knows (bigger than / the size of / fewer than / a well-known place)
  TURN       a "but / yet / only / fewer / almost nobody" turn within the first ~40 words
  QUESTION   the video's question is asked out loud within the first ~75 words (about 0:30)
  ONE NUM    no sentence carries more than one number (Mongolia lost 15 points on a run of three census figures)
  NO NEWS    no agency, report or "experts say" framing in the hook (the news openings held 50-60 % at 0:45)

Each check is pass / fail; the verdict is the number passed out of six. It is a checklist of our own retention
lessons, NOT a predictor: on the same 19 rival videos the six checks averaged 3.57 on videos at 50x+ and 3.58 under
50x (calibration 2026-11-27). The hook's text does not explain views/subscribers at all (that is the title and the
thumbnail); what a hook moves is the share still watching at 0:30, which only our own curves show. Re-run
--calibrate as transcripts are added, and compare hooks with our 0:30 retention once 10+ videos pass 50 views.
"""
import argparse
import glob
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NUM = re.compile(r"\b\d[\d,.]*\b|\b(one|two|three|four|five|six|seven|eight|nine|ten|hundred|thousand|million|billion)\b", re.I)
SCALE = re.compile(r"\b(bigger|larger|smaller|the size of|as big as|almost the size|fewer|more \w+ than|than (the )?(entire )?"
                   r"(UK|United Kingdom|England|France|Texas|London|London's|New York|Washington|Australia|Europe|Germany|Italy))\b", re.I)
TURN = re.compile(r"\b(but|yet|only|fewer|almost nobody|nobody|empty|virtually empty|instead)\b", re.I)
NEWS = re.compile(r"\b(according to|report(ed|s)?|experts?|officials?|agency|ministry|announced|study (says|finds))\b", re.I)


def sentences(t):
    return [s for s in re.split(r"(?<=[.?!])\s+", t.strip()) if s]


def check(text, place):
    w = text.split()
    s = sentences(text)
    first2 = " ".join(s[:2])
    first40 = " ".join(w[:40])
    first75 = " ".join(w[:75])
    places = [p.strip().lower() for p in place.split("|")] if place else []
    res = {
        "PLACE": bool(places) and any(p in first2.lower() for p in places),
        "SCALE": bool(SCALE.search(" ".join(w[:60]))),
        "TURN": bool(TURN.search(first40)),
        "QUESTION": "?" in first75,
        "ONE NUM": all(len(NUM.findall(x)) <= 1 for x in sentences(first75)),
        "NO NEWS": not NEWS.search(first75),
    }
    return res, sum(res.values())


FIX = {
    "PLACE": "name the place in sentence one or two: the viewer checks the title's promise first",
    "SCALE": "anchor the size to something the viewer knows (bigger than the UK, fewer people than Washington DC)",
    "TURN": "put the 'but' in the first 40 words: the size, then the surprise",
    "QUESTION": "ask the video's question out loud by about 0:30 (75 words)",
    "ONE NUM": "one number per sentence; move the rest to the body",
    "NO NEWS": "drop the report / agency framing from the hook; start from the place",
}


def show(text, place):
    res, n = check(text, place)
    print(f"\n  {text[:160]}{'...' if len(text) > 160 else ''}")
    for k, v in res.items():
        print(f"    {'ok ' if v else 'NO '} {k:9}" + ("" if v else f"  -> {FIX[k]}"))
    print(f"    verdict {n}/6")
    return n


def calibrate():
    sys.path.insert(0, os.path.join(ROOT, "tools"))
    sys.path.insert(0, os.path.join(ROOT, "pipeline"))
    import yt_analytics as t
    yt, _ = t.services()

    def secs(x):
        h, m, s = (int(v) for v in x.split(":"))
        return h * 3600 + m * 60 + s
    rows = []
    for f in glob.glob(os.path.join(ROOT, "youtube-transcript", "*", "*", "transcript-sentences.json")):
        meta = json.load(open(os.path.join(os.path.dirname(f), "meta.json"), encoding="utf-8"))
        if meta.get("duration", 0) < 480:
            continue
        sent = json.load(open(f, encoding="utf-8"))
        text = " ".join(x["text"] for x in sent if secs(x["start"]) < 32)
        place = re.sub(r"(?i)^(why|how)\s+|almost|nobody|lives?|in|on|the|\(.*|[^\w ']", " ", meta["title"]).split()
        rows.append((meta["videoId"], meta["title"], text, "|".join(p for p in place if p[:1].isupper())))
    vs = {v["id"]: v for v in yt.videos().list(part="statistics,snippet", id=",".join(r[0] for r in rows)).execute()["items"]}
    subs = {c["id"]: int(c["statistics"].get("subscriberCount", 0) or 1) for c in
            yt.channels().list(part="statistics", id=",".join({v["snippet"]["channelId"] for v in vs.values()})).execute()["items"]}
    out = []
    for vid, title, text, place in rows:
        v = vs[vid]
        ratio = int(v["statistics"]["viewCount"]) / max(subs[v["snippet"]["channelId"]], 1000)
        out.append((ratio, check(text, place)[1], title))
    out.sort(key=lambda r: -r[0])
    for r in out:
        print(f"{r[0]:8.1f}x  {r[1]}/6  {r[2][:70]}")
    hi = [r[1] for r in out if r[0] >= 50]
    lo = [r[1] for r in out if r[0] < 50]
    print(f"mean score, videos at 50x+: {sum(hi)/len(hi):.2f} (n={len(hi)}); under 50x: {sum(lo)/len(lo):.2f} (n={len(lo)})")


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--text")
    ap.add_argument("--file")
    ap.add_argument("--place", default="", help="place name(s), '|' between spellings")
    ap.add_argument("--calibrate", action="store_true")
    a = ap.parse_args()
    if a.calibrate:
        return calibrate()
    hooks = [a.text] if a.text else [h.strip() for h in open(a.file, encoding="utf-8").read().split("\n\n") if h.strip()]
    scored = sorted(((show(h, a.place), h) for h in hooks), key=lambda r: -r[0])
    if len(scored) > 1:
        print(f"\n  best: {scored[0][0]}/6  {scored[0][1][:100]}")


if __name__ == "__main__":
    main()
