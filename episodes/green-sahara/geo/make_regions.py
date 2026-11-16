"""Writes the painted-map regions of this episode (venv python -I: numpy, rasterio, shapely, pyproj).

megachad.geojson: Lake Mega-Chad at its Holocene highstand, drawn as every NOAA ETOPO 2022 (60 arc-second) cell
below 320 m that connects to today's Lake Chad. 320 m is where this grid fills the basin without spilling south
(325 m leaks across the Mayo Kebbi divide into the Benue lowlands); published shorelines are about 320-330 m and
published areas about 340,000-361,000 km2 (research.md). Our shape is an approximation for the map, not a survey.
sahara.geojson: Natural Earth "geography regions" polygon SAHARA (a generalised label region).
"""
import json
import sys
from pathlib import Path

import numpy as np
import shapely
from pyproj import Transformer
from rasterio import features
from rasterio.transform import from_origin
from shapely.geometry import mapping, shape
from shapely.ops import transform

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parents[2] / "pipeline"))
import bathy  # noqa: E402
import geo  # noqa: E402

fwd = Transformer.from_crs(4326, 6933, always_xy=True).transform  # equal-area
LEVEL = 320.0
z, west, south = bathy._grid((8.0, 5.0, 26.0, 22.0))
seed = (int((13.3 - south) * 60), int((14.2 - west) * 60))  # open water of today's Lake Chad
lake = bathy._connected(z < LEVEL, seed)
north = south + z.shape[0] / 60
grid = np.ascontiguousarray(lake[::-1]).astype(np.uint8)
parts = [shape(g) for g, v in features.shapes(grid, mask=grid.astype(bool), transform=from_origin(west, north, 1 / 60, 1 / 60))]
g = shapely.union_all(parts).buffer(0.03, quad_segs=2).buffer(-0.03, quad_segs=2)
g = max(getattr(g, "geoms", [g]), key=lambda p: p.area).simplify(0.01, preserve_topology=True)
(HERE / "megachad.geojson").write_text(json.dumps({"type": "FeatureCollection", "features": [
    {"type": "Feature", "properties": {"name": "Lake Mega-Chad (approx.)",
                                       "credit": "Shoreline: our calculation from NOAA ETOPO 2022 (public domain)"},
     "geometry": mapping(g)}]}), encoding="utf-8")
print(f"megachad (<{LEVEL:g} m): {transform(fwd, g).area / 1e6:,.0f} km2, bounds {tuple(round(b, 1) for b in g.bounds)}")

regions = {p.get("name") or p.get("NAME"): gg for p, gg in geo.ne_geoms("ne_10m_geography_regions_polys")}
sah = shapely.make_valid(regions["SAHARA"].simplify(0.03))
(HERE / "sahara.geojson").write_text(json.dumps({"type": "FeatureCollection", "features": [
    {"type": "Feature", "properties": {"name": "Sahara", "credit": "Natural Earth (public domain)"}, "geometry": mapping(sah)}]}), encoding="utf-8")
print(f"sahara: {transform(fwd, sah).area / 1e6:,.0f} km2")
