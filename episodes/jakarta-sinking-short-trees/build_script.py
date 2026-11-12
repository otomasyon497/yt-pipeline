"""Short for jakarta-sinking: the Giant Sea Wall began with a row of mangroves in a village the sea has already taken.
All facts from episodes/jakarta-sinking research.md, verification.md and our Landsat measurement.  python build_script.py
"""
import json
from pathlib import Path

HERE = Path(__file__).parent
AFTER = "2026-06-01/2026-10-31"


def place(name, lon, lat, label, kind="city"):
    return {"name": name, "lon": lon, "lat": lat, "kind": kind, "label": label}


TIMBUL = place("Timbulsloko", 110.518, -6.914, "TIMBULSLOKO")
GSW = {"from": [106.15, -6.03], "to": [112.65, -7.10], "mode": "line", "seconds": 3, "label": "About 575 km",
       "via": [[106.80, -6.07], [107.60, -6.20], [108.57, -6.70], [109.68, -6.86], [110.43, -6.93], [111.10, -6.55], [112.05, -6.88]]}


def m(text, *steps, at=0, cut=True):
    s = {"type": "map", "at": at, "map": {"steps": list(steps)}, "on_screen_text": text}
    if cut:
        s["map"]["cut"] = True
    return s


def v(lon, lat, span, date=AFTER, **kw):
    d = {"view": {"lon": lon, "lat": lat, "span": span}, **kw}
    if span <= 2:
        d["date"] = date
    return d


def P(text, *shots):
    return {"text": text, "shots": list(shots)}


paragraphs = [
    P("This village on the coast of Java, in 1990. And here it is this year, after the sea moved in.",
      m("Real satellite images · Landsat",
        {**v(110.505, -6.905, 0.12), "compare": {"before": "1990-06-01/1990-10-31", "after": AFTER, "source": "landsat", "seconds": 1.6, "until": "And here"}},
        {"at": "And here", "places": [TIMBUL]}, cut=False)),
    P("We measured it. Around Timbulsloko, nine tenths of the land has turned to water.",
      m("~90% of the land: now water · our measurement", v(110.517, -6.913, 0.05, places=[TIMBUL]))),
    P("In October, officials planted mangroves here and called it the start of Indonesia's Giant Sea Wall.",
      m("October 19, 2026", v(110.51, -6.905, 0.04)),
      m("The 'start' of the Giant Sea Wall", v(110.525, -6.92, 0.06), at="and called")),
    P("The wall is planned to run about five hundred and seventy-five kilometres along Java's north coast.",
      m("About 575 km", v(109.2, -6.7, 7.5, routes=[GSW])),
      m("Java's north coast", v(110.3, -6.85, 1.2), at="along Java's")),
    P("Three weeks later, residents told a local paper the seedlings had died.",
      m("Residents: the seedlings died", v(110.512, -6.918, 0.04, places=[TIMBUL]))),
    P("Can a wall save a coast that is already under water?",
      m("Can a wall save it?", v(110.50, -6.90, 0.14, places=[TIMBUL]))),
]

script = {
    "title": "Indonesia's Sea Wall Began With a Row of Trees",
    "format": "short",
    "voice": "am_michael",
    "music": "procedural",
    "map_style": "satellite",
    "captions": True,
    "sources": ["All facts from episodes/jakarta-sinking research.md, verification.md and demak_shoreline.json."],
    "thumbnail": {"text": "THE WALL", "focus": [110.505, -6.905, 0.12]},
    "chapters": [{"title": "A Wall of Trees", "mood": "tension", "paragraphs": paragraphs}],
    "youtube": {
        "title": "Indonesia's Giant Sea Wall Began With a Row of Trees",
        "description": "Timbulsloko, on Java's north coast, from orbit in 1990 and 2026: we measured about nine tenths of the land around the village turned to water. In October 2026 officials planted mangroves here as the start of a sea wall planned to run about 575 km.\n\nFull documentary on the channel: Sinking Jakarta\n\n#geography #satellite #indonesia",
        "tags": ["Giant Sea Wall", "Indonesia", "Java", "Demak", "Timbulsloko", "sinking land", "mangroves", "satellite images", "before and after", "Landsat", "shorts"],
        "pinned_comment": "Can a wall save a coast that is already under water?",
    },
}
(HERE / "script.json").write_text(json.dumps(script, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
print(sum(len(p["text"].split()) for p in paragraphs), "words")
