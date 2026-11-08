"""Archival images from Wikimedia Commons, licence-checked.

The script names exact files ("File:..."). We read the licence metadata and accept only public domain,
CC0 and CC BY (attribution); CC BY-SA, NC, ND, fair use and anything unclear are refused, so the episode
fails loudly instead of using an image we may not be allowed to use. Credits go to credits.txt.
"""
import hashlib
import html
import io
import json
import re
import time
from pathlib import Path

import requests
from PIL import Image, ImageEnhance, ImageFilter, ImageOps, ImageStat

from config import CACHE_DIR, HEIGHT, WIDTH

API = "https://commons.wikimedia.org/w/api.php"
# Wikimedia asks API clients for a descriptive User-Agent with a contact.
UA = {"User-Agent": "yt-pipeline/1.0 (https://github.com/otomasyon497/yt-pipeline)"}
OK_EXACT = {"pd", "cc0", "cc-pd", "public domain"}


def _allowed(code: str, short: str) -> bool:
    c, s = code.lower().strip(), short.lower().strip()
    if c in OK_EXACT or s.startswith("public domain") or s == "cc0" or s == "no restrictions":
        return True
    # CC BY 1.0-4.0 only (attribution); reject share-alike, non-commercial and no-derivatives
    return bool(re.fullmatch(r"cc-by-\d(\.\d)?", c)) or bool(re.fullmatch(r"cc by \d(\.\d)?", s))


def _clean(value: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", value or ""))).strip()


def fetch(title: str) -> tuple[Path, str]:
    """Download a Commons file (2400 px rendition) and return (local path, credit line)."""
    title = title if title.startswith("File:") else f"File:{title}"
    key = hashlib.sha1(title.encode()).hexdigest()
    img_path = CACHE_DIR / "commons" / f"{key}.jpg"
    meta_path = img_path.with_suffix(".json")
    if img_path.exists() and meta_path.exists():
        return img_path, json.loads(meta_path.read_text(encoding="utf-8"))["credit"]
    params = {"action": "query", "titles": title, "prop": "imageinfo", "iiprop": "url|extmetadata|mime|size",
              "iiurlwidth": 2400, "format": "json"}
    for attempt in range(4):
        try:
            r = requests.get(API, params=params, headers=UA, timeout=60)
            r.raise_for_status()
            break
        except requests.RequestException:
            if attempt == 3:
                raise
            time.sleep(3 * (attempt + 1))
    page = next(iter(r.json()["query"]["pages"].values()))
    if "imageinfo" not in page:
        raise ValueError(f"Commons file not found: {title}")
    info = page["imageinfo"][0]
    meta = info.get("extmetadata", {})
    code = meta.get("License", {}).get("value", "")
    short = _clean(meta.get("LicenseShortName", {}).get("value", ""))
    if not _allowed(code, short):
        raise ValueError(f"{title}: licence {short or code!r} is not public domain / CC0 / CC BY - choose another file")
    artist = _clean(meta.get("Artist", {}).get("value", "")) or "unknown author"
    url = info.get("thumburl") or info["url"]
    for attempt in range(4):
        try:
            data = requests.get(url, headers=UA, timeout=120)
            data.raise_for_status()
            break
        except requests.RequestException:
            if attempt == 3:
                raise
            time.sleep(3 * (attempt + 1))
    img = Image.open(io.BytesIO(data.content))
    img = img.convert("RGB")
    img_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(img_path, "JPEG", quality=92)
    name = re.sub(r"\.(jpe?g|png|tiff?|gif|webp)$", "", title[5:], flags=re.I)
    credit = f"{name} - {artist} - {short or code} - {info.get('descriptionurl', '')}"
    meta_path.write_text(json.dumps({"credit": credit, "licence": short or code}), encoding="utf-8")
    print(f"  commons: {title} ({short or code})")
    return img_path, credit


def fetch_video(title: str) -> tuple[Path, str]:
    """Download a Commons video (archival film): same licence rules as images; a transcode of 480-1080 lines
    (720 preferred) when Commons has one, else the original. Returns (local path, credit line)."""
    title = title if title.startswith("File:") else f"File:{title}"
    key = hashlib.sha1(title.encode()).hexdigest()
    meta_path = CACHE_DIR / "commons" / f"{key}.video.json"
    if meta_path.exists():
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        if Path(meta["path"]).exists():
            return Path(meta["path"]), meta["credit"]
    params = {"action": "query", "titles": title, "prop": "videoinfo", "viprop": "url|extmetadata|derivatives|mime",
              "format": "json"}
    for attempt in range(4):
        try:
            r = requests.get(API, params=params, headers=UA, timeout=60)
            r.raise_for_status()
            break
        except requests.RequestException:
            if attempt == 3:
                raise
            time.sleep(3 * (attempt + 1))
    page = next(iter(r.json()["query"]["pages"].values()))
    if "videoinfo" not in page:
        raise ValueError(f"Commons video not found: {title}")
    info = page["videoinfo"][0]
    meta = info.get("extmetadata", {})
    code = meta.get("License", {}).get("value", "")
    short = _clean(meta.get("LicenseShortName", {}).get("value", ""))
    if not _allowed(code, short):
        raise ValueError(f"{title}: licence {short or code!r} is not public domain / CC0 / CC BY - choose another film")
    artist = _clean(meta.get("Artist", {}).get("value", "")) or "unknown author"
    derivs = [d for d in info.get("derivatives", []) if 480 <= int(d.get("height") or 0) <= 1080]
    url = min(derivs, key=lambda d: abs(int(d["height"]) - 720))["src"] if derivs else info["url"]
    ext = Path(url.split("?")[0]).suffix or ".webm"
    path = CACHE_DIR / "commons" / f"{key}{ext}"
    path.parent.mkdir(parents=True, exist_ok=True)
    for attempt in range(4):
        try:
            with requests.get(url, headers=UA, timeout=300, stream=True) as resp:
                resp.raise_for_status()
                with open(path, "wb") as fh:
                    for chunk in resp.iter_content(1 << 20):
                        fh.write(chunk)
            break
        except requests.RequestException:
            if attempt == 3:
                raise
            time.sleep(5 * (attempt + 1))
    name = re.sub(r"\.(webm|ogv|ogg|mpe?g|mp4|mov)$", "", title[5:], flags=re.I)
    credit = f"{name} - {artist} - {short or code} - {info.get('descriptionurl', '')}"
    meta_path.write_text(json.dumps({"credit": credit, "licence": short or code, "path": str(path)}), encoding="utf-8")
    print(f"  commons film: {title} ({short or code}), {path.stat().st_size / 1e6:.1f} MB")
    return path, credit


# Photo quality (measured 2026-11-08 on the photos of episodes 5 and 6): sharp NASA renditions keep 0.71-0.85 of their
# edge detail when shown at 1600 px instead of 800 px; soft or upscaled ones keep about 0.53 and looked blurry on
# screen. Hazy astronaut photos (luminance spread under ~26) looked washed out: they get an automatic levels stretch.
MIN_DETAIL = 0.65
MIN_LONG_SIDE = 1400
HAZY = 26


def quality(img: Image.Image) -> dict:
    """{"long": px, "detail": fine/coarse edge ratio, "contrast": luminance spread} of a picture."""
    g = img.convert("L")

    def edges(w: int) -> float:
        s = g.resize((w, max(1, round(g.height * w / g.width))), Image.LANCZOS)
        return ImageStat.Stat(s.filter(ImageFilter.FIND_EDGES)).mean[0]

    coarse = edges(800)
    small = g.resize((400, max(1, round(g.height * 400 / g.width))))
    return {"long": max(img.size), "detail": edges(1600) / coarse if coarse > 0 else 0.0,
            "contrast": ImageStat.Stat(small).stddev[0]}


def check_quality(img: Image.Image, ref: str) -> dict:
    """Raise for a photo that would look blurry on screen; returns its measurements."""
    q = quality(img)
    if q["long"] < MIN_LONG_SIDE:
        raise ValueError(f"{ref}: {img.width}x{img.height} px is too small for a 1080p frame - choose a larger file")
    if q["detail"] < MIN_DETAIL:
        raise ValueError(f"{ref}: soft or upscaled (detail ratio {q['detail']:.2f} < {MIN_DETAIL}) - it looks blurry "
                         f"on screen; choose a sharper file (NASA originals are usually best)")
    return q


def prepare(src: Path, out_main: Path, out_bg: Path, ref: str = "", strict: bool = True) -> str:
    """Write the photo (fit inside the frame, with headroom for a slow push-in) and a blurred, darkened
    full-frame background from the same picture. Returns "cover" for near-16:9 pictures, else "contain".
    Blurry photos are refused (check_quality; only a note when not strict, for episodes made before the check);
    hazy ones get a levels stretch."""
    img = Image.open(src).convert("RGB")
    try:
        q = check_quality(img, ref or src.name)
    except ValueError as e:
        if strict:
            raise
        print(f"  note: {e}")
        q = quality(img)
    if q["contrast"] < HAZY:
        img = ImageOps.autocontrast(img, cutoff=0.5)
        print(f"  photo {ref or src.name}: hazy (spread {q['contrast']:.0f}), levels stretched")
    ratio = img.width / img.height
    mode = "cover" if 1.55 <= ratio <= 2.0 and img.width >= 1400 else "contain"
    main = img.copy()
    main.thumbnail((int(WIDTH * 1.25), int(HEIGHT * 1.25)), Image.LANCZOS)
    main.save(out_main, "JPEG", quality=90)
    # background: cover-crop to 16:9, small blur radius on a downscaled copy (cheap), darker
    bw, bh = 640, 360
    scale = max(bw / img.width, bh / img.height)
    bg = img.resize((max(bw, round(img.width * scale)), max(bh, round(img.height * scale))), Image.LANCZOS)
    left, top = (bg.width - bw) // 2, (bg.height - bh) // 2
    bg = bg.crop((left, top, left + bw, top + bh)).filter(ImageFilter.GaussianBlur(14))
    bg = ImageEnhance.Brightness(bg).enhance(0.45).resize((WIDTH, HEIGHT), Image.BICUBIC)
    bg.save(out_bg, "JPEG", quality=85)
    return mode
