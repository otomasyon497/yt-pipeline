"""Writes the painted-map regions of this episode (run with the venv python: shapely, pyproj).

wa_coast.geojson: Western Australia's mainland within 50 km of the sea (Natural Earth 10m land and admin-1, buffered in
GDA94 Australian Albers, EPSG:3577). cyclone_coast.geojson: the part of that strip between Exmouth and Broome (BoM's
"most cyclone-prone" stretch, R13). perth.geojson: a 30 km band along the coast from Two Rocks to Mandurah, an
approximation of Greater Perth, labelled as such. ridge.geojson: the latitudes 25-35 S, the belt of high pressure
"at about thirty degrees south" (schematic). hamersley.geojson: the Natural Earth label region for the Hamersley Range.
The script prints the areas for the fact check.
"""
import json
import sys
from pathlib import Path

import shapely
from pyproj import Transformer
from shapely.geometry import LineString, box, mapping
from shapely.ops import transform

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parents[2] / "pipeline"))
import geo  # noqa: E402
import maps  # noqa: E402

NE = "Natural Earth (public domain)"
fwd = Transformer.from_crs(4326, 3577, always_xy=True).transform
back = Transformer.from_crs(3577, 4326, always_xy=True).transform


def write(name, label, g, credit=NE, tol=0.01):
    g = shapely.make_valid(g.simplify(tol))
    (HERE / name).write_text(json.dumps({"type": "FeatureCollection", "features": [
        {"type": "Feature", "properties": {"name": label, "credit": credit}, "geometry": mapping(g)}]}), encoding="utf-8")
    print(f"{name}: {transform(fwd, g).area / 1e6:,.0f} km2")


wa = maps.resolve_area("Western Australia")[2]
aus = geo.country_geom(geo.country_code("Australia"), "10m")
mainland = max(aus.geoms, key=lambda p: p.area)
wa_main = transform(fwd, mainland.intersection(wa))
inner = wa_main.buffer(-50_000)
coast = wa_main.difference(inner)
write("wa_coast.geojson", "Within 50 km of the coast", transform(back, coast))
cyc = transform(back, coast).intersection(box(113.6, -23.2, 122.6, -17.2))
write("cyclone_coast.geojson", "Broome to Exmouth", cyc)
write("dry_coast.geojson", "The dry west coast", transform(back, coast).intersection(box(112.5, -30.5, 119.5, -20.0)))
band = transform(fwd, LineString([(115.68, -31.55), (115.74, -32.0), (115.72, -32.55)])).buffer(22_000)
write("perth.geojson", "Greater Perth (approx.)", transform(back, band.intersection(transform(fwd, mainland))))
write("ridge.geojson", "High-pressure belt (approx.)", box(-90.0, -35.0, 179.0, -25.0), credit="Schematic, after BoM")
regions = {p.get("name") or p.get("NAME"): g for p, g in geo.ne_geoms("ne_10m_geography_regions_polys")}
write("hamersley.geojson", "Hamersley Range", regions["Hamersley Ra."])
print(f"WA mainland {wa_main.area / 1e6:,.0f} km2, coast strip share {coast.area / wa_main.area:.1%}")
