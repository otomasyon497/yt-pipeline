"""M1/M2: how close Namibians live to the Atlantic, and the longest empty stretches of the coast.

Inputs: k_NA.gpkg = Kontur Population Namibia 2023-11-01 (CC BY 4.0, HDX), 400 m H3 hexagons, EPSG:3857 (path on the
command line); Natural Earth 10m land and admin-0 (.cache/geo/ne, public domain). Distances in UTM 33S.
Run: venv python -I geo/measure_population.py <k_NA.gpkg>   -> measure_population.txt
"""
import json, sqlite3, sys
from pathlib import Path
import numpy as np, shapely
from shapely.geometry import shape, box, Point
from shapely.ops import unary_union, transform
from pyproj import Transformer

ROOT = Path(__file__).resolve().parents[3]
NE = ROOT / ".cache/geo/ne"
ENV = {0: 0, 1: 32, 2: 48, 3: 48, 4: 64}
to_ll = Transformer.from_crs(3857, 4326, always_xy=True)
to_m = Transformer.from_crs(4326, 32733, always_xy=True).transform

c = sqlite3.connect(sys.argv[1])
xs, ys, pops = [], [], []
for blob, pop in c.execute("select geom, population from population"):
    g = shapely.from_wkb(bytes(blob[8 + ENV[(blob[3] >> 1) & 7]:]))
    p = g.centroid; xs.append(p.x); ys.append(p.y); pops.append(pop)
lon, lat = to_ll.transform(np.array(xs), np.array(ys)); pop = np.array(pops, float)

na = next(shape(f["geometry"]) for f in json.load(open(NE / "ne_10m_admin_0_countries.geojson", encoding="utf-8"))["features"]
          if f["properties"].get("ADM0_A3") == "NAM")
land = unary_union([shape(f["geometry"]) for f in json.load(open(NE / "ne_10m_land.geojson", encoding="utf-8"))["features"]
                    if shape(f["geometry"]).intersects(box(10, -30, 20, -16))])
coast_ll = land.boundary.intersection(na.buffer(0.05)).intersection(box(11.0, -29.2, 15.5, -16.9))
coast = transform(to_m, coast_ll)
coast_line = shapely.line_merge(coast)
pts = shapely.points(*np.array([to_m(a, b) for a, b in zip(lon, lat)]).T)
d = shapely.distance(pts, coast) / 1000
tot = pop.sum()
out = [f"Kontur Namibia total {tot:,.0f}; coastline length {coast.length/1000:,.0f} km (NE 10m)"]
for km in (5, 20, 50, 100):
    m = d <= km
    out.append(f"within {km} km of the sea: {pop[m].sum():,.0f} = {pop[m].sum()/tot*100:.1f} % of Namibians")
# empty stretches: positions along the coast of hexagons within 10 km of the sea holding >= 25 people
lines = list(getattr(coast_line, "geoms", [coast_line]))
main = max(lines, key=lambda l: l.length)
near = (d <= 10) & (pop >= 25)
pos = np.sort(np.array([main.project(p) for p in pts[near]]) / 1000)
pos = np.concatenate([[0], pos, [main.length / 1000]])
gaps = sorted(((b - a, a, b) for a, b in zip(pos, pos[1:])), reverse=True)[:5]
out.append(f"main coast line {main.length/1000:,.0f} km; settled hexagons near the sea: {near.sum()}")
for g, a, b in gaps:
    pa, pb = [transform(Transformer.from_crs(32733, 4326, always_xy=True).transform, main.interpolate(x * 1000)) for x in (a, b)]
    out.append(f"  empty stretch {g:,.0f} km: from ({pa.y:.2f}, {pa.x:.2f}) to ({pb.y:.2f}, {pb.x:.2f})")
Path(__file__).with_suffix(".txt").write_text("\n".join(out) + "\n"); print("\n".join(out))
