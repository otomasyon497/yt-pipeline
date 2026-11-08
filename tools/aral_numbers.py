"""Water area of the Aral Sea from Landsat (NDWI > threshold), for chosen summer windows, plus the 1960s outline.

    <venv python> tools/aral_numbers.py            # prints km2 per window and region, writes check PNGs + geo/

Grid: one unit-Mercator box over the whole former sea at ~105 m per pixel. For each window the least cloudy scenes
(cloud cover < 15 %) are laid down first and later ones only fill gaps, so each pixel comes from one clear scene.
Water = NDWI (green - nir) / (green + nir) > THRESH. The pixel area uses the Mercator scale (cos latitude) per row.
The 1960s shoreline is Natural Earth's historic-lake polygon "Aral Sea" (public domain), 67,190 km2 by the same
area method; published figures for 1960 are about 68,000 km2.
"""
import json
import math
import os
import sys

import numpy as np
import rasterio
import requests
from PIL import Image
from rasterio.transform import from_bounds

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, os.path.join(ROOT, "pipeline"))
import landsat  # noqa: E402
from sentinel import EARTH, _read  # noqa: E402

LON0, LAT0, LON1, LAT1 = 57.9, 43.3, 62.1, 47.0
THRESH = 0.05
WINDOWS = {"1989": "1989-05-01/1989-10-31", "2002": "2002-06-01/2002-10-31", "2026": "2026-07-01/2026-09-30"}
NORTH_BOX = (59.95, 46.1)  # lon, lat: the North (Small) Aral is the largest connected water body north-east of this
OUT = os.path.join(ROOT, "build", "aral-numbers")


def ux(lon): return (lon + 180) / 360


def uy(lat):
    s = math.radians(lat)
    return (1 - math.log(math.tan(s) + 1 / math.cos(s)) / math.pi) / 2


def lat_of(y):
    return math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * y))))


x0, y0, x1, y1 = ux(LON0), uy(LAT1), ux(LON1), uy(LAT0)
W = 3000
H = round(W * (y1 - y0) / (x1 - x0))
T = from_bounds((x0 - .5) * EARTH, (.5 - y1) * EARTH, (x1 - .5) * EARTH, (.5 - y0) * EARTH, W, H)
step = (x1 - x0) * EARTH / W  # metres per pixel in Mercator units
row_lat = np.array([lat_of(y0 + (r + .5) * (y1 - y0) / H) for r in range(H)])
pix_km2 = (step * np.cos(np.radians(row_lat))) ** 2 / 1e6  # per row
col_lon = np.array([LON0 + (c + .5) * (LON1 - LON0) / W for c in range(W)])


def search(window):
    start, end = window.split("/")
    body = {"collections": ["landsat-c2-l2"], "bbox": [LON0, LAT0, LON1, LAT1],
            "datetime": f"{start}T00:00:00Z/{end}T23:59:59Z", "limit": 400,
            "query": {"eo:cloud_cover": {"lt": 15}, "platform": {"in": ["landsat-5", "landsat-7", "landsat-8", "landsat-9"]}}}
    items = requests.post(landsat.STAC, json=body, timeout=120).json()["features"]
    if start >= "2003-05-31":
        items = [i for i in items if i["properties"].get("platform") != "landsat-7"]
    return sorted(items, key=lambda i: float(i["properties"].get("eo:cloud_cover", 100)))


def band(item, name, tok):
    buf = np.zeros((H, W), np.float32)
    for attempt in range(4):
        try:
            with rasterio.Env(**landsat.ENV):
                _read(f"{item['assets'][name]['href']}?{tok}", buf, T, step * 0.7, nearest=False)
            break
        except rasterio.errors.RasterioIOError:
            if attempt == 3:
                raise
    s, o = landsat._scale_offset(item["assets"][name])
    return np.where(buf > 0, buf * s + o, np.nan)


def water(window):
    tok = landsat._token()
    g = np.full((H, W), np.nan, np.float32)
    n = g.copy()
    used = []
    for it in search(window):
        if np.isfinite(g).mean() > 0.995:
            break
        gg, nn = band(it, "green", tok), band(it, "nir08", tok)
        f = np.isnan(g) & np.isfinite(gg) & np.isfinite(nn)
        if f.sum() < 1000:
            continue
        g[f], n[f] = gg[f], nn[f]
        used.append(f"{it['id']} ({it['properties'].get('eo:cloud_cover', 0):.0f} % cloud)")
    ndwi = (g - n) / (g + n + 1e-6)
    return ndwi > THRESH, np.isfinite(ndwi), used


def inside_1960():
    """Grid pixels inside the 1960s shoreline (water outside it, e.g. delta lakes, does not count)."""
    import shapely
    from shapely.geometry import shape
    g = shape(json.load(open(os.path.join(ROOT, "episodes", "aral-sea", "geo", "aral1960.geojson")))["features"][0]["geometry"])
    lon = np.broadcast_to(col_lon[None, :], (H, W))
    lat = np.broadcast_to(row_lat[:, None], (H, W))
    return shapely.contains_xy(g, lon.ravel(), lat.ravel()).reshape(H, W)


SEA = None


def km2(mask):
    return float(((mask & SEA) * pix_km2[:, None]).sum())


def north_body(mask):
    """The largest connected water body inside the outline north-east of NORTH_BOX: the North Aral (separate from the
    south since 1987; the Kokaral dam closes it since 2005)."""
    from scipy import ndimage
    lab, _ = ndimage.label(mask & SEA)
    sel = (row_lat[:, None] > NORTH_BOX[1]) & (col_lon[None, :] > NORTH_BOX[0]) & (lab > 0)
    if not sel.any():
        return np.zeros_like(mask)
    ids, counts = np.unique(lab[sel], return_counts=True)
    return lab == ids[np.argmax(counts)]


def from_saved():
    """Recompute the areas from the saved masks (build/aral-numbers/water_<tag>.npy) without downloading again."""
    global SEA
    SEA = inside_1960()
    path = os.path.join(OUT, "areas.json")
    res = json.load(open(path))
    for tag in res:
        f = os.path.join(OUT, f"water_{tag}.npy")
        if os.path.exists(f):
            m = np.unpackbits(np.load(f))[:H * W].reshape(H, W).astype(bool)
            res[tag]["total_km2"], res[tag]["north_km2"] = round(km2(m)), round(km2(north_body(m)))
            print(tag, res[tag]["total_km2"], res[tag]["north_km2"])
    json.dump(res, open(path, "w"), indent=1)


def main():
    global SEA
    os.makedirs(OUT, exist_ok=True)
    SEA = inside_1960()
    print(f"1960s outline on this grid: {float((SEA * pix_km2[:, None]).sum()):,.0f} km2")
    print(f"grid {W}x{H}, {step * math.cos(math.radians(45.2)):.0f} m per pixel at 45 N, NDWI > {THRESH}")
    res = {}
    for tag, win in ((t, w) for t, w in WINDOWS.items() if len(sys.argv) < 2 or t in sys.argv[1:]):
        m, valid, used = water(win)
        total, north = km2(m), km2(north_body(m))
        np.save(os.path.join(OUT, f"water_{tag}.npy"), np.packbits(m))
        res[tag] = {"total_km2": round(total), "north_km2": round(north), "valid": round(float(valid.mean()), 3), "scenes": used}
        gap = float((((~valid) & SEA) * pix_km2[:, None]).sum())
        res[tag]["no_data_inside_km2"] = round(gap)
        print(f"{tag}: water {total:,.0f} km2 (north {north:,.0f}), no data on {gap:,.0f} km2 of the old sea, {len(used)} scenes")
        img = np.zeros((H, W, 3), np.uint8)
        img[valid] = (200, 180, 140)
        img[m] = (30, 80, 160)
        Image.fromarray(img).resize((W // 3, H // 3)).save(os.path.join(OUT, f"water_{tag}.png"))
    path = os.path.join(OUT, "areas.json")
    old = json.load(open(path)) if os.path.exists(path) else {}
    old.update(res)
    json.dump(old, open(path, "w"), indent=1)


if __name__ == "__main__":
    from_saved() if sys.argv[1:] == ["--from-saved"] else main()
