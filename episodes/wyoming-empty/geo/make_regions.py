"""Writes the painted-map regions of wyoming-empty and prints the areas for the fact check (venv python -I).

Inputs (.cache/geo, downloaded 2026-11-27):
  blm_sma_wy.geojson        BLM Surface Management Agency, national dataset (public domain, US Government), queried for the
                            Wyoming envelope, generalised to ~200 m (maxAllowableOffset 0.002 deg)
  cb_2023_us_county_5m.zip  Census cartographic boundary counties 2023 (public domain)
  census/*                  see measure_rail.py (the 1868 line through its stations)
  ne/*                      Natural Earth admin-0 / admin-1 (public domain)
Writes:
  federal.geojson   all federal surface agencies except BIA trust land (BLM, USFS, NPS, FWS, DOD, DOE, USBR, USACE, ...)
  blm.geojson       Bureau of Land Management only
  parks.geojson     National Park Service (Yellowstone, Grand Teton, Devils Tower, Fossil Butte ...)
  rail20.geojson    20 km either side of the 1868 Union Pacific line (M1), clipped to Wyoming
  line1868.geojson  the line itself as a thin 2 km ribbon (for maps that draw it as an area)
  county_<name>.geojson  Johnson, Teton, Carbon, Campbell, Natrona
  uk_on_wy.geojson  Great Britain and Northern Ireland moved, at true size, onto Wyoming's centre (equal-area shift)
  checker.geojson   ILLUSTRATION of the railroad checkerboard: alternate one-mile squares, 12 x 8 miles at Elk Mountain
"""
import csv, io, json, sys, zipfile
from pathlib import Path
import shapefile, shapely
from shapely.geometry import shape, mapping, LineString, box
from shapely.ops import transform, unary_union
from pyproj import Transformer

HERE = Path(__file__).parent
ROOT = HERE.parents[2]
G = ROOT / ".cache/geo"
sys.path.insert(0, str(ROOT / "pipeline"))
import geo  # noqa: E402
alb = Transformer.from_crs(4326, 5070, always_xy=True).transform
SMA = "BLM Surface Management Agency (public domain)"
NE = "Natural Earth (public domain)"
CEN = "US Census Bureau (public domain)"


def km2(g):
    return transform(alb, g).area / 1e6


def write(name, label, g, credit, tol=0.005):
    g = shapely.make_valid(g.simplify(tol))
    (HERE / name).write_text(json.dumps({"type": "FeatureCollection", "features": [
        {"type": "Feature", "properties": {"name": label, "credit": credit}, "geometry": mapping(g)}]}), encoding="utf-8")
    print(f"{name:24s} {km2(g):9,.0f} km2  {(HERE / name).stat().st_size/1e3:7.0f} kB")
    return g


wy = next(g for p, g in geo.ne_geoms("ne_10m_admin_1_states_provinces") if p.get("iso_3166_2") == "US-WY").buffer(0)
WY = km2(wy)
print(f"Wyoming (Natural Earth) {WY:,.0f} km2")
sma = json.load(open(G / "blm_sma_wy.geojson", encoding="utf-8"))["features"]


def agency(codes):
    parts = [shapely.make_valid(shape(f["geometry"])) for f in sma
             if f["properties"]["ADMIN_AGENCY_CODE"] in codes and f["properties"]["ADMIN_ST"] == "WY"]
    return unary_union(parts).intersection(wy)


FED = {"BLM", "USFS", "NPS", "FWS", "DOD", "DOE", "USBR", "USACE", "VA", "GSA", "USDA"}
fed = agency(FED); blm = agency({"BLM"}); nps = agency({"NPS"})
print(f"federal {km2(fed)/WY*100:.1f} % of Wyoming; BLM {km2(blm)/WY*100:.1f} % = {km2(blm)*247.105/1e6:.1f} M acres; NPS {km2(nps)/WY*100:.1f} %")
write("federal.geojson", "Federal land", fed, SMA, 0.02)
write("blm.geojson", "Bureau of Land Management", blm, SMA, 0.02)
write("parks.geojson", "National parks", nps, SMA, 0.005)

# counties
zf = zipfile.ZipFile(G / "cb_2023_us_county_5m.zip")
stem = "cb_2023_us_county_5m"
r = shapefile.Reader(shp=io.BytesIO(zf.read(stem + ".shp")), dbf=io.BytesIO(zf.read(stem + ".dbf")), shx=io.BytesIO(zf.read(stem + ".shx")))
fields = [f[0] for f in r.fields[1:]]
for sr in r.shapeRecords():
    rec = dict(zip(fields, sr.record))
    if rec["STATEFP"] != "56" or rec["NAME"] not in ("Johnson", "Teton", "Carbon", "Campbell", "Natrona"):
        continue
    g = shape(sr.shape.__geo_interface__).buffer(0)
    c = write(f"county_{rec['NAME'].lower()}.geojson", f"{rec['NAME']} County", g, CEN, 0.003)
    if rec["NAME"] == "Teton":
        print(f"   Teton County federal share (SMA): {km2(fed.intersection(g))/km2(g)*100:.1f} %; "
              f"+ state: {km2(unary_union([fed, agency({'ST'})]).intersection(g))/km2(g)*100:.1f} %")

# the 1868 line and its 20 km band (same stations as measure_rail.py)
C = G / "census"
places = {row[3].strip(): (float(row[-1]), float(row[-2])) for row in csv.reader(open(C / "2020_gaz_place_56.txt", encoding="utf-8"), delimiter="\t") if row[0] != "USPS"}
ST = ["Pine Bluffs town", "Cheyenne city", "Laramie city", "Rock River town", "Medicine Bow town", "Rawlins city", "Wamsutter town",
      "Point of Rocks CDP", "Rock Springs city", "Green River city", "Granger town", "Evanston city"]
line = LineString([(-104.053, 41.18)] + [places[s] for s in ST] + [(-111.046, 41.25)])
inv = Transformer.from_crs(5070, 4326, always_xy=True).transform
lm = transform(alb, line)
write("rail20.geojson", "20 km from the 1868 railway", transform(inv, lm.buffer(20000)).intersection(wy), "Own measurement (Census places)", 0.005)
write("line1868.geojson", "Union Pacific, 1868", transform(inv, lm.buffer(1500)).intersection(wy), "Own drawing through the stations", 0.002)

# Britain at true size on Wyoming
uk = unary_union([g for p, g in geo.ne_geoms("ne_10m_admin_0_countries") if p.get("ADM0_A3") == "GBR"]).buffer(0)
c1, c2 = uk.centroid, wy.centroid
a1 = Transformer.from_crs(4326, f"+proj=laea +lat_0={c1.y} +lon_0={c1.x}", always_xy=True).transform
a2 = Transformer.from_crs(f"+proj=laea +lat_0={c2.y} +lon_0={c2.x}", 4326, always_xy=True).transform
write("uk_on_wy.geojson", "United Kingdom (same scale)", transform(a2, transform(a1, uk)), NE, 0.01)
print(f"   UK {km2(uk):,.0f} km2 vs Wyoming {WY:,.0f} km2")

# checkerboard illustration at Elk Mountain: odd squares (railroad) only
mile = 1609.344
x0, y0 = alb(-106.55, 41.60)
sq = [box(x0 + i * mile, y0 + j * mile, x0 + (i + 1) * mile, y0 + (j + 1) * mile) for i in range(12) for j in range(8) if (i + j) % 2 == 0]
write("checker.geojson", "Railroad sections (illustration)", transform(inv, unary_union(sq).buffer(-15)), "Illustration of the 1862 grant pattern", 0)
