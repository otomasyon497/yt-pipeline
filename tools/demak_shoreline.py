"""Own measurement for the jakarta-sinking episode: how much land the sea has taken at Sayung, Demak, from Landsat.

The coast of Sayung (Central Java) runs SW-NE with the Java Sea to the north-west. Fish ponds there turn into sea
as the ground sinks, so the robust measure is AREA: per site (a fixed box) and year, up to four of the clearest
dry-season (Jun-Oct) Landsat 5/7/8/9 days (Collection 2 Level-2 surface reflectance, 30 m, read at 15 m) give a
per-pixel median MNDWI over the clear observations (QA_PIXEL cloud, dilated cloud and shadow masked). A pixel is
water when that median MNDWI > 0 and land otherwise; "permanent land" is land on every clear day. Hectares lost =
land in the first year minus land in that year. A second, rougher measure walks every pixel row of a wider box in
from the sea (west) edge to the first run of three land pixels on the median composite: the mean of those rows is
the shoreline, and its landward shift is turned into a distance square to the coast with the base year's fitted
shoreline direction.
Usage: python -I tools/demak_shoreline.py <repo root> <out.json>
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

# Village areas from OpenStreetMap (reverse geocoding: Bedono west, Timbulsloko east of it, Surodadi north of
# Timbulsloko). name: (area box, walk box); boxes are (lon_west, lat_south, lon_east, lat_north). The walk box
# reaches west to where the sea already was in 1990.
SITES = {
    "Bedono": ((110.450, -6.935, 110.495, -6.900), (110.450, -6.935, 110.540, -6.905)),
    "Timbulsloko": ((110.495, -6.930, 110.540, -6.900), (110.465, -6.930, 110.540, -6.900)),
    "Surodadi": ((110.495, -6.900, 110.540, -6.870), (110.475, -6.900, 110.540, -6.870)),
}
UNION = (110.450, -6.935, 110.540, -6.870)
# year: list of (start, end) windows tried in order until enough clear days are found
YEARS = {1990: [("1990-06-01", "1990-10-31"), ("1988-06-01", "1992-10-31")]}
for _y in (1995, 2000, 2005, 2010, 2015, 2020, 2024, 2025, 2026):
    YEARS[_y] = [(f"{_y}-06-01", f"{_y}-10-31"), (f"{_y - 1}-06-01", f"{_y + 1}-10-31") if _y < 2026 else
                 (f"{_y}-04-01", f"{_y}-11-10")]
PX = 15.0
MAX_DAYS = 4
MIN_CLEAR = 0.85  # share of the union box that must be clear for a day to count


def merc(lon, lat):
    return lon / 360 * EARTH, np.log(np.tan(np.pi / 4 + np.radians(lat) / 2)) / (2 * np.pi) * EARTH


X0, Y0 = merc(UNION[0], UNION[1])
X1, Y1 = merc(UNION[2], UNION[3])
K = np.cos(np.radians((UNION[1] + UNION[3]) / 2))  # ground metres per Mercator metre
W = int(round((X1 - X0) * K / PX))
H = int(round((Y1 - Y0) * K / PX))
TRANSFORM = from_bounds(X0, Y0, X1, Y1, W, H)


def window(box):
    """Row/column slices of the union grid for a lon/lat box."""
    w, s, e, n = box
    xa, ya = merc(w, s)
    xb, yb = merc(e, n)
    c0 = int(round((xa - X0) / (X1 - X0) * W))
    c1 = int(round((xb - X0) / (X1 - X0) * W))
    r0 = int(round((Y1 - yb) / (Y1 - Y0) * H))
    r1 = int(round((Y1 - ya) / (Y1 - Y0) * H))
    return slice(r0, r1), slice(c0, c1)


def read_day(item):
    tok = landsat._token()
    bands = []
    for name in ("green", "swir16", "qa_pixel"):
        a = item["assets"][name]
        buf = np.zeros((H, W), dtype=np.float32)
        with rasterio.Env(**landsat.ENV):
            _read(f"{a['href']}?{tok}", buf, TRANSFORM, PX, nearest=name == "qa_pixel")
        bands.append(buf)
    g, s, qa = bands
    q = qa.astype(np.uint32)
    clear = (g > 0) & (s > 0) & ((q & 0b11010) == 0)
    g = g * 2.75e-5 - 0.2
    s = s * 2.75e-5 - 0.2
    m = (g - s) / np.maximum(np.abs(g + s), 1e-4)
    return np.where(clear, m, np.nan)


def composite(year):
    poly = {"type": "Polygon", "coordinates": [[[UNION[0], UNION[1]], [UNION[2], UNION[1]], [UNION[2], UNION[3]],
                                                [UNION[0], UNION[3]], [UNION[0], UNION[1]]]]}
    stack, days, tried = [], [], set()
    for start, end in YEARS[year]:
        plats = ["landsat-4", "landsat-5", "landsat-7", "landsat-8", "landsat-9"]
        items = landsat._post({"collections": ["landsat-c2-l2"], "intersects": poly,
                               "datetime": f"{start}T00:00:00Z/{end}T23:59:59Z", "limit": 200,
                               "query": {"eo:cloud_cover": {"lt": 60}, "platform": {"in": plats}}})

        def rank(i):  # Landsat 7 after the scan-line failure has 22 % gaps: only when nothing else is clear
            p = i["properties"]
            slc_off = p["platform"] == "landsat-7" and p["datetime"][:10] >= "2003-05-31"
            return (slc_off, abs(int(p["datetime"][:4]) - year), p["eo:cloud_cover"])
        # the dry season only, also when the window spans several years
        items = sorted((i for i in items if 6 <= int(i["properties"]["datetime"][5:7]) <= 10 or year == 2026), key=rank)
        for it in items[:16]:
            if it["id"] in tried or len(days) >= MAX_DAYS:
                continue
            tried.add(it["id"])
            try:
                m = read_day(it)
            except Exception as exc:  # one bad scene must not stop the year
                print("  skip", it["id"], str(exc)[:80], flush=True)
                continue
            p = it["properties"]
            slc_off = p["platform"] == "landsat-7" and p["datetime"][:10] >= "2003-05-31"
            share = float(np.isfinite(m).mean())
            if share < (0.6 if slc_off else MIN_CLEAR):
                continue
            stack.append(m)
            days.append({"date": p["datetime"][:10], "platform": p["platform"], "clear_share": round(share, 3)})
        if len(days) >= 2:
            break
    if not days:
        return None
    arr = np.array(stack)
    with np.errstate(all="ignore"):
        med = np.nanmedian(arr, axis=0)
        ever_water = np.nanmax(arr, axis=0) > 0
    return {"days": days, "median": med, "ever_water": ever_water, "n_obs": np.isfinite(arr).sum(0)}


def walk_west(water, valid):
    """Columns from the west edge to the first run of three land pixels, per row (NaN where not found)."""
    h, w = water.shape
    out = np.full(h, np.nan)
    for r in range(h):
        if valid[r].mean() < 0.98 or not water[r, :3].all():
            continue
        land = ~water[r]
        run = np.convolve(land.astype(int), np.ones(3, int), "valid") == 3
        idx = np.flatnonzero(run)
        if idx.size:
            out[r] = idx[0]
    return out


out_path = Path(sys.argv[2])
px_ha = PX * PX / 1e4
res = {name: {} for name in SITES}
profiles = {name: {} for name in SITES}
for year in YEARS:
    try:
        c = composite(year)
    except Exception as exc:
        print(year, "failed", str(exc)[:120], flush=True)
        c = None
    if c is None:
        print(year, "no clear days", flush=True)
        for name in SITES:
            res[name][year] = None
        continue
    if PNG_DIR is not None:
        from PIL import Image, ImageDraw
        m = c["median"]
        img = np.zeros(m.shape + (3,), np.uint8)
        img[m > 0] = (40, 90, 200)
        img[m <= 0] = (200, 180, 120)
        im = Image.fromarray(img)
        d = ImageDraw.Draw(im)
        for name, (box, wbox) in SITES.items():
            rs, cs = window(box)
            d.rectangle([cs.start, rs.start, cs.stop - 1, rs.stop - 1], outline=(255, 0, 0))
            d.text((cs.start + 4, rs.start + 4), name, fill=(255, 255, 255))
        d.text((4, H - 14), str(year), fill=(255, 255, 255))
        im.save(PNG_DIR / f"demak_mask_{year}.png")
    for name, (box, wbox) in SITES.items():
        rs, cs = window(box)
        med = c["median"][rs, cs]
        valid = np.isfinite(med)
        land = valid & (med <= 0)
        perm = valid & ~c["ever_water"][rs, cs] & (c["n_obs"][rs, cs] > 0)
        rec = {"days": c["days"], "valid_share": round(float(valid.mean()), 4),
               "box_ha": round(med.size * px_ha, 1),
               "land_ha": round(float(land.sum()) * px_ha, 1),
               "permanent_land_ha": round(float(perm.sum()) * px_ha, 1)}
        rs2, cs2 = window(wbox)
        wmed = c["median"][rs2, cs2]
        rows = walk_west(np.isfinite(wmed) & (wmed > 0), np.isfinite(wmed))
        ok = np.isfinite(rows)
        rec["shore_rows_share"] = round(float(ok.mean()), 3)
        if ok.mean() >= 0.6:
            rec["shore_from_west_m"] = round(float(np.nanmean(rows)) * PX, 1)
        profiles[name][year] = rows
        res[name][year] = rec
    print(year, [(n, res[n][year]["land_ha"], res[n][year].get("shore_from_west_m")) for n in SITES],
          c["days"], flush=True)

out = {}
for name, (box, wbox) in SITES.items():
    r = res[name]
    base = next((y for y in YEARS if r.get(y) and r[y]["valid_share"] > 0.98), None)
    slope_factor = None
    if base is not None:
        prof = profiles[name][base]
        ok = np.isfinite(prof)
        if ok.sum() > 10:
            s = np.polyfit(np.flatnonzero(ok), prof[ok], 1)[0]  # columns per row along the base-year shoreline
            slope_factor = 1 / np.sqrt(1 + s * s)  # west-east distance -> distance square to that shoreline
    for y in YEARS:
        if not r.get(y) or base is None:
            continue
        r[y]["land_lost_ha"] = round(r[base]["land_ha"] - r[y]["land_ha"], 1)
        r[y]["permanent_land_lost_ha"] = round(r[base]["permanent_land_ha"] - r[y]["permanent_land_ha"], 1)
        if "shore_from_west_m" in r[y] and "shore_from_west_m" in r[base]:
            a, b = profiles[name][base], profiles[name][y]
            both = np.isfinite(a) & np.isfinite(b)
            if both.mean() >= 0.5:
                d = float(np.mean(b[both] - a[both])) * PX
                r[y]["shore_advance_m_west_east"] = round(d, 1)
                if slope_factor is not None:
                    r[y]["shore_advance_m_normal"] = round(d * slope_factor, 1)
                r[y]["rows_advance_p10_p90_m"] = [round(float(np.percentile(b[both] - a[both], q)) * PX, 1)
                                                  for q in (10, 90)]
    out[name] = {"box": box, "walk_box": wbox, "base_year": base,
                 "shore_direction_factor": slope_factor and round(float(slope_factor), 3), "years": r}

out["method"] = (
    "Landsat Collection 2 Level-2 surface reflectance (USGS, via Microsoft Planetary Computer), Landsat 5 TM / 7 ETM+ / "
    "8-9 OLI, 30 m pixels resampled to a 15 m grid. Per year: up to 4 dry-season (Jun-Oct) days whose box is >=85 % "
    "clear after the QA_PIXEL cloud / dilated-cloud / shadow mask (Landsat 7 after May 2003 only as a last resort, "
    ">=60 %); if fewer than 2 such days, the window widens to the neighbouring years. Water = per-pixel median MNDWI "
    "(green - SWIR 1.6 um)/(green + SWIR) > 0 over the clear days; land = the rest. land_lost_ha = land in the base year "
    "minus land in that year inside the fixed site box. permanent_land = never water on any clear day. Shoreline: each "
    "row of the walk box from the west (sea) edge to the first run of 3 land pixels (45 m) on the median composite; "
    "shore_advance_m_normal is the mean row shift converted to a distance square to the base-year shoreline. "
    "CAVEATS: MNDWI cannot tell sea from flooded fish ponds (tambak): ponds full of water count as water, dry or "
    "vegetated pond beds and bunds count as land, so 'land' here is dry ground, villages, roads, mangroves, rice and "
    "dry pond beds, and part of the land loss before ~2000 is ponds being flooded, not open sea. Tide state on each "
    "day moves the wet line on the mudflats; single years are noisy, read decades. Mangrove belts planted after ~2005 "
    "count as land. Distances are ground metres.")
out_path.write_text(json.dumps(out, indent=1), encoding="utf-8")
print(json.dumps({n: {y: v and (v["land_ha"], v.get("land_lost_ha"), v.get("shore_advance_m_normal"))
                      for y, v in out[n]["years"].items()} for n in SITES}, indent=0))
