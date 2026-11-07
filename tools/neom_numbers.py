"""The Line's works corridor in 2026: length of the straight strip of works against the planned 170 km.

Traced by eye on Copernicus Sentinel-2 (24 Aug 2026, ~31 m/px over 34.95-36.25 E) against 2020 (12 Sep / 29 Oct,
before earthworks began in Oct 2021): the strip shows as graded ground, pads, plants and trench sections that are
absent in 2020. An automatic colour-change trace was tried first and dropped: shadows in the mountains and the
season difference made it miss long stretches that are plainly visible (see PLAN.md log 2026-11-07).

The end points below were read off the image; the line between them follows the corridor's straight fit (P0-P1).
Writes episodes/neom-the-line/geo/works.geojson (for the map highlight) and prints the lengths.
"""
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
P0, P1 = (35.06, 28.118), (36.22, 28.033)   # straight fit of the corridor (lon, lat)
SEGMENTS = [  # (from lon, to lon, what is visible)
    (35.00, 35.95, "continuous strip from near the Gulf of Aqaba coast through the mountains"),
    (35.98, 36.17, "eastern section in the red dunes: graded strip and large pads"),
]
PLANNED_KM = 170


def lat_on_line(lon: float) -> float:
    return P0[1] + (lon - P0[0]) * (P1[1] - P0[1]) / (P1[0] - P0[0])


def km(a, b) -> float:
    """Great-circle distance (haversine) in km between (lon, lat) points."""
    r = 6371.0088
    p1, p2 = math.radians(a[1]), math.radians(b[1])
    dp, dl = p2 - p1, math.radians(b[0] - a[0])
    h = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(h))


def main():
    feats, total = [], 0.0
    for lon_a, lon_b, what in SEGMENTS:
        a, b = (lon_a, round(lat_on_line(lon_a), 4)), (lon_b, round(lat_on_line(lon_b), 4))
        d = km(a, b)
        total += d
        print(f"{lon_a:.2f} E -> {lon_b:.2f} E: {d:.1f} km  ({what})")
        feats.append({"type": "Feature", "properties": {"what": what, "km": round(d, 1),
                      "credit": "Our trace on Copernicus Sentinel-2 imagery, 24 Aug 2026"},
                      "geometry": {"type": "LineString", "coordinates": [list(a), list(b)]}})
    gap = km((SEGMENTS[0][1], lat_on_line(SEGMENTS[0][1])), (SEGMENTS[1][0], lat_on_line(SEGMENTS[1][0])))
    print(f"total {total:.0f} km of works (gap {gap:.1f} km) = {total / PLANNED_KM:.0%} of the planned {PLANNED_KM} km")
    out = ROOT / "episodes" / "neom-the-line" / "geo" / "works.geojson"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"type": "FeatureCollection", "features": feats}, indent=1), encoding="utf-8")
    print("wrote", out.relative_to(ROOT))


if __name__ == "__main__":
    main()
