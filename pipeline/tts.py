"""Kokoro TTS (Apache 2.0) on CPU, with a content-addressed cache."""
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


def synth(text: str, voice: str, out_wav: Path, speed: float = TTS_SPEED) -> float:
    """Synthesise `text` to `out_wav` (24 kHz mono). Returns duration in seconds."""
    cached = cache_path("tts", f"{digest(voice, speed, text)}.wav")
    if not cached.exists():
        chunks = []
        for _gs, _ps, audio in _pipeline(voice)(text, voice=voice, speed=speed, split_pattern=r"\n+"):
            chunks.append(np.asarray(audio, dtype=np.float32))
        if not chunks:
            raise RuntimeError(f"Kokoro produced no audio for: {text[:60]!r}")
        sf.write(cached, np.concatenate(chunks), TTS_SAMPLE_RATE, subtype="PCM_16")
    out_wav.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(cached, out_wav)
    info = sf.info(out_wav)
    return info.frames / info.samplerate
