"""M2: how high the land of the Keys stands. Random points on land (2020 Census blocks with land, minus TIGER 2023
area water), elevation from USGS EPQS (3DEP, feet NAVD88). Writes measure_height.txt.
    python -I measure_height.py <tl_2023_12087_areawater.zip> [n_points]
"""
import json, sys, urllib.parse, urllib.request
from concurrent.futures import ThreadPoolExecutor
import numpy as np, shapefile
from shapely.geometry import shape, Point
from shapely.ops import unary_union
from shapely import prepared

Q = "https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/Tracts_Blocks/MapServer/2/query?"
def in_keys(lat, lon):
    return lat < 25.36 and lon > -82.2 and not (lon < -80.84 and lat > 25.12)
polys, off = [], 0
while True:
    p = {"where": "STATE='12' AND COUNTY='087' AND AREALAND>0", "outFields": "INTPTLAT,INTPTLON", "outSR": 4326,
         "returnGeometry": "true", "resultOffset": off, "resultRecordCount": 500, "f": "geojson"}
    d = json.load(urllib.request.urlopen(Q + urllib.parse.urlencode(p), timeout=180))
    for f in d["features"]:
        a = f["properties"]
        if in_keys(float(a["INTPTLAT"]), float(a["INTPTLON"])): polys.append(shape(f["geometry"]))
    if len(d["features"]) < 500: break
    off += len(d["features"])
land = unary_union(polys)
water = unary_union([shape(s.__geo_interface__) for s in shapefile.Reader(sys.argv[1]).shapes()])
land = land.difference(water.buffer(0))
n = int(sys.argv[2]) if len(sys.argv) > 2 else 2000
rng = np.random.default_rng(1)
minx, miny, maxx, maxy = land.bounds
pl, pts = prepared.prep(land), []
while len(pts) < n:
    x, y = rng.uniform(minx, maxx, 20000), rng.uniform(miny, maxy, 20000)
    pts += [(a, b) for a, b in zip(x, y) if pl.contains(Point(a, b))]
pts = pts[:n]
def elev(pt):
    u = "https://epqs.nationalmap.gov/v1/json?" + urllib.parse.urlencode({"x": pt[0], "y": pt[1], "units": "Feet", "wkid": 4326})
    for _ in range(4):
        try: return float(json.load(urllib.request.urlopen(u, timeout=60))["value"])
        except Exception: pass
    return None
with ThreadPoolExecutor(8) as ex: z = list(ex.map(elev, pts))
z = np.array([v for v in z if v is not None and v > -50])
out = [f"land points: {len(z)} of {n} (area {land.area*111.0*111.0*np.cos(np.radians(24.8))/2.59:.0f} sq mi approx)",
       f"median {np.median(z):.1f} ft NAVD88"]
for h in (2, 3, 5, 6, 10):
    out.append(f"below {h} ft: {np.mean(z < h)*100:.1f} %")
out.append(f"highest sampled: {z.max():.1f} ft")
open("measure_height.txt", "w").write("\n".join(out) + "\n"); print("\n".join(out))
