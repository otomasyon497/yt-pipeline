"""Thumbnail variants: Workers AI backgrounds (A-C) and, when the episode has a before/after compare, D: our own
imagery split down the middle (before | after) with the years, the amber wipe line and the headline.

D follows the niche's thumbnail language (the map or satellite view itself as the picture, 1-3 words; see
docs/channel-analysis-2026-11.md) and needs no AI image. It runs after prepare, which wrote the compare images.
"""
import json
import re
import shutil
import subprocess
from pathlib import Path

from PIL import Image, ImageFilter, ImageOps

import cf_images
import geo
from config import BUILD_DIR, PUBLIC_MEDIA, ROOT, THUMB_STYLE

# (id, text layout, background direction added to the prompt)
VARIANTS = [
    ("A", "left", "close-up of the main subject, shallow depth of field"),
    ("B", "center", "wide establishing shot, moody atmosphere"),
    ("C", "right", "macro detail of a symbolic object, strong contrast"),
]
MAX_BYTES = 2_000_000  # YouTube's thumbnail limit is 2 MB for the normal UI; stay below it


def _first_compare(slug: str) -> dict | None:
    """The first before/after compare element of the episode (from the prepared map blocks), or None."""
    tl_path = BUILD_DIR / slug / "timeline.json"
    if not tl_path.exists():
        return None
    for shot in json.loads(tl_path.read_text(encoding="utf-8"))["shots"]:
        if shot["visual"] != "map" or not shot.get("media"):
            continue
        block = json.loads((PUBLIC_MEDIA / shot["media"]).read_text(encoding="utf-8"))
        for el in block["elements"]:
            if el.get("kind") == "compare":
                return el
    return None


def _split_background(el: dict, out: Path, size=(1280, 720)) -> tuple[str, str]:
    """Left half of the 'before' image, right half of the 'after' one, both cropped to the view the camera showed
    (the compare images cover 1.5 x the view). A portrait size (Shorts cover) splits top | bottom instead.
    Returns the two year labels."""
    W, H = size
    halves = []
    for side in ("before", "after"):
        img = Image.open(PUBLIC_MEDIA / el[side]["src"]).convert("RGB")
        w, h = img.size
        cw, ch = w / 1.5, h / 1.5
        if cw / ch > W / H:  # crop the view to the target aspect
            cw = ch * W / H
        else:
            ch = cw * H / W
        img = img.crop((round((w - cw) / 2), round((h - ch) / 2), round((w + cw) / 2), round((h + ch) / 2)))
        halves.append(img.resize((W, H), Image.LANCZOS))
    split = halves[0].copy()
    if W >= H:
        split.paste(halves[1].crop((W // 2, 0, W, H)), (W // 2, 0))
    else:
        split.paste(halves[1].crop((0, H // 2, W, H)), (0, H // 2))
    split.save(out, quality=92)
    return _year_labels(el)


def _year_labels(el: dict) -> tuple[str, str]:
    years = []
    for key in ("labelBefore", "labelAfter"):
        m = re.search(r"\b(1[89]\d\d|20\d\d)\b", el.get(key) or "")
        years.append(m.group(1) if m else (el.get(key) or ""))
    return years[0], years[1]


def _stacked_background(el: dict, focus: tuple[float, float, float], out: Path, size=(1080, 1920)) -> tuple[str, str]:
    """Portrait cover whose two panels show the SAME spot: before on top, after below. `focus` = lon, lat, span.
    The crop stays inside the images' opaque part (their outer 7 % is feathered)."""
    W, H = size
    panel_h = H // 2
    fx, fy = float(geo.mx(focus[0])), float(geo.my(focus[1]))
    panels = []
    for side in ("before", "after"):
        r = el[side]
        img = Image.open(PUBLIC_MEDIA / r["src"]).convert("RGB")
        px = img.width / (r["x1"] - r["x0"])  # image pixels per Mercator unit
        cw = min(focus[2] / 360.0 * px, img.width * 0.86)
        ch = cw * panel_h / W
        mx, my = img.width * 0.07, img.height * 0.07
        x0 = min(max((fx - r["x0"]) * px - cw / 2, mx), img.width - mx - cw)
        y0 = min(max((fy - r["y0"]) * img.height / (r["y1"] - r["y0"]) - ch / 2, my), img.height - my - ch)
        panel = img.crop((round(x0), round(y0), round(x0 + cw), round(y0 + ch))).resize((W, panel_h), Image.LANCZOS)
        # Small on a phone: lift the shadows and sharpen, the picture stays the real one.
        panel = ImageOps.autocontrast(panel, cutoff=0.5, preserve_tone=True).point(lambda v: round(255 * (v / 255) ** 0.8))
        panels.append(panel.filter(ImageFilter.UnsharpMask(radius=3, percent=70, threshold=2)))
    stack = Image.new("RGB", (W, H))
    stack.paste(panels[0], (0, 0))
    stack.paste(panels[1], (0, panel_h))
    stack.save(out, quality=92)
    return _year_labels(el)


def _render(props: dict, dest: Path, out_dir: Path, vid: str, comp: str = "Thumbnail") -> None:
    path = out_dir / f"props_{vid}.json"
    path.write_text(json.dumps(props), encoding="utf-8")
    for quality in (90, 80, 70):  # lower quality until it fits the size limit
        r = subprocess.run(
            ["npx", "remotion", "still", "src/index.ts", comp, str(dest), f"--props={path}",
             "--image-format=jpeg", f"--jpeg-quality={quality}", "--log=warn"],
            cwd=ROOT / "remotion", capture_output=True, text=True,
        )
        if r.returncode != 0:
            raise RuntimeError(f"remotion still failed for variant {vid}:\n{(r.stdout + r.stderr)[-1500:]}")
        if dest.stat().st_size <= MAX_BYTES:
            break
    path.unlink()
    print(f"  thumbnail {vid}: {dest.stat().st_size / 1000:.0f} KB")


def make(script, out_dir: Path, slug: str | None = None) -> list[Path]:
    if script.thumbnail is None:
        raise RuntimeError("script.json has no 'thumbnail' block (text + prompt)")
    out_dir.mkdir(parents=True, exist_ok=True)
    PUBLIC_MEDIA.mkdir(parents=True, exist_ok=True)
    results = []
    # No prompt: our own imagery only (the user's no-AI decision, 2026-11-06); A-C need an AI background.
    for vid, layout, direction in (VARIANTS if script.thumbnail.prompt else []):
        bg_name = f"thumb_{vid}.jpg"
        shutil.copyfile(cf_images.generate(f"{script.thumbnail.prompt}, {direction}", style=THUMB_STYLE), PUBLIC_MEDIA / bg_name)
        dest = out_dir / f"thumbnail_{vid}.jpg"
        _render({"text": script.thumbnail.text, "background": bg_name, "layout": layout}, dest, out_dir, vid)
        results.append(dest)
    el = _first_compare(slug) if slug else None
    if el is not None:
        before, after = _split_background(el, PUBLIC_MEDIA / "thumb_D.jpg")
        dest = out_dir / "thumbnail_D.jpg"
        _render({"text": script.thumbnail.text, "background": "thumb_D.jpg", "layout": "split", "labels": [before, after]},
                dest, out_dir, "D")
        results.append(dest)
    return results


def make_short_cover(script, out_dir: Path, slug: str) -> list[Path]:
    """Shorts cover, 1080 x 1920: the first compare split top (before) | bottom (after) with the headline.
    YouTube shows it where the app lets the creator pick a cover image; otherwise it is a frame to match."""
    if script.thumbnail is None:
        return []
    el = _first_compare(slug)
    if el is None:
        print("short: no compare in the episode, no cover")
        return []
    out_dir.mkdir(parents=True, exist_ok=True)
    if script.thumbnail.focus:
        before, after = _stacked_background(el, script.thumbnail.focus, PUBLIC_MEDIA / "thumb_V.jpg")
    else:
        before, after = _split_background(el, PUBLIC_MEDIA / "thumb_V.jpg", size=(1080, 1920))
    dest = out_dir / "cover_short.jpg"
    _render({"text": script.thumbnail.text, "background": "thumb_V.jpg", "layout": "vsplit", "labels": [before, after]},
            dest, out_dir, "V", comp="ThumbnailVertical")
    return [dest]
