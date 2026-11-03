"""Reproduce the caspian-sea own calculations on the PC (stdlib + Pillow, a few MB of downloads, about 5 minutes).

1. Open water in the NE Caspian box on clear MODIS Terra days (NASA GIBS WMS, bands 7-2-1: water is dark in SWIR and
   NIR), median of Aug-Sep 2000-2002 vs 2023-2025.
2. Seafloor (NOAA ETOPO 2022, 60 arc-seconds, the same grid as pipeline/bathy.py): sea area today and after a fall of
   5 / 8 / 10 / 14 m; water left north of 44.5 N (the northern basin).

usage: python tools/caspian_numbers.py [modis] [seafloor]
"""
import io
import math
import re
import statistics
import sys
import urllib.parse
import urllib.request
from collections import deque
from datetime import date, timedelta

from PIL import Image

GIBS = "https://gibs.earthdata.nasa.gov/wms/epsg4326/best/wms.cgi"
ETOPO = ("https://www.ngdc.noaa.gov/thredds/dodsC/global/ETOPO2022/60s/60s_bed_elev_netcdf/"
         "ETOPO_2022_v1_60s_N90W180_bed.nc")
BOX = (44.40, 49.60, 47.70, 54.60)  # lat0, lon0, lat1, lon1 of the counting box


def gibs(day: str, layer: str, w: int, h: int, fmt: str) -> Image.Image:
    lat0, lon0, lat1, lon1 = BOX
    q = {"SERVICE": "WMS", "VERSION": "1.3.0", "REQUEST": "GetMap", "LAYERS": layer, "CRS": "EPSG:4326",
         "BBOX": f"{lat0},{lon0},{lat1},{lon1}", "WIDTH": w, "HEIGHT": h, "FORMAT": fmt, "TIME": day}
    return Image.open(io.BytesIO(urllib.request.urlopen(f"{GIBS}?{urllib.parse.urlencode(q)}", timeout=120).read())).convert("RGB")


def modis() -> None:
    lat0, lon0, lat1, lon1 = BOX
    w, h = 625, 412
    dlat, dlon = (lat1 - lat0) / h, (lon1 - lon0) / w
    cell = [(dlat * 111.32) * (dlon * 111.32 * math.cos(math.radians(lat1 - (y + 0.5) * dlat))) for y in range(h)]
    meds = []
    for years in ((2000, 2001, 2002), (2023, 2024, 2025)):
        vals = []
        for yr in years:
            d = date(yr, 8, 1)
            while d <= date(yr, 9, 30):
                try:
                    tc = list(gibs(d.isoformat(), "MODIS_Terra_CorrectedReflectance_TrueColor", w, h, "image/jpeg").getdata())
                except OSError:
                    d += timedelta(days=3)
                    continue
                cloud = sum(1 for r, g, b in tc if min(r, g, b) > 175 and max(r, g, b) - min(r, g, b) < 30) / len(tc)
                gaps = sum(1 for r, g, b in tc if max(r, g, b) < 8) / len(tc)
                if cloud < 0.01 and gaps < 0.002:
                    px = gibs(d.isoformat(), "MODIS_Terra_CorrectedReflectance_Bands721", w, h, "image/png").load()
                    vals.append(sum(cell[y] for y in range(h) for x in range(w) if px[x, y][0] < 45 and px[x, y][1] < 70))
                d += timedelta(days=3)
        meds.append(statistics.median(vals))
        print(f"MODIS {years[0]}-{years[-1]}: {len(vals)} clear days, median open water {meds[-1]:,.0f} km2")
    print(f"MODIS loss: {meds[0] - meds[1]:,.0f} km2 ({(meds[0] - meds[1]) / meds[0]:.0%})")


def seafloor() -> None:
    lon0, lat0, lon1, lat1, level = 46.0, 36.0, 55.5, 47.8, -29.3  # as bathy.BASINS["caspian"]
    r0, r1 = round((lat0 + 90) * 60), round((lat1 + 90) * 60) - 1
    c0, c1 = round((lon0 + 180) * 60), round((lon1 + 180) * 60) - 1
    txt = urllib.request.urlopen(f"{ETOPO}.ascii?z[{r0}:1:{r1}][{c0}:1:{c1}]", timeout=300).read().decode()
    z = [[float(v) for v in line.split(", ")[1:]] for line in txt.splitlines() if re.match(r"^\[\d+\], ", line)]
    h, w = len(z), len(z[0])
    lat = [-90 + (r0 + i + 0.5) / 60 for i in range(h)]
    cell = [(111.32 / 60) ** 2 * math.cos(math.radians(la)) for la in lat]
    seed = (int((42.0 - lat0) * 60), int((50.0 - lon0) * 60))

    def sea(lv: float) -> tuple[float, float]:
        seen = {seed}
        q = deque([seed])
        area = north = 0.0
        while q:
            i, j = q.popleft()
            area += cell[i]
            north += cell[i] if lat[i] > 44.5 else 0.0
            for a, b in ((i + 1, j), (i - 1, j), (i, j + 1), (i, j - 1)):
                if 0 <= a < h and 0 <= b < w and (a, b) not in seen and z[a][b] < lv:
                    seen.add((a, b))
                    q.append((a, b))
        return area, north

    now, north_now = sea(level)
    print(f"seafloor today ({level} m): sea {now:,.0f} km2, north of 44.5 N {north_now:,.0f} km2")
    for drop in (5, 8, 10, 14):
        a, n = sea(level - drop)
        print(f"  -{drop} m: {now - a:,.0f} km2 falls dry ({(now - a) / now:.0%}); north of 44.5 N left {n:,.0f} km2 "
              f"({1 - n / north_now:.0%} of it gone)")


if __name__ == "__main__":
    jobs = sys.argv[1:] or ["modis", "seafloor"]
    if "seafloor" in jobs:
        seafloor()
    if "modis" in jobs:
        modis()
