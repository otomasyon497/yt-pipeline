"""credits.txt - ready to paste into the YouTube description."""
import json
from pathlib import Path

from config import MUSIC_DIR


def music_credit(track: Path | None) -> str | None:
    if track is None:
        return None
    try:
        table = json.loads((MUSIC_DIR / "credits.json").read_text(encoding="utf-8"))
    except Exception:
        return None
    return table.get(track.name)


def write(path: Path, clips: list[dict], track: Path | None, used_ai_images: bool) -> None:
    lines = ["Videos provided by Pexels (https://www.pexels.com)", ""]
    if clips:
        lines.append("Stock footage:")
        seen = set()
        for c in clips:
            if c["id"] in seen:
                continue
            seen.add(c["id"])
            lines.append(f"- {c['user_name']} ({c['user_url']}) - {c['page_url']}")
        lines.append("")
    mc = music_credit(track)
    if mc:
        lines += ["Music:", f"- {mc}", ""]
    if used_ai_images:
        lines += ["Some images in this video were generated with AI (FLUX by Black Forest Labs, via Cloudflare Workers AI).", ""]
    lines.append("Narration: synthetic voice (Kokoro TTS).")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
