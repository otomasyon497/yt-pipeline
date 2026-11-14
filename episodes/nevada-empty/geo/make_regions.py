"""Writes the painted-map regions of this episode (venv python: shapely, pyproj).

sierra / great_basin / black_rock: Natural Earth "geography regions" polygons (generalised label regions, not surveyed
boundaries). rural.geojson: Nevada minus Clark and Washoe counties is NOT built here (no county data in Natural Earth);
the script paints Nevada and marks Las Vegas and Reno instead. Areas are printed for the fact check.
"""
import json
import sys
from pathlib import Path

import shapely
from pyproj import Transformer
from shapely.geometry import mapping
from shapely.ops import transform

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parents[2] / "pipeline"))
import geo  # noqa: E402

NE = "Natural Earth (public domain)"
fwd = Transformer.from_crs(4326, 5070, always_xy=True).transform  # NAD83 Conus Albers


def write(name, label, g, tol=0.01):
    g = shapely.make_valid(g.simplify(tol))
    (HERE / name).write_text(json.dumps({"type": "FeatureCollection", "features": [
        {"type": "Feature", "properties": {"name": label, "credit": NE}, "geometry": mapping(g)}]}), encoding="utf-8")
    print(f"{name}: {transform(fwd, g).area / 1e6:,.0f} km2")


regions = {p.get("name") or p.get("NAME"): g for p, g in geo.ne_geoms("ne_10m_geography_regions_polys")}
write("sierra.geojson", "Sierra Nevada", regions["SIERRA NEVADA"])
write("great_basin.geojson", "Great Basin", regions["GREAT BASIN"])
write("black_rock.geojson", "Black Rock Desert", regions["Black Rock Desert"])
nv = geo.admin1("Nevada")[1]
print(f"Nevada: {transform(fwd, nv).area / 1e6:,.0f} km2")
