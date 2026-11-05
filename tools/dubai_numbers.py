"""New land off Dubai, 22 May 2001 (Landsat 7) -> 24 Sep 2026 (Landsat 8), from NDWI water masks at 15 m."""
import math, os, sys
import numpy as np
import rasterio, requests
from rasterio.transform import from_bounds
from PIL import Image
sys.path.insert(0, r"C:\projeler\yt-pipeline\pipeline")
import landsat
from sentinel import EARTH, _read

lon0, lat0, lon1, lat1 = 54.95, 24.93, 55.32, 25.32
def ux(lon): return (lon + 180) / 360
def uy(lat):
    s = math.radians(lat); return (1 - math.log(math.tan(s) + 1 / math.cos(s)) / math.pi) / 2
x0, y0, x1, y1 = ux(lon0), uy(lat1), ux(lon1), uy(lat0)
W = 2600
H = round(W * (y1 - y0) / (x1 - x0))
T = from_bounds((x0 - .5) * EARTH, (.5 - y1) * EARTH, (x1 - .5) * EARTH, (.5 - y0) * EARTH, W, H)
res = (x1 - x0) * EARTH / W * math.cos(math.radians(25.1))
SCENES = {"2001": ["LE07_L2SP_160042_20010522_02_T1", "LE07_L2SP_160043_20010522_02_T1"],
          "2026": ["LC08_L2SP_160042_20260924_02_T1", "LC08_L2SP_160043_20260924_02_T1"]}
tok = landsat._token()

def band(item, name):
    buf = np.zeros((H, W), np.float32)
    with rasterio.Env(**landsat.ENV):
        _read(f"{item['assets'][name]['href']}?{tok}", buf, T, res, nearest=False)
    return np.where(buf > 0, buf * 2.75e-5 - 0.2, np.nan)

masks = {}
for tag, ids in SCENES.items():
    items = requests.post(landsat.STAC, json={"collections": ["landsat-c2-l2"], "ids": ids}, timeout=90).json()["features"]
    g = np.full((H, W), np.nan, np.float32); n = g.copy()
    for it in items:
        gg, nn = band(it, "green"), band(it, "nir08")
        f = np.isnan(g) & np.isfinite(gg); g[f] = gg[f]; n[f] = nn[f]
    ndwi = (g - n) / (g + n + 1e-6)
    masks[tag] = ndwi > 0.0
    print(tag, "valid", np.isfinite(ndwi).mean().round(3))

def lat_of(fy):
    yy = y0 + fy * (y1 - y0); return math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * yy))))
lats = np.array([lat_of((i + .5) / H) for i in range(H)])
dx = (lon1 - lon0) * 111.32 * np.cos(np.radians(lats)) / W
dy = np.array([abs(lat_of(i / H) - lat_of((i + 1) / H)) * 110.57 for i in range(H)])
pix = (dx * dy)[:, None]
new = masks["2001"] & ~masks["2026"]
print(f"pixel ~{res:.1f} m; new land total {(pix * new).sum():.1f} km2; water gained {(pix * (~masks['2001'] & masks['2026'])).sum():.1f} km2")
def box(a, b, c, d):
    cs = slice(int((a - lon0) / (lon1 - lon0) * W), int((c - lon0) / (lon1 - lon0) * W))
    r = np.where((lats >= b) & (lats <= d))[0]; return slice(r.min(), r.max() + 1), cs
for name, bx in {"Palm Jumeirah": (55.105, 25.095, 55.165, 25.14), "Palm Jebel Ali": (54.95, 24.96, 55.05, 25.035),
                 "The World": (55.13, 25.19, 55.24, 25.27), "Dubai Islands": (55.27, 25.27, 55.32, 25.32)}.items():
    r, c = box(*bx); print(f"{name}: {(pix[r] * new[r, c]).sum():.1f} km2")
D = "build/dubai-numbers/"
import os; os.makedirs(D, exist_ok=True)
Image.fromarray((np.dstack([new, ~masks["2001"] & masks["2026"], np.zeros_like(new)]) * 255).astype(np.uint8)).resize((800, round(800 * H / W))).save(D + "newland_ndwi.png")
np.save(D + "new_mask.npy", new)
