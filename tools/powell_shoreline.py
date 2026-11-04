"""Lake Powell's extent at chosen elevations, from the USGS 2017 multibeam bathymetry (public domain).

Runs on Actions (tools.yml, tool "powell_shoreline"); usage: python tools/powell_shoreline.py OUT_DIR
- Finds the 2 m bathymetry GeoTIFF in the USGS data release (doi:10.5066/P90BU2VS) on ScienceBase, downloads it and
  reads it at about 20 m.
- For each level, every surveyed cell below the level counts as water (a pool cut off from the lake keeps its water).
  The survey covers the bed that was under water in autumn 2017 (lake at about 3,630 ft), enough for levels below that.
- Writes powell_<level>.geojson (lon/lat, one feature, "name" = the label) and summary.json (areas), and tries the
  2018 elevation-area-capacity tables (doi:10.5066/P9O3IPG3) for the published areas at the same levels.
Levels are Reclamation's operating elevations (NGVD29 feet); the survey is in NAVD88 metres. At Lake Powell
NAVD88 = NGVD29 + 2.91 ft (USGS SIR 2022-5017: full pool 3,700 ft = 3,702.91 ft NAVD88).
"""
import json
import sys
import time
import zipfile
from pathlib import Path

import numpy as np
import rasterio
import requests
import shapely
from rasterio import features
from rasterio.enums import Resampling
from rasterio.warp import transform_geom
from shapely.geometry import mapping, shape

BATHY_ITEM = "5b90140ae4b0702d0e80756d"  # 2017 multibeam bathymetry, 2 m
EAC_ITEM = "614ccd07d34e0df5fb9868e2"  # 2018 elevation-area-capacity tables
LEVELS_FT = {  # NGVD29 feet -> label
    3516.62: "Record low, 15 Sep 2026",
    3490.0: "3,490 ft: turbines stop",
    3370.0: "3,370 ft: dead pool",
}
DATUM_SHIFT_FT = 2.91
TARGET_RES_M = 20
SMOOTH_M = 30
MIN_PART_M2 = 50_000  # drop pools under 5 ha
SIMPLIFY_M = 15
UA = {"User-Agent": "yt-pipeline data tool (GitHub Actions)"}


def get(url: str, **kw) -> requests.Response:
    for attempt in range(4):
        try:
            r = requests.get(url, headers=UA, timeout=600, **kw)
            r.raise_for_status()
            return r
        except requests.RequestException as e:
            print(f"  {url}: {e}")
            if attempt == 3:
                raise
            time.sleep(10 * (attempt + 1))
    raise AssertionError


def item_files(item: str) -> list[dict]:
    r = get(f"https://www.sciencebase.gov/catalog/item/{item}?format=json")
    if "json" not in r.headers.get("content-type", ""):
        raise SystemExit(f"ScienceBase item {item} did not return JSON (blocked?): {r.text[:200]!r}")
    d = r.json()
    files = d.get("files", [])
    for f in files:
        print(f"  file {f.get('name')}  {f.get('size', 0) / 1e6:,.1f} MB")
    for child in get(f"https://www.sciencebase.gov/catalog/items?parentId={item}&format=json&max=50").json().get("items", []):
        print(f"  child {child.get('id')}: {child.get('title')}")
    return files


def download(url: str, dest: Path) -> Path:
    with requests.get(url, headers=UA, stream=True, timeout=600) as r:
        r.raise_for_status()
        with open(dest, "wb") as f:
            for chunk in r.iter_content(1 << 20):
                f.write(chunk)
    print(f"  downloaded {dest.name}: {dest.stat().st_size / 1e6:,.1f} MB")
    return dest


def bathymetry(work: Path) -> Path:
    files = item_files(BATHY_ITEM)
    pick = [f for f in files if f.get("name", "").lower().endswith((".tif", ".tiff", ".zip")) and "bathy" in f.get("name", "").lower()]
    if not pick:
        raise SystemExit("no bathymetry GeoTIFF or zip in the ScienceBase item")
    f = max(pick, key=lambda f: f.get("size", 0))
    path = download(f["url"], work / f["name"])
    if path.suffix.lower() == ".zip":
        with zipfile.ZipFile(path) as z:
            tifs = [n for n in z.namelist() if n.lower().endswith((".tif", ".tiff"))]
            z.extract(tifs[0], work)
            path = work / tifs[0]
    return path


def eac_areas(levels_navd_ft: list[float]) -> dict:
    """Published 2018 areas (acres) and capacities (acre-feet) at the given NAVD88 elevations, if reachable."""
    out = {}
    try:
        for f in item_files(EAC_ITEM):
            if not f.get("name", "").lower().endswith(".csv"):
                continue
            text = get(f["url"]).text
            rows = [line.split(",") for line in text.splitlines()]
            head = [h.strip().lower() for h in rows[0]]
            print(f"  {f['name']}: columns {head}")
            out[f["name"]] = {"columns": head, "rows": len(rows) - 1}
            ie = next((i for i, h in enumerate(head) if "elev" in h), None)
            ia = next((i for i, h in enumerate(head) if "area" in h), None)
            ic = next((i for i, h in enumerate(head) if "capac" in h or "volume" in h or "storage" in h), None)
            if ie is None:
                continue
            table = []
            for r in rows[1:]:
                try:
                    table.append([float(r[ie]), float(r[ia]) if ia is not None else None, float(r[ic]) if ic is not None else None])
                except (ValueError, IndexError):
                    pass
            for lv in levels_navd_ft:
                best = min(table, key=lambda t: abs(t[0] - lv), default=None)
                if best:
                    out[f["name"]][f"{lv:.2f}"] = {"elevation": best[0], "area": best[1], "capacity": best[2]}
    except (SystemExit, requests.RequestException) as e:
        out["error"] = str(e)
    return out


def main(out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    work = Path("work")
    work.mkdir(exist_ok=True)
    tif = bathymetry(work)
    summary = {"source": "USGS 2017 multibeam bathymetry of Lake Powell, doi:10.5066/P90BU2VS", "levels": {}}
    with rasterio.open(tif) as src:
        print(f"  {tif.name}: {src.width} x {src.height}, res {src.res}, crs {src.crs}, nodata {src.nodata}, "
              f"overviews {src.overviews(1)}, units {src.units}, tags {src.tags()}")
        f = max(1, round(TARGET_RES_M / src.res[0]))
        shape_ = (src.height // f, src.width // f)
        t0 = time.time()
        z = src.read(1, out_shape=shape_, resampling=Resampling.average, masked=True)
        print(f"  read at 1/{f}: {shape_} in {time.time() - t0:.0f} s; z {float(z.min()):.2f} .. {float(z.max()):.2f}")
        transform = src.transform * src.transform.scale(src.width / shape_[1], src.height / shape_[0])
        crs = src.crs
        cell_m2 = abs(transform.a * transform.e)
    valid = ~np.ma.getmaskarray(z)
    zz = np.ma.filled(z, np.inf)
    # Elevations in metres (NAVD88) unless the values look like feet.
    in_feet = float(np.median(zz[valid])) > 2000
    print(f"  values look like {'feet' if in_feet else 'metres'} (median {float(np.median(zz[valid])):.1f})")
    for level_ft, label in sorted(LEVELS_FT.items(), reverse=True):
        navd_ft = level_ft + DATUM_SHIFT_FT
        level = navd_ft if in_feet else navd_ft * 0.3048
        water = valid & (zz < level)
        raw_km2 = water.sum() * cell_m2 / 1e6
        parts = [shape(g) for g, v in features.shapes(water.astype(np.uint8), mask=water, transform=transform) if v == 1]
        g = shapely.union_all(parts).buffer(SMOOTH_M, quad_segs=2).buffer(-SMOOTH_M, quad_segs=2)
        polys = [p for p in getattr(g, "geoms", [g]) if p.area >= MIN_PART_M2]
        if not polys:
            print(f"  {level_ft} ft: no water left in the survey (raw {raw_km2:,.2f} km2)")
            continue
        g = shapely.MultiPolygon(polys).simplify(SIMPLIFY_M, preserve_topology=True)
        km2 = g.area / 1e6
        ll = transform_geom(crs, "EPSG:4326", mapping(g), precision=5)
        name = f"powell_{int(round(level_ft))}"
        fc = {"type": "FeatureCollection", "features": [{"type": "Feature", "geometry": ll, "properties": {
            "name": label, "level_ft_ngvd29": level_ft, "area_km2": round(km2, 1), "area_acres": round(km2 * 247.105)}}]}
        (out_dir / f"{name}.geojson").write_text(json.dumps(fc, separators=(",", ":")))
        size_kb = (out_dir / f"{name}.geojson").stat().st_size / 1e3
        print(f"  {level_ft} ft: {km2:,.1f} km2 ({km2 * 247.105:,.0f} acres) in {len(polys)} parts "
              f"(raw {raw_km2:,.1f} km2), {size_kb:,.0f} KB")
        summary["levels"][str(level_ft)] = {"label": label, "navd88_ft": navd_ft, "area_km2": round(km2, 1),
                                           "area_acres": round(km2 * 247.105), "parts": len(polys), "raw_km2": round(raw_km2, 1)}
    summary["eac_2018"] = eac_areas([lv + DATUM_SHIFT_FT for lv in LEVELS_FT])
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main(Path(sys.argv[1] if len(sys.argv) > 1 else "out"))
