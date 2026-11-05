"""Photos and film from the NASA Image and Video Library (images.nasa.gov), referenced as "nasa:<nasa_id>".

NASA's own images and video are not protected by copyright in the United States (NASA media usage guidelines).
Items made by others say so in their description, so an item whose description names a copyright holder, or credits
someone other than NASA as the source ("courtesy of ..."), is refused and the episode fails loudly, as with Commons.
Credits go to credits.txt.
"""
import hashlib
import io
import json
import re
import time
from pathlib import Path

import requests
from PIL import Image

from config import CACHE_DIR

API = "https://images-api.nasa.gov"
UA = {"User-Agent": "yt-pipeline/1.0 (https://github.com/otomasyon497/yt-pipeline)"}


def _get(url: str, timeout: int = 60, stream: bool = False) -> requests.Response:
    for attempt in range(4):
        try:
            r = requests.get(url.replace(" ", "%20"), headers=UA, timeout=timeout, stream=stream)
            r.raise_for_status()
            return r
        except requests.RequestException:
            if attempt == 3:
                raise
            time.sleep(3 * (attempt + 1))
    raise RuntimeError("unreachable")


def _id(ref: str) -> str:
    return ref.split(":", 1)[1].strip() if ref.lower().startswith("nasa:") else ref.strip()


def _meta(nasa_id: str) -> tuple[str, str]:
    """(title, center); refuses items that name another owner."""
    m = _get(_get(f"{API}/metadata/{nasa_id}").json()["location"]).json()
    title = str(m.get("AVAIL:Title") or nasa_id).strip()
    center = str(m.get("AVAIL:Center") or "").strip()
    text = " ".join(str(m.get(k, "")) for k in ("AVAIL:Description", "AVAIL:Description508", "AVAIL:SecondaryCreator",
                                                 "AVAIL:Photographer", "AVAIL:Album"))
    courtesy = [c for c in re.findall(r"courtesy (?:of )?([A-Z][\w.&\- ]{2,40})", text, re.I)
                if not re.match(r"(NASA|JPL|the National Aeronautics)", c.strip(), re.I)]
    if re.search(r"©|\bcopyright", text, re.I) or courtesy:
        raise ValueError(f"nasa:{nasa_id}: its description names another owner ({(courtesy or ['copyright'])[0].strip()})"
                         " - choose another item")
    return title, center


def _assets(nasa_id: str) -> list[str]:
    return [i["href"] for i in _get(f"{API}/asset/{nasa_id}").json()["collection"]["items"]]


def _credit(nasa_id: str, title: str, center: str) -> str:
    who = f"NASA ({center})" if center else "NASA"
    return f"{title} - {who} - Public domain (NASA media guidelines) - https://images.nasa.gov/details/{nasa_id}"


def _cached(kind: str, nasa_id: str, suffix: str) -> tuple[Path, Path]:
    key = hashlib.sha1(f"nasa:{nasa_id}".encode()).hexdigest()
    path = CACHE_DIR / "nasa" / f"{key}_{kind}{suffix}"
    return path, path.with_suffix(".json")


def fetch(ref: str) -> tuple[Path, str]:
    """A NASA image (the large rendition, else the original, at most 3,000 px): (local JPEG, credit line)."""
    nasa_id = _id(ref)
    img_path, meta_path = _cached("img", nasa_id, ".jpg")
    if img_path.exists() and meta_path.exists():
        return img_path, json.loads(meta_path.read_text(encoding="utf-8"))["credit"]
    title, center = _meta(nasa_id)
    hrefs = _assets(nasa_id)
    pick = next((h for suf in ("~large.jpg", "~orig.jpg", "~medium.jpg") for h in hrefs if h.lower().endswith(suf)), None)
    if pick is None:
        raise ValueError(f"nasa:{nasa_id}: no JPEG rendition in its asset list")
    img = Image.open(io.BytesIO(_get(pick, timeout=180).content)).convert("RGB")
    img.thumbnail((3000, 3000))
    img_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(img_path, "JPEG", quality=92)
    credit = _credit(nasa_id, title, center)
    meta_path.write_text(json.dumps({"credit": credit}), encoding="utf-8")
    print(f"  nasa: {nasa_id} ({title[:60]})")
    return img_path, credit


def fetch_video(ref: str) -> tuple[Path, str]:
    """A NASA video: the large (about 1080p) rendition, else medium, else the original: (local MP4, credit line)."""
    nasa_id = _id(ref)
    path, meta_path = _cached("video", nasa_id, ".mp4")
    if path.exists() and meta_path.exists():
        return path, json.loads(meta_path.read_text(encoding="utf-8"))["credit"]
    title, center = _meta(nasa_id)
    hrefs = _assets(nasa_id)
    pick = next((h for suf in ("~large.mp4", "~medium.mp4", "~orig.mp4", "~small.mp4") for h in hrefs
                 if h.lower().endswith(suf)), None)
    if pick is None:
        raise ValueError(f"nasa:{nasa_id}: no MP4 rendition in its asset list")
    path.parent.mkdir(parents=True, exist_ok=True)
    with _get(pick, timeout=600, stream=True) as r, open(path, "wb") as f:
        for chunk in r.iter_content(1 << 20):
            f.write(chunk)
    credit = _credit(nasa_id, title, center)
    meta_path.write_text(json.dumps({"credit": credit}), encoding="utf-8")
    print(f"  nasa video: {nasa_id} ({title[:60]})")
    return path, credit
