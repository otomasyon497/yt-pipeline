"""youtube.txt: title, ready-to-paste description (intro + chapters + credits) and tags for a manual upload."""
from pathlib import Path


def _stamp(sec: int, hours: bool) -> str:
    h, m, s = sec // 3600, sec % 3600 // 60, sec % 60
    return f"{h}:{m:02d}:{s:02d}" if hours else f"{m:02d}:{s:02d}"


def chapter_lines(chapters: list[dict], fps: int, total_frames: int) -> list[str]:
    """YouTube chapters need the first one at 00:00, at least 3 chapters and each at least 10 s long."""
    if len(chapters) < 3:
        return []
    starts = [0] + [c["startFrame"] // fps for c in chapters[1:]]
    ends = starts[1:] + [total_frames // fps]
    if any(e - s < 10 for s, e in zip(starts, ends)):
        return []
    hours = total_frames // fps >= 3600
    return [f"{_stamp(s, hours)} {c['title']}" for s, c in zip(starts, chapters)]


def write(path: Path, script, timeline: dict, credits_text: str) -> list[str]:
    """Write youtube.txt and return a list of warnings (empty when everything is within YouTube's limits)."""
    warnings = []
    meta = script.youtube
    title = meta.title if meta else script.title[:100]
    chapters = chapter_lines(timeline["chapters"], timeline["fps"], timeline["totalFrames"])
    if not chapters and len(timeline["chapters"]) > 1:
        warnings.append("chapters left out: YouTube needs at least 3 chapters, each at least 10 s long")
    parts = []
    if meta and meta.description.strip():
        parts.append(meta.description.strip())
    if chapters:
        parts.append("Chapters:\n" + "\n".join(chapters))
    parts.append(credits_text.strip())
    description = "\n\n".join(parts) + "\n"
    for label, text in (("title", title), ("description", description)):
        if "<" in text or ">" in text:
            warnings.append(f"YouTube rejects '<' and '>' in the {label}")
    if len(description) > 5000:
        warnings.append(f"description is {len(description)} characters (limit 5000)")
    tags = meta.tags if meta else []
    tag_chars = sum(len(t) + (2 if " " in t else 0) for t in tags) + max(len(tags) - 1, 0)
    if tag_chars > 500:
        warnings.append(f"tags use {tag_chars} characters (limit 500)")
    pinned = meta.pinned_comment if meta else None
    extra = f"\nPINNED COMMENT (post it under the video and pin it)\n{pinned}\n" if pinned else ""
    path.write_text(f"TITLE\n{title}\n\nDESCRIPTION\n{description}\nTAGS\n{', '.join(tags)}\n{extra}", encoding="utf-8")
    return warnings
