"""Own measurements M1/M2: where Uruguayans live, and Rio Grande do Sul's regions for comparison.

Inputs (downloaded 2026-11-24, paths on the command line):
  k_UY.gpkg  Kontur Population Uruguay 2023-11-01 (CC BY 4.0, HDX), 400 m H3 hexagons, EPSG:3857
  k_BR.gpkg  Kontur Population Brazil 2023-11-01 (same)
  rs_meso.shp IBGE malha territorial 2022, Rio Grande do Sul mesorregioes (SIRGAS 2000 lon/lat)
  Uruguay departments: Natural Earth 10m admin-1 (.cache/geo/ne)
Run: venv python -I geo/measure_population.py <k_UY.gpkg> <k_BR.gpkg> <rs_meso.shp>
"""
import json, sqlite3, sys
from pathlib import Path
import numpy as np, shapefile, shapely
from shapely.geometry import shape
from shapely.ops import unary_union
from pyproj import Transformer, Geod

ROOT = Path(__file__).resolve().parents[3]
k_uy, k_br, meso = sys.argv[1:4]
to_ll = Transformer.from_crs(3857, 4326, always_xy=True)
geod = Geod(ellps="WGS84")
ENV = {0: 0, 1: 32, 2: 48, 3: 48, 4: 64}


def load(path, bbox=None):
    c = sqlite3.connect(path)
    xs, ys, pops, areas = [], [], [], []
    for blob, pop in c.execute("select geom, population from population"):
        off = 8 + ENV[(blob[3] >> 1) & 7]
        g = shapely.from_wkb(bytes(blob[off:]))
        p = g.centroid
        xs.append(p.x); ys.append(p.y); pops.append(pop); areas.append(g.area)
    lon, lat = to_ll.transform(np.array(xs), np.array(ys))
    # web-mercator area -> true area: scale by cos(lat)^2
    area_km2 = np.array(areas) * np.cos(np.radians(lat)) ** 2 / 1e6
    return lon, lat, np.array(pops), area_km2


def km2(geom):
    return abs(geod.geometry_area_perimeter(geom)[0]) / 1e6


# ---------------------------------------------------------------- Uruguay
lon, lat, pop, hexa = load(k_uy)
tot = pop.sum()
print(f"URUGUAY Kontur total {tot:,.0f}; populated hexagons {len(pop):,} covering {hexa.sum():,.0f} km2")
ne = json.load(open(ROOT / ".cache/geo/ne/ne_10m_admin_1_states_provinces.geojson", encoding="utf-8"))
deps = {f["properties"]["name"]: shape(f["geometry"]).buffer(0) for f in ne["features"] if f["properties"].get("adm0_a3") == "URY"}
uy = unary_union(list(deps.values()))
uy_area = km2(uy)
print(f"Uruguay land (Natural Earth departments) {uy_area:,.0f} km2")
# distance to Plaza Independencia, Montevideo
_, _, d = geod.inv(np.full(lon.shape, -56.2017), np.full(lat.shape, -34.9067), lon, lat)
for r in (30, 50, 100):
    s = pop[d <= r * 1000].sum()
    print(f"  within {r:3d} km of central Montevideo: {s:12,.0f} = {s/tot*100:5.1f} %")
# densest area that holds half / 90 % of the people
dens = pop / hexa
o = np.argsort(-dens)
cp = np.cumsum(pop[o]); ca = np.cumsum(hexa[o])
for share in (0.5, 0.9):
    i = np.searchsorted(cp, share * tot)
    print(f"  {share*100:.0f} % of people live on {ca[i]:,.0f} km2 = {ca[i]/uy_area*100:.2f} % of the land")
print(f"  land with no one counted at all: {(uy_area-hexa.sum()):,.0f} km2 = {(1-hexa.sum()/uy_area)*100:.0f} % (approx.)")
res = {}
for name, g in deps.items():
    shapely.prepare(g)
    ins = shapely.contains_xy(g, lon, lat)
    res[name] = (pop[ins].sum(), km2(g))
COAST = ["Montevideo", "Canelones", "San José", "Maldonado", "Rocha", "Colonia"]
cp_ = sum(v[0] for k, v in res.items() if any(k.startswith(c[:5]) for c in COAST))
ca_ = sum(v[1] for k, v in res.items() if any(k.startswith(c[:5]) for c in COAST))
print(f"  six southern coastal departments: pop {cp_/tot*100:.1f} %, area {ca_/uy_area*100:.1f} %")
for name, (p, a) in sorted(res.items(), key=lambda kv: kv[1][0] / kv[1][1]):
    print(f"  {name:16s} {p:10,.0f}  {a:8,.0f} km2  {p/a:7.1f} /km2")
rest = [(p, a) for k, (p, a) in res.items() if not any(k.startswith(c[:5]) for c in COAST)]
print(f"  outside the six: {sum(p for p,_ in rest)/sum(a for _,a in rest):.1f} people/km2")

# ---------------------------------------------------------------- Rio Grande do Sul
r = shapefile.Reader(meso, encoding="utf-8")
fields = [f[0] for f in r.fields[1:]]
mes = {}
for sr in r.shapeRecords():
    rec = dict(zip(fields, sr.record))
    nm = next(v for k, v in rec.items() if k.upper().startswith("NM_"))
    mes[nm] = shape(sr.shape.__geo_interface__).buffer(0)
rs = unary_union(list(mes.values()))
minx, miny, maxx, maxy = rs.bounds
lon, lat, pop, hexa = load(k_br)
keep = (lon > minx) & (lon < maxx) & (lat > miny) & (lat < maxy)
lon, lat, pop = lon[keep], lat[keep], pop[keep]
shapely.prepare(rs)
ins = shapely.contains_xy(rs, lon, lat)
rs_pop, rs_area = pop[ins].sum(), km2(rs)
print(f"\nRIO GRANDE DO SUL Kontur {rs_pop:,.0f} on {rs_area:,.0f} km2 = {rs_pop/rs_area:.1f} /km2")
for nm, g in sorted(mes.items()):
    shapely.prepare(g)
    p = pop[shapely.contains_xy(g, lon, lat)].sum(); a = km2(g)
    print(f"  {nm:40s} {p:11,.0f}  {a:8,.0f} km2  {p/a:7.1f} /km2")
