"""Kokoro TTS (Apache 2.0) on CPU with a content-addressed cache.

Also returns Kokoro's own word timestamps when the installed version provides them (Result.tokens with
start_ts/end_ts); otherwise None and captions fall back to faster-whisper.
"""
import json
import re
import shutil
from pathlib import Path

import numpy as np
import soundfile as sf

from cache import cache_path, digest
from config import TTS_SAMPLE_RATE, TTS_SPEED

_pipelines: dict = {}


def _pipeline(voice: str):
    from kokoro import KPipeline  # imported lazily: heavy

    lang = voice[0]  # 'a' = American, 'b' = British
    if lang not in _pipelines:
        _pipelines[lang] = KPipeline(lang_code=lang, repo_id="hexgrad/Kokoro-82M")
    return _pipelines[lang]


def _parts(result):
    """Kokoro >= 0.9 yields Result objects; older versions yield (graphemes, phonemes, audio) tuples."""
    if hasattr(result, "audio"):
        return result.phonemes, result.audio, getattr(result, "tokens", None)
    _gs, phonemes, audio = result
    return phonemes, audio, None


def synth(text: str, voice: str, out_wav: Path, speed: float = TTS_SPEED) -> tuple[float, list | None, str]:
    """Synthesise `text` to `out_wav` (24 kHz mono). Returns (seconds, [[word, start, end], ...] or None, phonemes)."""
    key = digest(voice, speed, text)
    wav_c, meta_c = cache_path("tts", f"{key}.wav"), cache_path("tts", f"{key}.json")
    if not (wav_c.exists() and meta_c.exists()):
        chunks, words, phonemes, offset, timed = [], [], [], 0.0, True
        for result in _pipeline(voice)(text, voice=voice, speed=speed, split_pattern=r"\n+"):
            ps, audio, tokens = _parts(result)
            if audio is None:
                continue
            a = np.asarray(audio, dtype=np.float32)
            chunks.append(a)
            phonemes.append(ps or "")
            if tokens:
                for tok in tokens:
                    st, et, txt = getattr(tok, "start_ts", None), getattr(tok, "end_ts", None), getattr(tok, "text", "")
                    if st is not None and et is not None and re.sub(r"[^\w]", "", txt):
                        words.append([txt, offset + float(st), offset + float(et)])
            else:
                timed = False
            offset += len(a) / TTS_SAMPLE_RATE
        if not chunks:
            raise RuntimeError(f"Kokoro produced no audio for: {text[:60]!r}")
        sf.write(wav_c, np.concatenate(chunks), TTS_SAMPLE_RATE, subtype="PCM_16")
        meta_c.write_text(json.dumps({"words": words if timed and words else None, "phonemes": " | ".join(phonemes)}),
                          encoding="utf-8")
    out_wav.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(wav_c, out_wav)
    meta = json.loads(meta_c.read_text(encoding="utf-8"))
    info = sf.info(out_wav)
    return info.frames / info.samplerate, meta["words"], meta["phonemes"]
