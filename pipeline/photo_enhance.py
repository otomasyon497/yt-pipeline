"""Photo upscaling and depth maps for archive photos (opt-in per episode, added 2026-11-19).

upscale(): small archive photos (long side under commons.MIN_LONG_SIDE) are enlarged 4x with Real-ESRGAN x4plus
    (xinntao/Real-ESRGAN, BSD-3-Clause weights), run on CPU through spandrel (MIT), in tiles. script.photo_upscale.
depth(): a depth map from Depth Anything V2 Small (Apache-2.0; the Base / Large / Giant models are CC-BY-NC and must
    not be used). PhotoScene turns it into a slow 2.5D camera move. script.photo_motion = "parallax".

Both cache their results in CACHE_DIR by the source file's hash, so re-renders cost nothing.
"""
import hashlib
from functools import lru_cache
from pathlib import Path

import numpy as np
import requests
from PIL import Image

from config import CACHE_DIR

ESRGAN_URL = "https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth"
DEPTH_MODEL = "depth-anything/Depth-Anything-V2-Small-hf"  # Apache-2.0: only the Small model
TILE, PAD = 256, 16


def _key(path: Path) -> str:
    return hashlib.sha1(path.read_bytes()).hexdigest()[:20]


@lru_cache(maxsize=1)
def _esrgan():
    import torch
    from spandrel import ModelLoader
    weights = CACHE_DIR / "models" / "RealESRGAN_x4plus.pth"
    if not weights.exists():
        weights.parent.mkdir(parents=True, exist_ok=True)
        r = requests.get(ESRGAN_URL, timeout=300)
        r.raise_for_status()
        weights.write_bytes(r.content)
    model = ModelLoader().load_from_file(str(weights))
    model.model.eval()
    torch.set_grad_enabled(False)
    return model


def upscale(src: Path) -> Path:
    """4x Real-ESRGAN copy of `src` (cached); tiles of 256 px with a 16-px overlap keep CPU memory small."""
    out = CACHE_DIR / "upscaled" / f"{_key(src)}.jpg"
    if out.exists():
        return out
    import torch
    model = _esrgan()
    img = np.asarray(Image.open(src).convert("RGB"), dtype=np.float32) / 255.0
    h, w, _ = img.shape
    x = torch.from_numpy(img).permute(2, 0, 1).unsqueeze(0)
    s = 4
    result = torch.zeros(1, 3, h * s, w * s)
    for y0 in range(0, h, TILE):
        for x0 in range(0, w, TILE):
            ya, xa = max(y0 - PAD, 0), max(x0 - PAD, 0)
            yb, xb = min(y0 + TILE + PAD, h), min(x0 + TILE + PAD, w)
            tile = model(x[:, :, ya:yb, xa:xb])
            oy, ox = (y0 - ya) * s, (x0 - xa) * s
            th, tw = (min(y0 + TILE, h) - y0) * s, (min(x0 + TILE, w) - x0) * s
            result[:, :, y0 * s:y0 * s + th, x0 * s:x0 * s + tw] = tile[:, :, oy:oy + th, ox:ox + tw]
    arr = (result.squeeze(0).permute(1, 2, 0).clamp(0, 1).numpy() * 255).round().astype(np.uint8)
    up = Image.fromarray(arr)
    up.thumbnail((2400, 2400), Image.LANCZOS)
    out.parent.mkdir(parents=True, exist_ok=True)
    up.save(out, "JPEG", quality=92)
    print(f"  photo upscaled 4x (Real-ESRGAN): {w}x{h} -> {up.width}x{up.height}")
    return out


@lru_cache(maxsize=1)
def _depth_pipe():
    from transformers import pipeline
    return pipeline("depth-estimation", model=DEPTH_MODEL, device="cpu")


def depth(src: Path, out_png: Path) -> None:
    """Write a smoothed 8-bit depth map (white = near) of `src`, at most 960 px wide, to `out_png`."""
    cached = CACHE_DIR / "depth" / f"{_key(src)}.png"
    if not cached.exists():
        img = Image.open(src).convert("RGB")
        img.thumbnail((960, 960), Image.LANCZOS)
        d = np.asarray(_depth_pipe()(img)["depth"].convert("F").resize(img.size, Image.BICUBIC), dtype=np.float32)
        lo, hi = np.percentile(d, 2), np.percentile(d, 98)
        d = np.clip((d - lo) / max(hi - lo, 1e-6), 0, 1)
        from PIL import ImageFilter
        dm = Image.fromarray((d * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(3))  # soft edges stretch less
        cached.parent.mkdir(parents=True, exist_ok=True)
        dm.save(cached)
    out_png.write_bytes(cached.read_bytes())
