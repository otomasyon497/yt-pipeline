"""Content-addressed cache helpers plus small persistent ledgers (rate limit, neuron budget)."""
import hashlib
import json
import time
from datetime import datetime, timezone
from pathlib import Path

from config import CACHE_DIR


def digest(*parts) -> str:
    return hashlib.sha1("\x1f".join(str(p) for p in parts).encode("utf-8")).hexdigest()[:16]


def cache_path(kind: str, name: str) -> Path:
    p = CACHE_DIR / kind
    p.mkdir(parents=True, exist_ok=True)
    return p / name


def _load(path: Path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def _save(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data), encoding="utf-8")


class HourlyLimiter:
    """Rolling one-hour request counter persisted in the cache directory."""

    def __init__(self, name: str, limit: int):
        self.path = cache_path("ledger", f"{name}.json")
        self.limit = limit

    def hit(self) -> None:
        now = time.time()
        stamps = [t for t in _load(self.path, []) if now - t < 3600]
        if len(stamps) >= self.limit:
            raise RuntimeError(f"Local rate limit reached ({self.limit}/hour). Try again later or rely on cache.")
        stamps.append(now)
        _save(self.path, stamps)


class DailyBudget:
    """Best-effort daily neuron ledger (UTC day, same reset as Cloudflare)."""

    def __init__(self, name: str, limit: int):
        self.path = cache_path("ledger", f"{name}.json")
        self.limit = limit

    def spend(self, amount: float) -> None:
        day = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        data = _load(self.path, {})
        used = data.get(day, 0.0)
        if used + amount > self.limit:
            raise RuntimeError(f"Daily neuron budget exceeded ({used:.0f}+{amount:.0f} > {self.limit}).")
        _save(self.path, {day: used + amount})


_STOP = {"aerial", "view", "video", "footage", "the", "and", "with", "from", "of", "a", "in", "on", "at"}


def relevance(query: str, text: str) -> int:
    """How many meaningful query words appear in a clip's tags / page slug (stock clip ranking)."""
    words = {w for w in query.lower().replace("-", " ").split() if len(w) > 2 and w not in _STOP}
    hay = text.lower().replace("-", " ").replace(",", " ")
    return sum(1 for w in words if w in hay or (w.endswith("s") and w[:-1] in hay))
