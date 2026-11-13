"""Landsat true colour (Collection 2 Level-2 surface reflectance) for before/after wipes back to 1982.

Scenes come from Microsoft Planetary Computer's STAC API (free, no account: asset URLs are signed with a short-lived
token from its SAS endpoint). Landsat 4-5 TM (1982-2012), 7 ETM+ only before its scan-line failure (31 May 2003),
8-9 OLI (2013 on). One day per side: the least cloudy day whose scenes (one path, consecutive rows) cover the whole
box, so a wipe never shows a seam between days. The tone curve is Sentinel-2's (sentinel._tone), so a Landsat image
looks like the rest of the map. Landsat data are public domain, courtesy of the U.S. Geological Survey.
"""
import hashlib
import json
import math
import time
from pathlib import Path

import numpy as np
import rasterio
import requests
import shapely
from PIL import Image, ImageEnhance, ImageFilter
from rasterio.transform import from_bounds
from shapely.geometry import shape

from config import CACHE_DIR
from sentinel import EARTH, GDAL_ENV, _read, _tone

STAC = "https://planetarycomputer.microsoft.com/api/stac/v1/search"
SAS = "https://planetarycomputer.microsoft.com/api/sas/v1/token/landsat-c2-l2"
# Signed URLs end in a query string, so GDAL's extension filter must not apply.
ENV = {k: v for k, v in GDAL_ENV.items() if k != "CPL_VSIL_CURL_ALLOWED_EXTENSIONS"}
YEARS_USED: set[int] = set()
_TOKEN: dict = {}


def _post(body: dict) -> list[dict]:
    for attempt in range(4):
        try:
            r = requests.post(STAC, json=body, timeout=90)
            r.raise_for_status()
            return r.json().get("features", [])
        except requests.RequestException:
            if attempt == 3:
                raise
            time.sleep(3 * (attempt + 1))
    return []


def _token() -> str:
    if not _TOKEN or _TOKEN["until"] < time.time():
        _TOKEN.update(tok=requests.get(SAS, timeout=60).json()["token"], until=time.time() + 1800)
    return _TOKEN["tok"]


def _scale_offset(asset: dict) -> tuple[float, float]:
    b = (asset.get("raster:bands") or [{}])[0]
    return float(b.get("scale", 2.75e-5)), float(b.get("offset", -0.2))  # Collection 2 Level-2 surface reflectance


def mosaic(unit_box, px_width: int, out: Path, when: str, feather=None) -> dict | None:
    """True colour for a unit-Mercator box from one Landsat day in `when` ("YYYY-MM-DD/YYYY-MM-DD" or a day).
    Returns a raster placement like sentinel.mosaic (with the scene "dates"), or None when no day covers the box."""
    from geo import mx as geo_mx, my as geo_my  # noqa: F401  (same projection helpers as sentinel)
    from maps import unit_box_to_lonlat  # local import: maps imports this module

    x0, y0, x1, y1 = max(0.0, unit_box[0]), max(0.0, unit_box[1]), min(1.0, unit_box[2]), min(1.0, unit_box[3])
    width = int(min(px_width, 4096))
    height = max(64, round(width * (y1 - y0) / (x1 - x0)))
    lonlat = unit_box_to_lonlat((x0, y0, x1, y1))
    mid_lat = (lonlat[1] + lonlat[3]) / 2
    ground_res = (x1 - x0) * EARTH / width * math.cos(math.radians(mid_lat))
    key = hashlib.sha1(json.dumps([round(v, 7) for v in (x0, y0, x1, y1)] + [width, when, "landsat-v2"]).encode()).hexdigest()
    cache = CACHE_DIR / "landsat" / f"{key}.png"
    meta = cache.with_suffix(".json")
    if not cache.exists():
        start, end = when.split("/") if "/" in when else (when, when)
        # A bare date range "D/D" is a zero-length instant for STAC: make it span whole days.
        start, end = (start if "T" in start else f"{start}T00:00:00Z"), (end if "T" in end else f"{end}T23:59:59Z")
        platforms = ["landsat-4", "landsat-5", "landsat-8", "landsat-9"] + (["landsat-7"] if start < "2003-05-31" else [])
        items = _post({"collections": ["landsat-c2-l2"], "bbox": list(lonlat), "datetime": f"{start}/{end}", "limit": 250,
                       "query": {"eo:cloud_cover": {"lt": 40}, "platform": {"in": platforms}}})
        gx, gy = np.meshgrid(np.linspace(lonlat[0], lonlat[2], 48), np.linspace(lonlat[1], lonlat[3], 27))
        gx, gy = gx.ravel(), gy.ravel()
        days: dict[tuple, list] = {}
        for it in items:
            if it["properties"].get("platform") == "landsat-7" and it["properties"]["datetime"][:10] >= "2003-05-31":
                continue
            days.setdefault((it["properties"]["datetime"][:10], it["properties"].get("platform")), []).append(it)

        def covers(group) -> bool:
            c = np.zeros(gx.size, dtype=bool)
            for it in group:
                c |= shapely.contains_xy(shape(it["geometry"]), gx, gy)
            return bool(c.mean() >= 0.995)

        ranked = sorted(days.values(), key=lambda g: max(float(i["properties"].get("eo:cloud_cover", 100)) for i in g))
        group = next((g for g in ranked if covers(g)), None)
        if group is None:
            print(f"  landsat: no single day covers the view in {when}")
            return None
        transform = from_bounds((x0 - 0.5) * EARTH, (0.5 - y1) * EARTH, (x1 - 0.5) * EARTH, (0.5 - y0) * EARTH, width, height)
        acc = np.full((height, width, 3), np.nan, dtype=np.float32)
        tok = _token()
        for it in sorted(group, key=lambda i: float(i["properties"].get("eo:cloud_cover", 100))):
            bands = []
            for name in ("red", "green", "blue"):
                buf = np.zeros((height, width), dtype=np.float32)
                asset = it["assets"][name]
                for attempt in range(4):
                    try:
                        with rasterio.Env(**ENV):
                            _read(f"{asset['href']}?{tok}", buf, transform, ground_res, nearest=False)
                        break
                    except rasterio.errors.RasterioIOError:
                        if attempt == 3:
                            raise
                        time.sleep(3 * (attempt + 1))
                scale, offset = _scale_offset(asset)
                bands.append(np.where(buf > 0, buf * scale + offset, np.nan))
            rgb = np.stack(bands, -1)
            fill = np.isfinite(rgb).all(-1) & np.isnan(acc[..., 0])
            acc[fill] = rgb[fill]
        valid = np.isfinite(acc[..., 0])
        if valid.mean() < 0.9:
            print(f"  landsat: only {valid.mean():.0%} of the view filled on {group[0]['properties']['datetime'][:10]}")
            return None
        disp = _tone(np.where(np.isfinite(acc), acc, 0), valid, stretch=False)
        img = Image.fromarray((disp * 255).astype(np.uint8))
        img = ImageEnhance.Color(img).enhance(1.22)
        img = img.filter(ImageFilter.UnsharpMask(radius=1.6, percent=55, threshold=2))
        img.putalpha(Image.fromarray((valid * 255).astype(np.uint8)))
        cache.parent.mkdir(parents=True, exist_ok=True)
        img.save(cache)
        day = group[0]["properties"]["datetime"][:10]
        meta.write_text(json.dumps({"dates": [day], "years": [int(day[:4])], "scenes": [i["id"] for i in group]}),
                        encoding="utf-8")
        print(f"  landsat: {group[0]['properties'].get('platform')} {day}, {len(group)} scene(s), {width}x{height} px "
              f"at {ground_res:.0f} m/px")
    meta_d = json.loads(meta.read_text(encoding="utf-8"))
    YEARS_USED.update(meta_d["years"])
    img = Image.open(cache).convert("RGBA")
    if feather is not None:
        img = feather(img)
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out, "WEBP", quality=86, method=4)
    return {"src": out.name, "x0": x0, "y0": y0, "x1": x1, "y1": y1, "layer": "s2", "px": width, "dates": meta_d["dates"]}


def credit() -> str | None:
    if not YEARS_USED:
        return None
    return (f"Landsat images ({', '.join(map(str, sorted(YEARS_USED)))}): courtesy of the U.S. Geological Survey "
            "(public domain), via Microsoft Planetary Computer.")
