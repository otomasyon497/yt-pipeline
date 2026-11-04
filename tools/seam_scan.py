"""Find straight vertical seams (tiles of two dates or two satellite passes) in frames of a rendered video.

A seam is a colour step at the same column, with the same sign, in three horizontal bands of the frame (above the
captions). Rivers, shores, border lines, wipes and crossfades fire too, so look at every hit; real seams found so far
stepped 13-16 levels in blue (colorado-river: P5.7 at -111.0 degrees, the cold open's July 2019 image).

    python tools/seam_scan.py VIDEO.mp4 --at 5,272.5,640     # pulls the frames with Remotion's ffmpeg
    python tools/seam_scan.py frame1.jpg frame2.jpg           # frames already on disk

Needs numpy and Pillow (the pipeline's requirements).
"""
import argparse
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image

FFMPEG = Path(__file__).resolve().parents[1] / "remotion/node_modules/@remotion/compositor-win32-x64-msvc/ffmpeg.exe"
HALF = 8  # px averaged on each side of a candidate column
MIN_STEP = 4.0  # smallest step (0-255) reported


def column_steps(band: np.ndarray) -> np.ndarray:
    """Right-minus-left mean colour around every column, (columns, 3)."""
    col = band.mean(0)
    cs = np.vstack([np.zeros((1, 3)), np.cumsum(col, 0)])
    xs = np.arange(HALF, col.shape[0] - HALF)
    return (cs[xs + HALF] - cs[xs]) / HALF - (cs[xs] - cs[xs - HALF]) / HALF


def scan(img: Image.Image, top: int = 3) -> list[str]:
    a = np.asarray(img.convert("RGB"), dtype=np.float32)
    h = min(a.shape[0], 880) // 3
    s = np.stack([column_steps(a[i * h:(i + 1) * h]) for i in range(3)])  # (bands, columns, channels)
    ch = np.abs(s).mean(0).argmax(1)
    per = s[:, np.arange(s.shape[1]), ch]
    same = (np.sign(per) == np.sign(per[0])).all(0)
    score = np.where(same, np.abs(per).min(0), 0.0)
    hits: list[str] = []
    taken: list[int] = []
    for i in np.argsort(-score):
        if score[i] < MIN_STEP or len(hits) == top:
            break
        x = int(i + HALF)
        if all(abs(x - t) >= 20 for t in taken):
            taken.append(x)
            hits.append(f"x={x} step {score[i]:.1f} ({'RGB'[ch[i]]})")
    return hits


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("inputs", nargs="+", help="a video (with --at) or image files")
    ap.add_argument("--at", default="", help="seconds, comma-separated (video input)")
    args = ap.parse_args()
    frames: list[tuple[str, Image.Image]] = []
    if args.at:
        video = args.inputs[0]
        with tempfile.TemporaryDirectory() as tmp:
            for t in [float(v) for v in args.at.split(",") if v.strip()]:
                out = Path(tmp) / f"{t}.png"
                subprocess.run([str(FFMPEG), "-hide_banner", "-loglevel", "error", "-y", "-ss", str(t), "-i", video,
                                "-frames:v", "1", str(out)], check=True)
                frames.append((f"{t:.1f}s", Image.open(out).copy()))
    else:
        frames = [(p, Image.open(p)) for p in args.inputs]
    for name, img in frames:
        hits = scan(img)
        print(f"{name}: " + ("; ".join(hits) if hits else f"no straight vertical step of {MIN_STEP:.0f} or more"))


if __name__ == "__main__":
    sys.exit(main())
