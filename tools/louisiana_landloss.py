"""Own measurement for the louisiana-land-loss episode: land area per site box and year, from Landsat.

Modelled on tools/demak_shoreline.py. Per site (a fixed lon/lat box, each on its own 15 m grid and with its own
scene choice, since the boxes are up to 160 km apart and fall on different Landsat paths) and year: up to four of
the clearest October-November Landsat 4/5/8/9 days (Collection 2 Level-2 surface reflectance, 30 m, read at 15 m;
October ranked before November; Landsat 7 after its May 2003 scan-line failure only as a last resort) give a
per-pixel median MNDWI over the clear observations (QA_PIXEL cloud, dilated cloud and shadow masked). Same-day
scenes of one path (consecutive rows) are joined. A pixel is water when that median MNDWI > 0 and land otherwise;
"permanent land" is land on every clear day. Change = land in that year minus land in the base year (1985).
Usage: python -I tools/louisiana_landloss.py <repo root> <out.json> [png dir]
"""
import json
import sys
import warnings
from pathlib import Path

import numpy as np
import rasterio
from rasterio.transform import from_bounds

warnings.filterwarnings("ignore", "All-NaN slice")
ROOT = Path(sys.argv[1])
PNG_DIR = Path(sys.argv[3]) if len(sys.argv) > 3 else None  # optional: land/water masks for a visual check
sys.path.insert(0, str(ROOT / "pipeline"))
import landsat  # noqa: E402
from sentinel import EARTH, _read  # noqa: E402

# Boxes (lon_west, lat_south, lon_east, lat_north) from episodes/louisiana-land-loss/research.md. Sub-boxes are
# measured on their parent's composite (same days).
SITES = {
    "Isle de Jean Charles": (-90.53, 29.36, -90.45, 29.45),
    "Wax Lake Delta": (-91.50, 29.44, -91.38, 29.56),
    "Atchafalaya Delta": (-91.36, 29.40, -91.22, 29.52),
    "Barataria": (-90.10, 29.40, -89.85, 29.65),
}
SUBS = {"Isle de Jean Charles ridge": ("Isle de Jean Charles", (-90.50, 29.38, -90.475, 29.43))}
YEARS = [1985, 1990, 1995, 2000, 2005, 2010, 2015, 2020, 2024, 2026]
PX = 15.0
MAX_DAYS = 4
MIN_CLEAR = 0.85  # share of the site box that must be clear for a day to count


def windows(year):
    """(start, end, months) windows tried in order until at least two clear days are found."""
    w = [(f"{year}-10-01", f"{year}-11-30", (10, 11))]
    if year == 1985:
        w.append(("1984-10-01", "1984-11-30", (10, 11)))  # Landsat 5 from March 1984; NASA's Wax Lake pair uses Nov 1984
    elif year < 2026:
        w.append((f"{year - 1}-10-01", f"{year + 1}-11-30", (10, 11)))
    w.append((f"{year}-09-01", f"{year}-12-31", (9, 10, 11, 12)))
    return w


def merc(lon, lat):
    return lon / 360 * EARTH, np.log(np.tan(np.pi / 4 + np.radians(lat) / 2)) / (2 * np.pi) * EARTH


class Grid:
    def __init__(self, box):
        self.box = box
        self.x0, self.y0 = merc(box[0], box[1])
        self.x1, self.y1 = merc(box[2], box[3])
        k = np.cos(np.radians((box[1] + box[3]) / 2))  # ground metres per Mercator metre
        self.w = int(round((self.x1 - self.x0) * k / PX))
        self.h = int(round((self.y1 - self.y0) * k / PX))
        self.transform = from_bounds(self.x0, self.y0, self.x1, self.y1, self.w, self.h)

    def window(self, box):
        w, s, e, n = box
        xa, ya = merc(w, s)
        xb, yb = merc(e, n)
        c0 = int(round((xa - self.x0) / (self.x1 - self.x0) * self.w))
        c1 = int(round((xb - self.x0) / (self.x1 - self.x0) * self.w))
        r0 = int(round((self.y1 - yb) / (self.y1 - self.y0) * self.h))
        r1 = int(round((self.y1 - ya) / (self.y1 - self.y0) * self.h))
        return slice(r0, r1), slice(c0, c1)


def read_day(grid, items):
    """Median-ready MNDWI for one day: same-day scenes of one path fill each other's gaps."""
    tok = landsat._token()
    bands = {}
    for name in ("green", "swir16", "qa_pixel"):
        acc = np.zeros((grid.h, grid.w), dtype=np.float32)
        for it in items:
            a = it["assets"][name]
            buf = np.zeros((grid.h, grid.w), dtype=np.float32)
            with rasterio.Env(**landsat.ENV):
                _read(f"{a['href']}?{tok}", buf, grid.transform, PX, nearest=name == "qa_pixel")
            acc = np.where(acc == 0, buf, acc)
        bands[name] = acc
    g, s, qa = bands["green"], bands["swir16"], bands["qa_pixel"]
    q = qa.astype(np.uint32)
    clear = (g > 0) & (s > 0) & ((q & 0b11010) == 0)
    g = g * 2.75e-5 - 0.2
    s = s * 2.75e-5 - 0.2
    m = (g - s) / np.maximum(np.abs(g + s), 1e-4)
    return np.where(clear, m, np.nan)


def slc_off(p):
    return p["platform"] == "landsat-7" and p["datetime"][:10] >= "2003-05-31"


def composite(grid, year):
    b = grid.box
    poly = {"type": "Polygon", "coordinates": [[[b[0], b[1]], [b[2], b[1]], [b[2], b[3]], [b[0], b[3]], [b[0], b[1]]]]}
    stack, days, tried = [], [], set()

    def covered():
        return float(np.isfinite(np.array(stack)).any(0).mean()) if stack else 0.0

    def done():
        return len(days) >= MAX_DAYS
    # Pass 1 without Landsat 7 SLC-off (22 % striped gaps); pass 2 allows it only if pass 1 came up short.
    for allow_slc_off in (False, True):
        for start, end, months in windows(year):
            if done():
                break
            plats = ["landsat-4", "landsat-5", "landsat-7", "landsat-8", "landsat-9"]
            items = landsat._post({"collections": ["landsat-c2-l2"], "intersects": poly,
                                   "datetime": f"{start}T00:00:00Z/{end}T23:59:59Z", "limit": 200,
                                   "query": {"eo:cloud_cover": {"lt": 70}, "platform": {"in": plats}}})
            groups = {}
            for i in items:
                p = i["properties"]
                if int(p["datetime"][5:7]) not in months or slc_off(p) and not allow_slc_off:
                    continue
                key = (p["datetime"][:10], p["platform"], p.get("landsat:wrs_path"))
                groups.setdefault(key, []).append(i)

            def rank(key):
                return (abs(int(key[0][:4]) - year), int(key[0][5:7]) != 10,
                        min(x["properties"]["eo:cloud_cover"] for x in groups[key]))
            for key in sorted(groups, key=rank)[:16]:
                if key in tried or done():
                    continue
                tried.add(key)
                try:
                    m = read_day(grid, groups[key])
                except Exception as exc:  # one bad scene must not stop the year
                    print("  skip", key, str(exc)[:80], flush=True)
                    continue
                share = float(np.isfinite(m).mean())
                # partly cloudy days are kept when they add clear pixels: the per-pixel median fills the gaps
                if share < MIN_CLEAR and (share < 0.3 or covered() >= 0.99):
                    continue
                stack.append(m)
                days.append({"date": key[0], "platform": key[1], "path": key[2],
                             "scenes": [x["id"] for x in groups[key]], "clear_share": round(share, 3)})
            if len(days) >= 2 and covered() >= 0.98:
                break
        if len(days) >= 2 and covered() >= 0.98:
            break
    if not days:
        return None
    arr = np.array(stack)
    with np.errstate(all="ignore"):
        med = np.nanmedian(arr, axis=0)
    # Drop days that disagree with the composite on their own clear pixels (haze or thin cloud that passed the
    # QA mask reads as water everywhere, e.g. Wax Lake 22 Oct 1984), then recompute.
    keep = []
    for k, m in enumerate(arr):
        ok = np.isfinite(m) & np.isfinite(med)
        d_land = float((m[ok] <= 0).mean()) if ok.any() else 0.0
        c_land = float((med[ok] <= 0).mean()) if ok.any() else 0.0
        days[k]["land_share_that_day"] = round(d_land, 3)
        days[k]["land_ha_that_day"] = round(float((m <= 0).sum()) * PX * PX / 1e4, 1)
        if len(arr) >= 3 and abs(d_land - c_land) > 0.2:
            days[k]["dropped"] = f"land share {d_land:.2f} vs composite {c_land:.2f} on the same pixels"
        else:
            keep.append(k)
    dropped = [d for k, d in enumerate(days) if k not in keep]
    arr = arr[keep]
    days = [days[k] for k in keep]
    with np.errstate(all="ignore"):
        med = np.nanmedian(arr, axis=0)
        ever_water = np.nanmax(arr, axis=0) > 0
    return {"days": days, "dropped_days": dropped, "median": med, "ever_water": ever_water,
            "n_obs": np.isfinite(arr).sum(0)}


def measure(c, rs, cs, px_ha):
    med = c["median"][rs, cs]
    valid = np.isfinite(med)
    land = valid & (med <= 0)
    perm = valid & ~c["ever_water"][rs, cs] & (c["n_obs"][rs, cs] > 0)
    return {"days": c["days"], "dropped_days": c["dropped_days"], "valid_share": round(float(valid.mean()), 4), "box_ha": round(med.size * px_ha, 1),
            "land_ha": round(float(land.sum()) * px_ha, 1), "permanent_land_ha": round(float(perm.sum()) * px_ha, 1),
            "land_share": round(float(land.sum()) / max(1, valid.sum()), 4)}


def save_png(c, grid, name, year, subs):
    from PIL import Image, ImageDraw
    m = c["median"]
    img = np.zeros(m.shape + (3,), np.uint8)
    img[m > 0] = (40, 90, 200)
    img[m <= 0] = (200, 180, 120)
    im = Image.fromarray(img)
    d = ImageDraw.Draw(im)
    for sub_name, (_, sbox) in subs.items():
        rs, cs = grid.window(sbox)
        d.rectangle([cs.start, rs.start, cs.stop - 1, rs.stop - 1], outline=(255, 0, 0))
    d.text((4, 4), f"{name} {year} " + ",".join(x["date"] for x in c["days"]), fill=(255, 255, 255))
    im.save(PNG_DIR / f"louisiana_{name.lower().replace(' ', '_')}_{year}.png")


out_path = Path(sys.argv[2])
px_ha = PX * PX / 1e4
res = {name: {} for name in list(SITES) + list(SUBS)}
for name, box in SITES.items():
    grid = Grid(box)
    subs = {k: v for k, v in SUBS.items() if v[0] == name}
    for year in YEARS:
        try:
            c = composite(grid, year)
        except Exception as exc:
            print(name, year, "failed", str(exc)[:120], flush=True)
            c = None
        if c is None:
            print(name, year, "no clear days", flush=True)
            res[name][year] = None
            for k in subs:
                res[k][year] = None
            continue
        if PNG_DIR is not None:
            save_png(c, grid, name, year, subs)
        res[name][year] = measure(c, slice(None), slice(None), px_ha)
        for k, (_, sbox) in subs.items():
            res[k][year] = measure(c, *grid.window(sbox), px_ha)
        print(name, year, res[name][year]["land_ha"], [(d["date"], d["platform"], d["land_ha_that_day"])
                                                       for d in c["days"]], flush=True)

out = {}
for name in res:
    r = res[name]
    base = next((y for y in YEARS if r.get(y) and r[y]["valid_share"] > 0.98), None)
    for y in YEARS:
        if not r.get(y) or base is None:
            continue
        r[y]["land_change_ha"] = round(r[y]["land_ha"] - r[base]["land_ha"], 1)
        r[y]["land_change_pct"] = round(100 * (r[y]["land_ha"] - r[base]["land_ha"]) / max(1e-6, r[base]["land_ha"]), 1)
        r[y]["permanent_land_change_ha"] = round(r[y]["permanent_land_ha"] - r[base]["permanent_land_ha"], 1)
    box = SITES.get(name) or SUBS[name][1]
    out[name] = {"box": box, "base_year": base, "years": r}

out["method"] = (
    "Landsat Collection 2 Level-2 surface reflectance (USGS, via Microsoft Planetary Computer), Landsat 5 TM / 8-9 OLI "
    "(Landsat 7 ETM+ after May 2003 only as a last resort), 30 m pixels resampled to a 15 m grid per site box. Per "
    "site and year: up to 4 October-November days (October ranked first; partly cloudy days >=30 % clear are added until "
    "every pixel has a clear observation, at least one day >=85 % clear) after the QA_PIXEL "
    "cloud / dilated-cloud / shadow mask; same-day scenes of one path joined; a day whose land share on its clear pixels "
    "differs from the composite by >0.2 is dropped (haze); if the box is not covered, the window "
    "widens to Oct-Nov of the neighbouring years, then Sep-Dec of the year. 1985 may use Oct-Nov 1984. Water = "
    "per-pixel median MNDWI (green - SWIR 1.6 um)/(green + SWIR) > 0 over the clear days; land = the rest (MNDWI <= 0 "
    "threshold, not tuned per site). permanent_land = land on every clear day. land_change = land in that year minus "
    "land in the base year inside the fixed box. CAVEATS: 'land' means land or vegetated marsh above water on those "
    "days: emergent and floating marsh (flotant) reads as land, so marsh that is still there but degraded or "
    "floating counts, and loss is the conversion of marsh to open water. Water level on each day (tide range ~0.3 m, "
    "but cold-front north winds in Nov push water out and expose mudflats, south winds and river stage push it in) "
    "moves the wet edge on the flat deltas and marsh fringes; bare wet mud can read either way, and on the Wax Lake / "
    "Atchafalaya deltas subaqueous bars and shallow mudflats are counted only when exposed. Sediment-laden water near "
    "the river outlets lowers MNDWI a little. Single years are noisy (see land_ha_that_day for the spread within a "
    "composite); read decades. Hectares are ground hectares (Mercator scale corrected).")
out_path.write_text(json.dumps(out, indent=1), encoding="utf-8")
print(json.dumps({n: {y: v and (v["land_ha"], v.get("land_change_ha"), v.get("land_change_pct"),
                                [d["date"] for d in v["days"]]) for y, v in out[n]["years"].items()}
                  for n in res}, indent=0))
