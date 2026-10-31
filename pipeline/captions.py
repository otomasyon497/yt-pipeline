"""Word-level timestamps via faster-whisper, aligned onto the exact script wording."""
import json
import re
from difflib import SequenceMatcher
from pathlib import Path

import soundfile as sf

from cache import cache_path, digest
from config import WHISPER_MODEL

_model = None


def _whisper():
    global _model
    if _model is None:
        from faster_whisper import WhisperModel

        _model = WhisperModel(WHISPER_MODEL, device="cpu", compute_type="int8", cpu_threads=2)
    return _model


def _norm(w: str) -> str:
    return re.sub(r"[^\w]", "", w.lower())


def _spread(out, i1, i2, t0, t1):
    n = i2 - i1
    for k in range(n):
        out[i1 + k] = (t0 + (t1 - t0) * k / n, t0 + (t1 - t0) * (k + 1) / n)


def align(script_text: str, heard: list[tuple[str, float, float]], total: float) -> list[dict]:
    """Map whisper word timings onto script tokens (keeps the script's spelling and numerals)."""
    toks = script_text.split()
    a = [_norm(t) for t in toks]
    b = [_norm(w[0]) for w in heard]
    out: list = [None] * len(toks)
    if heard:
        for tag, i1, i2, j1, j2 in SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
            if tag == "equal" or (tag == "replace" and i2 - i1 == j2 - j1):
                for k in range(i2 - i1):
                    out[i1 + k] = (heard[j1 + k][1], heard[j1 + k][2])
            elif tag == "replace":
                _spread(out, i1, i2, heard[j1][1], heard[j2 - 1][2])
    # Fill the gaps (deleted/unmatched tokens) between known neighbours.
    i = 0
    while i < len(out):
        if out[i] is not None:
            i += 1
            continue
        j = i
        while j < len(out) and out[j] is None:
            j += 1
        t0 = out[i - 1][1] if i > 0 else 0.0
        t1 = out[j][0] if j < len(out) else total
        _spread(out, i, j, t0, max(t1, t0))
        i = j
    return [{"t": toks[k], "s": round(out[k][0], 3), "e": round(out[k][1], 3)} for k in range(len(toks))]


def word_timings(wav: Path, script_text: str, tts_words: list | None = None) -> tuple[list[dict], str]:
    """Word timings for `script_text`: Kokoro's own timestamps when available, otherwise faster-whisper.

    Returns (words, source) where source is "kokoro" or "whisper".
    """
    info = sf.info(wav)
    total = info.frames / info.samplerate
    if tts_words:
        return align(script_text, [(w[0], w[1], w[2]) for w in tts_words], total), "kokoro"
    cached = cache_path("captions", f"{digest(WHISPER_MODEL, script_text, round(total, 3))}.json")
    if cached.exists():
        return json.loads(cached.read_text(encoding="utf-8")), "whisper"
    segments, _ = _whisper().transcribe(str(wav), language="en", word_timestamps=True, beam_size=1, vad_filter=False)
    heard = [(w.word, w.start, w.end) for seg in segments for w in (seg.words or [])]
    words = align(script_text, heard, total)
    cached.write_text(json.dumps(words), encoding="utf-8")
    return words, "whisper"
