"""Short for louisiana-land-loss: the first community the US paid to move away from the sea, and a resident's advice.
All facts from episodes/louisiana-land-loss research.md / verification.md.  python build_script.py
"""
import json
from pathlib import Path

HERE = Path(__file__).parent
LA_DAY = "2026-10-13/2026-10-13"
AFTER = "2026-10-01/2026-11-10"


def place(name, lon, lat, label, kind="city"):
    return {"name": name, "lon": lon, "lat": lat, "kind": kind, "label": label}


IJC = place("Isle de Jean Charles", -90.4886, 29.3992, "ISLE DE JEAN CHARLES")
NEWISLE = place("The New Isle", -90.776, 29.711, "THE NEW ISLE")
MOVE = {"from": [-90.4886, 29.3992], "to": [-90.776, 29.711], "mode": "line", "seconds": 3, "label": "About 40 miles"}


def m(text, *steps, at=0, cut=True):
    s = {"type": "map", "at": at, "map": {"steps": list(steps)}, "on_screen_text": text}
    if cut:
        s["map"]["cut"] = True
    return s


def v(lon, lat, span, date=LA_DAY, **kw):
    d = {"view": {"lon": lon, "lat": lat, "span": span}, **kw}
    if span <= 2:
        d["date"] = date
    return d


def P(text, *shots):
    return {"text": text, "shots": list(shots)}


paragraphs = [
    P("This island in Louisiana, in 1985. And here it is this autumn, after the sea moved in.",
      m("Real satellite images · Landsat",
        {**v(-90.49, 29.405, 0.14), "compare": {"before": "1985-09-14/1985-09-18", "after": "2026-10-10/2026-10-28", "source": "landsat", "seconds": 1.6, "until": "And here"}},
        {"at": "And here", "places": [IJC]}, cut=False)),
    P("By the state's count, the land around it shrank from more than twenty-two thousand acres to about three hundred and twenty.",
      m("22,000 acres -> 320", v(-90.487, 29.40, 0.05, places=[IJC])),
      m("By the state's count", v(-90.48, 29.42, 0.04), at="to about")),
    P("In 2016 the US government paid to move a whole community away from the sea, in what was called a first for the country.",
      m("2016: called a US first", v(-90.55, 29.45, 0.3, places=[IJC])),
      m("A whole community", v(-90.49, 29.395, 0.035), at="to move"),
      m("Called a first", v(-90.47, 29.43, 0.06), at="in what")),
    P("Thirty-seven families moved about forty miles inland.",
      m("37 families, ~40 miles", v(-90.62, 29.55, 0.6, places=[IJC, NEWISLE], routes=[MOVE]))),
    P("This year, one of them told The New York Times what she would tell the next town. Don't do it.",
      m("The New Isle", v(-90.776, 29.711, 0.04, places=[NEWISLE])),
      m("What she would tell", v(-90.79, 29.72, 0.06), at="what she"),
      m("\"Don't do it.\"", v(-90.77, 29.705, 0.035), at="Don't do it.")),
    P("Would you leave your home before the sea takes it?",
      m("Would you leave?", v(-90.49, 29.40, 0.1, places=[IJC]))),
]

script = {
    "title": "The US Moved a Whole Island. Then This Happened",
    "format": "short",
    "voice": "am_michael",
    "music": "procedural",
    "map_style": "satellite",
    "captions": True,
    "sources": ["All facts from episodes/louisiana-land-loss research.md and verification.md (Louisiana OCD, HUD, The New York Times 2026)."],
    "thumbnail": {"text": "DON'T DO IT", "focus": [-90.49, 29.405, 0.14]},
    "chapters": [{"title": "Don't Do It", "mood": "tension", "paragraphs": paragraphs}],
    "youtube": {
        "title": "The US Paid to Move a Whole Island. One Resident Says Don't",
        "description": "Isle de Jean Charles, Louisiana, from orbit in 1985 and 2026. By the state's count the land around it shrank from more than 22,000 acres to about 320. In 2016 the US paid for the first time to move a whole community away from the sea; 37 families moved about 40 miles inland.\n\nFull documentary on the channel: Vanishing Louisiana\n\n#geography #satellite #louisiana",
        "tags": ["Isle de Jean Charles", "Louisiana", "climate relocation", "coastal land loss", "satellite images", "before and after", "Landsat", "shorts"],
        "pinned_comment": "Would you leave your home before the sea takes it?",
    },
}
(HERE / "script.json").write_text(json.dumps(script, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
print(sum(len(p["text"].split()) for p in paragraphs), "words")
