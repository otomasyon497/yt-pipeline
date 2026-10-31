"""Cloudflare Workers AI image generation with caching and a neuron budget guard."""
import base64
import io
import math
import os

import requests
from PIL import Image

from cache import DailyBudget, cache_path, digest
from config import (
    CF_DAILY_BUDGET_NEURONS,
    CF_IMAGE_HEIGHT,
    CF_IMAGE_WIDTH,
    CF_MODEL_FALLBACK,
    CF_MODEL_PRIMARY,
    CF_STYLE_SUFFIX,
    HEIGHT,
    WIDTH,
    secret,
)

_budget = DailyBudget("cf_neurons", CF_DAILY_BUDGET_NEURONS)
_FALLBACK_STEPS = 6


def _url(model: str) -> str:
    return f"https://api.cloudflare.com/client/v4/accounts/{secret('CF_ACCOUNT_ID')}/ai/run/{model}"


def _auth() -> dict:
    return {"Authorization": f"Bearer {secret('CF_API_TOKEN')}"}


def _decode(resp: requests.Response) -> bytes:
    if resp.headers.get("content-type", "").startswith("image/"):
        return resp.content
    body = resp.json()
    img = (body.get("result") or body).get("image")
    if not img:
        raise RuntimeError(f"Unexpected Workers AI response: {str(body)[:200]}")
    return base64.b64decode(img)


def _klein(prompt: str, seed: int) -> bytes:
    tiles = math.ceil(CF_IMAGE_WIDTH / 512) * math.ceil(CF_IMAGE_HEIGHT / 512)
    _budget.spend(tiles * 26.05)
    # Workers AI requires multipart/form-data for this model, even for a plain prompt.
    form = {k: (None, str(v)) for k, v in {"prompt": prompt, "width": CF_IMAGE_WIDTH, "height": CF_IMAGE_HEIGHT, "seed": seed}.items()}
    r = requests.post(_url(CF_MODEL_PRIMARY), headers=_auth(), files=form, timeout=180)
    if not r.ok:
        raise RuntimeError(f"{CF_MODEL_PRIMARY} HTTP {r.status_code}: {r.text[:300]}")
    return _decode(r)


def _schnell(prompt: str, seed: int) -> bytes:
    _budget.spend(4 * 4.8 + _FALLBACK_STEPS * 9.6)  # 1024x1024 = 4 tiles + steps
    r = requests.post(_url(CF_MODEL_FALLBACK), headers=_auth(), json={"prompt": prompt, "steps": _FALLBACK_STEPS}, timeout=180)
    if not r.ok:
        raise RuntimeError(f"{CF_MODEL_FALLBACK} HTTP {r.status_code}: {r.text[:300]}")
    return _decode(r)


def _fit_16_9(raw: bytes) -> Image.Image:
    """Centre-crop to 16:9 and resize to the output resolution."""
    img = Image.open(io.BytesIO(raw)).convert("RGB")
    w, h = img.size
    target_h = round(w * 9 / 16)
    if target_h <= h:
        top = (h - target_h) // 2
        img = img.crop((0, top, w, top + target_h))
    else:
        target_w = round(h * 16 / 9)
        left = (w - target_w) // 2
        img = img.crop((left, 0, left + target_w, h))
    return img.resize((WIDTH, HEIGHT), Image.LANCZOS)


def generate(prompt: str, style: str | None = None):
    """Return the path of a 1920x1080 JPEG for `prompt` (cached by prompt + model settings)."""
    full = f"{prompt}, {style or CF_STYLE_SUFFIX}"
    key = digest(CF_MODEL_PRIMARY, CF_IMAGE_WIDTH, CF_IMAGE_HEIGHT, full)
    dest = cache_path("cf_images", f"{key}.jpg")
    if dest.exists():
        print(f"  cf: cache hit {key}")
        return dest
    seed = int(key[:8], 16) % (2**31)
    if CF_MODEL_PRIMARY == CF_MODEL_FALLBACK:  # schnell selected explicitly (e.g. licence caution)
        raw, used = _schnell(full, seed), CF_MODEL_FALLBACK
    else:
        try:
            raw, used = _klein(full, seed), CF_MODEL_PRIMARY
        except RuntimeError as e:
            if "budget" in str(e):
                raise
            print(f"  cf: primary model failed ({e}); falling back to {CF_MODEL_FALLBACK}")
            raw, used = _schnell(full, seed), CF_MODEL_FALLBACK
    _fit_16_9(raw).save(dest, "JPEG", quality=92)
    print(f"  cf: generated {key} with {used}")
    return dest
