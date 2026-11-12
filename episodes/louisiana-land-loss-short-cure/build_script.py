"""Short for louisiana-land-loss: Louisiana spent $618 million on a river diversion to rebuild its coast, then cancelled it.
All facts from episodes/louisiana-land-loss research.md / verification.md.  python build_script.py
"""
import json
from pathlib import Path

HERE = Path(__file__).parent
LA_DAY = "2026-10-13/2026-10-13"
AFTER = "2026-10-01/2026-11-10"


def place(name, lon, lat, label, kind="site"):
    return {"name": name, "lon": lon, "lat": lat, "kind": kind, "label": label}


MBSD = place("Mid-Barataria", -89.9626, 29.6482, "MID-BARATARIA SITE")
WAX = place("Wax Lake Delta", -91.4463, 29.5010, "WAX LAKE DELTA")


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
    P("Louisiana has lost about two thousand square miles of land since 1932.",
      m("~2,000 sq mi lost since 1932", v(-90.35, 29.35, 0.7))),
    P("Here, on the Mississippi, the state was building a gate in the levee to let the river's mud rebuild the marsh.",
      m("Mid-Barataria Sediment Diversion", v(-89.97, 29.62, 0.12, places=[MBSD])),
      m("Let the river rebuild", v(-89.96, 29.646, 0.04), at="to let")),
    P("In July 2025 it cancelled the project. Six hundred and eighteen million dollars had already been spent.",
      m("Cancelled: July 17, 2025", v(-90.0, 29.55, 0.2)),
      m("$618.5 million spent", v(-89.955, 29.64, 0.05), at="Six hundred")),
    P("Oystermen had fought it: fresh water would have changed the bay they fish.",
      m("Oystermen fought it", v(-89.85, 29.45, 0.12))),
    P("Yet where the river does reach the sea, at Wax Lake, Louisiana is still building new land.",
      m("Where the river reaches the sea", v(-91.40, 29.56, 0.5)),
      m("Wax Lake: land still growing", v(-91.44, 29.50, 0.1, places=[WAX]), at="Louisiana is")),
    P("Should Louisiana let the river back in?",
      m("Let the river back in?", v(-90.05, 29.45, 0.6))),
]

script = {
    "title": "Louisiana Spent $618 Million, Then Cancelled the Cure",
    "format": "short",
    "voice": "am_michael",
    "music": "procedural",
    "map_style": "satellite",
    "captions": True,
    "sources": ["All facts from episodes/louisiana-land-loss research.md and verification.md (USGS SIM 3381, CPRA Jul 17 2025, WWNO)."],
    "thumbnail": {"text": "CANCELLED", "focus": [-89.97, 29.62, 0.12]},
    "chapters": [{"title": "The Cancelled Cure", "mood": "tension", "paragraphs": paragraphs}],
    "youtube": {
        "title": "Louisiana Spent $618 Million, Then Cancelled the Cure",
        "description": "Louisiana has lost about 2,000 square miles of land since 1932. The Mid-Barataria Sediment Diversion was meant to let the Mississippi rebuild the marsh; in July 2025 the state cancelled it after $618.5 million had been spent. At Wax Lake, where the river does reach the sea, the coast is still growing.\n\nFull documentary on the channel: Vanishing Louisiana\n\n#geography #satellite #louisiana",
        "tags": ["Louisiana", "Mid-Barataria", "sediment diversion", "Mississippi River", "coastal land loss", "Wax Lake Delta", "satellite images", "shorts"],
        "pinned_comment": "Should Louisiana let the river back in, even if it changes the fishing towns?",
    },
}
(HERE / "script.json").write_text(json.dumps(script, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
print(sum(len(p["text"].split()) for p in paragraphs), "words")
