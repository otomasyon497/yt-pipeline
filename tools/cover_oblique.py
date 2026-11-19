"""Oblique satellite covers: our own Sentinel-2 image of the subject, tilted like an aerial shot, in vivid colour.

    %USERPROFILE%\\.yt-pipeline\\venv\\Scripts\\python.exe tools/cover_oblique.py <slug>      # episodes/<slug>/cover_oblique.json
    ... --out some.jpg                                                                      # default Videos\\yt-pipeline\\<slug>\\cover_oblique.jpg

Why (thumbnail study 2026-11-19, 48 outliers in our niche, docs/thumbnail-study-2026-11-19.md): the covers that beat
their channel 50-300x show ONE subject from a low oblique aerial angle, in saturated turquoise water and bright land,
with 0-3 huge words (white / yellow, black outline) and sometimes one red arrow. Most of them are AI renders; we get
the same grammar from real imagery, so the cover stays honest: the place on it is the real place.

cover_oblique.json:
    {"bbox": [lon0, lat0, lon1, lat1], "date": "2025-04-01/2025-05-31",   # Sentinel-2 window (clear day)
     "rotate": -20,                    # degrees, so the subject runs across the frame
     "crop": [0.1, 0.1, 0.9, 0.9],     # after rotating, the part to keep (fractions)
     "tilt": 0.42,                     # 0 = straight down; ~0.4 = a low aerial angle
     "water": "turquoise",             # recolour dark water ("turquoise" | "blue" | null)
     "text": [{"t": "SINKING", "color": "yellow"}], "text_at": [0.05, 0.06], "text_size": 170,
     "arrow": {"from": [0.62, 0.30], "to": [0.62, 0.62]}}   # red arrow in picture fractions (optional)
"""
import argparse
import json
import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "pipeline"))
import geo  # noqa: E402
import sentinel  # noqa: E402

W, H, SS = 1280, 720, 2
FONT = str(Path(__file__).parent / "assets" / "BebasNeue-Regular.ttf")
COLORS = {"yellow": (255, 214, 10), "white": (255, 255, 255), "red": (230, 32, 28)}
VIDEOS = Path.home() / "Videos" / "yt-pipeline"


def fetch(cfg: dict, cache: Path) -> Image.Image:
    lon0, lat0, lon1, lat1 = cfg["bbox"]
    box = (geo.mx(lon0), geo.my(lat1), geo.mx(lon1), geo.my(lat0))
    out = cache / "cover_oblique_s2.webp"
    if not out.exists():
        r = sentinel.mosaic(box, 3200, out, cfg.get("date"))
        if r is None:
            raise SystemExit("no Sentinel-2 image for that box / window")
    return Image.open(out).convert("RGB")


def grade(img: Image.Image, water: str | None) -> Image.Image:
    a = np.asarray(img, dtype=np.float32) / 255.0
    lum = a.mean(axis=2)
    if water:
        # water = dark, low-saturation pixels; keep its texture (waves, wakes) as brightness variation
        mask = np.clip((0.30 - lum) / 0.12, 0, 1)
        mask = np.asarray(Image.fromarray((mask * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(3)), np.float32) / 255
        deep, shallow = ((0.02, 0.36, 0.62), (0.05, 0.72, 0.80)) if water == "turquoise" else ((0.02, 0.22, 0.55), (0.10, 0.50, 0.85))
        t = np.clip((lum - lum[mask > 0.5].min(initial=0)) / 0.18, 0, 1)[..., None] if mask.max() > 0 else lum[..., None]
        col = np.array(deep) * (1 - t) + np.array(shallow) * t
        col = col * (0.85 + 0.6 * (lum[..., None] - lum.mean()))
        a = a * (1 - mask[..., None]) + col * mask[..., None]
    out = Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8))
    out = ImageEnhance.Contrast(out).enhance(1.18)
    out = ImageEnhance.Color(out).enhance(1.35)
    return ImageEnhance.Brightness(out).enhance(1.12)


def perspective(img: Image.Image, tilt: float) -> Image.Image:
    """Lay the image on a plane seen from a low angle: the far edge shrinks and climbs to a horizon at the top."""
    w, h = W * SS, H * SS
    horizon = int(h * (0.05 + 0.10 * (1 - tilt)))
    # The plane is wider than the frame at both edges, so its borders never show: the near edge spreads far out
    # (that is the perspective), the far edge still overhangs the frame a little.
    spread = 0.15 + 0.7 * tilt
    dst = [(-w * spread, h), (w * (1 + spread), h), (w * 1.06, horizon), (-w * 0.06, horizon)]
    src = [(0, img.height), (img.width, img.height), (img.width, 0), (0, 0)]
    coeffs = _coeffs(dst, src)
    plane = img.transform((w, h), Image.PERSPECTIVE, coeffs, Image.BICUBIC)
    sa = np.zeros((h, w, 3), np.float32)
    y = np.linspace(0, 1, h)[:, None]
    top, low = np.array([0.42, 0.66, 0.92]), np.array([0.90, 0.94, 0.98])
    for c in range(3):
        sa[..., c] = (top[c] + (low[c] - top[c]) * np.clip(y / max(horizon / h, 1e-3), 0, 1))
    sky = Image.fromarray((sa * 255).astype(np.uint8))
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).polygon(dst, fill=255)
    out = Image.composite(plane, sky, mask)
    # haze: distance fades into the sky colour near the horizon
    hz = np.clip(1 - (np.arange(h) - horizon) / (h * 0.55), 0, 1) ** 1.6
    haze = np.asarray(out, np.float32) * (1 - 0.55 * hz[:, None, None]) + np.array([228, 236, 245]) * 0.55 * hz[:, None, None]
    return Image.fromarray(np.clip(haze, 0, 255).astype(np.uint8))


def _coeffs(dst, src):
    """PIL perspective coefficients mapping output (dst) points back to input (src) points."""
    m = []
    for (x, y), (u, v) in zip(dst, src):
        m.append([x, y, 1, 0, 0, 0, -u * x, -u * y])
        m.append([0, 0, 0, x, y, 1, -v * x, -v * y])
    b = np.array([c for p in src for c in p], dtype=np.float64)
    return np.linalg.solve(np.array(m, dtype=np.float64), b).tolist()


def text_block(img: Image.Image, lines: list[dict], at, size: int) -> None:
    d = ImageDraw.Draw(img)
    f = ImageFont.truetype(FONT, size * SS)
    x, y = at[0] * W * SS, at[1] * H * SS
    for ln in lines:
        d.text((x, y), ln["t"], font=f, fill=COLORS.get(ln.get("color", "white")), stroke_width=int(size * SS * 0.07),
               stroke_fill=(10, 10, 12))
        y += size * SS * 0.92


def arrow(img: Image.Image, a: dict) -> None:
    d = ImageDraw.Draw(img)
    (x0, y0), (x1, y1) = [(p[0] * W * SS, p[1] * H * SS) for p in (a["from"], a["to"])]
    ang = math.atan2(y1 - y0, x1 - x0)
    wid, head = 34 * SS, 90 * SS
    bx, by = x1 - head * math.cos(ang), y1 - head * math.sin(ang)
    nx, ny = -math.sin(ang), math.cos(ang)
    shaft = [(x0 + nx * wid / 2, y0 + ny * wid / 2), (bx + nx * wid / 2, by + ny * wid / 2),
             (bx - nx * wid / 2, by - ny * wid / 2), (x0 - nx * wid / 2, y0 - ny * wid / 2)]
    tip = [(x1, y1), (bx + nx * head * 0.8, by + ny * head * 0.8), (bx - nx * head * 0.8, by - ny * head * 0.8)]
    for poly in (shaft, tip):
        d.polygon(poly, fill=(10, 10, 12))
    grow = 8 * SS
    d.polygon([(x0 + nx * (wid / 2 - grow), y0 + ny * (wid / 2 - grow)), (bx + nx * (wid / 2 - grow), by + ny * (wid / 2 - grow)),
               (bx - nx * (wid / 2 - grow), by - ny * (wid / 2 - grow)), (x0 - nx * (wid / 2 - grow), y0 - ny * (wid / 2 - grow))],
              fill=COLORS["red"])
    c = ((tip[0][0] + tip[1][0] + tip[2][0]) / 3, (tip[0][1] + tip[1][1] + tip[2][1]) / 3)
    d.polygon([(px + (c[0] - px) * 0.18, py + (c[1] - py) * 0.18) for px, py in tip], fill=COLORS["red"])


def build(cfg: dict, cache: Path) -> Image.Image:
    img = fetch(cfg, cache)
    img = grade(img, cfg.get("water", "turquoise"))
    if cfg.get("rotate"):
        img = img.rotate(cfg["rotate"], Image.BICUBIC, expand=False)
    if cfg.get("crop"):
        c = cfg["crop"]
        img = img.crop((int(c[0] * img.width), int(c[1] * img.height), int(c[2] * img.width), int(c[3] * img.height)))
    out = perspective(img, cfg.get("tilt", 0.42))
    vign = Image.new("L", out.size, 0)
    ImageDraw.Draw(vign).ellipse((-out.width * 0.25, -out.height * 0.35, out.width * 1.25, out.height * 1.35), fill=255)
    vign = vign.filter(ImageFilter.GaussianBlur(120 * SS))
    out = Image.composite(out, ImageEnhance.Brightness(out).enhance(0.55), vign)
    if cfg.get("arrow"):
        arrow(out, cfg["arrow"])
    if cfg.get("text"):
        text_block(out, cfg["text"], cfg.get("text_at", (0.05, 0.06)), cfg.get("text_size", 170))
    return out.resize((W, H), Image.LANCZOS)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("slug")
    ap.add_argument("--config", help="default episodes/<slug>/cover_oblique.json")
    ap.add_argument("--out")
    a = ap.parse_args()
    cfg = json.loads(Path(a.config or ROOT / "episodes" / a.slug / "cover_oblique.json").read_text(encoding="utf-8"))
    out = Path(a.out) if a.out else VIDEOS / a.slug / "cover_oblique.jpg"
    out.parent.mkdir(parents=True, exist_ok=True)
    build(cfg, out.parent).save(out, quality=92)
    print(f"cover: {out}")


if __name__ == "__main__":
    main()
