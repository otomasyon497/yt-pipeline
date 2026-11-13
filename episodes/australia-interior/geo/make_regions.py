"""Writes the painted-map regions of this episode (run with the venv python: shapely, pyproj).

inland.geojson / coast.geojson: the mainland more than / less than 50 km from the sea (Natural Earth 10m land, buffered
in GDA94 Australian Albers, EPSG:3577). eyre_basin / mdb / nw_plateau / sw_plateau come from Geoscience Australia (see research.md). The other files are Natural Earth "geography regions" polygons: generalised
label regions, not surveyed boundaries, so the script prints their areas for the fact check.
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
fwd = Transformer.from_crs(4326, 3577, always_xy=True).transform
back = Transformer.from_crs(3577, 4326, always_xy=True).transform


def write(name, label, g, credit=NE, tol=0.02):
    g = shapely.make_valid(g.simplify(tol))
    (HERE / name).write_text(json.dumps({"type": "FeatureCollection", "features": [
        {"type": "Feature", "properties": {"name": label, "credit": credit}, "geometry": mapping(g)}]}), encoding="utf-8")
    print(f"{name}: {transform(fwd, g).area / 1e6:,.0f} km2")


aus = geo.country_geom(geo.country_code("Australia"), "10m")
mainland = max(aus.geoms, key=lambda p: p.area)
m = transform(fwd, mainland)
inner = m.buffer(-50_000)
write("inland.geojson", "More than 50 km from the sea", transform(back, inner))
write("coast.geojson", "Within 50 km of the sea", transform(back, m.difference(inner)))
print(f"mainland {m.area / 1e6:,.0f} km2, inland share {inner.area / m.area:.1%}")

regions = {p.get("name") or p.get("NAME"): g for p, g in geo.ne_geoms("ne_10m_geography_regions_polys")}
write("range.geojson", "Great Dividing Range", regions["GREAT DIVIDING RANGE"])
write("gab.geojson", "Great Artesian Basin", regions["GREAT ARTESIAN BASIN"])
deserts = [g for n, g in regions.items() if n and "desert" in n.lower() and 110 < g.bounds[0] < 150 and g.bounds[1] < -15]
write("deserts.geojson", "Deserts", shapely.union_all(deserts))
