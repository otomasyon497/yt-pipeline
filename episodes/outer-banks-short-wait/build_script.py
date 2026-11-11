"""Short for outer-banks: the shore at Rodanthe from orbit, and the insurance rule that makes owners wait.
All facts from episodes/outer-banks research.md and factcheck.md (the long episode's own lines).  python build_script.py
"""
import json
from pathlib import Path

HERE = Path(__file__).parent
AFTER = "2026-10-20/2026-11-08"


def place(name, lon, lat, label, kind="city"):
    return {"name": name, "lon": lon, "lat": lat, "kind": kind, "label": label}


RODANTHE = place("Rodanthe", -75.468, 35.594, "RODANTHE")
BUXTON = place("Buxton", -75.535, 35.267, "BUXTON")


def m(text, *steps, at=0, cut=True):
    s = {"type": "map", "at": at, "map": {"steps": list(steps)}, "on_screen_text": text}
    if cut:
        s["map"]["cut"] = True
    return s


def v(lon, lat, span, date=AFTER, **kw):
    return {"view": {"lon": lon, "lat": lat, "span": span}, "date": date, **kw}


P = lambda text, *shots: {"text": text, "shots": list(shots)}

paragraphs = [
    P("Rodanthe, North Carolina, in August 1985. And here is the same shore this October, after the autumn storms.",
      m("Real satellite images · Landsat",
        {**v(-75.47, 35.60, 0.11), "compare": {"before": "1985-08-16", "after": "2026-10-27", "source": "landsat", "seconds": 2.4, "until": "And here"}},
        {"at": "And here"}, cut=False)),
    P("We measured it. The shore moved about a hundred and fifty-five metres inland.",
      m("About 155 m inland since 1985 · our measurement", v(-75.466, 35.590, 0.05, places=[RODANTHE]))),
    P("Since 2020, thirty-two houses on this seashore have fallen into the Atlantic.",
      m("32 houses since 2020", v(-75.50, 35.43, 0.4, places=[RODANTHE, BUXTON]))),
    P("Federal flood insurance pays when a house collapses. Not before.",
      m("Insurance pays after, not before", v(-75.518, 35.262, 0.05, places=[BUXTON]))),
    P("Tearing one down costs an owner at least thirty thousand dollars. A collapse pays up to two hundred and fifty thousand.",
      m("Tear it down: $30,000+", v(-75.471, 35.604, 0.05)),
      m("Let it fall: up to $250,000", v(-75.464, 35.582, 0.05), at="A collapse")),
    P("So owners wait for the ocean.",
      m("So they wait", v(-75.468, 35.596, 0.035))),
    P("Should the government pay before the house falls?",
      m("Pay before it falls?", v(-75.6, 35.45, 0.75, places=[RODANTHE, BUXTON]))),
]

script = {
    "title": "Insurance Pays Only After the House Falls",
    "format": "short",
    "voice": "am_michael",
    "music": "procedural",
    "map_style": "satellite",
    "captions": True,
    "sources": ["All facts from episodes/outer-banks research.md and factcheck.md."],
    "thumbnail": {"text": "PAID TO WAIT", "focus": [-75.468, 35.594, 0.05]},
    "chapters": [{"title": "Paid to Wait", "mood": "tension", "paragraphs": paragraphs}],
    "youtube": {
        "title": "Insurance Pays Only After the House Falls",
        "description": "Rodanthe, North Carolina, from orbit in 1985 and 2026: we measured the shore move about 155 metres inland. Federal flood insurance pays when a house collapses, not before, so owners wait for the ocean.\n\nFull documentary on the channel: the Outer Banks\n\n#geography #satellite #erosion",
        "tags": ["Outer Banks", "Rodanthe", "coastal erosion", "flood insurance", "satellite images", "before and after", "Landsat", "shorts"],
        "pinned_comment": "Should the government pay to move a house before the ocean takes it?",
    },
}
(HERE / "script.json").write_text(json.dumps(script, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
print(sum(len(p["text"].split()) for p in paragraphs), "words")
