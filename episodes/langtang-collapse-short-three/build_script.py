"""Short for langtang-collapse: one valley destroyed three times in eleven years (2015, 2025, 2026).
All facts from episodes/langtang-collapse research.md and factcheck.md (the long episode's own lines).  python build_script.py
"""
import json
from pathlib import Path

HERE = Path(__file__).parent
BEFORE = "2025-10-15/2025-11-10"
AFTER = "2026-10-18/2026-10-27"


def place(name, lon, lat, label, kind="site"):
    return {"name": name, "lon": lon, "lat": lat, "kind": kind, "label": label}


SRC = place("Collapse", 85.5252, 28.2853, "WHERE THE ICE BROKE", "event")
RASUWAGADHI = place("Rasuwagadhi", 85.3778, 28.2778, "RASUWAGADHI")
TRISHULI = place("Trishuli", 85.148, 27.9232, "TRISHULI", "city")
PATH = {"from": [85.5252, 28.2853], "to": [85.1101, 27.86], "mode": "line", "seconds": 4, "label": "The flood's path",
        "via": [[85.505, 28.315], [85.481, 28.338], [85.43, 28.335], [85.395, 28.322], [85.3778, 28.2778], [85.3667, 28.2528],
                [85.345, 28.20], [85.343, 28.160], [85.30, 28.10], [85.207, 28.0718], [85.219, 28.0326], [85.186, 27.9731],
                [85.148, 27.9232]]}


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


P = lambda text, *shots: {"text": text, "shots": list(shots)}
LANGTANG = place("Langtang", 85.509, 28.2158, "LANGTANG VILLAGE")

paragraphs = [
    P("This valley in Nepal has been destroyed three times in eleven years.",
      m("3 disasters in 11 years", v(85.43, 28.25, 0.35))),
    P("April 2015. A magnitude 7.8 earthquake broke ice off the mountain, and the debris buried Langtang village.",
      m("2015: M 7.8 earthquake", v(85.50, 28.22, 0.12, places=[LANGTANG])),
      m("Langtang village, buried", v(85.512, 28.214, 0.05), at="and the debris")),
    P("Officially 306 people died. The villagers say it was closer to five hundred.",
      m("306 dead · villagers say ~500", v(85.53, 28.22, 0.07))),
    P("July 2025. A lake on a glacier in Tibet burst. Nine dead, nineteen missing.",
      m("2025: a glacial lake bursts", v(85.40, 28.30, 0.12, date=BEFORE, places=[RASUWAGADHI])),
      m("9 dead, 19 missing", v(85.378, 28.275, 0.05, date=BEFORE), at="Nine dead")),
    P("August 2026. Ice and rock broke off Langtang Lirung, and the flood ran about a hundred kilometres.",
      m("2026: the ice breaks", v(85.515, 28.29, 0.09, places=[SRC])),
      m("About 100 km of flood", v(85.32, 28.10, 0.75, routes=[PATH]), at="and the flood")),
    P("Three times in eleven years. Is it still safe to live here?",
      m("Is it still safe here?", v(85.45, 28.27, 0.25))),
]

script = {
    "title": "One Valley, Destroyed Three Times in 11 Years",
    "format": "short",
    "voice": "am_michael",
    "music": "procedural",
    "map_style": "satellite",
    "captions": True,
    "sources": ["All facts from episodes/langtang-collapse research.md and factcheck.md (Himal Southasian, USGS, Kathmandu Post, ICIMOD)."],
    "thumbnail": {"text": "3 TIMES", "focus": [85.45, 28.27, 0.3]},
    "chapters": [{"title": "Three Times", "mood": "tension", "paragraphs": paragraphs}],
    "youtube": {
        "title": "One Valley in Nepal, Destroyed Three Times in 11 Years",
        "description": "The Langtang and Bhotekoshi valleys in Nepal from orbit: the 2015 earthquake avalanche that buried Langtang village, the glacial lake that burst in Tibet in July 2025, and the ice that broke off Langtang Lirung in August 2026.\n\nFull documentary on the channel: the Langtang collapse\n\n#geography #satellite #nepal",
        "tags": ["Langtang", "Nepal", "2015 earthquake", "glacial lake outburst", "glacier collapse", "Rasuwa", "satellite images", "shorts"],
        "pinned_comment": "Three disasters in eleven years. Would you rebuild here?",
    },
}
(HERE / "script.json").write_text(json.dumps(script, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
print(sum(len(p["text"].split()) for p in paragraphs), "words")
