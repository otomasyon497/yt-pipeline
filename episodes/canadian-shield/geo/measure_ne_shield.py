"""Own measurement 2: people inside Natural Earth's 'CANADIAN SHIELD' region (ne_10m_geography_regions_polys),
clipped to Canada (ne_10m_admin_0_countries), with Kontur Population Canada 2023-11-01 (CC BY 4.0).
REJECTED (see the end). Run from the repo root:
  venv python -I episodes/canadian-shield/geo/measure_ne_shield.py <kontur.gpkg>
"""
import json, sqlite3, sys
from pathlib import Path
sys.path[:0] = ["pipeline", "."]
import geo
import numpy as np, shapely
from shapely.geometry import mapping
from shapely.ops import unary_union
from pyproj import Transformer

shield = unary_union([g for p, g in geo.ne_geoms("ne_10m_geography_regions_polys") if p.get("NAME") == "CANADIAN SHIELD"])
canada = unary_union([g for p, g in geo.ne_geoms("ne_10m_admin_0_countries") if p.get("ADM0_A3") == "CAN"])
cs = shield.intersection(canada)
to_aea = Transformer.from_crs(4326, 3978, always_xy=True)
area = lambda g: shapely.transform(g, lambda xy: np.column_stack(to_aea.transform(xy[:, 0], xy[:, 1]))).area / 1e6
print(f"Shield in Canada {area(cs):,.0f} km2 of Canada {area(canada):,.0f} km2 = {area(cs)/area(canada)*100:.1f} %")
print(f"Shield outside Canada {area(shield.difference(canada)):,.0f} km2")
ENV = {0: 0, 1: 32, 2: 48, 3: 48, 4: 64}
to_ll = Transformer.from_crs(3857, 4326, always_xy=True)
xs, ys, pops = [], [], []
for blob, pop in sqlite3.connect(sys.argv[1]).execute("select geom, population from population"):
    c = shapely.from_wkb(bytes(blob[8 + ENV[(blob[3] >> 1) & 7]:])).centroid
    xs.append(c.x); ys.append(c.y); pops.append(pop)
lon, lat = to_ll.transform(np.array(xs), np.array(ys)); pops = np.array(pops)
shapely.prepare(cs)
inside = shapely.contains_xy(cs, lon, lat)
print(f"people: {pops[inside].sum():,.0f} of {pops.sum():,.0f} = {pops[inside].sum()/pops.sum()*100:.2f} %")
# biggest clusters inside: 0.5-degree cells
cells = {}
for x, y, p in zip(lon[inside], lat[inside], pops[inside]):
    k = (round(x * 2) / 2, round(y * 2) / 2); cells[k] = cells.get(k, 0) + p
for k, v in sorted(cells.items(), key=lambda kv: -kv[1])[:15]:
    print("  cell", k, f"{v:,.0f}")
# Not used for the maps or the narration: the region is too coarse (it takes in Montreal, which is on the
# St Lawrence Lowlands, not the Shield): 14.85 % of people is wrong. Kept as a record of the rejected source.
