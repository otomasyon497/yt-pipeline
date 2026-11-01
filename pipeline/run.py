"""Pipeline orchestrator (long-form, script.json v2).

  python pipeline/run.py prepare    <slug>  # TTS, word timings, media, audio mix, timeline.json, youtube.txt
  (remotion render happens as a separate workflow step)
  python pipeline/run.py thumbnails <slug>  # 3 thumbnail variants (needs the Remotion deps)
  python pipeline/run.py finalize   <slug>  # mux audio, collect final.mp4 + youtube.txt + thumbnails in out/<slug>/
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
import maps
import media
import pexels
import pronounce
import sfx
import thumbnails
import timeline as tl
import tts
import youtube_meta
from config import (BUILD_DIR, DEFAULT_VOICE, FPS, MAP_STYLE, MAP_STYLES, MUSIC_DIR, OUT_DIR, PUBLIC_MEDIA, ROOT,
                    SAMPLE_MIN_SECONDS, SAMPLE_VOICES, TTS_SAMPLE_RATE)
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
        print("  no tracks in /music -> narration only")
        return None
    return tracks[int(hashlib.sha1(slug.encode()).hexdigest(), 16) % len(tracks)]


def reading_order(script) -> list[tuple[int, int, object]]:
    """(chapter index, paragraph index, Paragraph) for every paragraph, in narration order."""
    return [(ci, pi, p) for ci, ch in enumerate(script.chapters) for pi, p in enumerate(ch.paragraphs)]


def voice_samples(script, out_dir: Path) -> None:
    """Render ~10 s of the opening narration with each candidate voice (whole paragraphs, no cut-off words)."""
    out_dir.mkdir(parents=True, exist_ok=True)
    texts = [p.text for _, _, p in reading_order(script)]
    for voice in SAMPLE_VOICES:
        parts, total = [], 0.0
        for k, text in enumerate(texts):
            tmp = out_dir / f"_{voice}_{k}.wav"
            total += tts.synth(text, voice, tmp)[0]
            parts.append(sf.read(tmp, dtype="float32")[0])
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
    table = pronounce.load(slug)
    flat = reading_order(script)

    with step("tts"):
        wavs, durs, tts_words = [], [], []
        for ci, pi, para in flat:
            text, used = pronounce.apply(para.text, table)
            wav = work / "audio" / f"c{ci + 1:02d}p{pi + 1:02d}.wav"
            dur, words, phonemes = tts.synth(text, voice, wav)
            wavs.append(wav)
            durs.append(dur)
            tts_words.append(words)
            for key in used:
                ipa = table[key].get("ipa")
                status = "respelled" if ipa is None else "applied" if ipa in phonemes else "NOT applied"
                print(f"  pronunciation {key!r}: {status}")
        print(f"  {len(flat)} paragraphs, {sum(durs):.1f}s of narration")

    with step("word-timings"):
        words, sources = [], {}
        for (_, _, para), wav, tw in zip(flat, wavs, tts_words):
            w, source = captions.word_timings(wav, para.text, tw)
            words.append(w)
            sources[source] = sources.get(source, 0) + 1
        print(f"  word timings from: {sources}")

    def per_chapter(values: list) -> list[list]:
        return [[v for (c, _, _), v in zip(flat, values) if c == ci] for ci in range(len(script.chapters))]

    lay = tl.layout(script, per_chapter(durs), per_chapter(words))

    style = os.environ.get("MAP_STYLE") or script.map_style or MAP_STYLE  # env wins (style reels)
    if style not in MAP_STYLES:
        raise ValueError(f"unknown map style {style!r} (choose from {MAP_STYLES})")
    clips, media_files, used_ids, used_ai = [], {}, set(), False
    sfx_events, extra_credits, map_warnings = [], {"Map data: Natural Earth (public domain)."}, []
    with step("media"):
        for u in lay["units"]:
            src, seconds = u["subs"][0]["src"], u["drawFrames"] / FPS
            if u["kind"] == "map":
                subs = [{"shot": s["src"], "startFrame": s["startFrame"] - u["startFrame"], "frames": s["frames"],
                         "steps": [round(x * FPS) - u["startFrame"] for x in s["steps"]]} for s in u["subs"]]
                res = maps.build_block(u["id"], subs, style, script.captions, u["drawFrames"], PUBLIC_MEDIA)
                media_files[u["id"]] = res["file"]
                sfx_events += [((u["startFrame"] + f) / FPS, kind, gain) for f, kind, gain in res["events"]]
                extra_credits |= res["credits"]
                map_warnings += res["warnings"]
            elif src is None:
                continue
            elif src.type == "stock":
                clip = pexels.get_clip(src.query, seconds, used_ids)
                clips.append(clip)
                media_files[u["id"]] = f"{u['id']}.mp4"
                media.normalize_clip(clip["path"], PUBLIC_MEDIA / media_files[u["id"]], seconds)
            elif src.type == "ai_image":
                used_ai = True
                media_files[u["id"]] = f"{u['id']}.jpg"
                shutil.copyfile(cf_images.generate(src.prompt), PUBLIC_MEDIA / media_files[u["id"]])
        for w in map_warnings:
            print(f"  map warning: {w}")
        print(f"  map style: {style}")

    with step("timeline+audio"):
        timeline = tl.to_timeline(lay, script, media_files, style)
        (work / "timeline.json").write_text(json.dumps(timeline, indent=1), encoding="utf-8")
        total_sec = tl.build_narration_track(wavs, lay, work / "narration.wav")
        effects = None
        if os.environ.get("SFX", "1") != "0":
            effects = work / "sfx.wav"
            n = sfx.build_track(sfx_events + tl.card_sfx(timeline), total_sec, effects)
            print(f"  sound effects: {n} placed")
        track = pick_music(script.music, slug)
        print(f"  music: {track.name if track else 'none'}")
        media.mix_audio(work / "narration.wav", track, total_sec, work / "audio_mix.m4a", effects)
        credits.write(work / "credits.txt", clips, track, used_ai,
                      sorted(extra_credits) if any(u["kind"] == "map" for u in lay["units"]) else [])
        for warning in youtube_meta.write(work / "youtube.txt", script, timeline,
                                          (work / "credits.txt").read_text(encoding="utf-8")):
            print(f"  youtube.txt warning: {warning}")
        print(f"  total video length: {total_sec:.1f}s ({timeline['totalFrames']} frames, "
              f"{len(timeline['shots'])} units from {len(lay['shots'])} shots, {len(timeline['chapters'])} chapters)")

    if os.environ.get("VOICE_SAMPLES") == "1":  # voice is decided (am_michael); samples are opt-in
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
    for name in ("youtube.txt", "credits.txt"):
        shutil.copyfile(work / name, out / name)
    for folder in ("thumbnails", "voice_samples"):
        if (work / folder).exists():
            shutil.copytree(work / folder, out / folder)
    print(f"final.mp4: {(out / 'final.mp4').stat().st_size / 1e6:.1f} MB")


if __name__ == "__main__":
    cmd, slug = sys.argv[1], sys.argv[2]
    {"prepare": prepare, "thumbnails": make_thumbnails, "finalize": finalize}[cmd](slug)
