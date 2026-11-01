"""NASA GIBS imagery (WMS) for map backdrops: satellite, night lights and shaded relief.

Layers (all NASA data, free to reuse with acknowledgement):
  day    - Blue Marble shaded relief + bathymetry (500 m)
  night  - VIIRS Black Marble 2016 (500 m)
  relief - ASTER GDEM greyscale shaded relief (NASA/METI, ~30 m; no redistribution limits since v3)
Requests are cached by URL in CACHE_DIR/gibs, so re-renders do not hit NASA again.
"""
import hashlib
import io
import time
from pathlib import Path

import numpy as np
import requests
from PIL import Image, ImageFilter

from config import CACHE_DIR

WMS_3857 = "https://gibs.earthdata.nasa.gov/wms/epsg3857/best/wms.cgi"
WMS_4326 = "https://gibs.earthdata.nasa.gov/wms/epsg4326/best/wms.cgi"
EARTH = 40075016.68557849  # Web Mercator world width in metres
# name -> (GIBS layer, TIME or None, image format, finest useful pixels per world width)
LAYERS = {
    "day": ("BlueMarble_ShadedRelief_Bathymetry", None, "image/jpeg", 2 ** 8 * 256),
    "night": ("VIIRS_Black_Marble", "2016-01-01", "image/jpeg", 2 ** 8 * 256),
    "relief": ("ASTER_GDEM_Greyscale_Shaded_Relief", None, "image/png", 2 ** 12 * 256),
}
CREDIT = ("Map imagery: NASA Blue Marble, NASA VIIRS Black Marble and ASTER GDEM (NASA/METI), via NASA's Global "
          "Imagery Browse Services (GIBS), part of NASA's Earth Science Data and Information System (ESDIS).")
MAX_PX = 4096


def _get(url: str) -> Image.Image:
    cache = CACHE_DIR / "gibs" / (hashlib.sha1(url.encode()).hexdigest() + ".img")
    if not cache.exists():
        cache.parent.mkdir(parents=True, exist_ok=True)
        for attempt in range(4):
            try:
                r = requests.get(url, timeout=180)
                r.raise_for_status()
                if not r.headers.get("content-type", "").startswith("image/"):
                    raise RuntimeError(f"GIBS returned {r.headers.get('content-type')}: {r.text[:300]}")
                break
            except (requests.RequestException, RuntimeError):
                if attempt == 3:
                    raise
                time.sleep(4 * (attempt + 1))
        cache.write_bytes(r.content)
    return Image.open(io.BytesIO(cache.read_bytes())).convert("RGB")


def _relief(img: Image.Image) -> Image.Image:
    """Greyscale hillshade: stretch contrast around flat ground, make water (flat constant grey) transparent."""
    g = np.asarray(img.convert("L"), dtype=np.float32)
    flat = np.asarray(Image.fromarray(g.astype(np.uint8)).filter(ImageFilter.BoxBlur(2)), dtype=np.float32)
    water = (np.abs(g - flat) < 0.75) & (g < 100)  # ASTER water is one flat dark grey
    land_vals = g[~water]
    mid = float(np.median(land_vals)) if land_vals.size else 128.0
    v = np.clip(128 + (g - mid) * 2.2, 0, 255)
    v = np.asarray(Image.fromarray(v.astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.7)), dtype=np.uint8)
    alpha = np.where(water, 0, 255).astype(np.uint8)
    return Image.merge("RGBA", [Image.fromarray(v)] * 3 + [Image.fromarray(alpha)])


def _feather(img: Image.Image, frac: float = 0.07) -> Image.Image:
    """Soft edges so a detail image blends into the coarser one under it."""
    img = img.convert("RGBA")
    w, h = img.size
    fx = np.clip(np.minimum(np.arange(w), np.arange(w)[::-1]) / max(1, w * frac), 0, 1)
    fy = np.clip(np.minimum(np.arange(h), np.arange(h)[::-1]) / max(1, h * frac), 0, 1)
    ramp = np.outer(fy, fx)
    a = np.asarray(img.getchannel("A"), dtype=np.float32) * (ramp * ramp * (3 - 2 * ramp))
    img.putalpha(Image.fromarray(a.astype(np.uint8)))
    return img


def backdrop(layer: str, box: tuple[float, float, float, float], px_width: int, out: Path, feather: bool = True) -> dict | None:
    """Fetch `layer` for a unit-Mercator box (x0, y0, x1, y1), save as WebP, return its placement."""
    name, when, fmt, finest = LAYERS[layer]
    x0, y0, x1, y1 = max(0.0, box[0]), max(0.0, box[1]), min(1.0, box[2]), min(1.0, box[3])
    if x1 - x0 <= 1e-6 or y1 - y0 <= 1e-6:
        return None
    width = int(min(px_width, MAX_PX, max(256, (x1 - x0) * finest)))
    height = max(64, round(width * (y1 - y0) / (x1 - x0)))
    if height > MAX_PX:
        width, height = round(width * MAX_PX / height), MAX_PX
    bbox = f"{(x0 - 0.5) * EARTH:.1f},{(0.5 - y1) * EARTH:.1f},{(x1 - 0.5) * EARTH:.1f},{(0.5 - y0) * EARTH:.1f}"
    url = (f"{WMS_3857}?SERVICE=WMS&REQUEST=GetMap&VERSION=1.3.0&LAYERS={name}&STYLES=&CRS=EPSG:3857"
           f"&BBOX={bbox}&WIDTH={width}&HEIGHT={height}&FORMAT={fmt}" + (f"&TIME={when}" if when else ""))
    img = _get(url)
    img = _relief(img) if layer == "relief" else img.convert("RGBA")
    if feather:
        img = _feather(img)
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out, "WEBP", quality=84, method=4)
    return {"src": out.name, "x0": x0, "y0": y0, "x1": x1, "y1": y1, "layer": layer, "px": width}


def globe_texture(layer: str, out: Path, width: int = 4096) -> str:
    """Equirectangular world image (for the spinning globe)."""
    name, when, fmt, _ = LAYERS[layer]
    url = (f"{WMS_4326}?SERVICE=WMS&REQUEST=GetMap&VERSION=1.3.0&LAYERS={name}&STYLES=&CRS=EPSG:4326"
           f"&BBOX=-90,-180,90,180&WIDTH={width}&HEIGHT={width // 2}&FORMAT={fmt}" + (f"&TIME={when}" if when else ""))
    img = _get(url)
    if layer == "relief":
        img = _relief(img)
    out.parent.mkdir(parents=True, exist_ok=True)
    img.convert("RGB").save(out, "JPEG", quality=88)
    return out.name
