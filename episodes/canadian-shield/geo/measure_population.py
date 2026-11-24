"""Own measurement: how many people live on Canada's Shield ecozones.

Inputs (downloaded 2026-11-24, paths given on the command line):
  kontur.gpkg  Kontur Population Canada 2023-11-01 (CC BY 4.0, HDX), 400 m H3 hexagons, EPSG:3857
  ecozones.shp Ecological Framework of Canada, ecozones (AAFC/CanSIS, nsdb ecozone_shp.zip), lon/lat
Writes geo/shield.geojson (Boreal + Taiga Shield ecozones, simplified) and prints the shares.
Run: venv python -I geo/measure_population.py <kontur.gpkg> <ecozones.shp>
"""
import json, sqlite3, struct, sys
from pathlib import Path
import numpy as np, shapefile, shapely
from shapely.geometry import shape, mapping
from shapely.ops import unary_union
from pyproj import Transformer

kontur, eco = sys.argv[1], sys.argv[2]
r = shapefile.Reader(eco, encoding="latin-1")
zones = {}
for sr in r.shapeRecords():
    name = sr.record["ZONE_NAME"].strip()
    zones.setdefault(name, []).append(shape(sr.shape.__geo_interface__).buffer(0))
zones = {k: unary_union(v) for k, v in zones.items()}
print("ecozones:", sorted(zones))

to_ll = Transformer.from_crs(3857, 4326, always_xy=True)
to_aea = Transformer.from_crs(4326, 3978, always_xy=True)  # Canada Atlas Lambert, equal-area enough for shares
ENV = {0: 0, 1: 32, 2: 48, 3: 48, 4: 64}
c = sqlite3.connect(kontur)
xs, ys, pops = [], [], []
for blob, pop in c.execute("select geom, population from population"):
    off = 8 + ENV[(blob[3] >> 1) & 7]
    g = shapely.from_wkb(bytes(blob[off:]))
    p = g.centroid
    xs.append(p.x); ys.append(p.y); pops.append(pop)
lon, lat = to_ll.transform(np.array(xs), np.array(ys))
pops = np.array(pops)
total = pops.sum()
print(f"Kontur total population: {total:,.0f}")
res = {}
for name, geom in zones.items():
    shapely.prepare(geom)
    inside = shapely.contains_xy(geom, lon, lat)
    area = shapely.transform(geom, lambda xy: np.column_stack(to_aea.transform(xy[:, 0], xy[:, 1]))).area / 1e6
    res[name] = (pops[inside].sum(), area)
for name, (p, a) in sorted(res.items(), key=lambda kv: -kv[1][0]):
    print(f"{name:22s} pop {p:12,.0f} ({p/total*100:5.2f} %)  area {a:12,.0f} km2")
shield = [k for k in zones if "Shield" in k]
sp = sum(res[k][0] for k in shield); sa = sum(res[k][1] for k in shield)
ta = sum(a for _, a in res.values())
print(f"SHIELD ecozones {shield}: pop {sp:,.0f} = {sp/total*100:.2f} % of people, area {sa:,.0f} km2 = {sa/ta*100:.1f} % of land+")
out = Path(__file__).with_name("shield.geojson")
g = unary_union([zones[k] for k in shield]).simplify(0.05)
out.write_text(json.dumps({"type": "FeatureCollection", "features": [{"type": "Feature",
    "properties": {"name": "The Canadian Shield (ecozones)"}, "geometry": mapping(g)}]}), encoding="utf-8")
print("wrote", out)
