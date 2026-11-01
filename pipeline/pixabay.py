"""Pixabay video search/download: second free stock source next to Pexels.

Pixabay Content License: free for commercial use, attribution not required (we credit anyway).
API terms: cache search results for 24 hours; at most 100 requests per 60 seconds.
"""
import json
import time

import requests

from cache import cache_path, digest
from config import secret

API = "https://pixabay.com/api/videos/"
_last_call = [0.0]


def search(query: str) -> list[dict]:
    cached = cache_path("pixabay_search", f"{digest(query)}.json")
    if cached.exists() and time.time() - cached.stat().st_mtime < 24 * 3600:
        return json.loads(cached.read_text(encoding="utf-8"))
    time.sleep(max(0.0, 0.7 - (time.time() - _last_call[0])))  # well under 100 requests per minute
    r = requests.get(API, params={"key": secret("PIXABAY_API_KEY"), "q": query[:100], "video_type": "film",
                                  "per_page": 30, "safesearch": "true"}, timeout=60)
    _last_call[0] = time.time()
    r.raise_for_status()
    hits = r.json().get("hits", [])
    cached.write_text(json.dumps(hits), encoding="utf-8")
    return hits


def _best_file(video: dict) -> dict | None:
    """Smallest rendition that is still at least 1920 px wide, else the largest one."""
    files = [f for f in (video.get("videos") or {}).values() if f.get("url") and f.get("width")]
    if not files:
        return None
    full_hd = [f for f in files if f["width"] >= 1920]
    return min(full_hd, key=lambda f: f["width"]) if full_hd else max(files, key=lambda f: f["width"])


def get_clip(query: str, need_sec: float, used_ids: set) -> dict:
    """Same result shape as pexels.get_clip (ids are prefixed "pixabay:" so both sources share used_ids)."""
    hits = [v for v in search(query) if f"pixabay:{v['id']}" not in used_ids and _best_file(v)]
    if not hits:
        raise RuntimeError(f"No usable Pixabay clip for query {query!r}")
    hits.sort(key=lambda v: 0 if v.get("duration", 0) >= need_sec else 1)  # long enough first, then API ranking
    v = hits[0]
    used_ids.add(f"pixabay:{v['id']}")
    f = _best_file(v)
    dest = cache_path("pixabay_video", f"{v['id']}_{f['width']}.mp4")
    if not dest.exists():
        data = requests.get(f["url"], timeout=300)
        data.raise_for_status()
        dest.write_bytes(data.content)
    user = v.get("user", "Pixabay user")
    return {
        "path": dest,
        "id": f"pixabay:{v['id']}",
        "user_name": user,
        "user_url": f"https://pixabay.com/users/{user}-{v.get('user_id')}/",
        "page_url": v.get("pageURL", ""),
        "duration": v.get("duration", 0),
        "source": "pixabay",
    }
