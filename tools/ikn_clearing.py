"""Own measurement for the jakarta-sinking episode: forest turned to bare ground or buildings in Nusantara's core zone.

A fixed 6 x 6 km box centred on the Garuda Palace (OpenStreetMap: lon 116.6962, lat -0.9587), East Kalimantan.
Sentinel-2 L2A surface reflectance (10 m; Element 84 Earth Search, the Collection-1 reprocessing first and the
original L2A archive where Collection 1 has gaps, as in 2022). For each period it reads up to eight of the least
cloudy days, keeps only pixels the scene classification (SCL) calls vegetation, bare soil or water (clouds, shadows,
cirrus, unclassified, saturated are dropped), and takes the per-pixel median NDVI over the clear observations.
Cleared = NDVI > 0.6 (vegetated) in the baseline, NDVI < 0.3 (bare / built) in that period.
Usage: python -I tools/ikn_clearing.py <repo root> <out.json> [png dir]
"""
import json
import sys
from pathlib import Path

import numpy as np
import rasterio
from PIL import Image, ImageDraw
from rasterio.transform import from_bounds

ROOT = Path(sys.argv[1])
sys.path.insert(0, str(ROOT / "pipeline"))
import sentinel  # noqa: E402
from sentinel import EARTH, GDAL_ENV, _read, _scale_offset  # noqa: E402

PALACE = (116.6962, -0.9587)
HALF = 0.027  # degrees: 6.0 km at the equator
BOX = (PALACE[0] - HALF, PALACE[1] - HALF, PALACE[0] + HALF, PALACE[1] + HALF)
PERIODS = {  # name: windows tried in order until the box is covered
    "baseline_2019": [("2019-01-01", "2019-08-25"), ("2018-06-01", "2018-12-31")],
    "2022": [("2022-07-01", "2022-12-31")],
    "2024": [("2024-05-01", "2024-10-31"), ("2024-01-01", "2024-12-31")],
    "2026": [("2026-04-01", "2026-11-10")],
}
PX = 10.0
MAX_DAYS = 8
CLEAR_SCL = (4, 5, 6)  # vegetation, not-vegetated (bare / built), water
VEG, BARE = 0.6, 0.3


def merc(lon, lat):
    return lon / 360 * EARTH, np.log(np.tan(np.pi / 4 + np.radians(lat) / 2)) / (2 * np.pi) * EARTH


X0, Y0 = merc(BOX[0], BOX[1])
X1, Y1 = merc(BOX[2], BOX[3])
K = np.cos(np.radians((BOX[1] + BOX[3]) / 2))
W = int(round((X1 - X0) * K / PX))
H = int(round((Y1 - Y0) * K / PX))
TRANSFORM = from_bounds(X0, Y0, X1, Y1, W, H)


def search(start, end):
    found = {}
    for coll in ("sentinel-2-c1-l2a", "sentinel-2-l2a"):
        items = sentinel._post({"collections": [coll], "bbox": list(BOX), "limit": 300,
                                "datetime": f"{start}T00:00:00Z/{end}T23:59:59Z",
                                "query": {"eo:cloud_cover": {"lt": 70}}})
        for it in items:
            if not all(it["assets"].get(b, {}).get("href", "").startswith("https://") for b in ("red", "nir", "scl")):
                continue
            key = (it["properties"]["datetime"][:10], it["properties"].get("grid:code") or it["id"][4:10])
            found.setdefault(key, (coll, it))  # Collection 1 first
    days = {}
    for (day, _), (coll, it) in found.items():
        days.setdefault(day, []).append((coll, it))
    return sorted(days.items(), key=lambda d: np.mean([i["properties"]["eo:cloud_cover"] for _, i in d[1]]))


def read_band(it, name):
    buf = np.zeros((H, W), dtype=np.float32)
    with rasterio.Env(**GDAL_ENV):
        _read(it["assets"][name]["href"], buf, TRANSFORM, PX, nearest=name == "scl")
    return buf


def read_day(group):
    """One day's scenes (the box spans two tiles) into NDVI and RGB, NaN where not clear."""
    ndvi = np.full((H, W), np.nan, np.float32)
    rgb = np.full((H, W, 3), np.nan, np.float32)
    for _, it in group:
        scl = read_band(it, "scl")
        fill = np.isin(scl.astype(int), CLEAR_SCL) & np.isnan(ndvi)
        if not fill.any():
            continue
        refl = {}
        for b in ("red", "nir", "green", "blue"):
            raw = read_band(it, b)
            scale, offset = _scale_offset(it["assets"][b])
            refl[b] = np.where(raw > 0, raw * scale + offset, np.nan)
        nd = (refl["nir"] - refl["red"]) / np.maximum(refl["nir"] + refl["red"], 1e-4)
        fill &= np.isfinite(nd)
        ndvi[fill] = nd[fill]
        for c, b in enumerate(("red", "green", "blue")):
            rgb[..., c][fill] = refl[b][fill]
    return ndvi, rgb


def period(name):
    stack, rgbs, used = [], [], []
    for start, end in PERIODS[name]:
        for day, group in search(start, end)[:3 * MAX_DAYS]:
            if len(used) >= MAX_DAYS:
                break
            try:
                nd, rgb = read_day(group)
            except Exception as exc:
                print("  skip", day, str(exc)[:80], flush=True)
                continue
            share = float(np.isfinite(nd).mean())
            if share < 0.15:
                continue
            stack.append(nd)
            rgbs.append(rgb)
            used.append({"date": day, "scenes": [i["id"] for _, i in group], "collection": group[0][0],
                         "clear_share": round(share, 3)})
            print(" ", name, day, f"{share:.0%} clear", flush=True)
        cover = float(np.isfinite(np.array(stack)).any(0).mean()) if stack else 0.0
        if cover >= 0.97:
            break
    arr = np.array(stack)
    with np.errstate(all="ignore"):
        return {"days": used, "ndvi": np.nanmedian(arr, 0), "rgb": np.nanmedian(np.array(rgbs), 0),
                "n_obs": np.isfinite(arr).sum(0)}


def save_png(rgb, path, title):
    disp = np.clip(np.nan_to_num(rgb) / 0.22, 0, 1) ** (1 / 1.4)
    img = Image.fromarray((disp * 255).astype(np.uint8))
    d = ImageDraw.Draw(img)
    px = (PALACE[0] - BOX[0]) / (BOX[2] - BOX[0]) * W
    my = merc(*PALACE)[1]
    py = (Y1 - my) / (Y1 - Y0) * H
    d.ellipse([px - 12, py - 12, px + 12, py + 12], outline=(255, 40, 40), width=2)
    d.text((8, 8), title, fill=(255, 255, 255))
    img.save(path)


out_path = Path(sys.argv[2])
png_dir = Path(sys.argv[3]) if len(sys.argv) > 3 else None
res = {name: period(name) for name in PERIODS}
ha = PX * PX / 1e4
base = res["baseline_2019"]
veg0 = base["ndvi"] > VEG
out = {"box": BOX, "box_km": [round(W * PX / 1000, 2), round(H * PX / 1000, 2)], "box_ha": round(W * H * ha, 1),
       "palace": PALACE, "thresholds": {"vegetated_ndvi_gt": VEG, "bare_or_built_ndvi_lt": BARE}, "periods": {}}
for name, r in res.items():
    nd = r["ndvi"]
    valid = np.isfinite(nd) & np.isfinite(base["ndvi"])
    rec = {"days": r["days"], "valid_share": round(float(np.isfinite(nd).mean()), 4),
           "vegetated_ha": round(float((nd > VEG).sum()) * ha, 1),
           "bare_or_built_ha": round(float((nd < BARE).sum()) * ha, 1),
           "median_ndvi": round(float(np.nanmedian(nd)), 3)}
    if name != "baseline_2019":
        rec["cleared_since_baseline_ha"] = round(float((veg0 & (nd < BARE) & valid).sum()) * ha, 1)
        # pixels that could not be compared (no clear observation in one of the two periods)
        rec["not_comparable_ha"] = round(float((~valid).sum()) * ha, 1)
    out["periods"][name] = rec
    print(name, {k: v for k, v in rec.items() if k != "days"}, flush=True)
    if png_dir is not None:
        save_png(r["rgb"], png_dir / f"ikn_{name}.png", f"{name}  ({r['days'][0]['date'] if r['days'] else '-'} ...)")
out["method"] = (
    "Sentinel-2 L2A surface reflectance (ESA Copernicus, via Element 84 Earth Search on AWS; Collection-1 "
    "reprocessing, original L2A archive where Collection 1 has no scenes), 10 m. Box: 6 x 6 km centred on the Garuda "
    "Palace (OpenStreetMap position). Per period: up to 8 of the least cloudy days; pixels kept only where the Sen2Cor "
    "scene classification (SCL) says vegetation, bare/built or water; per-pixel median NDVI over the clear "
    "observations. Vegetated = NDVI > 0.6, bare or built = NDVI < 0.3. cleared_since_baseline_ha = pixels vegetated in "
    "the baseline (Jan - 25 Aug 2019, before the 26 Aug 2019 announcement) and bare/built in that period. CAVEATS: much "
    "of the zone was an industrial eucalyptus/acacia plantation (not natural forest) before 2019, so 'vegetation' "
    "includes plantation trees and some clearing comes from plantation harvest cycles, not only construction. Sen2Cor "
    "sometimes calls bright new roofs and concrete 'cloud', which removes them from a day (the median uses the other "
    "days). Ground in between NDVI 0.3 and 0.6 (grass, young regrowth, landscaped lawns) counts as neither.")
out_path.write_text(json.dumps(out, indent=1), encoding="utf-8")
