"""Builds the two Shorts of ogallala-aquifer; every fact comes from its script and factcheck.md.  python build_shorts.py"""
import json
from pathlib import Path

ROOT = Path(__file__).parent.parent
W24 = "2024-07-01/2024-08-31"
W26 = "2026-07-01/2026-08-31"
AQ = "file:aquifer.geojson"


def map_shot(at, steps, text=None):
    s = {"type": "map", "at": at, "map": {"steps": steps}}
    if text:
        s["on_screen_text"] = text
    return s


def place(name, lon, lat, label, kind="site"):
    return {"name": name, "lon": lon, "lat": lat, "kind": kind, "label": label}


DALLAM = {"lon": -102.6, "lat": 36.1, "span": 0.16}
DAL_CLOSE = {"lon": -102.68, "lat": 36.18, "span": 0.08}
PANHANDLE = {"lon": -102.2, "lat": 35.9, "span": 2.4}
KS = {"lon": -100.9, "lat": 38.3, "span": 3.4}
GARDEN = {"lon": -100.95, "lat": 37.85, "span": 0.16}
GOODLAND = {"lon": -101.7, "lat": 39.35, "span": 0.16}
HOXIE = {"lon": -100.45, "lat": 39.35, "span": 0.16}
SHER_W = {"lon": -100.45, "lat": 39.3, "span": 2.4}
WHOLE = {"lon": -100.8, "lat": 37.8, "span": 15}
DALHART = place("Dalhart", -102.52, 36.06, "DALHART", "city")
GC = place("Garden City", -100.87, 37.97, "GARDEN CITY", "city")
SHERIDAN = place("Hoxie", -100.44, 39.35, "SHERIDAN COUNTY")


def build(slug, title, description, tags, comment, thumb, focus, chapter_title, paragraphs):
    d = {"title": title, "format": "short", "voice": "am_michael", "music": "procedural", "map_style": "satellite", "captions": True,
         "sources": ["All facts from episodes/ogallala-aquifer research.md and factcheck.md."],
         "thumbnail": {"text": thumb, "focus": focus},
         "chapters": [{"title": chapter_title, "mood": "tension", "card": False, "paragraphs": paragraphs}],
         "youtube": {"title": title, "description": description, "tags": tags, "pinned_comment": comment}}
    out = ROOT / slug
    out.mkdir(exist_ok=True)
    (out / "script.json").write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    geo = ROOT / "ogallala-aquifer" / "geo" / "aquifer.geojson"
    (out / "geo").mkdir(exist_ok=True)
    (out / "geo" / "aquifer.geojson").write_bytes(geo.read_bytes())
    print(slug, sum(len(p["text"].split()) for p in paragraphs), "words")


build("ogallala-short-orbit", "From Space, These Farms Look Fine",
      "The Texas Panhandle in 1986 and 2024, from orbit: we measured green land near Dalhart go from 17 percent to 58. Below it, the water tells another story.\n\nFull documentary on the channel: the Ogallala aquifer\n\n#geography #water #satellite",
      ["Ogallala aquifer", "Texas Panhandle", "groundwater", "irrigation", "center pivot", "satellite images", "before and after", "shorts"],
      "Who should decide how fast the water goes: the farmers who own the wells, or the state?",
      "LOOKS FINE?", [-102.6, 36.1, 0.09], "Dalhart", [
    {"text": "The Texas Panhandle, 1986. Now, 2024, on the same day of the year.", "shots": [map_shot(0, [{"view": DALLAM, "date": W24, "compare": {"before": "1986-08-17", "after": "2024-08-17", "source": "landsat", "seconds": 1.6, "until": "Now,"}}, {"at": "Now,"}], "The same day, 38 years apart")]},
    {"text": "We measured it. Land actively green went from seventeen percent to fifty-eight.", "shots": [map_shot(0, [{"view": DAL_CLOSE, "date": W24}], "17% to 58% green, our measurement")]},
    {"text": "From orbit, a triumph. Every circle is a well.", "shots": [map_shot(0, [{"view": DALLAM, "date": W24, "places": [DALHART]}], "Every circle is a well")]},
    {"text": "But the water comes from one aquifer under eight states.", "shots": [map_shot(0, [{"view": WHOLE, "highlight": [AQ]}], "The High Plains aquifer")]},
    {"text": "Here in Texas, it has fallen forty-four feet on average since about 1950.", "shots": [map_shot(0, [{"view": PANHANDLE, "places": [DALHART]}], "Texas: down 44 feet on average")]},
    {"text": "One well dropped two hundred sixty-five.", "shots": [map_shot(0, [{"view": DAL_CLOSE, "date": W24}], "One Texas well: down 265 feet")]},
    {"text": "In Kansas, the state's chief engineer warns that in one district the groundwater could be near unusable within fifty years.", "shots": [map_shot(0, [{"view": KS, "places": [GC]}], "Kansas chief engineer, Nov 2026")]},
    {"text": "So how long can the circles stay green?", "shots": [map_shot(0, [{"view": DALLAM, "date": W24}], "How long can they stay green?")]},
])

build("ogallala-short-farmers", "These Kansas Farmers Cut Their Own Water",
      "Northwest Kansas from orbit, 1986 and 2026. In 2013 farmers in Sheridan County capped their own pumping, and the decline of the aquifer slowed from two feet a year to half a foot. Southwest Kansas is now fighting over how far to follow.\n\nFull documentary on the channel: the Ogallala aquifer\n\n#geography #kansas #water",
      ["Ogallala aquifer", "Kansas", "Sheridan County", "groundwater", "water conservation", "satellite images", "before and after", "shorts"],
      "Would you cut your own water before anyone made you?",
      "IT WORKED", [-101.7, 39.35, 0.09], "Sheridan 6", [
    {"text": "Northwest Kansas, 1986. Now, the same land, in 2026.", "shots": [map_shot(0, [{"view": GOODLAND, "date": W26, "compare": {"before": "1986-07-16", "after": "2026-07-06", "source": "landsat", "seconds": 1.6, "until": "Now,"}}, {"at": "Now,"}], "More circles, more wells")]},
    {"text": "Every new circle pumps from the same aquifer.", "shots": [map_shot(0, [{"view": SHER_W}], "One aquifer under eight states")]},
    {"text": "But in 2013, farmers in Sheridan County did something nobody made them do.", "shots": [map_shot(0, [{"view": SHER_W, "places": [SHERIDAN]}], "Sheridan County, Kansas")]},
    {"text": "They capped their own pumping. The target was twenty percent.", "shots": [map_shot(0, [{"view": HOXIE, "date": W24}], "Target: a 20% cut")]},
    {"text": "They cut about twenty-three.", "shots": [map_shot(0, [{"view": {"lon": -100.6, "lat": 39.35, "span": 0.08}, "date": W24}], "They reached 23%")]},
    {"text": "The water level had been falling two feet a year. It slowed to half a foot.", "shots": [map_shot(0, [{"view": HOXIE, "date": W24}], "2 feet a year, then half a foot")]},
    {"text": "Now southwest Kansas is fighting about it. The state just rejected the plan from around Garden City as too weak.", "shots": [map_shot(0, [{"view": {"lon": -100.9, "lat": 38.3, "span": 3.4}, "places": [GC]}], "Rejected, Sept 30, 2026"), map_shot("The state", [{"view": GARDEN, "date": W24}])]},
    {"text": "Would you cut your own water before anyone made you?", "shots": [map_shot(0, [{"view": HOXIE, "date": W24}], "Would you cut first?")]},
])
