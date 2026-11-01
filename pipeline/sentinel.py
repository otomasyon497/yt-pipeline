"""Sentinel-2 true-colour mosaics (10 m) for close map views.

Scenes: ESA Copernicus Sentinel-2 L2A surface reflectance, read straight from the AWS Open Data copy
(Cloud-Optimised GeoTIFFs, found through Element 84's Earth Search STAC; no account needed). Only the window
and overview level a view needs are downloaded. Licence: Copernicus Sentinel data is free for any use,
including commercial; credit "Contains modified Copernicus Sentinel data <years>".
"""
import hashlib
import json
import math
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import date, timedelta
from pathlib import Path

import numpy as np
import rasterio
import rasterio.errors
import requests
import shapely
from PIL import Image, ImageEnhance, ImageFilter
from rasterio.enums import Resampling
from rasterio.transform import from_bounds
from affine import Affine
from rasterio.warp import reproject, transform_bounds
from rasterio.windows import Window
from rasterio.windows import from_bounds as from_bounds_window
from shapely.geometry import box as shp_box
from shapely.geometry import shape

from config import CACHE_DIR

STAC = "https://earth-search.aws.element84.com/v1/search"
EARTH = 40075016.68557849  # Web Mercator world width (m)
RECENT = ("2023-01-01", "2024-12-31")  # default window for "today" mosaics
CLOUD_SCL = {3, 8, 9, 10}  # cloud shadow, cloud medium/high, cirrus (Sen2Cor also flags bright sand: see mosaic)
GDAL_ENV = {"GDAL_DISABLE_READDIR_ON_OPEN": "EMPTY_DIR", "CPL_VSIL_CURL_ALLOWED_EXTENSIONS": ".tif",
            "GDAL_HTTP_MAX_RETRY": "4", "GDAL_HTTP_RETRY_DELAY": "2", "VSI_CACHE": "TRUE",
            "GDAL_HTTP_MERGE_CONSECUTIVE_RANGES": "YES", "GDAL_HTTP_MULTIPLEX": "YES", "GDAL_HTTP_VERSION": "2"}
BANDS = ("red", "green", "blue", "scl")
YEARS_USED: set[int] = set()  # for the credit line


def _post(body: dict) -> list[dict]:
    for attempt in range(4):
        try:
            r = requests.post(STAC, json=body, timeout=90)
            r.raise_for_status()
            return r.json()["features"]
        except requests.RequestException:
            if attempt == 3:
                raise
            time.sleep(4 * (attempt + 1))
    return []


def _search(lonlat_box, start: str, end: str, max_cloud: float) -> list[dict]:
    """Least-cloudy scenes per Sentinel-2 tile (MGRS) touching the box, best first.

    A single search returns at most a few hundred items and the clearest tiles fill it, so we first list the
    tiles (two recent months are enough to see every tile), then ask for the best scenes of each tile.
    """
    base = {"collections": ["sentinel-2-c1-l2a"], "bbox": list(lonlat_box), "datetime": f"{start}T00:00:00Z/{end}T23:59:59Z"}
    if start == end or (date.fromisoformat(end) - date.fromisoformat(start)).days <= 7:  # event imagery: few items
        return sorted(_post({**base, "limit": 200}), key=_rank)
    probe_end = date.fromisoformat(end)
    probe = _post({**base, "datetime": f"{probe_end - timedelta(days=45)}T00:00:00Z/{probe_end}T23:59:59Z", "limit": 250,
                   "fields": {"include": ["id", "properties.grid:code"], "exclude": ["assets", "links", "geometry"]}})
    tiles = sorted({i["properties"].get("grid:code") for i in probe if i["properties"].get("grid:code")})
    items = []
    for tile in tiles:
        # Full scenes first: thin slivers at the edge of an orbit report ~0 % cloud but cover almost nothing.
        query = {"grid:code": {"eq": tile}, "eo:cloud_cover": {"lt": max_cloud}}
        found = _post({**base, "limit": 5, "query": {**query, "s2:nodata_pixel_percentage": {"lt": 5}},
                       "sortby": [{"field": "properties.eo:cloud_cover", "direction": "asc"}]})
        items += found or _post({**base, "limit": 3, "query": query,
                                 "sortby": [{"field": "properties.eo:cloud_cover", "direction": "asc"}]})
    # Scenes from the same day (same orbit pass) match in colour: put the days that cover most tiles first.
    tiles_per_day: dict[str, set] = {}
    for i in items:
        tiles_per_day.setdefault(i["properties"]["datetime"][:10], set()).add(i["properties"].get("grid:code"))
    return sorted(items, key=lambda i: (-len(tiles_per_day[i["properties"]["datetime"][:10]]),
                                        i["properties"]["datetime"][:10], _rank(i)))


def _rank(item: dict) -> tuple:
    p = item["properties"]
    return (p.get("s2:nodata_pixel_percentage", 0) > 50, round(p.get("eo:cloud_cover", 100), 1),
            p.get("s2:nodata_pixel_percentage", 0))


def _candidates(items: list[dict], lonlat_box) -> list[dict]:
    """Public COG scenes touching the box, least cloudy first, one per tile and day."""
    out, seen = [], set()
    target = shp_box(*lonlat_box)
    for it in items:
        if not all(it["assets"].get(b, {}).get("href", "").startswith("https://") for b in BANDS[:3]):
            continue  # requester-pays JP2 copies are not readable without an AWS account
        key = (it["properties"].get("grid:code") or it["id"][4:10], it["properties"]["datetime"][:10])
        if key in seen or not shape(it["geometry"]).intersects(target):
            continue
        seen.add(key)
        out.append(it)
    return out


def _scale_offset(asset: dict) -> tuple[float, float]:
    b = (asset.get("raster:bands") or [{}])[0]
    return float(b.get("scale", 1e-4)), float(b.get("offset", 0.0))


def _read(href: str, dst: np.ndarray, dst_transform, ground_res: float, nearest: bool) -> None:
    """Warp the part of one COG band that covers `dst` (EPSG:3857) into it.

    Reads only the needed window, decimated to about the output resolution (GDAL then reads the matching
    overview), and reprojects that small array in memory.
    """
    h, w = dst.shape
    left, top = dst_transform * (0, 0)
    right, bottom = dst_transform * (w, h)
    with rasterio.open(href) as src:
        sb = transform_bounds("EPSG:3857", src.crs, left, bottom, right, top, densify_pts=21)
        win = from_bounds_window(*sb, transform=src.transform)
        win = win.intersection(Window(0, 0, src.width, src.height))
        if win.width < 1 or win.height < 1:
            return
        factor = max(1.0, ground_res / abs(src.res[0]) / 1.2)
        out_w, out_h = max(1, int(win.width / factor)), max(1, int(win.height / factor))
        data = src.read(1, window=win, out_shape=(out_h, out_w),
                        resampling=Resampling.nearest if nearest else Resampling.average)
        t = src.window_transform(win) * Affine.scale(win.width / out_w, win.height / out_h)
        reproject(data, dst, src_transform=t, src_crs=src.crs, dst_transform=dst_transform, dst_crs="EPSG:3857",
                  src_nodata=0, dst_nodata=0, resampling=Resampling.nearest if nearest else Resampling.bilinear)


def _tone(rgb: np.ndarray, valid: np.ndarray, stretch: bool) -> np.ndarray:
    """Reflectance -> display.

    Clear mosaics: light haze removal and a filmic shoulder (bright desert never clips).
    Event imagery (stretch=True, e.g. a dust storm day): percentile stretch on luminance, which brings the
    contrast back without changing the colours' balance.
    """
    out = np.empty_like(rgb)
    if stretch and valid.any():
        lum = rgb[..., 0] * 0.3 + rgb[..., 1] * 0.59 + rgb[..., 2] * 0.11
        lo, hi = np.percentile(lum[valid], [0.8, 99.7])
        out = np.clip((rgb - lo) / max(1e-6, hi - lo), 0, 1) ** (1 / 1.12)
        return out
    for c in range(3):
        ch = rgb[..., c]
        vals = ch[valid]
        dark = min(float(np.percentile(vals, 0.5)), 0.05) if vals.size else 0.0
        v = np.clip(ch - dark * 0.8, 0, None)
        out[..., c] = (1 - np.exp(-v / 0.17)) / (1 - np.exp(-0.62 / 0.17))
    return np.clip(out, 0, 1)


def mosaic(unit_box, px_width: int, out: Path, when: str | None = None, feather=None, mask=None) -> dict | None:
    """True-colour mosaic for a unit-Mercator box. `when` = "YYYY-MM-DD" for imagery of that day (events);
    otherwise the least cloudy recent scenes. Returns a raster placement like gibs.backdrop, or None."""
    from geo import mx as geo_mx, my as geo_my
    from maps import unit_box_to_lonlat  # local import: maps imports this module

    x0, y0, x1, y1 = max(0.0, unit_box[0]), max(0.0, unit_box[1]), min(1.0, unit_box[2]), min(1.0, unit_box[3])
    width = int(min(px_width, 4096))
    height = max(64, round(width * (y1 - y0) / (x1 - x0)))
    lonlat = unit_box_to_lonlat((x0, y0, x1, y1))
    mid_lat = (lonlat[1] + lonlat[3]) / 2
    ground_res = (x1 - x0) * EARTH / width * math.cos(math.radians(mid_lat))  # metres per output pixel on the ground
    key = hashlib.sha1(json.dumps([round(v, 7) for v in (x0, y0, x1, y1)] + [width, when, "v2"]).encode()).hexdigest()
    cache = CACHE_DIR / "s2" / f"{key}.png"
    meta = cache.with_suffix(".json")
    if not cache.exists():
        if when:
            d = date.fromisoformat(when)
            items = _search(lonlat, str(d - timedelta(days=1)), str(d + timedelta(days=1)), 70)
        else:
            items = _search(lonlat, *RECENT, 12)
        scenes = _candidates(items, lonlat)
        if not scenes:
            return None
        transform = from_bounds((x0 - 0.5) * EARTH, (0.5 - y1) * EARTH, (x1 - 0.5) * EARTH, (0.5 - y0) * EARTH, width, height)
        acc = np.full((height, width, 3), np.nan, dtype=np.float32)
        # Coarse check points: which ones any scene can cover (open sea has no Sentinel-2 data at all).
        gx, gy = np.meshgrid(np.linspace(lonlat[0], lonlat[2], 64), np.linspace(lonlat[1], lonlat[3], 36))
        gx, gy = gx.ravel(), gy.ravel()
        px = np.clip(((np.asarray(geo_mx(gx)) - x0) / (x1 - x0) * width).astype(int), 0, width - 1)
        py = np.clip(((np.asarray(geo_my(gy)) - y0) / (y1 - y0) * height).astype(int), 0, height - 1)
        feet = [shape(it["geometry"]) for it in scenes]
        coverable = np.zeros(gx.size, dtype=bool)
        for foot in feet:
            coverable |= shapely.contains_xy(foot, gx, gy)

        def read_band(it, name):
            buf = np.zeros((height, width), dtype=np.float32)
            if name not in it["assets"]:
                return buf
            for attempt in range(4):  # transient network errors (DNS, resets) happen on long runs
                try:
                    with rasterio.Env(**GDAL_ENV):
                        _read(it["assets"][name]["href"], buf, transform, ground_res, nearest=(name == "scl"))
                    return buf
                except rasterio.errors.RasterioIOError:
                    if attempt == 3:
                        raise
                    time.sleep(3 * (attempt + 1))
            return buf

        used = []
        with ThreadPoolExecutor(max_workers=4) as pool:
            for it, foot in zip(scenes, feet):
                missing = coverable & np.isnan(acc[py, px, 0])
                if not missing.any():
                    break
                if not shapely.contains_xy(foot, gx[missing], gy[missing]).any():
                    continue
                # Cloud mask only for scenes with real clouds, never for event imagery: Sen2Cor flags
                # bright desert and dust as cloud, which punched holes into otherwise clear scenes.
                use_scl = when is None and float(it["properties"].get("eo:cloud_cover", 0)) >= 2.0
                names = BANDS if use_scl else BANDS[:3]
                red, green, blue, *rest = pool.map(lambda b: read_band(it, b), names)
                bands = []
                for name, buf in zip(BANDS[:3], (red, green, blue)):
                    scale, offset = _scale_offset(it["assets"][name])
                    bands.append(np.where(buf > 0, buf * scale + offset, np.nan))
                rgb = np.stack(bands, -1)
                ok = np.isfinite(rgb).all(-1)
                if rest:
                    scl = rest[0]
                    ok &= ~np.isin(scl.astype(np.int32), list(CLOUD_SCL))
                fill = ok & np.isnan(acc[..., 0])
                if fill.any():
                    acc[fill] = rgb[fill]
                    used.append(it)
        scenes = used
        valid = np.isfinite(acc[..., 0])
        if not valid.any():
            return None
        filled = float(np.isfinite(acc[py, px, 0])[coverable].mean()) if coverable.any() else 0.0
        if filled < 0.9:  # a half-filled mosaic shows as a pale patch over Blue Marble: better none at all
            print(f"  sentinel-2: skipped, only {filled:.0%} of the view filled")
            return None
        disp = _tone(np.where(np.isfinite(acc), acc, 0), valid, stretch=when is not None)
        img = Image.fromarray((disp * 255).astype(np.uint8))
        img = ImageEnhance.Color(img).enhance(1.22)
        img = ImageEnhance.Brightness(img).enhance(0.92)
        img = img.filter(ImageFilter.UnsharpMask(radius=1.6, percent=55, threshold=2))
        alpha = Image.fromarray((valid * 255).astype(np.uint8))
        img.putalpha(alpha)
        cache.parent.mkdir(parents=True, exist_ok=True)
        img.save(cache)
        YEARS_USED.update(int(i["properties"]["datetime"][:4]) for i in scenes)
        meta.write_text(json.dumps({"years": sorted({int(i["properties"]["datetime"][:4]) for i in scenes}),
                                    "scenes": [i["id"] for i in scenes]}), encoding="utf-8")
        print(f"  sentinel-2: {len(scenes)} scene(s) for {width}x{height} px at {ground_res:.0f} m/px"
              f"{' on ' + when if when else ''}")
    else:
        YEARS_USED.update(json.loads(meta.read_text(encoding="utf-8"))["years"])
    img = Image.open(cache).convert("RGBA")
    if mask is not None:  # e.g. land only on wide views: sea tiles from different days look patchy
        m = np.asarray(mask((x0, y0, x1, y1), img.size), dtype=np.float32) / 255.0
        img.putalpha(Image.fromarray((np.asarray(img.getchannel("A"), dtype=np.float32) * m).astype(np.uint8)))
    if feather is not None:
        img = feather(img)
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out, "WEBP", quality=86, method=4)
    return {"src": out.name, "x0": x0, "y0": y0, "x1": x1, "y1": y1, "layer": "s2", "px": width}


def credit() -> str | None:
    if not YEARS_USED:
        return None
    return f"Satellite images: contains modified Copernicus Sentinel data {', '.join(map(str, sorted(YEARS_USED)))}."
