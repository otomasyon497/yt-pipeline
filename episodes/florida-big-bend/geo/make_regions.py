"""Writes the painted-map regions of florida-big-bend (run with the venv python: shapely, rasterio, pyproj).

shallow10.geojson: Gulf and Atlantic seafloor off Florida shallower than 10 m (NOAA ETOPO 2022 60 arc-second bed
elevation, sea cells only, connected to the open Gulf). bigbend_coast.geojson: Florida land within 25 km of the Gulf
shore between the Ochlockonee River mouth (84.4 W) and the Withlacoochee mouth (29.0 N), the stretch the Big Bend
Seagrasses Aquatic Preserve faces. Both print their areas for the fact check.
"""
import json
import sys
from pathlib import Path

import numpy as np
import shapely
from pyproj import Transformer
from rasterio import features
from rasterio.transform import from_origin
from shapely.geometry import box, mapping, shape
from shapely.ops import transform

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parents[2] / "pipeline"))
import bathy  # noqa: E402
import geo  # noqa: E402

ETOPO_CREDIT = "Seafloor depth: NOAA NCEI ETOPO 2022 (public domain); shallow area is our calculation"
NE = "Natural Earth (public domain)"
fwd = Transformer.from_crs(4326, 5070, always_xy=True).transform  # NAD83 Conus Albers, metres
back = Transformer.from_crs(5070, 4326, always_xy=True).transform


def write(name, label, g, credit, tol=0.01):
    g = shapely.make_valid(g.simplify(tol, preserve_topology=True))
    (HERE / name).write_text(json.dumps({"type": "FeatureCollection", "features": [
        {"type": "Feature", "properties": {"name": label, "credit": credit}, "geometry": mapping(g)}]}), encoding="utf-8")
    print(f"{name}: {transform(fwd, g).area / 1e6:,.0f} km2")


# ---- seafloor shallower than 10 m, Florida Gulf coast only (Panhandle to the Keys)
BOX = (-87.6, 24.4, -80.0, 30.8)
z, west, south = bathy._grid(BOX)
sea = z < 0
seed = (int((27.0 - south) * 60), int((-85.0 - west) * 60))  # open Gulf
gulf = bathy._connected(sea, seed)
shallow = gulf & (z > -10)
north = south + z.shape[0] / 60
grid = np.ascontiguousarray(shallow[::-1]).astype(np.uint8)
parts = [shape(g) for g, v in features.shapes(grid, mask=grid.astype(bool), transform=from_origin(west, north, 1 / 60, 1 / 60)) if v == 1]
g = shapely.union_all(parts).buffer(0.02, quad_segs=2).buffer(-0.02, quad_segs=2)
g = shapely.union_all([p for p in getattr(g, "geoms", [g]) if p.area > 0.004])
g = g.intersection(box(-87.6, 24.4, -80.0, 30.8)).difference(box(-81.75, 25.35, -79.0, 31.0))  # Gulf side only (no Atlantic coast)
write("shallow10.geojson", "Shallower than 10 m", g, ETOPO_CREDIT)

# ---- the Big Bend coast: Florida land within 25 km of the Gulf between 84.4 W and 29.0 N
fl = geo.admin1("Florida")[1]
flm = transform(fwd, fl)
gulf_side = transform(fwd, box(-84.4, 29.0, -82.55, 30.35))
strip = flm.intersection(flm.boundary.buffer(25_000)).intersection(gulf_side)
write("bigbend_coast.geojson", "Big Bend", transform(back, strip), NE)
