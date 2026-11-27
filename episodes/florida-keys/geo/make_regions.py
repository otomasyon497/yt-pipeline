"""Writes the painted-map regions of florida-keys and prints their areas (venv python -I).

Inputs: 2020 Census blocks with land (TIGERweb layer 2, public domain) minus TIGER 2023 area water for Monroe County
(tl_2023_12087_areawater.zip, pass its path), so the islands are drawn as land, not as county lines over the sea;
.cache/geo/cb_2023_us_county_5m.zip for the Miami-Dade tip.
Writes:
  keys.geojson        Monroe County's islands (the county clipped to the Keys, mainland Everglades part dropped)
  upper_mid.geojson   Upper and Middle Keys (Key Largo to the Seven Mile Bridge), where the 1935 storm struck
  lower.geojson       Lower Keys west of the Seven Mile Bridge (Irma's landfall area)
  keywest.geojson     Key West island and Stock Island
  dade_south.geojson  the southern tip of Miami-Dade (Florida City / Homestead), the mainland end of the road
"""
import io, json, sys, zipfile
from pathlib import Path
import shapefile
from shapely.geometry import shape, mapping, box
from shapely.ops import transform
from pyproj import Transformer

HERE = Path(__file__).parent
G = HERE.parents[2] / ".cache/geo"
alb = Transformer.from_crs(4326, 5070, always_xy=True).transform
z = zipfile.ZipFile(G / "cb_2023_us_county_5m.zip")
r = shapefile.Reader(shp=io.BytesIO(z.read("cb_2023_us_county_5m.shp")), dbf=io.BytesIO(z.read("cb_2023_us_county_5m.dbf")))
names = [f[0] for f in r.fields[1:]]
geoms = {}
for sr in r.iterShapeRecords():
    rec = dict(zip(names, sr.record))
    if rec["STATEFP"] == "12" and rec["COUNTYFP"] in ("087", "086"):
        geoms[rec["COUNTYFP"]] = shape(sr.shape.__geo_interface__)
dade = geoms["086"]
import urllib.parse, urllib.request
from shapely.ops import unary_union
Q = "https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/Tracts_Blocks/MapServer/2/query?"
polys, off = [], 0
while True:
    p = {"where": "STATE='12' AND COUNTY='087' AND AREALAND>0", "outFields": "GEOID", "outSR": 4326,
         "returnGeometry": "true", "resultOffset": off, "resultRecordCount": 500, "f": "geojson"}
    d = json.load(urllib.request.urlopen(Q + urllib.parse.urlencode(p), timeout=180))
    polys += [shape(f["geometry"]) for f in d["features"]]
    if len(d["features"]) < 500: break
    off += len(d["features"])
water = unary_union([shape(s.__geo_interface__) for s in shapefile.Reader(sys.argv[1]).shapes()]).buffer(0)
keys = unary_union(polys).difference(water).intersection(box(-82.2, 24.4, -80.0, 25.36)).difference(box(-81.9, 25.12, -80.84, 26.0))
keys = keys.buffer(0.0004).buffer(-0.0002).simplify(0.0003)
out = {
    "keys": keys,
    "upper_mid": keys.intersection(box(-81.03, 24.6, -80.0, 25.36)),
    "lower": keys.intersection(box(-82.2, 24.4, -81.20, 24.78)),
    "keywest": keys.intersection(box(-81.82, 24.53, -81.71, 24.59)),
    "dade_south": dade.intersection(box(-80.70, 25.25, -80.35, 25.52)),
}
for k, g in out.items():
    (HERE / f"{k}.geojson").write_text(json.dumps({"type": "FeatureCollection", "features": [
        {"type": "Feature", "properties": {"name": k, "source": "US Census Bureau (public domain)"}, "geometry": mapping(g)}]}))
    print(f"{k}: {transform(alb, g).area/1e6:.1f} km2 = {transform(alb, g).area/2.59e6:.1f} sq mi")
