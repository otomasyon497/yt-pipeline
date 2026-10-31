"""Pronunciation dictionary -> Kokoro inline phonemes ("[Port Said](/pˈɔɹt sɑˈid/)") or plain respellings.

Global entries live in pipeline/pronunciations.json; an episode can add or override them in
episodes/<slug>/pronunciations.json. Entry formats: {"ipa": "..."} (Kokoro/misaki phonemes) or {"say": "..."}.
Only the text sent to TTS changes; captions keep the script's spelling.
"""
import json
import re

from config import ROOT


def load(slug: str) -> dict:
    table: dict = {}
    for path in (ROOT / "pipeline" / "pronunciations.json", ROOT / "episodes" / slug / "pronunciations.json"):
        if path.exists():
            table.update(json.loads(path.read_text(encoding="utf-8")))
    return table


def apply(text: str, table: dict) -> tuple[str, list[str]]:
    """Single pass, longest phrase first, so replacements never nest. Returns (tts_text, entries used)."""
    if not table:
        return text, []
    keys = sorted(table, key=len, reverse=True)
    pattern = re.compile(r"(?<!\w)(" + "|".join(re.escape(k) for k in keys) + r")(?!\w)")
    used: list[str] = []

    def sub(m: re.Match) -> str:
        key = m.group(1)
        used.append(key)
        entry = table[key]
        return f"[{key}](/{entry['ipa']}/)" if "ipa" in entry else entry["say"]

    return pattern.sub(sub, text), sorted(set(used))
