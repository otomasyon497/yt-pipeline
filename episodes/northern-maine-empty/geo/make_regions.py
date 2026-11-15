"""Writes the painted-map regions of this episode (venv python -I: shapely, pyproj, pyshp).

Input: US Census 2020 cartographic boundary files (public domain), passed as a folder argument:
  cb_2020_23_cousub_500k.shp (Maine county subdivisions), cb_2020_us_county_500k.shp (counties).
unorganized.geojson: the 40 unorganized territories (names ending " UT"). aroostook / piscataquis: counties.
south_coast.geojson: Cumberland + York, for the contrast with the empty north. Areas are printed for the fact check.
    python -I make_regions.py <folder with the .shp files>
"""
import json
import sys
from pathlib import Path

import shapefile
import shapely
from pyproj import Transformer
from shapely.geometry import mapping, shape
from shapely.ops import transform, unary_union

HERE = Path(__file__).parent
SRC = Path(sys.argv[1])
CREDIT = "US Census Bureau, 2020 cartographic boundary files (public domain)"
fwd = Transformer.from_crs(4269, 5070, always_xy=True).transform  # NAD83 -> Conus Albers


def read(name, keep):
    r = shapefile.Reader(str(SRC / name))
    fields = [f[0] for f in r.fields[1:]]
    return [shape(sr.shape.__geo_interface__) for sr in r.iterShapeRecords() if keep(dict(zip(fields, sr.record)))]


def write(name, label, geoms, tol=0.004):
    g = shapely.make_valid(unary_union(geoms).simplify(tol))
    (HERE / name).write_text(json.dumps({"type": "FeatureCollection", "features": [
        {"type": "Feature", "properties": {"name": label, "credit": CREDIT}, "geometry": mapping(g)}]}), encoding="utf-8")
    print(f"{name}: {transform(fwd, g).area / 2.58999e6:,.0f} sq mi (incl. inland water)")


ut = read("cb_2020_23_cousub_500k.shp", lambda d: str(d["NAME"]).endswith(" UT") or str(d.get("NAMELSAD", "")).endswith(" UT"))
print("UT polygons:", len(ut))
write("unorganized.geojson", "Maine's unorganized territory", ut)
co = lambda n: (lambda d: d["STATEFP"] == "23" and d["NAME"] == n)  # noqa: E731
write("aroostook.geojson", "Aroostook County", read("cb_2020_us_county_500k.shp", co("Aroostook")))
write("piscataquis.geojson", "Piscataquis County", read("cb_2020_us_county_500k.shp", co("Piscataquis")))
write("south_coast.geojson", "Cumberland and York counties",
      read("cb_2020_us_county_500k.shp", co("Cumberland")) + read("cb_2020_us_county_500k.shp", co("York")))
me = read("cb_2020_us_county_500k.shp", lambda d: d["STATEFP"] == "23")
print(f"Maine (counties): {transform(fwd, unary_union(me)).area / 2.58999e6:,.0f} sq mi")
