"""Photo covers with huge outlined words, the "95% OF URUGUAY IS EMPTY" grammar (thumbnail study 2026-11-19).

    %USERPROFILE%\\.yt-pipeline\\venv\\Scripts\\python.exe tools/cover_photo.py <slug> [--out x.jpg]   # episodes/<slug>/cover_photo.json

A bright, licence-checked photo of the place (Commons PD / CC0 / CC BY, through pipeline/commons.py) fills the frame,
lifted in colour; 2-4 short lines of heavy type sit on the clear side, white with one accent colour, a thick black
outline and a soft shadow, and an optional red underline under the last line. The words must be something the video
shows (see the cover-map skill: honest covers).

cover_photo.json:
    {"photo": "File:....jpg", "focus": [0.62, 0.55],          # point of the photo kept in frame when cropping to 16:9
     "zoom": 1.0,
     "lines": [{"t": "26% OF IT", "color": "white"}, {"t": "IS BELOW", "color": "yellow"}, {"t": "THE SEA", "color": "white"}],
     "text_at": [0.04, 0.05], "text_size": 150, "underline": true, "align": "left"}
"""
import argparse
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "pipeline"))
import commons  # noqa: E402

W, H, SS = 1280, 720, 2
FONTS = [Path(__file__).parent / "assets" / "Anton-Regular.ttf", Path("C:/Windows/Fonts/impact.ttf"),
         Path(__file__).parent / "assets" / "BebasNeue-Regular.ttf"]
COLORS = {"white": (255, 255, 255), "yellow": (255, 214, 10), "red": (232, 36, 30)}
VIDEOS = Path.home() / "Videos" / "yt-pipeline"


def font(size: int) -> ImageFont.FreeTypeFont:
    for f in FONTS:
        if f.exists():
            return ImageFont.truetype(str(f), size)
    raise SystemExit("no heavy font found (Anton / Impact / Bebas)")


def frame(img: Image.Image, focus, zoom: float) -> Image.Image:
    w, h = W * SS, H * SS
    s = max(w / img.width, h / img.height) * zoom
    img = img.resize((round(img.width * s), round(img.height * s)), Image.LANCZOS)
    x = min(max(int(focus[0] * img.width - w / 2), 0), img.width - w)
    y = min(max(int(focus[1] * img.height - h / 2), 0), img.height - h)
    return img.crop((x, y, x + w, y + h))


def build(cfg: dict) -> Image.Image:
    path, _ = commons.fetch(cfg["photo"])
    img = frame(Image.open(path).convert("RGB"), cfg.get("focus", (0.5, 0.5)), cfg.get("zoom", 1.0))
    img = ImageEnhance.Color(img).enhance(1.3)
    img = ImageEnhance.Contrast(img).enhance(1.12)
    img = ImageEnhance.Brightness(img).enhance(1.05)
    size = cfg.get("text_size", 150) * SS
    f = font(size)
    x0, y0 = cfg.get("text_at", (0.04, 0.05))
    x, y = x0 * W * SS, y0 * H * SS
    stroke = int(size * 0.075)
    layout = []
    for ln in cfg["lines"]:
        bb = f.getbbox(ln["t"], stroke_width=stroke)
        layout.append((ln, x, y, bb))
        y += (bb[3] - bb[1]) * 1.02
    # soft shadow behind the words so they read on any sky
    shadow = Image.new("L", img.size, 0)
    sd = ImageDraw.Draw(shadow)
    for ln, lx, ly, bb in layout:
        sd.text((lx + 10 * SS, ly + 12 * SS), ln["t"], font=f, fill=200, stroke_width=stroke, stroke_fill=200)
    shadow = shadow.filter(ImageFilter.GaussianBlur(14 * SS))
    img = Image.composite(Image.new("RGB", img.size, (0, 0, 0)), img, shadow.point(lambda v: int(v * 0.75)))
    d = ImageDraw.Draw(img)
    for ln, lx, ly, bb in layout:
        d.text((lx, ly), ln["t"], font=f, fill=COLORS.get(ln.get("color", "white"), (255, 255, 255)),
               stroke_width=stroke, stroke_fill=(8, 8, 10))
    if cfg.get("underline"):
        ln, lx, ly, bb = layout[-1]
        y_line = ly + bb[3] + 6 * SS
        x_end = lx + bb[2] * 0.95
        th = 26 * SS
        d.polygon([(lx + 6 * SS, y_line), (x_end, y_line - th * 0.6), (x_end + 10 * SS, y_line + th * 0.2),
                   (lx + 10 * SS, y_line + th)], fill=COLORS["red"], outline=(8, 8, 10))
    return img.resize((W, H), Image.LANCZOS)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("slug")
    ap.add_argument("--config")
    ap.add_argument("--out")
    a = ap.parse_args()
    cfg = json.loads(Path(a.config or ROOT / "episodes" / a.slug / "cover_photo.json").read_text(encoding="utf-8"))
    out = Path(a.out) if a.out else VIDEOS / a.slug / "cover_photo.jpg"
    out.parent.mkdir(parents=True, exist_ok=True)
    build(cfg).save(out, quality=92)
    print(f"cover: {out}")


if __name__ == "__main__":
    main()
