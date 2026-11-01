"""Transcribe a reference video's audio (any language) for script analysis. Runs on Actions, not the PC.

  python tools/transcribe.py <audio> <out.txt> [--model small] [--language tr]

Writes the text grouped into ~30 s blocks with [mm:ss] markers (compact enough to read and quote).
"""
import argparse
from pathlib import Path

from faster_whisper import WhisperModel


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("audio", type=Path)
    ap.add_argument("out", type=Path)
    ap.add_argument("--model", default="small")
    ap.add_argument("--language", default=None)
    a = ap.parse_args()
    model = WhisperModel(a.model, device="cpu", compute_type="int8")
    segments, info = model.transcribe(str(a.audio), language=a.language, beam_size=1, vad_filter=True)
    lines, block, block_start = [], [], 0.0
    for seg in segments:
        if not block:
            block_start = seg.start
        block.append(seg.text.strip())
        if seg.end - block_start >= 30:
            lines.append(f"[{int(block_start // 60):02d}:{int(block_start % 60):02d}] " + " ".join(block))
            block = []
    if block:
        lines.append(f"[{int(block_start // 60):02d}:{int(block_start % 60):02d}] " + " ".join(block))
    a.out.write_text(f"language={info.language} ({info.language_probability:.2f}), duration={info.duration:.0f}s\n\n"
                     + "\n\n".join(lines) + "\n", encoding="utf-8")
    print(f"{len(lines)} blocks, language {info.language}")


if __name__ == "__main__":
    main()
