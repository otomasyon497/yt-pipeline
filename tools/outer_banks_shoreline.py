"""Own measurement for the outer-banks episode: where the ocean shoreline sits, by year, from Landsat.

For each site (a box a few km long on the ocean side of the island) and year it takes up to four of the clearest
Landsat 5/8/9 days (Collection 2 Level-2 surface reflectance, read at ~15 m), marks water with MNDWI > 0
(green vs short-wave infrared 1.6 um), and for every pixel row walks in from the ocean (east) edge to the first run of
three land pixels: that is the shoreline on that row. A day counts when 80 % of rows are clear; its value is the mean
shoreline over the rows. A year is the median of its days. Tides and wave run-up move the wet line by tens of metres
on a single day, so read decades, not single years. Distances are ground metres, positive = landward retreat
since the first year.
Usage: python -I tools/outer_banks_shoreline.py <repo root> <out.json>
"""
import json
import sys
from pathlib import Path

import numpy as np
import rasterio
from rasterio.transform import from_bounds

ROOT = Path(sys.argv[1])
sys.path.insert(0, str(ROOT / "pipeline"))
import landsat  # noqa: E402
from sentinel import EARTH, _read  # noqa: E402

# name: (lon_west, lat_south, lon_east, lat_north); the east edge must be open ocean.
SITES = {
    "Rodanthe": (-75.49, 35.575, -75.43, 35.605),
    "Pea Island (visitor center)": (-75.51, 35.700, -75.46, 35.730),
    "Avon": (-75.52, 35.340, -75.47, 35.365),
    "Buxton": (-75.545, 35.255, -75.49, 35.285),
}
YEARS = [1985, 1990, 1995, 2000, 2005, 2010, 2014, 2018, 2022, 2024, 2025, 2026]
PX = 15.0  # ground metres per output pixel (Landsat is 30 m; the row mean gets below a pixel)
PLATS = ["landsat-5", "landsat-8", "landsat-9"]


def merc(lon, lat):
    return lon / 360 * EARTH, np.log(np.tan(np.pi / 4 + np.radians(lat) / 2)) / (2 * np.pi) * EARTH


def grid(box):
    w, s, e, n = box
    x0, y0 = merc(w, s)
    x1, y1 = merc(e, n)
    k = np.cos(np.radians((s + n) / 2))  # ground metres per Mercator metre
    width = int(round((x1 - x0) * k / PX))
    height = int(round((y1 - y0) * k / PX))
    return from_bounds(x0, y0, x1, y1, width, height), width, height, k


def shoreline(water, clear):
    """Columns from the east edge to the first run of three land pixels, per row; NaN where unclear or not found."""
    h, w = water.shape
    out = np.full(h, np.nan)
    for r in range(h):
        if clear[r].mean() < 0.95 or not water[r, -3:].all():
            continue
        land = ~water[r, ::-1]
        run = np.convolve(land.astype(int), np.ones(3, int), "valid") == 3
        idx = np.flatnonzero(run)
        if idx.size:
            out[r] = idx[0]
    return out


def day_value(item, transform, width, height):
    tok = landsat._token()
    bands = []
    for name in ("green", "swir16", "qa_pixel"):
        a = item["assets"][name]
        buf = np.zeros((height, width), dtype=np.float32)
        with rasterio.Env(**landsat.ENV):
            _read(f"{a['href']}?{tok}", buf, transform, PX, nearest=name == "qa_pixel")
        bands.append(buf)
    g, s, qa = bands
    q = qa.astype(np.uint32)
    clear = (g > 0) & (s > 0) & ((q & 0b11010) == 0)
    g = g * 2.75e-5 - 0.2
    s = s * 2.75e-5 - 0.2
    water = (g - s) / np.maximum(np.abs(g + s), 1e-4) > 0
    rows = shoreline(water, clear)
    ok = np.isfinite(rows)
    if ok.mean() < 0.8:
        return None, None
    return float(np.nanmean(rows)) * PX, rows * PX  # metres from the east edge


def measure(box, year):
    w, s, e, n = box
    poly = {"type": "Polygon", "coordinates": [[[w, s], [e, s], [e, n], [w, n], [w, s]]]}
    items = landsat._post({"collections": ["landsat-c2-l2"], "intersects": poly,
                           "datetime": f"{year}-01-01T00:00:00Z/{year}-12-31T23:59:59Z", "limit": 100,
                           "query": {"eo:cloud_cover": {"lt": 10}, "platform": {"in": PLATS}}})
    items = sorted(items, key=lambda i: i["properties"]["eo:cloud_cover"])[:8]
    transform, width, height, _ = grid(box)
    days, profiles = [], []
    for it in items:
        try:
            v, prof = day_value(it, transform, width, height)
        except Exception as exc:  # one bad scene must not stop the year
            print("  skip", it["id"], str(exc)[:80], flush=True)
            continue
        if v is not None:
            days.append({"date": it["properties"]["datetime"][:10], "platform": it["properties"]["platform"], "from_east_m": round(v, 1)})
            profiles.append(prof)
        if len(days) == 4:
            break
    if not days:
        return None, None
    return {"days": days, "from_east_m": round(float(np.median([d["from_east_m"] for d in days])), 1),
            "spread_m": round(float(np.ptp([d["from_east_m"] for d in days])), 1)}, np.nanmedian(np.array(profiles), axis=0)


out_path = Path(sys.argv[2])
out = {}
for name, box in SITES.items():
    res, prof = {}, {}
    for y in YEARS:
        try:
            res[y], prof[y] = measure(box, y)
        except Exception as exc:
            res[y] = None
            print(name, y, "failed", str(exc)[:110], flush=True)
        print(name, y, res[y] and (res[y]["from_east_m"], res[y]["spread_m"], len(res[y]["days"])), flush=True)
    base_year = next((y for y in YEARS if res.get(y)), None)
    for y in YEARS:
        if res.get(y) and base_year is not None:
            # landward retreat since the first year = how much farther from the east edge the shoreline now sits
            res[y]["retreat_m"] = round(res[y]["from_east_m"] - res[base_year]["from_east_m"], 1)
            # the same, row by row (only rows valid in both years), to show it is not one stretch
            a, b = prof[base_year], prof[y]
            ok = np.isfinite(a) & np.isfinite(b)
            if ok.any():
                d = b[ok] - a[ok]
                res[y]["rows_retreat_p10_p90"] = [round(float(np.percentile(d, 10)), 1), round(float(np.percentile(d, 90)), 1)]
    out[name] = {"box": box, "base_year": base_year, "years": res}
    out_path.write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(name, {y: (v and v.get("retreat_m")) for y, v in res.items()}, flush=True)
