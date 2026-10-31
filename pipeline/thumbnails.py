"""Thumbnail variants: Workers AI background + Remotion still with big headline text."""
import json
import shutil
import subprocess
from pathlib import Path

import cf_images
from config import PUBLIC_MEDIA, ROOT, THUMB_STYLE

# (id, text layout, background direction added to the prompt)
VARIANTS = [
    ("A", "left", "close-up of the main subject, shallow depth of field"),
    ("B", "center", "wide establishing shot, moody atmosphere"),
    ("C", "right", "macro detail of a symbolic object, strong contrast"),
]
MAX_BYTES = 2_000_000  # YouTube's thumbnail limit is 2 MB for the normal UI; stay below it


def make(script, out_dir: Path) -> list[Path]:
    if script.thumbnail is None:
        raise RuntimeError("script.json has no 'thumbnail' block (text + prompt)")
    out_dir.mkdir(parents=True, exist_ok=True)
    PUBLIC_MEDIA.mkdir(parents=True, exist_ok=True)
    results = []
    for vid, layout, direction in VARIANTS:
        bg_name = f"thumb_{vid}.jpg"
        shutil.copyfile(cf_images.generate(f"{script.thumbnail.prompt}, {direction}", style=THUMB_STYLE), PUBLIC_MEDIA / bg_name)
        props = out_dir / f"props_{vid}.json"
        props.write_text(json.dumps({"text": script.thumbnail.text, "background": bg_name, "layout": layout}), encoding="utf-8")
        dest = out_dir / f"thumbnail_{vid}.jpg"
        for quality in (90, 80, 70):  # lower quality until it fits the size limit
            r = subprocess.run(
                ["npx", "remotion", "still", "src/index.ts", "Thumbnail", str(dest), f"--props={props}",
                 "--image-format=jpeg", f"--jpeg-quality={quality}", "--log=warn"],
                cwd=ROOT / "remotion", capture_output=True, text=True,
            )
            if r.returncode != 0:
                raise RuntimeError(f"remotion still failed for variant {vid}:\n{(r.stdout + r.stderr)[-1500:]}")
            if dest.stat().st_size <= MAX_BYTES:
                break
        print(f"  thumbnail {vid}: {dest.stat().st_size / 1000:.0f} KB")
        props.unlink()
        results.append(dest)
    return results
