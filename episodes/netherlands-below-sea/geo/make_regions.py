"""Writes the painted-map regions of this episode (venv python -I: numpy, rasterio, shapely, pyproj).

belowsea.geojson: land of the Netherlands below 0 m in NOAA ETOPO 2022 (60 arc-second cells), clipped to the
Natural Earth 10m country (open water such as the IJsselmeer and Wadden Sea is not land in that polygon).
A coarse grid, so the map shape is an approximation; the published share (PBL 2010) is 26 % of the country below
sea level (NAP). Printed areas go into the fact check.
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
nl = geo.main_body(geo.country_geom(geo.country_code("Netherlands"), "10m"))
z, west, south = bathy._grid((3.2, 50.7, 7.3, 53.7))
north = south + z.shape[0] / 60
low = np.ascontiguousarray((z < 0.0)[::-1]).astype(np.uint8)
parts = [shape(g) for g, v in features.shapes(low, mask=low.astype(bool), transform=from_origin(west, north, 1 / 60, 1 / 60))]
g = shapely.union_all(parts).intersection(nl)
g = g.buffer(0.01, quad_segs=2).buffer(-0.01, quad_segs=2).simplify(0.005, preserve_topology=True)
area, nl_area = transform(fwd, g).area / 1e6, transform(fwd, nl).area / 1e6
(HERE / "belowsea.geojson").write_text(json.dumps({"type": "FeatureCollection", "features": [
    {"type": "Feature", "properties": {"name": "Below sea level (approx.)",
                                       "credit": "Our calculation from NOAA ETOPO 2022 (public domain); Natural Earth"},
     "geometry": mapping(g)}]}), encoding="utf-8")
print(f"below 0 m: {area:,.0f} km2 of {nl_area:,.0f} km2 land polygon = {100 * area / nl_area:.0f} %")
