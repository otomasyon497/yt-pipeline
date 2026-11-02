"""'Where are we' mini map: a small locator image (land, the country around the point, a dot) for stock and photo shots."""
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from shapely.geometry import Point, box

import geo
from config import CACHE_DIR

W, H = 660, 440  # drawn at 2x, shown at 330 x 220
SPAN = 34.0  # degrees of longitude across the inset: enough for continental context
BG = (11, 15, 26, 235)
LAND = (52, 64, 92, 255)
BORDER = (90, 104, 138, 255)
ACCENT = (245, 166, 35)
RIVER = (127, 178, 229, 255)
RIVERS = ("Nile", "Blue Nile", "White Nile")  # curated lines from lines.json drawn on every inset


def make(lon: float, lat: float, out: Path) -> None:
    key = hashlib.sha1(f"{lon:.4f},{lat:.4f},{SPAN},v2".encode()).hexdigest()[:16]
    cache = CACHE_DIR / "locator" / f"{key}.png"
    if not cache.exists():
        cache.parent.mkdir(parents=True, exist_ok=True)
        _draw(lon, lat).save(cache)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(cache.read_bytes())


def _draw(lon: float, lat: float) -> Image.Image:
    cx, cy = float(geo.mx(lon)), float(geo.my(lat))
    w = SPAN / 360.0
    h = w * H / W
    x0, y0 = cx - w / 2, cy - h / 2
    k = W / w

    def px(lons, lats):
        return list(zip(((np.asarray(geo.mx(lons)) - x0) * k).tolist(), ((np.asarray(geo.my(lats)) - y0) * k).tolist()))

    # lon/lat window around the inset (a little wider so polygons run off the edges cleanly)
    lon0, lat1 = geo.unmerc(x0, y0)
    lon1, lat0 = geo.unmerc(x0 + w, y0 + h)
    window = box(lon0 - 2, lat0 - 2, lon1 + 2, lat1 + 2)

    img = Image.new("RGBA", (W, H), BG)
    d = ImageDraw.Draw(img)
    home = None
    countries = geo.country_geoms("50m")
    pt = Point(lon, lat)
    for code, g in countries.items():
        if not g.intersects(window):
            continue
        g = g.intersection(window)
        polys = [p for p in getattr(g, "geoms", [g]) if p.geom_type == "Polygon"]
        inside = g.buffer(0.05).contains(pt)
        for p in polys:
            ring = px(*p.exterior.xy)
            if len(ring) > 2:
                d.polygon(ring, fill=(*ACCENT, 105) if inside else LAND, outline=BORDER, width=2)
        if inside:
            home = polys
    if home:  # crisp accent outline on top of the neighbours' borders
        for p in home:
            d.line(px(*p.exterior.xy) + px(*p.exterior.xy)[:1], fill=(*ACCENT, 255), width=4)

    lines = json.loads((Path(__file__).with_name("lines.json")).read_text(encoding="utf-8"))
    for name in RIVERS:
        if name in lines:
            lons, lats = zip(*lines[name])
            d.line(px(lons, lats), fill=RIVER, width=4, joint="curve")

    # The dot: soft glow, white ring, accent core.
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse([W / 2 - 34, H / 2 - 34, W / 2 + 34, H / 2 + 34], fill=(*ACCENT, 140))
    img.alpha_composite(glow.filter(ImageFilter.GaussianBlur(12)))
    d = ImageDraw.Draw(img)
    d.ellipse([W / 2 - 15, H / 2 - 15, W / 2 + 15, H / 2 + 15], fill=(255, 255, 255, 255))
    d.ellipse([W / 2 - 10, H / 2 - 10, W / 2 + 10, H / 2 + 10], fill=(*ACCENT, 255))

    # Rounded corners.
    mask = Image.new("L", (W, H), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, W - 1, H - 1], radius=26, fill=255)
    img.putalpha(Image.fromarray(np.minimum(np.asarray(img.getchannel("A")), np.asarray(mask))))
    return img


def card_background(block: dict, cam_index: int = 0) -> dict | None:
    """Placement of a map block's sharpest image around its first view, for a blurred chapter-card backdrop."""
    if not block.get("cams") or not block.get("rasters"):
        return None
    c = block["cams"][min(cam_index, len(block["cams"]) - 1)]
    hits = [r for r in block["rasters"] if r["layer"] in ("day", "s2") and r["x0"] <= c["x"] <= r["x1"] and r["y0"] <= c["y"] <= r["y1"]]
    if not hits:
        return None
    r = min(hits, key=lambda r: (r["x1"] - r["x0"]) * (r["y1"] - r["y0"]))  # the sharpest one
    k = 1920 / c["w"]
    left = (r["x0"] - c["x"]) * k + 960
    top = (r["y0"] - c["y"]) * k + 540
    return {"src": r["src"], "left": round(left, 1), "top": round(top, 1),
            "width": round((r["x1"] - r["x0"]) * k, 1), "height": round((r["y1"] - r["y0"]) * k, 1)}


if __name__ == "__main__":  # quick look: python pipeline/locator.py 35.09 11.21 out.png
    import sys
    make(float(sys.argv[1]), float(sys.argv[2]), Path(sys.argv[3]))
    print("written", sys.argv[3])
