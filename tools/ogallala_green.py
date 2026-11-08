"""Own measurement for the ogallala-aquifer episode: share of each area actively green in mid-summer, Landsat, by year.

For each area and year it takes the clearest July-August day that covers the box and measures NDVI (Collection 2 Level-2
surface reflectance, 30 m read at about 60 m): the share of clear pixels with NDVI over 0.5. Landsat 5 and 8/9 differ
slightly in band response, so read long trends, not single percentage points. One day a year also catches the crop
calendar, so each year uses up to three clear days and keeps the highest (a field green on any of them was growing).
Usage: python -I tools/ogallala_green.py <repo root> <out.json>
"""
import json
import sys
from pathlib import Path

import numpy as np
import rasterio
from rasterio.transform import from_bounds

ROOT = Path(sys.argv[1])
sys.path.insert(0, str(ROOT / "pipeline"))
import types  # noqa: E402

import geo  # noqa: E402

stub = types.ModuleType("maps")
stub.unit_box_to_lonlat = lambda b: (*geo.unmerc(b[0], b[3]), *geo.unmerc(b[2], b[1]))
sys.modules["maps"] = stub
import landsat  # noqa: E402
from sentinel import EARTH, _read  # noqa: E402

AREAS = {"Dallam TX": (-102.6, 36.1), "Stratford TX": (-102.1, 36.35), "Hale TX": (-101.9, 33.95), "Goodland KS": (-101.7, 39.35),
         "Leoti KS": (-101.35, 38.48), "Garden City KS": (-100.95, 37.85), "Sheridan KS": (-100.65, 39.35)}
YEARS = [1986, 1990, 1995, 2000, 2005, 2010, 2015, 2020, 2022, 2024, 2025, 2026]
SPAN = 0.5
WIDTH = 760


def measure(lon, lat, year):
    w = SPAN / 360
    cx, cy = float(geo.mx(lon)), float(geo.my(lat))
    x0, y0, x1, y1 = cx - w / 2, cy - w * 0.4, cx + w / 2, cy + w * 0.4
    height = round(WIDTH * 0.8)
    lon0, lat1 = geo.unmerc(x0, y0)
    lon1, lat0 = geo.unmerc(x1, y1)
    res = (x1 - x0) * EARTH / WIDTH * np.cos(np.radians((lat0 + lat1) / 2))
    transform = from_bounds((x0 - 0.5) * EARTH, (0.5 - y1) * EARTH, (x1 - 0.5) * EARTH, (0.5 - y0) * EARTH, WIDTH, height)
    plats = ["landsat-5", "landsat-8", "landsat-9"]  # not 7: its stripes after 2003 and a different look
    items = landsat._post({"collections": ["landsat-c2-l2"], "intersects": {"type": "Point", "coordinates": [lon, lat]},
                           "datetime": f"{year}-07-01T00:00:00Z/{year}-08-31T23:59:59Z", "limit": 60,
                           "query": {"eo:cloud_cover": {"lt": 8}, "platform": {"in": plats}}})
    items = sorted(items, key=lambda i: i["properties"]["eo:cloud_cover"])[:3]
    tok, best = landsat._token(), None
    for it in items:
        bands = []
        for name in ("red", "nir08", "qa_pixel"):
            a = it["assets"][name]
            buf = np.zeros((height, WIDTH), dtype=np.float32)
            with rasterio.Env(**landsat.ENV):
                _read(f"{a['href']}?{tok}", buf, transform, res, nearest=name == "qa_pixel")
            bands.append(buf)
        red, nir, qa = bands
        q = qa.astype(np.uint32)
        clear = (red > 0) & (nir > 0) & ((q & 0b11010) == 0)  # no dilated cloud, cirrus-free where flagged, no shadow, no cloud
        if clear.mean() < 0.9:
            continue
        r = red * 2.75e-5 - 0.2
        n = nir * 2.75e-5 - 0.2
        ndvi = (n - r) / np.maximum(n + r, 1e-4)
        share = float(((ndvi > 0.5) & clear).sum() / clear.sum())
        rec = {"date": it["properties"]["datetime"][:10], "platform": it["properties"]["platform"], "green": round(100 * share, 1), "clear": round(float(clear.mean()), 3)}
        if best is None or rec["green"] > best["green"]:
            best = rec
    return best


out = {}
for name, (lon, lat) in AREAS.items():
    out[name] = {}
    for y in YEARS:
        try:
            out[name][y] = measure(lon, lat, y)
        except Exception as exc:
            out[name][y] = None
            print(name, y, "failed", str(exc)[:110], flush=True)
    print(name, {y: (v and v["green"]) for y, v in out[name].items()}, flush=True)
    Path(sys.argv[2]).write_text(json.dumps(out, indent=1), encoding="utf-8")
