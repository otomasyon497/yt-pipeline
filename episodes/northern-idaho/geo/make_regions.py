"""Writes the painted-map regions of northern-idaho and prints their areas (venv python -I).

Inputs:
  .cache/geo/cb_2023_us_county_5m.zip          US Census county boundaries (public domain)
  .cache/geo/ne/ne_10m_admin_1_states_provinces.geojson   Natural Earth states (public domain)
  .cache/geo/osm_id/wild.geojson, forests.geojson   US Forest Service EDW wilderness / forest boundaries (public domain),
                                                     fetched 2026-11-28 from apps.fs.usda.gov/arcx (EDW_Wilderness_01,
                                                     EDW_ForestSystemBoundaries_01)
  .cache/geo/osm_id/ne_rivers_nw.geojson       Natural Earth 10m river centre lines (Salmon), public domain
Writes (geo/<name>.geojson):
  idaho, north (the ten northern counties), south, idaho_county, kootenai, shoshone, washington, montana,
  fire1910 (Shoshone County ID + Mineral County MT, the heart of the 1910 fires: an illustration, not a fire perimeter),
  territory1863 (Idaho + Montana + Wyoming: approximate extent of Idaho Territory in 1863),
  vt_nh (Vermont + New Hampshire moved onto north Idaho for scale), frank_church, selway, gospel, wilderness (all three),
  forests (Idaho Panhandle + Nez Perce-Clearwater NF, administrative boundaries incl. private inholdings),
  salmon (the Salmon River as a 2 km ribbon: the Pacific / Mountain time line)
"""
import io, json, zipfile
from pathlib import Path
import shapefile
from shapely.geometry import shape, mapping
from shapely.ops import unary_union, transform
from shapely import affinity
from pyproj import Transformer

HERE = Path(__file__).parent
G = HERE.parents[2] / ".cache/geo"
alb = Transformer.from_crs(4326, 5070, always_xy=True).transform
to_ll = Transformer.from_crs(5070, 4326, always_xy=True).transform
CEN, NE, USFS = "US Census Bureau (public domain)", "Natural Earth (public domain)", "US Forest Service EDW (public domain)"
NORTH = ["021", "017", "055", "079", "009", "057", "035", "069", "061", "049"]

z = zipfile.ZipFile(G / "cb_2023_us_county_5m.zip")
r = shapefile.Reader(shp=io.BytesIO(z.read("cb_2023_us_county_5m.shp")), dbf=io.BytesIO(z.read("cb_2023_us_county_5m.dbf")))
names = [f[0] for f in r.fields[1:]]
cty = {}
for sr in r.iterShapeRecords():
    a = dict(zip(names, sr.record))
    if a["STATEFP"] in ("16", "30"):
        cty[a["STATEFP"] + a["COUNTYFP"]] = shape(sr.shape.__geo_interface__)
st = {f["properties"]["name"]: shape(f["geometry"]) for f in
      json.load(open(G / "ne/ne_10m_admin_1_states_provinces.geojson", encoding="utf-8"))["features"]
      if f["properties"].get("iso_a2") == "US"}
wild = {f["properties"]["wildernessname"]: shape(f["geometry"]).buffer(0) for f in json.load(open(G / "osm_id/wild.geojson"))["features"]}
forests = unary_union([shape(f["geometry"]).buffer(0) for f in json.load(open(G / "osm_id/forests.geojson"))["features"]])
salmon = next(shape(f["geometry"]) for f in json.load(open(G / "osm_id/ne_rivers_nw.geojson"))["features"] if f["properties"]["name"] == "Salmon")

idaho = unary_union([g for k, g in cty.items() if k.startswith("16")]).buffer(0)
north = unary_union([cty["16" + c] for c in NORTH]).buffer(0)
south = idaho.difference(north).buffer(0)
# Vermont + New Hampshire, moved (in Albers metres) so their centre sits on north Idaho's centre
vtnh = transform(alb, unary_union([st["Vermont"], st["New Hampshire"]]).buffer(0))
n_a = transform(alb, north)
vtnh = transform(to_ll, affinity.translate(vtnh, n_a.centroid.x - vtnh.centroid.x, n_a.centroid.y - vtnh.centroid.y))
wild_all = unary_union(list(wild.values()))

out = {
    "idaho": (idaho, "Idaho", CEN), "north": (north, "North Idaho", CEN), "south": (south, "Southern Idaho", CEN),
    "idaho_county": (cty["16049"], "Idaho County", CEN), "kootenai": (cty["16055"], "Kootenai County", CEN),
    "shoshone": (cty["16079"], "Shoshone County", CEN),
    "clearwater_co": (cty["16035"], "Clearwater County", CEN), "nezperce_co": (cty["16069"], "Nez Perce County", CEN),
    "latah": (cty["16057"], "Latah County", CEN),
    "washington": (st["Washington"], "Washington", NE), "montana": (st["Montana"], "Montana", NE),
    "fire1910": (unary_union([cty["16079"], cty["30061"]]), "Heart of the 1910 fires", CEN),
    "territory1863": (unary_union([st["Idaho"], st["Montana"], st["Wyoming"]]), "Idaho Territory, 1863 (approx.)", NE),
    "vt_nh": (vtnh, "Vermont + New Hampshire", NE),
    "frank_church": (wild["Frank Church-River of No Return Wilderness"], "Frank Church wilderness", USFS),
    "selway": (wild["Selway-Bitterroot Wilderness"], "Selway-Bitterroot wilderness", USFS),
    "gospel": (wild["Gospel-Hump Wilderness"], "Gospel-Hump wilderness", USFS),
    "wilderness": (wild_all, "Wilderness", USFS),
    "forests": (forests.intersection(idaho.buffer(0.02)), "National forests", USFS),
    "salmon": (transform(to_ll, transform(alb, salmon).buffer(1000)), "Salmon River", NE),
}
lines = []
for k, (g, nm, src) in out.items():
    g = g.simplify(0.002)
    (HERE / f"{k}.geojson").write_text(json.dumps({"type": "FeatureCollection", "features": [
        {"type": "Feature", "properties": {"name": nm, "source": src}, "geometry": mapping(g)}]}))
    a = transform(alb, g).area
    lines.append(f"{k}: {a/1e6:,.0f} km2 = {a/2.58999e6:,.0f} sq mi = {a/4046.86/1e6:.2f} M acres")
(HERE / "make_regions.txt").write_text("\n".join(lines) + "\n"); print("\n".join(lines))
