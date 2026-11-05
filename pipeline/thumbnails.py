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

from PIL import Image

import cf_images
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


def _split_background(el: dict, out: Path) -> tuple[str, str]:
    """Left half of the 'before' image, right half of the 'after' one, both cropped to the view the camera showed
    (the compare images cover 1.5 x the view). Returns the two year labels."""
    halves = []
    for side in ("before", "after"):
        img = Image.open(PUBLIC_MEDIA / el[side]["src"]).convert("RGB")
        w, h = img.size
        cw, ch = w / 1.5, h / 1.5
        img = img.crop((round((w - cw) / 2), round((h - ch) / 2), round((w + cw) / 2), round((h + ch) / 2)))
        halves.append(img.resize((1280, 720), Image.LANCZOS))
    split = halves[0].copy()
    split.paste(halves[1].crop((640, 0, 1280, 720)), (640, 0))
    split.save(out, quality=92)
    years = []
    for key in ("labelBefore", "labelAfter"):
        m = re.search(r"\b(1[89]\d\d|20\d\d)\b", el.get(key) or "")
        years.append(m.group(1) if m else (el.get(key) or ""))
    return years[0], years[1]


def _render(props: dict, dest: Path, out_dir: Path, vid: str) -> None:
    path = out_dir / f"props_{vid}.json"
    path.write_text(json.dumps(props), encoding="utf-8")
    for quality in (90, 80, 70):  # lower quality until it fits the size limit
        r = subprocess.run(
            ["npx", "remotion", "still", "src/index.ts", "Thumbnail", str(dest), f"--props={path}",
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
