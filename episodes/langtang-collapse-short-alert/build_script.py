"""Short for langtang-collapse: the valley before and after, and the alert that came 38 minutes late.
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

paragraphs = [
    P("This valley in Nepal, last October. And here is the same valley this October, two months after the disaster.",
      m("Real satellite images · Sentinel-2",
        {**v(85.45, 28.30, 0.4), "compare": {"before": BEFORE, "after": AFTER, "seconds": 2.0, "until": "And here"}},
        {"at": "And here"}, cut=False)),
    P("That grey line is where a block of ice and rock broke off Langtang Lirung on August 26.",
      m("August 26, 2026", v(85.515, 28.30, 0.09, places=[SRC])),
      m("Langtang Lirung, 7,227 m", v(85.52, 28.27, 0.06), at="broke off")),
    P("It became a flood that ran about a hundred kilometres into Nepal.",
      m("About 100 km of flood", v(85.32, 28.10, 0.75, routes=[PATH]))),
    P("Cameras at the border crossing filmed the water arriving within minutes.",
      m("Rasuwagadhi, on the border with Tibet", v(85.38, 28.28, 0.07, places=[RASUWAGADHI]))),
    P("Text alerts went out thirty-eight minutes after the collapse.",
      m("Alerts: 38 minutes after", v(85.343, 28.16, 0.07))),
    P("Downstream in Trishuli, a headteacher moved about nine hundred children out of his school. The flood reached it ten minutes later.",
      m("About 900 children moved out", v(85.148, 27.923, 0.07, places=[TRISHULI])),
      m("The flood came 10 minutes later", v(85.155, 27.93, 0.045), at="The flood")),
    P("Nothing on either side was watching the ice in real time. Who should?",
      m("No one watched in real time", v(85.50, 28.32, 0.08)),
      m("Who watches the ice?", v(85.45, 28.30, 0.3), at="Who should?")),
]

script = {
    "title": "Nepal's Flood Alert Came 38 Minutes Late",
    "format": "short",
    "voice": "am_michael",
    "music": "procedural",
    "map_style": "satellite",
    "captions": True,
    "sources": ["All facts from episodes/langtang-collapse research.md and factcheck.md."],
    "thumbnail": {"text": "38 MINUTES", "focus": [85.45, 28.30, 0.4]},
    "chapters": [{"title": "Thirty-Eight Minutes", "mood": "tension", "paragraphs": paragraphs}],
    "youtube": {
        "title": "Nepal's Flood Alert Came 38 Minutes Late",
        "description": "A Nepal valley from orbit, a year apart: on 26 August 2026 ice and rock broke off Langtang Lirung and became a flood that ran about 100 km into Nepal. Text alerts went out 38 minutes after the collapse.\n\nFull documentary on the channel: the Langtang collapse\n\n#geography #satellite #nepal",
        "tags": ["Nepal flood", "Langtang", "glacier collapse", "early warning", "satellite images", "before and after", "Sentinel-2", "shorts"],
        "pinned_comment": "Who should watch the ice above a river two countries share?",
    },
}
(HERE / "script.json").write_text(json.dumps(script, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
print(sum(len(p["text"].split()) for p in paragraphs), "words")
