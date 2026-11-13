"""Map covers: a bright flat map, the subject in red, one white arrow, one or two words in a box. 1280 x 720.

    %USERPROFILE%\\.yt-pipeline\\venv\\Scripts\\python.exe tools/cover_map.py <slug>            # episodes/<slug>/cover.json
    ...python.exe tools/cover_map.py <slug> --out some.jpg                                    # default: Videos\\yt-pipeline\\<slug>\\cover.jpg

Why this look (research 2026-11-13, .claude/skills/cover-map): the long videos of small channels that broke out in
our niche all use it, because a viewer sees where and what in half a second at feed size. Our photo covers did not
say where. Land is the channel's amber, the sea its navy, so the template stays ours.

cover.json:
    {"view": {"lon": -90.4, "lat": 29.6, "span": 6.0},          # span = degrees of longitude across the picture
     "subject": [{"admin1": "Louisiana"}, {"country": "Egypt"}, {"lake": "Aral Sea"}, {"box": [lon0, lat0, lon1, lat1]}, {"file": "x.geojson"},
                 {"circle": [lon, lat, km]}, {"polygon": [[lon, lat], ...]}, {"line": [[lon, lat], ...], "km": 12}],
     "clip": "land" | "sea" | null,                             # keep only the subject's land (a coast strip) or sea part
     "text": [{"t": "RUNNING", "style": "white"}, {"t": "DRY", "style": "red"}],
     "text_at": [0.05, 0.56], "text_size": 150,                 # top-left corner in picture fractions; cap height in px at 720p
     "arrow": {"to": [lon, lat], "from": [0.36, 0.7], "bend": 0.28},   # from = picture fraction; omit "arrow" for none
     "labels": [{"t": "NEW ORLEANS", "lon": -90.07, "lat": 29.95}],
     "outline": [{"country": "Ethiopia"}]}                      # optional: white outline only (a second actor)
"""
import argparse
import json
import math
import sys
import tempfile
from pathlib import Path

import numpy as np
import shapely
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from shapely.geometry import LineString, Point, Polygon, box as shp_box

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "pipeline"))
import geo  # noqa: E402
import gibs  # noqa: E402

W, H, SS = 1280, 720, 2
FONT = str(Path(__file__).parent / "assets" / "BebasNeue-Regular.ttf")
LAND, LAND_EDGE = (245, 176, 40), (120, 74, 8)
SEA_IN, SEA_OUT = (26, 104, 196), (9, 44, 110)
RED, RED_EDGE = (226, 30, 26), (92, 6, 6)
INK = (10, 12, 18)
VIDEOS = Path.home() / "Videos" / "yt-pipeline"


class Frame:
    """The picture's Web-Mercator window and its pixel grid (supersampled)."""

    def __init__(self, view: dict):
        self.w, self.h = W * SS, H * SS
        cx, cy = float(geo.mx(view["lon"])), float(geo.my(view["lat"]))
        half_w = view["span"] / 360.0 / 2
        half_h = half_w * H / W
        self.box = (cx - half_w, cy - half_h, cx + half_w, cy + half_h)
        lon0, lat1 = geo.unmerc(self.box[0], self.box[1])
        lon1, lat0 = geo.unmerc(self.box[2], self.box[3])
        self.lonlat = shp_box(lon0 - 0.5, lat0 - 0.5, lon1 + 0.5, lat1 + 0.5)
        self.km_per_px = view["span"] * 111.32 * math.cos(math.radians(view["lat"])) / self.w

    def xy(self, lon, lat):
        x = (np.asarray(geo.mx(lon)) - self.box[0]) / (self.box[2] - self.box[0]) * self.w
        y = (np.asarray(geo.my(lat)) - self.box[1]) / (self.box[3] - self.box[1]) * self.h
        return x, y

    def ring(self, coords):
        a = np.asarray(coords, dtype=float)
        x, y = self.xy(a[:, 0], a[:, 1])
        return list(zip(x.tolist(), y.tolist()))

    def mask(self, geom) -> Image.Image:
        m = Image.new("L", (self.w, self.h), 0)
        d = ImageDraw.Draw(m)
        geom = geom.intersection(self.lonlat) if geom is not None else None
        if geom is None or geom.is_empty:
            return m
        for poly in _polys(geom):
            if len(poly.exterior.coords) >= 3:
                d.polygon(self.ring(poly.exterior.coords), fill=255)
        for poly in _polys(geom):  # holes after all shells, so a lake inside another polygon's shell stays open
            for hole in poly.interiors:
                d.polygon(self.ring(hole.coords), fill=0)
        return m

    def lines(self, draw: ImageDraw.ImageDraw, geom, fill, width: int) -> None:
        geom = geom.intersection(self.lonlat)
        for part in getattr(geom, "geoms", [geom]):
            if part.geom_type == "LineString" and len(part.coords) >= 2:
                draw.line(self.ring(part.coords), fill=fill, width=width, joint="curve")


def _polys(geom):
    if geom.geom_type == "Polygon":
        return [geom]
    return [g for g in getattr(geom, "geoms", []) if g.geom_type == "Polygon"]


def _union(name: str):
    return shapely.union_all([g for _, g in geo.ne_geoms(name)])


def _lake(name: str):
    want = geo.key(name)
    for layer in ("ne_10m_lakes", "ne_10m_lakes_historic", "ne_10m_geography_marine_polys"):
        for p, g in geo.ne_geoms(layer):
            if want in {geo.key(str(p.get(f) or "")) for f in ("name", "name_en", "name_alt")}:
                return g
    raise SystemExit(f"cover_map: no lake or sea named {name!r} in Natural Earth")


GEO_DIR = ROOT / "episodes"  # set to the episode's geo/ folder in main()


def shape_of(item: dict, frame: Frame):
    if "country" in item:
        code = geo.country_code(item["country"])
        if not code:
            raise SystemExit(f"cover_map: unknown country {item['country']!r}")
        return geo.country_geom(code, "10m")
    if "admin1" in item:
        hit = geo.admin1(item["admin1"])
        if not hit:
            raise SystemExit(f"cover_map: unknown state/province {item['admin1']!r}")
        return hit[1]
    if "lake" in item:
        return _lake(item["lake"])
    if "box" in item:
        return shp_box(*item["box"])
    if "polygon" in item:
        return Polygon(item["polygon"])
    if "file" in item:  # a GeoJSON of the episode: {"file": "inland.geojson"} -> episodes/<slug>/geo/inland.geojson
        data = json.loads((GEO_DIR / item["file"]).read_text(encoding="utf-8"))
        feats = data["features"] if data.get("type") == "FeatureCollection" else [data]
        return shapely.union_all([shapely.make_valid(shapely.geometry.shape(f["geometry"])) for f in feats])
    deg = lambda km, lat: km / (111.32 * math.cos(math.radians(lat)))  # noqa: E731  (km -> degrees of longitude)
    if "circle" in item:
        lon, lat, km = item["circle"]
        return shapely.affinity.scale(Point(lon, lat).buffer(deg(km, lat), 48), 1, math.cos(math.radians(lat)))
    if "line" in item:
        lat = item["line"][0][1]
        return LineString(item["line"]).buffer(deg(item.get("km", 10), lat) / 2, cap_style="round")
    raise SystemExit(f"cover_map: unknown subject {item}")


def _relief(frame: Frame) -> np.ndarray | None:
    """Hillshade as a multiplier (about 0.62-1.22), 1.0 where there is none (sea, flat ground, no network)."""
    try:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "relief.webp"
            if not gibs.backdrop("relief", frame.box, frame.w, out, feather=False):
                return None
            img = Image.open(out).convert("RGBA").resize((frame.w, frame.h), Image.LANCZOS)
    except Exception as e:  # the cover still works flat
        print(f"  cover_map: no relief ({type(e).__name__})")
        return None
    v = np.asarray(img.getchannel("R"), dtype=np.float32) / 255.0
    a = np.asarray(img.getchannel("A"), dtype=np.float32) / 255.0
    return 1.0 + (v - 0.5) * 1.2 * a


def _paint(base: np.ndarray, mask: Image.Image, colour, shade: np.ndarray | None) -> None:
    m = np.asarray(mask, dtype=np.float32)[..., None] / 255.0
    col = np.asarray(colour, dtype=np.float32)[None, None, :] * (shade[..., None] if shade is not None else 1.0)
    base[:] = base * (1 - m) + np.clip(col, 0, 255) * m


def _edge(mask: Image.Image, px: int) -> Image.Image:
    """A line of about `px` along the inside of a mask's border."""
    inner = mask.filter(ImageFilter.MinFilter(px * 2 + 1))
    return Image.fromarray(np.clip(np.asarray(mask, np.int16) - np.asarray(inner, np.int16), 0, 255).astype(np.uint8))


def _arrow(img: Image.Image, start, end, bend: float) -> None:
    """A curved white arrow with a dark rim: the one thing that moves the eye from the words to the place."""
    (x0, y0), (x1, y1) = start, end
    dx, dy = x1 - x0, y1 - y0
    length = math.hypot(dx, dy)
    cx, cy = (x0 + x1) / 2 - dy * bend, (y0 + y1) / 2 + dx * bend
    head = max(46 * SS, min(70 * SS, length * 0.3))
    pts = [((1 - t) ** 2 * x0 + 2 * (1 - t) * t * cx + t ** 2 * x1, (1 - t) ** 2 * y0 + 2 * (1 - t) * t * cy + t ** 2 * y1)
           for t in np.linspace(0, 1, 60)]
    ang = math.atan2(y1 - pts[-4][1], x1 - pts[-4][0])
    tip = (x1, y1)
    back = (x1 - math.cos(ang) * head, y1 - math.sin(ang) * head)
    wing = head * 0.52
    tri = [tip, (back[0] - math.sin(ang) * wing, back[1] + math.cos(ang) * wing),
           (back[0] + math.sin(ang) * wing, back[1] - math.cos(ang) * wing)]
    shaft = [p for p in pts if math.hypot(p[0] - x1, p[1] - y1) > head * 0.8] + [back]
    d = ImageDraw.Draw(img)
    for colour, grow in ((INK, 9 * SS), ((255, 255, 255), 0)):
        d.line(shaft, fill=colour, width=22 * SS + 2 * grow, joint="curve")
        r = (22 * SS + 2 * grow) / 2
        d.ellipse((shaft[0][0] - r, shaft[0][1] - r, shaft[0][0] + r, shaft[0][1] + r), fill=colour)
        if grow:
            c = (sum(p[0] for p in tri) / 3, sum(p[1] for p in tri) / 3)
            k = 1 + grow * 2.4 / head
            d.polygon([(c[0] + (p[0] - c[0]) * k, c[1] + (p[1] - c[1]) * k) for p in tri], fill=colour)
        else:
            d.polygon(tri, fill=colour)


def _text(img: Image.Image, lines: list[dict], at, size: int) -> None:
    """Stacked word boxes: white on ink, or white on red for the word that carries the twist."""
    d = ImageDraw.Draw(img)
    f = ImageFont.truetype(FONT, round(size * SS * 1.38))  # Bebas cap height is about 0.72 of the font size
    x, y = at[0] * img.width, at[1] * img.height
    pad_x, pad_y = size * SS * 0.2, size * SS * 0.1
    for ln in lines:
        l, t, r, b = d.textbbox((0, 0), ln["t"], font=f)
        w, h = r - l, b - t
        style = ln.get("style", "white")
        fill, ink = {"red": (RED, (255, 255, 255)), "white": (INK, (255, 255, 255)), "amber": (INK, (255, 190, 50))}[style]
        rect = (x, y, x + w + 2 * pad_x, y + h + 2 * pad_y)
        d.rectangle((rect[0] + 7 * SS, rect[1] + 7 * SS, rect[2] + 7 * SS, rect[3] + 7 * SS), fill=(0, 0, 0))
        d.rectangle(rect, fill=fill, outline=(255, 255, 255), width=3 * SS)
        d.text((x + pad_x - l, y + pad_y - t), ln["t"], font=f, fill=ink)
        y += h + 2 * pad_y + 8 * SS


def _label(img: Image.Image, text: str, xy) -> None:
    d = ImageDraw.Draw(img)
    f = ImageFont.truetype(FONT, 46 * SS)
    x, y = xy
    r = 9 * SS
    d.ellipse((x - r - 3 * SS, y - r - 3 * SS, x + r + 3 * SS, y + r + 3 * SS), fill=INK)
    d.ellipse((x - r, y - r, x + r, y + r), fill=(255, 255, 255))
    l, t, rr, b = d.textbbox((0, 0), text, font=f)
    bx = x + r + 10 * SS
    if bx + (rr - l) + 20 * SS > img.width:
        bx = x - r - 10 * SS - (rr - l) - 16 * SS
    by = y - (b - t) / 2 - 7 * SS
    d.rectangle((bx, by, bx + (rr - l) + 16 * SS, by + (b - t) + 14 * SS), fill=(255, 255, 255), outline=INK, width=2 * SS)
    d.text((bx + 8 * SS - l, by + 7 * SS - t), text, font=f, fill=INK)


def make(spec: dict, out: Path) -> Path:
    frame = Frame(spec["view"])
    yy, xx = np.mgrid[0:frame.h, 0:frame.w].astype(np.float32)
    far = np.clip(np.hypot((xx / frame.w - 0.5) * 1.15, yy / frame.h - 0.5) / 0.62, 0, 1)[..., None]
    base = np.asarray(SEA_IN, np.float32) * (1 - far) + np.asarray(SEA_OUT, np.float32) * far
    shade = _relief(frame)

    land = _union("ne_10m_land").intersection(frame.lonlat)
    lakes = shapely.union_all([g for p, g in geo.ne_geoms("ne_10m_lakes")
                               if g.intersects(frame.lonlat) and g.area > (frame.km_per_px * 14 / 111.32) ** 2])
    land = land.difference(lakes) if not lakes.is_empty else land
    land_mask = frame.mask(land)
    _paint(base, land_mask, LAND, shade)

    subject = shapely.union_all([shape_of(s, frame) for s in spec["subject"]])
    if spec.get("clip") == "land":
        subject = subject.intersection(land)
    elif spec.get("clip") == "sea":
        subject = subject.difference(land)
    sub_mask = frame.mask(subject)
    if not np.asarray(sub_mask).any():
        raise SystemExit("cover_map: the subject is outside the view (or empty after clip)")
    _paint(base, sub_mask, RED, None if shade is None else 1.0 + (shade - 1.0) * 0.55)

    img = Image.fromarray(base.astype(np.uint8))
    d = ImageDraw.Draw(img, "RGBA")
    span = spec["view"]["span"]
    for p, g in geo.ne_geoms("ne_10m_admin_0_countries"):  # borders: enough to place the subject, never a second focus
        if g.intersects(frame.lonlat):
            frame.lines(d, g.boundary, (70, 40, 0, 150), 3 * SS)
    if span <= 16:
        for p, g in geo.ne_geoms("ne_10m_admin_1_states_provinces"):
            if g.intersects(frame.lonlat) and p.get("iso_a2") in ("US", "CA", "AU", "IN", "BR", "CN", "RU"):
                frame.lines(d, g.boundary, (70, 40, 0, 80), 2 * SS)
    img.paste(Image.new("RGB", img.size, LAND_EDGE), mask=_edge(land_mask, 2 * SS))
    img.paste(Image.new("RGB", img.size, RED_EDGE), mask=_edge(sub_mask, 3 * SS))
    glow = sub_mask.filter(ImageFilter.MaxFilter(6 * SS + 1))
    rim = Image.fromarray(np.clip(np.asarray(glow, np.int16) - np.asarray(sub_mask, np.int16), 0, 255).astype(np.uint8))
    img.paste(Image.new("RGB", img.size, (255, 255, 255)), mask=rim)
    for item in spec.get("outline", []):
        om = frame.mask(shape_of(item, frame))
        img.paste(Image.new("RGB", img.size, (255, 255, 255)), mask=_edge(om, 4 * SS))

    for lb in spec.get("labels", []):
        x, y = frame.xy(lb["lon"], lb["lat"])
        _label(img, lb["t"], (float(x), float(y)))
    if spec.get("arrow"):
        a = spec["arrow"]
        if "to" in a:
            tx, ty = frame.xy(*a["to"])
        else:
            c = subject.representative_point()
            tx, ty = frame.xy(c.x, c.y)
        fx, fy = a.get("from", [0.34, 0.74])
        _arrow(img, (fx * frame.w, fy * frame.h), (float(tx), float(ty)), a.get("bend", 0.28))
    if spec.get("text"):
        _text(img, spec["text"], spec.get("text_at", [0.04, 0.08]), spec.get("text_size", 130))

    img = img.resize((W, H), Image.LANCZOS)
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out, "JPEG", quality=92, optimize=True)
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("slug")
    ap.add_argument("--out")
    a = ap.parse_args()
    global GEO_DIR
    GEO_DIR = ROOT / "episodes" / a.slug / "geo"
    spec = json.loads((ROOT / "episodes" / a.slug / "cover.json").read_text(encoding="utf-8"))
    out = Path(a.out) if a.out else VIDEOS / a.slug / "cover.jpg"
    print(f"cover: {make(spec, out)}")


if __name__ == "__main__":
    main()
