"""Channel art for "Ink & Orbit": profile picture (800 x 800), banner (2560 x 1440) and review previews.

One idea in both pictures: the same coasts drawn in ink on paper (left) and seen from orbit (right), split by the
amber wipe line the videos use for before/after views. The profile picture adds the orbit ring and a satellite.
Data: Natural Earth (public domain) and NASA Blue Marble via GIBS (NASA imagery, free to reuse, no endorsement
implied). Fonts: Bebas Neue, Inter and EB Garamond, all under the SIL Open Font Licence 1.1.
Usage: python tools/channel_art.py <out_dir>    (seconds of CPU; downloads are cached in CACHE_DIR)
"""
import math
import sys
from pathlib import Path

import numpy as np
import requests
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from scipy import ndimage
from shapely.geometry import box as lonlat_box

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "pipeline"))
import geo  # noqa: E402
import gibs  # noqa: E402
from config import CACHE_DIR  # noqa: E402

NAVY, PANEL, CREAM, AMBER = (11, 15, 26), (20, 26, 43), (244, 241, 234), (245, 166, 35)  # remotion/src/theme.ts
PAPER, INK = (236, 227, 207), (24, 32, 52)
FONT_URL = "https://raw.githubusercontent.com/google/fonts/main/ofl/"
FONTS = {"bebas": "bebasneue/BebasNeue-Regular.ttf", "inter": "inter/Inter%5Bopsz%2Cwght%5D.ttf",
         "garamond": "ebgaramond/EBGaramond-Italic%5Bwght%5D.ttf"}
K = 2  # supersampling for line work

# Banner: the Mediterranean, words in the middle (on the wipe line).
BW, BH = 2560, 1440
VIEW = {"lon_w": -2.5, "lon_e": 39.5, "lat": 37.9}  # desktop band: Balearics, Sardinia, Sicily | Greece, Aegean, Anatolia
SAFE = (507, 508, 2053, 931)  # YouTube: text and logos inside 1546 x 423 in the middle
TOPICS = ("GEOPOLITICS  ·  BORDERS  ·  EMPIRES", "ECONOMY  ·  WATER  ·  TRADE ROUTES")
# Hand-lettered sea names on the ink side (lon, lat, size); only those left of the line are drawn.
# Rose and the big sea name sit left of the safe area: whole on desktop, cropped away (not cut) on phones.
SEA_LABELS = [("Mediterranean Sea", 2.0, 37.35, 30), ("Balearic Sea", 1.6, 40.2, 24), ("Tyrrhenian Sea", 12.0, 39.9, 26),
              ("Alboran Sea", -3.4, 35.9, 22), ("Strait of Sicily", 11.6, 36.6, 21), ("Ionian Sea", 17.6, 37.0, 24)]
ROSE = (4.5, 38.45, 46)  # compass rose: lon, lat, radius in px


# ---------------------------------------------------------------- helpers

def font(name: str, size: float, weight: int | None = None) -> ImageFont.FreeTypeFont:
    path = CACHE_DIR / "fonts" / f"{name}.ttf"
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        r = requests.get(FONT_URL + FONTS[name], timeout=120)
        r.raise_for_status()
        path.write_bytes(r.content)
    f = ImageFont.truetype(str(path), round(size))
    if weight is not None:
        vals = []
        for a in f.get_variation_axes():
            label = (a["name"].decode() if isinstance(a["name"], bytes) else str(a["name"])).lower()
            if label.startswith("weight"):
                vals.append(weight)
            elif label.startswith("optical"):
                vals.append(min(max(size, a["minimum"]), a["maximum"]))
            else:
                vals.append(a.get("default", a["minimum"]))
        f.set_variation_by_axes(vals)
    return f


def text_w(f, s: str, track: float = 0.0) -> float:
    return sum(f.getlength(c) for c in s) + track * max(0, len(s) - 1)


def put(draw, x: float, y: float, s: str, f, fill, track: float = 0.0, align: str = "left") -> float:
    """Letter-spaced text; y is the baseline."""
    w = text_w(f, s, track)
    x -= {"left": 0.0, "center": w / 2, "right": w}[align]
    for c in s:
        draw.text((x, y), c, font=f, fill=fill, anchor="ls")
        x += f.getlength(c) + track
    return w


def over(rgb, color, alpha):
    """Paint `color` (0-255 tuple or HxWx3 array in 0..1) over float RGB with an HxW alpha."""
    a = np.clip(alpha, 0, 1)[..., None]
    c = np.asarray(color, np.float32)
    c = c / 255.0 if c.ndim == 1 else c
    return rgb * (1 - a) + c * a


def mask_alpha(img: Image.Image) -> np.ndarray:
    return np.asarray(img, np.float32) / 255.0


def grown(mask: Image.Image, grow: int, blur: float) -> np.ndarray:
    m = mask.filter(ImageFilter.MaxFilter(grow)) if grow > 1 else mask
    return mask_alpha(m.filter(ImageFilter.GaussianBlur(blur)))


def paper(w: int, h: int, seed: int = 3) -> np.ndarray:
    """Warm paper: soft mottling, fine grain and slightly aged edges."""
    rng = np.random.default_rng(seed)
    t = np.ones((h, w), np.float32)
    for cell, amp in ((260, 0.03), (70, 0.012)):
        n = rng.normal(0, 1, (h // cell + 3, w // cell + 3)).astype(np.float32)
        t += amp * np.asarray(Image.fromarray(n).resize((w, h), Image.BICUBIC))
    t += 0.05 * ndimage.gaussian_filter(rng.normal(0, 1, (h, w)).astype(np.float32), 0.7)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    r = ((xx - w / 2) / (w / 2)) ** 2 + ((yy - h / 2) / (h / 2)) ** 2
    t *= 1 - 0.07 * np.clip(r - 0.3, 0, None)
    return np.asarray(PAPER, np.float32)[None, None] / 255.0 * t[..., None]


def dashed(draw, pts, on: float, off: float, width: int, fill=255) -> None:
    drawing, left = True, on
    for (xa, ya), (xb, yb) in zip(pts, pts[1:]):
        seg = math.hypot(xb - xa, yb - ya)
        t = 0.0
        while t < seg:
            step = min(left, seg - t)
            if drawing:
                f0, f1 = t / seg, (t + step) / seg
                draw.line([(xa + (xb - xa) * f0, ya + (yb - ya) * f0), (xa + (xb - xa) * f1, ya + (yb - ya) * f1)],
                          fill=fill, width=width)
            t += step
            left -= step
            if left <= 1e-9:
                drawing = not drawing
                left = on if drawing else off


def gibs_image(layer: str, box, w: int, h: int) -> Image.Image:
    """GIBS WMS image of a unit-Mercator box at exactly w x h (raw colours)."""
    name, when, fmt, _ = gibs.LAYERS[layer]
    x0, y0, x1, y1 = box
    e = gibs.EARTH
    bbox = f"{(x0 - 0.5) * e:.1f},{(0.5 - y1) * e:.1f},{(x1 - 0.5) * e:.1f},{(0.5 - y0) * e:.1f}"
    url = (f"{gibs.WMS_3857}?SERVICE=WMS&REQUEST=GetMap&VERSION=1.3.0&LAYERS={name}&STYLES=&CRS=EPSG:3857"
           f"&BBOX={bbox}&WIDTH={w}&HEIGHT={h}&FORMAT={fmt}" + (f"&TIME={when}" if when else ""))
    return gibs._get(url)


def polys(geom):
    for p in getattr(geom, "geoms", [geom]):
        if p.geom_type == "Polygon" and not p.is_empty:
            yield p
        elif p.geom_type in ("MultiPolygon", "GeometryCollection"):
            yield from polys(p)


def lines(geom):
    for g in getattr(geom, "geoms", [geom]):
        if g.geom_type == "LineString" and not g.is_empty:
            yield g
        elif g.geom_type in ("MultiLineString", "GeometryCollection"):
            yield from lines(g)


def fill_land(draw, proj, clip, scale: str = "10m", land_value: int = 255) -> None:
    """Natural Earth land with lakes cut out, drawn with `proj` (lon/lat -> px)."""
    for layer, value in ((f"ne_{scale}_land", land_value), (f"ne_{scale}_lakes", 255 - land_value)):
        for _, g in geo.ne_geoms(layer):
            if not g.intersects(clip):
                continue
            for p in polys(g.intersection(clip)):
                draw.polygon(proj(p.exterior.coords), fill=value)
                for ring in p.interiors:
                    draw.polygon(proj(ring.coords), fill=255 - value)


def ink_work(land: np.ndarray, k: int, waterlines, wobble_seed: int = 11) -> np.ndarray:
    """Ink alpha (at the supersampled size) for coastline + waterlining, from a boolean land mask."""
    h, w = land.shape
    d_sea = ndimage.distance_transform_edt(~land).astype(np.float32)
    d_land = ndimage.distance_transform_edt(land).astype(np.float32)
    rng = np.random.default_rng(wobble_seed)
    wob = np.asarray(Image.fromarray(rng.normal(0, 1, (h // 80 + 3, w // 80 + 3)).astype(np.float32))
                     .resize((w, h), Image.BICUBIC))
    a = np.where(land, np.clip(0.75 * k - d_land, 0, 1), np.clip((1.35 + 0.3 * wob) * k - d_sea, 0, 1))
    for i, d in enumerate(waterlines):  # old engraved-map waterlining: ripples parallel to the coast
        line = np.clip(0.6 * k - np.abs(d_sea - d * k), 0, 1) * (0.5 * 0.8 ** i)
        a = 1 - (1 - a) * (1 - np.where(land, 0, line))
    return a


def reduce(a: np.ndarray, k: int) -> np.ndarray:
    return np.asarray(Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8)).reduce(k), np.float32) / 255.0


# ---------------------------------------------------------------- banner

def banner_box():
    x0, x1 = float(geo.mx(VIEW["lon_w"])), float(geo.mx(VIEW["lon_e"]))
    s = BW / (x1 - x0)
    yc = float(geo.my(VIEW["lat"]))
    return (x0, yc - BH / 2 / s, x1, yc + BH / 2 / s), s


def compass_rose(size: tuple[int, int], cx: float, cy: float, r: float, k: int = 4) -> tuple[Image.Image, Image.Image]:
    """Classic eight-point rose: (ink mask, paper mask) at 1x; drawn at k x and reduced."""
    ink, fill = Image.new("L", (size[0] * k, size[1] * k), 0), Image.new("L", (size[0] * k, size[1] * k), 0)
    di, df = ImageDraw.Draw(ink), ImageDraw.Draw(fill)
    cx, cy, r = cx * k, cy * k, r * k
    for ring, w in ((1.0, 1.4), (0.84, 0.8), (0.28, 0.8)):
        di.ellipse((cx - r * ring, cy - r * ring, cx + r * ring, cy + r * ring), outline=255, width=round(w * k))
    for i in range(8):
        a = math.radians(i * 45 - 90)
        tip = r * (1.18 if i % 2 == 0 else 0.72)
        side = r * (0.16 if i % 2 == 0 else 0.11)
        p_tip = (cx + tip * math.cos(a), cy + tip * math.sin(a))
        p_l = (cx + side * math.cos(a - math.pi / 2), cy + side * math.sin(a - math.pi / 2))
        p_r = (cx + side * math.cos(a + math.pi / 2), cy + side * math.sin(a + math.pi / 2))
        df.polygon([(cx, cy), p_tip, p_l, p_r], fill=255)  # paper under the point hides the rings behind it
        di.polygon([(cx, cy), p_tip, p_l], fill=255)  # dark half
        di.line([(cx, cy), p_tip, p_r, (cx, cy)], fill=255, width=round(1.1 * k), joint="curve")  # light half: outline
    return ink.reduce(k), fill.reduce(k)


def banner(out_dir: Path) -> Path:
    box, s = banner_box()
    x0, y0 = box[0], box[1]

    def px(lon, lat, k=1):
        return (float(geo.mx(lon)) - x0) * s * k, (float(geo.my(lat)) - y0) * s * k

    def proj(k):
        def f(coords):
            c = np.asarray(coords, dtype=float)
            return list(zip(((geo.mx(c[:, 0]) - x0) * s * k).tolist(), ((geo.my(c[:, 1]) - y0) * s * k).tolist()))
        return f

    # Wordmark layout first: the ampersand decides where the wipe line runs.
    f_name, track, gap = font("bebas", 250), 5.0, 30.0
    w_l, w_amp, w_r = text_w(f_name, "INK", track), f_name.getlength("&"), text_w(f_name, "ORBIT", track)
    x_l = BW / 2 - (w_l + gap + w_amp + gap + w_r) / 2
    split = round(x_l + w_l + gap + w_amp / 2)
    base = 722  # wordmark baseline; Bebas caps are 0.7 em tall
    cap_top = base - 0.7 * 250

    # Ink side: paper map of the part left of the line.
    wi = split + 4
    lon_a, lat_n = geo.unmerc(x0, y0)
    lon_b, lat_s = geo.unmerc(x0 + wi / s, box[3])
    clip = lonlat_box(lon_a - 1, lat_s - 1, lon_b + 1, lat_n + 1)
    land_img = Image.new("L", (wi * K, BH * K), 0)
    fill_land(ImageDraw.Draw(land_img), proj(K), clip)
    land = np.asarray(land_img) > 127
    ink_a = ink_work(land, K, (7, 14, 22, 31, 41, 52))
    extra = Image.new("L", land_img.size, 0)
    d = ImageDraw.Draw(extra)
    for lon in range(-5, 45, 5):  # graticule
        d.line([(px(lon, 0, K)[0], 0), (px(lon, 0, K)[0], BH * K)], fill=60, width=K)
    for lat in range(20, 55, 5):
        d.line([(0, px(0, lat, K)[1]), (wi * K, px(0, lat, K)[1])], fill=60, width=K)
    for p, g in geo.ne_geoms("ne_10m_admin_0_boundary_lines_land"):
        if p.get("FEATURECLA") == "International boundary (verify)" and g.intersects(clip):
            for ln in lines(g.intersection(clip)):
                dashed(d, proj(K)(ln.coords), 9 * K, 6 * K, round(1.4 * K), 150)
    for p, g in geo.ne_geoms("ne_10m_rivers_lake_centerlines"):
        if (p.get("scalerank") or 99) <= 7 and g.intersects(clip):
            for ln in lines(g.intersection(clip)):
                d.line(proj(K)(ln.coords), fill=130, width=K, joint="curve")
    ink_a = 1 - (1 - ink_a) * (1 - mask_alpha(extra))
    ink_a, land1 = reduce(ink_a, K), reduce(land.astype(np.float32), K)

    rel = gibs._relief(gibs_image("relief", (x0, y0, x0 + wi / s, box[3]), wi, BH))
    shade = np.clip(1 + (np.asarray(rel.getchannel("R"), np.float32) - 128) / 128 * 0.22, 0.78, 1.12)
    pap = paper(wi, BH)
    land_tone = pap * np.array([0.955, 0.93, 0.875], np.float32) * shade[..., None]  # printed land tint + relief
    ink_rgb = over(pap * (1 - land1[..., None]) + land_tone * land1[..., None], INK, ink_a)

    # Old-map furniture on the paper (kept clear of the words): compass rose, hand-lettered sea names.
    keep_out = (x_l - 60, cap_top - 50, split, 900)

    def clear(x_a, y_a, x_b, y_b):
        return x_b < keep_out[0] or x_a > keep_out[2] or y_b < keep_out[1] or y_a > keep_out[3]

    rx_, ry_ = px(ROSE[0], ROSE[1])
    if clear(rx_ - ROSE[2] * 1.3, ry_ - ROSE[2] * 1.6, rx_ + ROSE[2] * 1.3, ry_ + ROSE[2] * 1.3) and rx_ + ROSE[2] * 1.3 < split:
        rose_ink, rose_fill = compass_rose((wi, BH), rx_, ry_, ROSE[2])
        yy_i, xx_i = np.mgrid[0:BH, 0:wi].astype(np.float32)
        disc = np.clip(ROSE[2] * 0.9 - np.hypot(xx_i - rx_, yy_i - ry_), 0, 1)
        ink_rgb = over(ink_rgb, pap, np.maximum(disc * 0.85, mask_alpha(rose_fill)))
        ink_rgb = over(ink_rgb, INK, mask_alpha(rose_ink) * 0.88)
        n_m = Image.new("L", (wi, BH), 0)
        put(ImageDraw.Draw(n_m), rx_, ry_ - ROSE[2] * 1.18 - 9, "N", font("garamond", 28, 600), 255, 0, "center")
        ink_rgb = over(ink_rgb, INK, mask_alpha(n_m) * 0.88)
    lab = Image.new("L", (wi, BH), 0)
    dlab = ImageDraw.Draw(lab)
    for text, lon, lat, size in SEA_LABELS:
        f = font("garamond", size, 500)
        x, y = px(lon, lat)
        w = text_w(f, text, size * 0.12)
        if clear(x - w / 2, y - size, x + w / 2, y + 6) and 10 < x - w / 2 and x + w / 2 < split - 30 and 30 < y < BH - 20:
            put(dlab, x, y, text, f, 255, size * 0.12, "center")
    ink_rgb = over(ink_rgb, pap, grown(lab, 9, 3.0) * 0.9)
    ink_rgb = over(ink_rgb, INK, mask_alpha(lab) * 0.8)

    # Orbit side: NASA Blue Marble, slightly darker toward the edges.
    sat = np.asarray(gibs_image("day", box, BW, BH), np.float32) / 255.0
    yy, xx = np.mgrid[0:BH, 0:BW].astype(np.float32)
    vig = 1 - 0.28 * np.clip(((xx - BW / 2) / (BW / 2)) ** 2 + ((yy - BH / 2) / (BH / 2)) ** 2 - 0.15, 0, None)
    rgb = sat * (0.92 * vig)[..., None]
    rgb[:, :split] = ink_rgb[:, :split]
    rgb[:, split - 1] = 0.5 * (ink_rgb[:, split - 1] + rgb[:, split - 1])

    # Words: ink on paper left of the line, cream over the satellite image right of it.
    f_tag, f_top = font("inter", 33, 650), font("inter", 23, 520)
    left_m, right_m = Image.new("L", (BW, BH), 0), Image.new("L", (BW, BH), 0)
    dl, dr = ImageDraw.Draw(left_m), ImageDraw.Draw(right_m)
    put(dl, x_l, base, "INK", f_name, 255, track)
    put(dr, x_l + w_l + gap + w_amp + gap, base, "ORBIT", f_name, 255, track)
    put(dl, split - 30, 800, "DRAWN IN INK", f_tag, 255, 5.5, "right")
    put(dr, split + 30, 800, "CHECKED FROM ORBIT", f_tag, 255, 5.5, "left")
    put(dl, split - 26, 862, TOPICS[0], f_top, 235, 4.5, "right")
    put(dr, split + 26, 862, TOPICS[1], f_top, 235, 4.5, "left")
    halo = grown(left_m, 17, 6.0) * 0.93
    side = (xx < split)
    rgb = over(rgb, np.concatenate([pap, np.zeros((BH, BW - wi, 3), np.float32)], axis=1), halo * side)
    rgb = over(rgb, NAVY, grown(right_m, 9, 11.0) * 0.62 * ~side)
    rgb = over(rgb, INK, mask_alpha(left_m) * side)
    rgb = over(rgb, CREAM, mask_alpha(right_m) * ~side)

    # The wipe line, broken where the amber ampersand sits on it.
    line = Image.new("L", (BW, BH), 0)
    dline = ImageDraw.Draw(line)
    amp_top, amp_bot = cap_top - 22, base + 22
    dline.line([(split, 0), (split, amp_top)], fill=255, width=5)
    dline.line([(split, amp_bot), (split, BH)], fill=255, width=5)
    amp = Image.new("L", (BW, BH), 0)
    put(ImageDraw.Draw(amp), split - w_amp / 2, base, "&", f_name, 255)
    glow = mask_alpha(line.filter(ImageFilter.GaussianBlur(7))) * 0.45 + mask_alpha(amp.filter(ImageFilter.GaussianBlur(9))) * 0.35
    rgb = 1 - (1 - rgb) * (1 - np.asarray(AMBER, np.float32)[None, None] / 255.0 * glow[..., None])  # screen
    rgb = over(rgb, NAVY, grown(amp, 5, 5.0) * 0.35)
    rgb = over(rgb, AMBER, np.maximum(mask_alpha(line), mask_alpha(amp)))

    out = out_dir / "banner_2560x1440.jpg"
    Image.fromarray((np.clip(rgb, 0, 1) * 255).astype(np.uint8)).save(out, "JPEG", quality=93, optimize=True)
    return out


# ---------------------------------------------------------------- profile picture

def ortho(n: int, r: float, lon0: float, lat0: float):
    yy, xx = np.mgrid[0:n, 0:n].astype(np.float32)
    u, v = (xx + 0.5 - n / 2) / r, (n / 2 - (yy + 0.5)) / r
    rho = np.sqrt(u * u + v * v)
    rc = np.clip(rho, 1e-9, 1.0)
    c = np.arcsin(rc)
    p0, l0 = math.radians(lat0), math.radians(lon0)
    lat = np.arcsin(np.clip(np.cos(c) * math.sin(p0) + v * np.sin(c) * math.cos(p0) / rc, -1, 1))
    lon = l0 + np.arctan2(u * np.sin(c), rc * np.cos(c) * math.cos(p0) - v * np.sin(c) * math.sin(p0))
    return np.degrees(lat), (np.degrees(lon) + 180) % 360 - 180, rho, xx, yy


def sample(img: np.ndarray, lon, lat) -> np.ndarray:
    h, w = img.shape[:2]
    coords = [(90 - lat) / 180 * h - 0.5, (lon + 180) / 360 * w - 0.5]
    if img.ndim == 2:
        return ndimage.map_coordinates(img, coords, order=1, mode="wrap")
    return np.stack([ndimage.map_coordinates(img[..., i], coords, order=1, mode="wrap") for i in range(img.shape[2])], -1)


def equirect_land(w: int = 8192) -> np.ndarray:
    """World land mask; the 1:110m scale keeps an icon-sized globe free of island speckle."""
    h = w // 2
    img = Image.new("L", (w, h), 0)

    def proj(coords):
        c = np.asarray(coords, dtype=float)
        return list(zip(((c[:, 0] + 180) / 360 * w).tolist(), ((90 - c[:, 1]) / 180 * h).tolist()))
    fill_land(ImageDraw.Draw(img), proj, lonlat_box(-180, -90, 180, 90), "110m")
    return np.asarray(img, np.float32) / 255.0


def profile(out_dir: Path) -> Path:
    n, k = 800, K
    N, R = n * k, 282 * k
    lat, lon, rho, xx, yy = ortho(N, R, 15.0, 33.0)
    disc = rho <= 1.0
    left = xx < N / 2
    cx = cy = N / 2

    # background: deep navy, a little lighter behind the globe
    r_px = np.hypot(xx - cx, yy - cy)
    rgb = over(np.zeros((N, N, 3), np.float32) + np.asarray(NAVY, np.float32) / 255, PANEL, np.clip(1 - r_px / (N * 0.55), 0, 1) * 0.9)

    # orbit ring (amber) around the globe; the back half goes behind it
    rx, ry, rot = 374 * k, 108 * k, math.radians(-20)  # stays inside YouTube's circle crop (radius 400)
    ring_w = 11 * k
    ring = Image.new("L", (N, N), 0)
    ImageDraw.Draw(ring).ellipse((cx - rx - ring_w / 2, cy - ry - ring_w / 2, cx + rx + ring_w / 2, cy + ry + ring_w / 2),
                                 outline=255, width=ring_w)
    ring = mask_alpha(ring.rotate(-math.degrees(rot), resample=Image.BICUBIC, center=(cx, cy)))
    near = (-(xx - cx) * math.sin(rot) + (yy - cy) * math.cos(rot)) > 0  # lower half of the ring passes in front
    back, front = ring * ~near, ring * near
    rgb = over(rgb, AMBER, back * 0.9)

    # atmosphere on the orbit side
    glow = np.exp(-np.clip(r_px - R, 0, None) / (11 * k)) * (~disc) * (~left) * 0.55
    rgb = 1 - (1 - rgb) * (1 - np.array([0.36, 0.62, 1.0], np.float32)[None, None] * glow[..., None])

    # globe, orbit half: NASA Blue Marble with limb shading
    tex = gibs.globe_texture("day", CACHE_DIR / "brand" / "globe_day.jpg", 4096)
    tex = np.asarray(Image.open(CACHE_DIR / "brand" / tex).convert("RGB"), np.float32) / 255.0
    sat = sample(tex, lon, lat) * (0.62 + 0.38 * np.sqrt(np.clip(1 - rho ** 2, 0, 1)))[..., None]
    sat = over(sat, (120, 175, 255), 0.35 * np.clip(rho, 0, 1) ** 8)

    # globe, ink half: paper, coast, waterlines, graticule
    land = (sample(equirect_land(), lon, lat) > 0.5) & disc
    a = ink_work(land, k, (5, 10, 16))
    glon, glat = np.abs(((lon + 7.5) % 15) - 7.5), np.abs(((lat + 7.5) % 15) - 7.5)
    dlon = np.clip(np.hypot(*np.gradient(lon)), 1e-6, 5)
    dlat = np.clip(np.hypot(*np.gradient(lat)), 1e-6, 5)
    grat = np.maximum(np.clip(0.55 * k - glon / dlon, 0, 1), np.clip(0.55 * k - glat / dlat, 0, 1)) * 0.28
    a = 1 - (1 - a) * (1 - grat * disc)
    pap = paper(N, N, seed=5)
    ink_rgb = pap * np.where(land, 1, 0)[..., None] * np.array([0.95, 0.925, 0.87], np.float32) + pap * np.where(land, 0, 1)[..., None]
    ink_rgb = over(ink_rgb, INK, a)

    edge = np.clip((1 - rho) * R + 0.5, 0, 1)  # anti-aliased disc
    rgb = over(rgb, np.where(left[..., None], ink_rgb, sat), edge)
    limb = np.clip(1.6 * k - np.abs(r_px - R), 0, 1) * left
    rgb = over(rgb, INK, limb)

    # the wipe line across the globe
    line = Image.new("L", (N, N), 0)
    ImageDraw.Draw(line).line([(cx, cy - R - 20 * k), (cx, cy + R + 20 * k)], fill=255, width=10 * k)
    rgb = 1 - (1 - rgb) * (1 - np.asarray(AMBER, np.float32)[None, None] / 255 * (mask_alpha(line.filter(ImageFilter.GaussianBlur(8 * k))) * 0.5)[..., None])
    rgb = over(rgb, AMBER, mask_alpha(line))

    # front half of the ring, with a thin navy edge so it reads over paper
    front_img = Image.fromarray((front * 255).astype(np.uint8))
    rgb = over(rgb, NAVY, grown(front_img, 3 * k + 1, 1.0 * k) * 0.55)
    rgb = over(rgb, AMBER, front)

    # the satellite: a cream point on the ring, outside the globe
    ts = 0.1 * math.pi
    sx = cx + rx * math.cos(ts) * math.cos(rot) - ry * math.sin(ts) * math.sin(rot)
    sy = cy + rx * math.cos(ts) * math.sin(rot) + ry * math.sin(ts) * math.cos(rot)
    dot_d = np.hypot(xx - sx, yy - sy)
    rgb = 1 - (1 - rgb) * (1 - np.asarray(AMBER, np.float32)[None, None] / 255 * (np.exp(-dot_d / (16 * k)) * 0.8)[..., None])
    rgb = over(rgb, NAVY, np.clip(24 * k - dot_d, 0, 1))
    rgb = over(rgb, CREAM, np.clip(19 * k - dot_d, 0, 1))

    img = Image.fromarray((np.clip(rgb, 0, 1) * 255).astype(np.uint8)).resize((n, n), Image.LANCZOS)
    out = out_dir / "profile_800.png"
    img.save(out, optimize=True)
    return out


# ---------------------------------------------------------------- previews

def previews(out_dir: Path, banner_path: Path, profile_path: Path) -> Path:
    b = Image.open(banner_path).convert("RGB")
    p = Image.open(profile_path).convert("RGB")
    W = 1800
    canvas = Image.new("RGB", (W, 1640), (15, 15, 15))
    d = ImageDraw.Draw(canvas)
    f = font("inter", 26, 600)
    y = 30

    def label(text, x, y):
        d.text((x, y), text, font=f, fill=(170, 170, 170))

    label("Desktop (visible band of the banner)", 40, y)
    desk = b.crop((0, SAFE[1], BW, SAFE[3])).resize((W - 80, round((W - 80) * 423 / BW)), Image.LANCZOS)
    canvas.paste(desk, (40, y + 40))
    y += 40 + desk.height + 40
    label("Phone (safe area only)", 40, y)
    phone = b.crop(SAFE).resize((1000, round(1000 * 423 / 1546)), Image.LANCZOS)
    canvas.paste(phone, (40, y + 40))
    label("TV (whole image)", 1090, y)
    tv = b.resize((670, 377), Image.LANCZOS)
    canvas.paste(tv, (1090, y + 40))
    y += 40 + max(phone.height, tv.height) + 50

    label("Profile picture as YouTube shows it (circle), dark and light mode", 40, y)
    y += 50
    x = 40
    for bg in ((15, 15, 15), (255, 255, 255)):
        panel = Image.new("RGB", (820, 300), bg)
        px_ = 20
        for size in (240, 98, 48, 32):
            av = p.resize((size, size), Image.LANCZOS)
            m = Image.new("L", (size * 4, size * 4), 0)
            ImageDraw.Draw(m).ellipse((0, 0, size * 4 - 1, size * 4 - 1), fill=255)
            panel.paste(av, (px_, 150 - size // 2), m.resize((size, size), Image.LANCZOS))
            px_ += size + 40
        canvas.paste(panel, (x, y))
        x += 860
    out = out_dir / "preview.png"
    canvas.save(out)
    return out


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("out_dir", type=Path)
    ap.add_argument("--lat", type=float, help="banner centre latitude")
    ap.add_argument("--lon-w", type=float)
    ap.add_argument("--lon-e", type=float)
    ap.add_argument("--banner-only", action="store_true", help="banner + its desktop band only (for trying views)")
    args = ap.parse_args()
    for k_, v_ in (("lat", args.lat), ("lon_w", args.lon_w), ("lon_e", args.lon_e)):
        if v_ is not None:
            VIEW[k_] = v_
    args.out_dir.mkdir(parents=True, exist_ok=True)
    (CACHE_DIR / "brand").mkdir(parents=True, exist_ok=True)
    b = banner(args.out_dir)
    print("banner:", b, f"{b.stat().st_size / 1e6:.2f} MB")
    if args.banner_only:
        Image.open(b).crop((0, SAFE[1], BW, SAFE[3])).resize((1600, 264), Image.LANCZOS).save(args.out_dir / "desktop.png")
        sys.exit(0)
    p = profile(args.out_dir)
    print("profile:", p, f"{p.stat().st_size / 1e6:.2f} MB")
    print("preview:", previews(args.out_dir, b, p))
