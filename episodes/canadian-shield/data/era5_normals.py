"""Own measurement: 1991-2020 mean temperatures from ERA5 (Open-Meteo archive API, ~25 km grid cells).
Prints annual, January and July means and the number of days with a daily mean below 0 C, per place.
Run: python -I data/era5_normals.py  (writes data/era5_normals.json)
"""
import json, urllib.request
from pathlib import Path
PLACES = {"Churchill": (58.77, -94.17), "Helsinki": (60.17, 24.94), "Stockholm": (59.33, 18.07),
          "Thunder Bay": (48.38, -89.25), "Timmins": (48.48, -81.33), "Oulu": (65.01, 25.47), "Schefferville": (54.80, -66.82)}
out = {}
for name, (lat, lon) in PLACES.items():
    u = (f"https://archive-api.open-meteo.com/v1/archive?latitude={lat}&longitude={lon}&start_date=1991-01-01"
         f"&end_date=2020-12-31&daily=temperature_2m_mean&timezone=UTC")
    d = json.load(urllib.request.urlopen(u, timeout=120))["daily"]
    t = [(day, v) for day, v in zip(d["time"], d["temperature_2m_mean"]) if v is not None]
    mean = lambda xs: sum(xs) / len(xs)
    out[name] = {"lat": lat, "lon": lon, "annual": round(mean([v for _, v in t]), 1),
                 "jan": round(mean([v for day, v in t if day[5:7] == "01"]), 1),
                 "jul": round(mean([v for day, v in t if day[5:7] == "07"]), 1),
                 "days_below_0_per_year": round(sum(1 for _, v in t if v < 0) / 30)}
    print(name, out[name])
Path(__file__).with_name("era5_normals.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
