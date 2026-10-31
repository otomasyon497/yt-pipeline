"""Pexels video search/download using the current /v1/videos/ endpoints, with caching and a local rate limit."""
import json
import os
from pathlib import Path

import requests

from cache import HourlyLimiter, cache_path, digest
from config import PEXELS_BASE, PEXELS_HOURLY_SOFT_LIMIT, secret

_limiter = HourlyLimiter("pexels", PEXELS_HOURLY_SOFT_LIMIT)


def _headers() -> dict:
    return {"Authorization": secret("PEXELS_API_KEY")}


def search(query: str) -> list[dict]:
    cached = cache_path("pexels_search", f"{digest(query)}.json")
    if cached.exists():
        return json.loads(cached.read_text(encoding="utf-8"))
    _limiter.hit()
    r = requests.get(
        f"{PEXELS_BASE}/search",
        headers=_headers(),
        params={"query": query, "orientation": "landscape", "size": "medium", "per_page": 15},
        timeout=30,
    )
    if r.status_code == 429:
        raise RuntimeError("Pexels returned 429 (rate limited)")
    r.raise_for_status()
    print(f"  pexels: '{query}' -> {len(r.json().get('videos', []))} results, remaining={r.headers.get('X-Ratelimit-Remaining')}")
    videos = r.json().get("videos", [])
    cached.write_text(json.dumps(videos), encoding="utf-8")
    return videos


def _best_file(video: dict):
    files = [f for f in video.get("video_files", []) if f.get("file_type") == "video/mp4" and 1280 <= (f.get("width") or 0) <= 2560]
    return min(files, key=lambda f: abs(f["width"] - 1920)) if files else None


def get_clip(query: str, need_sec: float, used_ids: set) -> dict:
    """Return {path, id, user_name, user_url, page_url, duration} for the best matching clip."""
    videos = search(query)
    if not videos and len(query.split()) > 2:
        videos = search(" ".join(query.split()[:2]))
    candidates = [v for v in videos if v["id"] not in used_ids and _best_file(v)]
    if not candidates:
        raise RuntimeError(f"No usable Pexels clip for query {query!r}")
    # Prefer clips long enough for the scene (no loop needed); otherwise keep search ranking.
    candidates.sort(key=lambda v: 0 if v.get("duration", 0) >= need_sec else 1)
    v = candidates[0]
    f = _best_file(v)
    dest = cache_path("pexels_video", f"{v['id']}_{f['width']}.mp4")
    if not dest.exists():
        with requests.get(f["link"], stream=True, timeout=120) as r:
            r.raise_for_status()
            with open(dest, "wb") as fh:
                for chunk in r.iter_content(1 << 20):
                    fh.write(chunk)
    used_ids.add(v["id"])
    return {
        "path": dest,
        "id": v["id"],
        "user_name": v["user"]["name"],
        "user_url": v["user"]["url"],
        "page_url": v["url"],
        "duration": v.get("duration", 0),
    }
