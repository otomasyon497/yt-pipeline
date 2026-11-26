"""Writes the painted-map regions of this episode (venv python: shapely, pyproj).

  coast6.geojson     the six southern coastal departments (Montevideo, Canelones, San José, Maldonado, Rocha, Colonia),
                     Natural Earth admin-1 (public domain): 70 % of Uruguayans on 18 % of the land (measure_population.txt)
  interior.geojson   the other thirteen departments
  mvd30.geojson      30 km around Plaza Independencia, clipped to land: 49 % of Uruguayans
  england.geojson    Natural Earth map unit "England" (public domain), for the size comparison in the hook
  rs_sudoeste.geojson / rs_nordeste.geojson   IBGE mesorregiões 4306 Sudoeste Rio-grandense (the Campanha) and
                     4302 Nordeste Rio-grandense (the old colonies), IBGE malhas API v3 (open data)
Run: venv python -I geo/make_regions.py
"""
import json, sys
from pathlib import Path
import requests, shapely
from shapely.geometry import shape, mapping, Point
from shapely.ops import unary_union, transform
from pyproj import Transformer, Geod

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parents[2] / "pipeline"))
import geo  # noqa: E402
geod = Geod(ellps="WGS84")
NE = "Natural Earth"
IBGE = "IBGE malhas territoriais (mesorregiões)"


def write(name, label, g, credit, tol=0.01):
    g = shapely.make_valid(g.simplify(tol))
    (HERE / name).write_text(json.dumps({"type": "FeatureCollection", "features": [
        {"type": "Feature", "properties": {"name": label, "credit": credit}, "geometry": mapping(g)}]}), encoding="utf-8")
    print(f"{name}: {abs(geod.geometry_area_perimeter(g)[0]) / 1e6:,.0f} km2")


deps = {p.get("name"): g.buffer(0) for p, g in geo.ne_geoms("ne_10m_admin_1_states_provinces") if p.get("adm0_a3") == "URY"}
COAST = {"Montevideo", "Canelones", "San José", "Maldonado", "Rocha", "Colonia"}
write("coast6.geojson", "Six coastal departments", unary_union([g for k, g in deps.items() if k in COAST]), NE)
write("interior.geojson", "The interior", unary_union([g for k, g in deps.items() if k not in COAST]), NE)
uy = unary_union(list(deps.values()))
aeqd = Transformer.from_crs("+proj=aeqd +lat_0=-34.9064 +lon_0=-56.1990", 4326, always_xy=True)
circle = transform(aeqd.transform, Point(0, 0).buffer(30000, 128))
write("mvd30.geojson", "30 km from Montevideo", circle.intersection(uy), NE, tol=0.003)
eng = unary_union([g for p, g in geo.ne_geoms("ne_10m_admin_0_map_units") if (p.get("NAME") or p.get("name")) == "England"])
write("england.geojson", "England", eng, NE)
for code, fname, label in [(4306, "rs_sudoeste.geojson", "The Campanha (Sudoeste)"), (4302, "rs_nordeste.geojson", "The old colonies (Nordeste)")]:
    d = requests.get(f"https://servicodados.ibge.gov.br/api/v3/malhas/mesorregioes/{code}",
                     params={"formato": "application/vnd.geo+json", "qualidade": "intermediaria"}, timeout=60).json()
    feats = d["features"] if d.get("type") == "FeatureCollection" else [d]
    write(fname, label, unary_union([shape(f["geometry"]).buffer(0) for f in feats]), IBGE)
