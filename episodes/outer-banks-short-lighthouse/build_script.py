"""Short for outer-banks: the Cape Hatteras Lighthouse that was moved 2,900 ft inland in 1999.
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

LIGHTHOUSE = place("Cape Hatteras Lighthouse", -75.5289, 35.2506, "LIGHTHOUSE TODAY", "site")
OLD_SITE = place("Old site", -75.5220, 35.2562, "WHERE IT STOOD UNTIL 1999", "site")  # 2,900 ft NE of today's site
MOVE = {"from": [-75.5220, 35.2562], "to": [-75.5289, 35.2506], "mode": "line", "seconds": 3, "label": "2,900 ft in 23 days"}

paragraphs = [
    P("In 1870 this lighthouse stood fifteen hundred feet from the ocean. By 1970 the water was a hundred and twenty feet away.",
      m("Cape Hatteras Lighthouse, 1870", v(-75.53, 35.25, 0.05, places=[LIGHTHOUSE])),
      m("1970: the ocean 120 ft away", v(-75.52, 35.26, 0.035), at="By 1970")),
    P("They tried groins, new sand and a seawall study. Then, in June 1999, crews lifted 4,830 tons of brick onto rails.",
      m("Groins, sand, a seawall study", v(-75.51, 35.27, 0.06)),
      m("4,830 tons of brick", v(-75.54, 35.25, 0.04), at="Then, in")),
    P("Twenty-three days later it stood 2,900 feet to the southwest. It cost 11.8 million dollars.",
      m("Moved 2,900 ft in 23 days", v(-75.525, 35.255, 0.08, places=[OLD_SITE, LIGHTHOUSE], routes=[MOVE])),
      m("$11.8 million", v(-75.55, 35.24, 0.045), at="It cost")),
    P("Today it stands about fifteen hundred feet from the ocean again.",
      m("1,500 ft from the ocean again", v(-75.53, 35.24, 0.07, places=[LIGHTHOUSE]))),
    P("The houses just north of it in Buxton were never moved. Four fell in two days this February.",
      m("Never moved", v(-75.52, 35.275, 0.055, places=[BUXTON])),
      m("Buxton: 4 houses in two days", v(-75.515, 35.265, 0.04), at="Four fell")),
    P("They moved a lighthouse. Should they move the houses too?",
      m("Move the houses too?", v(-75.54, 35.26, 0.12, places=[LIGHTHOUSE, BUXTON]))),
]

script = {
    "title": "They Moved a 4,830-Ton Lighthouse",
    "format": "short",
    "voice": "am_michael",
    "music": "procedural",
    "map_style": "satellite",
    "captions": True,
    "sources": ["All facts from episodes/outer-banks research.md and factcheck.md (NPS, Moving the Cape Hatteras Lighthouse; NPS Threatened Oceanfront Structures)."],
    "thumbnail": {"text": "MOVED IT", "focus": [-75.5289, 35.2506, 0.04]},
    "chapters": [{"title": "Moved It", "mood": "tension", "paragraphs": paragraphs}],
    "youtube": {
        "title": "They Moved a 4,830-Ton Lighthouse Away From the Ocean",
        "description": "The Cape Hatteras Lighthouse stood 1,500 feet from the ocean in 1870 and 120 feet in 1970. In 1999 crews moved all 4,830 tons of it 2,900 feet inland in 23 days. The houses next to it stayed.\n\nFull documentary on the channel: the Outer Banks\n\n#geography #satellite #lighthouse",
        "tags": ["Cape Hatteras Lighthouse", "Outer Banks", "lighthouse move", "coastal erosion", "Buxton", "satellite images", "North Carolina", "shorts"],
        "pinned_comment": "They moved a lighthouse. Should they move the houses too?",
    },
}
(HERE / "script.json").write_text(json.dumps(script, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
print(sum(len(p["text"].split()) for p in paragraphs), "words")
