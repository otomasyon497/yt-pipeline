"""M1: Key West (NOAA 8724580) monthly mean sea level, 1913-2025 -> rise and trends. Writes measure_sealevel.txt."""
import json, sys, urllib.request
import numpy as np
URL = ("https://api.tidesandcurrents.noaa.gov/api/prod/datagetter?product=monthly_mean&station=8724580"
       "&begin_date=19130101&end_date=20251231&datum=MSL&units=english&time_zone=gmt&format=json&application=yt_pipeline")
src = sys.argv[1] if len(sys.argv) > 1 else None
d = json.load(open(src)) if src else json.load(urllib.request.urlopen(URL))
rows = [(int(r["year"]) + (int(r["month"]) - 0.5) / 12, float(r["MSL"])) for r in d["data"] if r.get("MSL") not in ("", None)]
t, h = np.array(rows).T
out = [f"months with data: {len(t)} ({t.min():.1f}-{t.max():.1f})"]
for a, b in [(1913, 2026), (1996, 2026), (2011, 2026)]:
    m = (t >= a) & (t < b)
    k = np.polyfit(t[m], h[m], 1)[0]  # ft per year
    out.append(f"trend {a}-{b-1}: {k*304.8:.2f} mm/yr = {k*12*100:.1f} in per century")
def mean(a, b):
    m = (t >= a) & (t < b); return h[m].mean()
first, last = mean(1913, 1923), mean(2016, 2026)
out.append(f"mean 1913-1922 vs 2016-2025: +{(last-first)*12:.1f} in")
k = np.polyfit(t, h, 1)
out.append(f"full-record fit, 1913 -> 2025: +{k[0]*(2025-1913)*12:.1f} in")
open("measure_sealevel.txt", "w").write("\n".join(out) + "\n"); print("\n".join(out))
