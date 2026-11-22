"""Approximate crater outline for the map (a circle, not a survey line).

Centre 37.283 N, 76.017 W and outer diameter ~85 km (Earth Impact Database via Wikipedia; USGS describes the structure
under the lower bay and the peninsulas of SE Virginia). The on-screen label says "approximate".
Run: python episodes/chesapeake-bay-bridge-tunnel/geo/make_regions.py
"""
import json
import math
from pathlib import Path

HERE = Path(__file__).parent
LAT0, LON0 = 37.283, -76.017


def circle(radius_km: float, n: int = 120) -> list:
    pts = []
    for i in range(n + 1):
        a = 2 * math.pi * i / n
        dlat = radius_km * math.cos(a) / 111.32
        dlon = radius_km * math.sin(a) / (111.32 * math.cos(math.radians(LAT0)))
        pts.append([round(LON0 + dlon, 5), round(LAT0 + dlat, 5)])
    return pts


def write(name: str, radius_km: float, label: str) -> None:
    gj = {"type": "FeatureCollection", "features": [{"type": "Feature", "properties": {"name": label},
          "geometry": {"type": "Polygon", "coordinates": [circle(radius_km)]}}]}
    (HERE / f"{name}.geojson").write_text(json.dumps(gj), encoding="utf-8")


write("crater_outer", 42.5, "Buried impact crater (approximate)")   # ~85 km across
write("crater_inner", 19.0, "Inner basin")   # ~38 km inner basin
print("ok")
