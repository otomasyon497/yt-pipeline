"""Writes the painted-map regions of skeleton-coast and prints their areas (venv python -I).

Inputs: OSM relations via Overpass, saved 2026-11-27 (ODbL, (c) OpenStreetMap contributors): Skeleton_Coast.json
(Skeleton Coast Park) and parks2.json (Tsau //Khaeb (Sperrgebiet) NP 4869664, Namib-Naukluft NP 4150085), folder on
the command line; Natural Earth 10m admin-0 / land (.cache/geo/ne, public domain); measure_population.txt stretches.
Writes: namibia, coast30 (30 km coastal strip), skeleton_np, sperrgebiet, namib_naukluft, walvis_enclave (approx.
1,124 km2 circle-free polygon: the bay area as a 20 km buffer clipped to land - illustration), empty_south and
empty_north (the coast stretches without settled squares, as 10 km ribbons).
"""
import json, sys
from pathlib import Path
from shapely.geometry import shape, mapping, LineString, box
from shapely.ops import polygonize, unary_union, transform
from pyproj import Transformer

HERE = Path(__file__).parent
NE = HERE.parents[2] / ".cache/geo/ne"
SRC = Path(sys.argv[1])
to_m = Transformer.from_crs(4326, 32733, always_xy=True).transform
to_ll = Transformer.from_crs(32733, 4326, always_xy=True).transform
OSM = "(c) OpenStreetMap contributors, ODbL"


def osm_poly(path, rel_id=None):
    out = []
    for e in json.load(open(path, encoding="utf-8"))["elements"]:
        if rel_id and e["id"] != rel_id:
            continue
        lines = [LineString([(p["lon"], p["lat"]) for p in m["geometry"]]) for m in e.get("members", [])
                 if m.get("type") == "way" and m.get("role") in ("outer", "") and len(m.get("geometry", [])) > 1]
        out += list(polygonize(unary_union(lines)))
    return unary_union(out)


na = next(shape(f["geometry"]) for f in json.load(open(NE / "ne_10m_admin_0_countries.geojson", encoding="utf-8"))["features"]
          if f["properties"].get("ADM0_A3") == "NAM")
land = unary_union([shape(f["geometry"]) for f in json.load(open(NE / "ne_10m_land.geojson", encoding="utf-8"))["features"]
                    if shape(f["geometry"]).intersects(box(10, -30, 20, -16))])
coast = land.boundary.intersection(na.buffer(0.05)).intersection(box(11.0, -29.2, 15.5, -16.9))
na_m = transform(to_m, na)
strip = transform(to_ll, transform(to_m, coast).buffer(30000).intersection(na_m))


def ribbon(lat_a, lat_b):
    seg = coast.intersection(box(10, min(lat_a, lat_b), 17, max(lat_a, lat_b)))
    return transform(to_ll, transform(to_m, seg).buffer(10000).intersection(na_m))


wb = transform(to_ll, transform(to_m, box(14.42, -23.15, 14.55, -22.85).centroid).buffer(20000).intersection(na_m))
regions = {
    "namibia": (na, "Namibia", "Natural Earth"),
    "coast30": (strip, "The coast", "Natural Earth"),
    "skeleton_np": (osm_poly(SRC / "Skeleton_Coast.json"), "Skeleton Coast Park", OSM),
    "sperrgebiet": (osm_poly(SRC / "parks2.json", 4869664), "Sperrgebiet", OSM),
    "namib_naukluft": (osm_poly(SRC / "parks2.json", 4150085), "Namib-Naukluft", OSM),
    "walvis_enclave": (wb, "Walvis Bay", "illustration"),
    "empty_south": (ribbon(-26.62, -22.98), "481 km, nobody", "Own measurement (measure_population.py)"),
    "empty_north": (ribbon(-20.00, -17.26), "347 km, nobody", "Own measurement (measure_population.py)"),
}
for k, (g, name, src) in regions.items():
    g = g.simplify(0.002)
    (HERE / f"{k}.geojson").write_text(json.dumps({"type": "FeatureCollection", "features": [
        {"type": "Feature", "properties": {"name": name, "credit": src}, "geometry": mapping(g)}]}))
    print(f"{k}: {transform(to_m, g).area/1e6:,.0f} km2")
