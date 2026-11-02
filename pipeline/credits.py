"""credits.txt - ready to paste into the YouTube description."""
import json
import re
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


def compact(text: str) -> str:
    """Shorter credits for the YouTube description (5,000-character limit); credits.txt keeps every link.

    Stock clips (Pexels / Pixabay licences need no attribution) become one line of names; archive images keep
    title, author and licence, and the link only where the licence asks for it (CC BY)."""
    out, names = [], []
    for line in text.splitlines():
        stock = re.match(r"- (.+?) \(https?://[^)]*\) - https?://\S+$", line)
        if stock:
            names.append(stock.group(1))
            continue
        if names:
            out.append("Footage by: " + ", ".join(dict.fromkeys(names)) + ".")
            names = []
        if line == "Stock footage:":
            continue
        photo = re.match(r"- (.+) - (.+?) - (.+?) - (https?://\S+)$", line)
        if photo:
            title, artist, licence, url = photo.groups()
            title = title if len(title) <= 70 else title[:67].rstrip() + "..."
            artist = artist if len(artist) <= 50 else artist[:47].rstrip() + "..."
            line = f"- {title} - {artist} - {licence}" + (f" - {url}" if licence.upper().startswith("CC BY") else "")
        out.append(line)
    if names:
        out.append("Footage by: " + ", ".join(dict.fromkeys(names)) + ".")
    return "\n".join(out)


def write(path: Path, clips: list[dict], track: Path | None, used_ai_images: bool, extra: list[str] = ()) -> None:
    lines = []
    headers = {"pexels": "Videos provided by Pexels (https://www.pexels.com)",
               "pixabay": "Videos from Pixabay (https://pixabay.com)"}
    for source, header in headers.items():
        group = [c for c in clips if c.get("source", "pexels") == source]
        if not group:
            continue
        lines += [header, "", "Stock footage:"]
        seen = set()
        for c in group:
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
    if extra:
        lines += [*extra, ""]
    lines.append("Narration: synthetic voice (Kokoro TTS).")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
