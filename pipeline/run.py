"""Pipeline orchestrator.

  python pipeline/run.py prepare  <slug>   # TTS, captions, media, audio mix, timeline.json
  (remotion render happens as a separate workflow step)
  python pipeline/run.py thumbnails <slug> # 3 thumbnail variants (needs the Remotion deps)
  python pipeline/run.py finalize <slug>   # mux audio, copy credits/samples into out/<slug>/
"""
import hashlib
import json
import os
import shutil
import sys
import time
from contextlib import contextmanager
from pathlib import Path

import numpy as np
import soundfile as sf

import captions
import cf_images
import credits
import media
import pexels
import thumbnails
import timeline as tl
import tts
from config import (BUILD_DIR, DEFAULT_VOICE, FPS, MUSIC_DIR, OUT_DIR, PUBLIC_MEDIA, ROOT, SAMPLE_MIN_SECONDS,
                    SAMPLE_VOICES, TTS_SAMPLE_RATE)
from schema import load_script

_timings: dict[str, float] = {}


@contextmanager
def step(name: str):
    print(f"\n=== {name} ===", flush=True)
    t0 = time.time()
    yield
    _timings[name] = round(time.time() - t0, 1)
    print(f"--- {name}: {_timings[name]}s", flush=True)


def pick_music(setting: str, slug: str) -> Path | None:
    if setting == "none":
        return None
    tracks = sorted(p for p in MUSIC_DIR.glob("*") if p.suffix.lower() in {".mp3", ".wav", ".m4a", ".ogg", ".flac"})
    if setting != "auto":
        named = MUSIC_DIR / setting
        return named if named.exists() else None
    if not tracks:
        print("  no tracks in /music -> video will have narration only")
        return None
    return tracks[int(hashlib.sha1(slug.encode()).hexdigest(), 16) % len(tracks)]


def voice_samples(script, out_dir: Path) -> None:
    """Render ~10 s of the opening narration with each candidate voice (whole scenes, so no cut-off words)."""
    out_dir.mkdir(parents=True, exist_ok=True)
    for voice in SAMPLE_VOICES:
        parts, total = [], 0.0
        for sc in script.scenes:
            tmp = out_dir / f"_{voice}_{sc.id}.wav"
            total += tts.synth(sc.narration, voice, tmp)
            data, _ = sf.read(tmp, dtype="float32")
            parts.append(data)
            tmp.unlink()
            if total >= SAMPLE_MIN_SECONDS:
                break
        sf.write(out_dir / f"voice_{voice}.wav", np.concatenate(parts), TTS_SAMPLE_RATE, subtype="PCM_16")
        print(f"  sample {voice}: {total:.1f}s")


def prepare(slug: str) -> None:
    script = load_script(ROOT / "episodes" / slug / "script.json")
    work = BUILD_DIR / slug
    shutil.rmtree(work, ignore_errors=True)
    shutil.rmtree(PUBLIC_MEDIA, ignore_errors=True)
    (work / "audio").mkdir(parents=True)
    PUBLIC_MEDIA.mkdir(parents=True)
    voice = script.voice or DEFAULT_VOICE

    with step("tts"):
        wavs, durations = [], []
        for sc in script.scenes:
            wav = work / "audio" / f"{sc.id}.wav"
            durations.append(tts.synth(sc.narration, voice, wav))
            wavs.append(wav)
            print(f"  {sc.id}: {durations[-1]:.1f}s")

    with step("captions"):
        words = [captions.word_timings(w, sc.narration) for w, sc in zip(wavs, script.scenes)]

    # Pass 1 of the timeline gives every scene its duration, which stock clips need.
    draft = tl.build(script.scenes, durations, words, [None] * len(script.scenes))

    clips, media_files, used_ids, used_ai = [], [], set(), False
    with step("media"):
        for sc, item in zip(script.scenes, draft["scenes"]):
            name = None
            if sc.visual == "stock":
                clip = pexels.get_clip(sc.query, item["durationFrames"] / FPS, used_ids)
                clips.append(clip)
                name = f"{sc.id}.mp4"
                media.normalize_clip(clip["path"], PUBLIC_MEDIA / name, item["durationFrames"] / FPS)
            elif sc.visual == "ai_image":
                used_ai = True
                name = f"{sc.id}.jpg"
                shutil.copyfile(cf_images.generate(sc.prompt), PUBLIC_MEDIA / name)
            media_files.append(name)

    with step("timeline+audio"):
        timeline = tl.build(script.scenes, durations, words, media_files)
        (work / "timeline.json").write_text(json.dumps(timeline, indent=1), encoding="utf-8")
        total_sec = tl.build_narration_track(wavs, timeline, work / "narration.wav")
        track = pick_music(script.music, slug)
        print(f"  music: {track.name if track else 'none'}")
        media.mix_audio(work / "narration.wav", track, total_sec, work / "audio_mix.m4a")
        credits.write(work / "credits.txt", clips, track, used_ai)
        print(f"  total video length: {total_sec:.1f}s ({timeline['totalFrames']} frames)")

    if os.environ.get("VOICE_SAMPLES") == "1":  # voice is decided (am_michael); samples are opt-in now
        with step("voice-samples"):
            voice_samples(script, work / "voice_samples")

    (work / "timings_prepare.json").write_text(json.dumps(_timings), encoding="utf-8")


def make_thumbnails(slug: str) -> None:
    script = load_script(ROOT / "episodes" / slug / "script.json")
    with step("thumbnails"):
        thumbnails.make(script, BUILD_DIR / slug / "thumbnails")


def finalize(slug: str) -> None:
    work, out = BUILD_DIR / slug, OUT_DIR / slug
    shutil.rmtree(out, ignore_errors=True)
    with step("mux"):
        media.mux(work / "video.mp4", work / "audio_mix.m4a", out / "final.mp4")
    shutil.copyfile(work / "credits.txt", out / "credits.txt")
    if (work / "thumbnails").exists():
        shutil.copytree(work / "thumbnails", out / "thumbnails")
    if (work / "voice_samples").exists():
        shutil.copytree(work / "voice_samples", out / "voice_samples")
    size = (out / "final.mp4").stat().st_size / 1e6
    print(f"final.mp4: {size:.1f} MB")


if __name__ == "__main__":
    cmd, slug = sys.argv[1], sys.argv[2]
    {"prepare": prepare, "thumbnails": make_thumbnails, "finalize": finalize}[cmd](slug)
