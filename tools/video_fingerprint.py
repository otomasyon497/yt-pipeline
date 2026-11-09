"""Fingerprint of a rendered video, shared by tools/frame_audit.py and tools/yt_upload.py (no third-party imports)."""
import hashlib
from pathlib import Path


def fingerprint(path: Path) -> str:
    """Size + SHA-256 of the first and last 8 MB: changes with any re-render, fast on 500 MB files."""
    h = hashlib.sha256()
    size = Path(path).stat().st_size
    with open(path, "rb") as f:
        h.update(f.read(8 << 20))
        f.seek(max(0, size - (8 << 20)))
        h.update(f.read(8 << 20))
    return f"{size}:{h.hexdigest()}"
