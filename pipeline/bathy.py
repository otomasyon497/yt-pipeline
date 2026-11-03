"""Lake and inland-sea beds from NOAA ETOPO 2022 (60 arc-second bed elevation, public domain).

`exposed(basin, drop)` returns the bed a basin would lose if its surface fell by `drop` metres, as lon/lat polygons
for map highlights ("seafloor:caspian:10"). The grid is fetched once per basin through NOAA's OPeNDAP server (an
ASCII subset of a few MB) and cached in CACHE_DIR/etopo. Water = cells below the level that connect to a seed point
in deep water, so dry depressions on land (e.g. Karagiye, -132 m, next to the Caspian) never count as sea.
Coastal plains are where global grids are weakest: use the result for shapes and orders of magnitude, and quote
published studies for exact areas.
"""
import hashlib
import re
import time
from collections import deque

import numpy as np
import requests
import shapely
from rasterio import features
from rasterio.transform import from_origin
from shapely.geometry import shape

from config import CACHE_DIR

ETOPO = ("https://www.ngdc.noaa.gov/thredds/dodsC/global/ETOPO2022/60s/60s_bed_elev_netcdf/"
         "ETOPO_2022_v1_60s_N90W180_bed.nc")
CREDIT = ("Lake and seafloor depths: NOAA NCEI ETOPO 2022 Global Relief Model (public domain); future shorelines "
          "are our calculation.")
# basin -> ((lon0, lat0, lon1, lat1), seed (lon, lat) in deep water, surface level in metres the drops count from)
BASINS = {
    # -29.3 m: Kazakh sector mean for 2025, -29.27 m (Kazakh Research Institute of the Caspian Sea, Euronews 7 Oct 2026)
    "caspian": ((46.0, 36.0, 55.5, 47.8), (50.0, 42.0), -29.3),
}
MIN_PART_DEG2 = 0.01  # drop specks under ~80 km2
SMOOTH_DEG = 0.03  # close gaps of a cell or two so the outline reads as one shore
_GEOMS: dict = {}


def _grid(box: tuple[float, float, float, float]) -> tuple[np.ndarray, float, float]:
    """Bed elevation (m) for a lon/lat box, rows south -> north; returns (z, west edge, south edge)."""
    lon0, lat0, lon1, lat1 = box
    r0, r1 = round((lat0 + 90) * 60), round((lat1 + 90) * 60) - 1
    c0, c1 = round((lon0 + 180) * 60), round((lon1 + 180) * 60) - 1
    url = f"{ETOPO}.ascii?z[{r0}:1:{r1}][{c0}:1:{c1}]"
    cache = CACHE_DIR / "etopo" / (hashlib.sha1(url.encode()).hexdigest() + ".npy")
    if cache.exists():
        z = np.load(cache)
    else:
        for attempt in range(4):
            try:
                r = requests.get(url, timeout=300)
                r.raise_for_status()
                break
            except requests.RequestException:
                if attempt == 3:
                    raise
                time.sleep(5 * (attempt + 1))
        rows = [line for line in r.text.splitlines() if re.match(r"^\[\d+\], ", line)]
        z = np.array([[float(v) for v in line.split(", ")[1:]] for line in rows], dtype=np.float32)
        if z.shape != (r1 - r0 + 1, c1 - c0 + 1):
            raise RuntimeError(f"ETOPO subset has shape {z.shape}, expected {(r1 - r0 + 1, c1 - c0 + 1)}")
        cache.parent.mkdir(parents=True, exist_ok=True)
        np.save(cache, z)
    return z, -180 + c0 / 60, -90 + r0 / 60


def _connected(below: np.ndarray, seed: tuple[int, int]) -> np.ndarray:
    """Cells of `below` reachable from `seed` through edge neighbours."""
    if not below[seed]:
        raise ValueError(f"bathy seed {seed} is not under water at this level")
    h, w = below.shape
    flat = below.ravel().tolist()
    out = [False] * (h * w)
    start = seed[0] * w + seed[1]
    out[start] = True
    q = deque([start])
    while q:
        k = q.popleft()
        i, j = divmod(k, w)
        for n, ok in ((k + w, i + 1 < h), (k - w, i > 0), (k + 1, j + 1 < w), (k - 1, j > 0)):
            if ok and flat[n] and not out[n]:
                out[n] = True
                q.append(n)
    return np.array(out, dtype=bool).reshape(h, w)


def km2(geom) -> float:
    """Approximate area of a lon/lat (Multi)Polygon in km2."""
    return float(sum(p.area * 111.32 ** 2 * np.cos(np.radians(p.centroid.y)) for p in getattr(geom, "geoms", [geom])))


def exposed(basin: str, drop: float):
    """Lon/lat (Multi)Polygon of the bed that falls dry if `basin`'s level drops by `drop` metres."""
    key = (basin, float(drop))
    if key in _GEOMS:
        return _GEOMS[key]
    if basin not in BASINS:
        raise ValueError(f"unknown basin {basin!r} (known: {', '.join(BASINS)})")
    if not 0 < drop <= 200:
        raise ValueError(f"seafloor drop must be between 0 and 200 m, not {drop}")
    box, (slon, slat), level = BASINS[basin]
    z, west, south = _grid(box)
    seed = (int((slat - south) * 60), int((slon - west) * 60))
    gone = _connected(z < level, seed) & ~_connected(z < level - drop, seed)
    if not gone.any():
        raise ValueError(f"seafloor:{basin}:{drop:g} exposes nothing")
    north = south + z.shape[0] / 60
    grid = np.ascontiguousarray(gone[::-1]).astype(np.uint8)  # rasterio wants north-up rows
    parts = [shape(g) for g, v in features.shapes(grid, mask=grid.astype(bool), transform=from_origin(west, north, 1 / 60, 1 / 60))
             if v == 1]
    g = shapely.union_all(parts).buffer(SMOOTH_DEG, quad_segs=2).buffer(-SMOOTH_DEG, quad_segs=2)
    polys = [p for p in getattr(g, "geoms", [g]) if p.area >= MIN_PART_DEG2]
    if not polys:
        raise ValueError(f"seafloor:{basin}:{drop:g} exposes only specks smaller than {MIN_PART_DEG2} square degrees")
    g = (shapely.MultiPolygon(polys) if len(polys) > 1 else polys[0]).simplify(0.01, preserve_topology=True)
    print(f"  seafloor {basin} -{drop:g} m: about {km2(g):,.0f} km2 of bed falls dry ({len(polys)} parts)")
    _GEOMS[key] = g
    return g
