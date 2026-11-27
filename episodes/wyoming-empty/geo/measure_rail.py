"""Own measurement M1: how many Wyomingites live near the 1868 Union Pacific line.

Inputs (downloaded 2026-11-27 into .cache/geo/census, both US Census Bureau, public domain):
  CenPop2020_Mean_BG56.txt  2020 census population and centre of population of every block group in Wyoming
  2020_gaz_place_56.txt     2020 Gazetteer, Wyoming places (internal points) for the line's stations
  Wyoming outline: Natural Earth 10m admin-1 (.cache/geo/ne)
The 1868 line is drawn through its stations, east to west (Pine Bluffs ... Evanston, then the Utah border);
it runs within a few km of the real track, which a 20 km band absorbs. Medicine Bow -> Rawlins stands for the
1868 route by Carbon (the Hanna cut-off came in 1900).
Run: venv python -I episodes/wyoming-empty/geo/measure_rail.py
"""
import csv, json
from pathlib import Path
import numpy as np, shapely
from shapely.geometry import LineString, shape
from shapely.ops import transform, unary_union
from pyproj import Transformer, Geod

ROOT = Path(__file__).resolve().parents[3]
C = ROOT / ".cache/geo/census"
STATIONS = ["Pine Bluffs town", "Cheyenne city", "Laramie city", "Rock River town", "Medicine Bow town",
            "Rawlins city", "Wamsutter town", "Point of Rocks CDP", "Rock Springs city", "Green River city",
            "Granger town", "Evanston city"]
places = {}
for row in csv.reader(open(C / "2020_gaz_place_56.txt", encoding="utf-8"), delimiter="\t"):
    if row[0] == "USPS":
        continue
    places[row[3].strip()] = (float(row[-1]), float(row[-2]))
pts = [(-104.053, 41.18)] + [places[s] for s in STATIONS] + [(-111.046, 41.25)]

bg = list(csv.DictReader(open(C / "CenPop2020_Mean_BG56.txt", encoding="utf-8-sig")))
pop = np.array([int(r["POPULATION"]) for r in bg]); lat = np.array([float(r["LATITUDE"]) for r in bg])
lon = np.array([float(r["LONGITUDE"]) for r in bg])
tot = pop.sum()

ne = json.load(open(ROOT / ".cache/geo/ne/ne_10m_admin_1_states_provinces.geojson", encoding="utf-8"))
wy = next(shape(f["geometry"]) for f in ne["features"] if f["properties"].get("iso_3166_2") == "US-WY").buffer(0)
fwd = Transformer.from_crs(4326, 5070, always_xy=True)   # US Albers equal-area, metres
geod = Geod(ellps="WGS84")
wy_m = transform(fwd.transform, wy); line_m = transform(fwd.transform, LineString(pts))
x, y = fwd.transform(lon, lat)
print(f"Wyoming 2020 census (block groups): {tot:,} people in {len(pop)} block groups; land {wy_m.area/1e6:,.0f} km2 (NE outline)")
print(f"1868 line drawn through {len(STATIONS)} stations: {line_m.length/1000:,.0f} km")
for km in (10, 20, 30, 50):
    band = line_m.buffer(km * 1000).intersection(wy_m)
    inside = shapely.contains_xy(band, x, y)
    print(f"  within {km:2d} km: {pop[inside].sum():9,} = {pop[inside].sum()/tot*100:5.1f} % of people "
          f"on {band.area/wy_m.area*100:4.1f} % of the land")
