"""M3: how close the people of the Keys live to US 1 (Overseas Highway).

2020 Census blocks (TIGERweb layer 2: POP100 + internal point) for Monroe County, Keys only; US 1 from TIGER/Line 2023
roads (tl_2023_12087_roads.zip, pass its path). Distances in UTM 17N. Writes measure_road.txt.
    python -I measure_road.py <tl_2023_12087_roads.zip>
"""
import json, sys, urllib.parse, urllib.request
import numpy as np, shapefile
from shapely.geometry import LineString, Point
from shapely.ops import unary_union, transform
from pyproj import Transformer

Q = "https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/Tracts_Blocks/MapServer/2/query?"
def blocks():
    out, off = [], 0
    while True:
        p = {"where": "STATE='12' AND COUNTY='087'", "outFields": "GEOID,POP100,HU100,AREALAND,INTPTLAT,INTPTLON",
             "returnGeometry": "false", "resultOffset": off, "resultRecordCount": 1000, "f": "json"}
        d = json.load(urllib.request.urlopen(Q + urllib.parse.urlencode(p), timeout=120))
        out += [f["attributes"] for f in d["features"]]
        if not d.get("exceededTransferLimit") and len(d["features"]) < 1000: return out
        off += len(d["features"])

def in_keys(lat, lon):  # drop mainland Monroe (Everglades) and the Dry Tortugas
    return lat < 25.36 and lon > -82.2 and not (lon < -80.84 and lat > 25.12)

to_m = Transformer.from_crs(4326, 32617, always_xy=True).transform
r = shapefile.Reader(sys.argv[1])
names = [f[0] for f in r.fields[1:]]
lines = []
for sr in r.iterShapeRecords():
    rec = dict(zip(names, sr.record))
    if rec.get("RTTYP") == "U" and str(rec.get("FULLNAME", "")).replace(" ", "") in ("USHwy1", "US Hwy 1".replace(" ", "")):
        pts = sr.shape.points
        if len(pts) > 1 and any(in_keys(y, x) for x, y in pts): lines.append(transform(to_m, LineString(pts)))
road = unary_union(lines)
B = [b for b in blocks() if in_keys(float(b["INTPTLAT"]), float(b["INTPTLON"]))]
pop = np.array([b["POP100"] for b in B], float); hu = np.array([b["HU100"] for b in B], float)
d = np.array([road.distance(Point(*to_m(float(b["INTPTLON"]), float(b["INTPTLAT"])))) for b in B])
land = sum(b["AREALAND"] for b in B) / 2.59e6
out = [f"US 1 segments: {len(lines)}, length in the Keys {road.length/1609.34:.1f} mi",
       f"Keys blocks: {len(B)}, people {pop.sum():,.0f}, housing units {hu.sum():,.0f}, land {land:.1f} sq mi"]
for mi in (0.25, 0.5, 1, 2):
    m = d <= mi * 1609.34
    out.append(f"within {mi} mi of US 1: {pop[m].sum()/pop.sum()*100:.1f} % of people, {hu[m].sum()/hu.sum()*100:.1f} % of homes")
out.append(f"farthest populated block: {d[pop > 0].max()/1609.34:.2f} mi")
open("measure_road.txt", "w").write("\n".join(out) + "\n"); print("\n".join(out))
