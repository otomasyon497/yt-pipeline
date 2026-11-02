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

# The format (16:9 long / 9:16 short) sets frame size and pacing in config.py, which every module below reads at
# import time, so take it from the episode's script.json first. An explicit YTP_FORMAT wins; prepare() checks both agree.
if __name__ == "__main__" and len(sys.argv) > 2:
    _script = Path(__file__).resolve().parent.parent / "episodes" / sys.argv[2] / "script.json"
    if _script.exists():
        os.environ.setdefault("YTP_FORMAT", json.loads(_script.read_text(encoding="utf-8")).get("format", "long"))

import numpy as np
import soundfile as sf

import captions
import cf_images
import commons
import credits
import locator
import maps
import media
import music
import pexels
import pixabay
import pronounce
import sentinel
import sfx
import thumbnails
import timeline as tl
import tts
import youtube_meta
from config import (BUILD_DIR, DEFAULT_VOICE, FORMAT, FPS, MAP_STYLE, MAP_STYLES, MUSIC_DIR, OUT_DIR, PUBLIC_MEDIA,
                    ROOT, SAMPLE_MIN_SECONDS, SAMPLE_VOICES, SHORT, SHORT_MAX_SEC, TTS_SAMPLE_RATE)
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
    """A track from /music ("auto" picks one if any exist, or name a file); None -> procedural or silence."""
    if setting in ("none", "procedural"):
        return None
    tracks = sorted(p for p in MUSIC_DIR.glob("*") if p.suffix.lower() in {".mp3", ".wav", ".m4a", ".ogg", ".flac"})
    if setting != "auto":
        named = MUSIC_DIR / setting
        return named if named.exists() else None
    if not tracks:
        print("  no tracks in /music -> narration only")
        return None
    return tracks[int(hashlib.sha1(slug.encode()).hexdigest(), 16) % len(tracks)]


def stock_clip(src, seconds: float, used_ids: set) -> dict:
    """Pexels first (or as requested); Pixabay as the second source when its key is set."""
    # The requested source first, then the other one if it has nothing relevant (a missing clip should not stop a render).
    order = {"pexels": ["pexels", "pixabay"], "pixabay": ["pixabay", "pexels"], "auto": ["pexels", "pixabay"]}[src.source]
    if "pixabay" in order and not os.environ.get("PIXABAY_API_KEY", "").strip():
        order = [o for o in order if o != "pixabay"] or ["pexels"]
    last_error = None
    for name in order:
        try:
            clip = (pexels if name == "pexels" else pixabay).get_clip(src.query, seconds, used_ids)
            clip.setdefault("source", name)
            return clip
        except RuntimeError as exc:
            last_error = exc
    raise last_error


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
    if script.format != FORMAT:
        raise RuntimeError(f"script.json says format {script.format!r} but YTP_FORMAT is {FORMAT!r}")
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
    if SHORT:
        seconds = lay["total_frames"] / FPS
        if seconds > SHORT_MAX_SEC:
            raise ValueError(f"a Short may last {SHORT_MAX_SEC} s at most (longer vertical videos are not Shorts); "
                             f"this one runs {seconds:.1f} s")
        print(f"  short: {seconds:.1f} s")

    style = os.environ.get("MAP_STYLE") or script.map_style or MAP_STYLE  # env wins (style reels)
    if style not in MAP_STYLES:
        raise ValueError(f"unknown map style {style!r} (choose from {MAP_STYLES})")
    clips, media_files, used_ids, used_ai = [], {}, set(), False
    sfx_events, extra_credits, map_warnings = [], {"Map data: Natural Earth (public domain)."}, []
    photo_fit, photo_credits, locs = {}, [], {}
    with step("media"):
        for u in lay["units"]:
            src, seconds = u["subs"][0]["src"], u["drawFrames"] / FPS
            if u["kind"] == "map":
                subs = [{"shot": s["src"], "startFrame": s["startFrame"] - u["startFrame"], "frames": s["frames"],
                         "steps": [round(x * FPS) - u["startFrame"] for x in s["steps"]]} for s in u["subs"]]
                res = maps.build_block(u["id"], subs, style, script.captions, u["drawFrames"], PUBLIC_MEDIA,
                                       ROOT / "episodes" / slug)
                media_files[u["id"]] = res["file"]
                sfx_events += [((u["startFrame"] + f) / FPS, kind, gain) for f, kind, gain in res["events"]]
                extra_credits |= res["credits"]
                map_warnings += res["warnings"]
            elif src is None:
                continue
            elif src.type == "stock":
                clip = stock_clip(src, seconds, used_ids)
                clips.append(clip)
                media_files[u["id"]] = f"{u['id']}.mp4"
                media.normalize_clip(clip["path"], PUBLIC_MEDIA / media_files[u["id"]], seconds)
            elif src.type == "ai_image":
                used_ai = True
                media_files[u["id"]] = f"{u['id']}.jpg"
                shutil.copyfile(cf_images.generate(src.prompt), PUBLIC_MEDIA / media_files[u["id"]])
            elif src.type == "photo":
                path, credit = commons.fetch(src.photo)
                media_files[u["id"]] = f"{u['id']}.jpg"
                photo_fit[u["id"]] = commons.prepare(path, PUBLIC_MEDIA / f"{u['id']}.jpg", PUBLIC_MEDIA / f"{u['id']}_bg.jpg")
                photo_credits.append(credit)
            if src is not None and src.where is not None:
                lon, lat, label, _ = maps.resolve_point(src.where)
                locs[u["id"]] = {"src": f"{u['id']}_loc.png", "label": src.where_label or label or ""}
                locator.make(lon, lat, PUBLIC_MEDIA / locs[u["id"]]["src"])
        card_bg = {}
        for u, nxt in zip(lay["units"], lay["units"][1:]):  # chapter cards over a blurred look at what comes next
            if u["kind"] != "chapter_card" or nxt["id"] not in media_files:
                continue
            if nxt["kind"] == "map":
                card_bg[u["id"]] = locator.card_background(json.loads((PUBLIC_MEDIA / media_files[nxt["id"]]).read_text(encoding="utf-8")))
            elif nxt["kind"] in ("photo", "ai_image"):
                card_bg[u["id"]] = {"src": media_files[nxt["id"]], "left": 0, "top": 0, "width": 1920, "height": 1080, "cover": True}
        for w in map_warnings:
            print(f"  map warning: {w}")
        print(f"  map style: {style}")

    with step("timeline+audio"):
        timeline = tl.to_timeline(lay, script, media_files, style, photo_fit, locs, card_bg)
        (work / "timeline.json").write_text(json.dumps(timeline, indent=1), encoding="utf-8")
        total_sec = tl.build_narration_track(wavs, lay, work / "narration.wav")
        voice_lufs = media.loudness(work / "narration.wav")
        effects = None
        if os.environ.get("SFX", "1") != "0":
            effects = work / "sfx.wav"
            n = sfx.build_track(sfx_events + tl.card_sfx(timeline), total_sec, effects, voice_lufs)
            print(f"  sound effects: {n} placed (narration {voice_lufs:.1f} LUFS)")
        track = pick_music(script.music, slug)
        if track is None and script.music in ("auto", "procedural"):  # own music, one bed per chapter mood
            track = work / "music.wav"
            music.build([(c["startFrame"] / FPS, c["mood"]) for c in timeline["chapters"]], total_sec, track,
                        int(hashlib.sha1(slug.encode()).hexdigest(), 16) % 1000)
        gain = (voice_lufs - music.BED_UNDER_VOICE_DB - media.loudness(track)) if track else 0.0
        print(f"  music: {track.name if track else 'none'}" + (f" ({gain:+.1f} dB, bed {music.BED_UNDER_VOICE_DB} dB under the voice)" if track else ""))
        media.mix_audio(work / "narration.wav", track, total_sec, work / "audio_mix.m4a", effects, music_gain_db=gain)
        if sentinel.credit():  # once, after all map blocks (per-block lines repeated it with fewer years)
            extra_credits.add(sentinel.credit())
        extra = sorted(extra_credits) if any(u["kind"] == "map" for u in lay["units"]) else []
        if photo_credits:
            extra = ["Archive images (Wikimedia Commons):", *[f"- {c}" for c in dict.fromkeys(photo_credits)], ""] + extra
        credits.write(work / "credits.txt", clips, track, used_ai, extra)
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
    if SHORT:
        print("short: no custom thumbnail (YouTube shows a frame of the Short)")
        return
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


def storyboard(slug: str) -> None:
    """Pick one frame per shot (and per map camera stop) for a quick review before the full render."""
    work = BUILD_DIR / slug
    tlj = json.loads((work / "timeline.json").read_text(encoding="utf-8"))
    words = tlj["words"]

    def said(frame: int) -> str:
        near = [w["text"] for w in words if frame - 30 <= w["start"] <= frame + 50]
        return " ".join(near[:10])

    items = []
    for s in tlj["shots"]:
        start, n = s["startFrame"], s["durationFrames"]
        frames = {start + max(s.get("transitionIn", 0) + 4, n // 2 if s["visual"] != "map" else 18)}
        if s["visual"] == "map" and s["media"]:
            block = json.loads((PUBLIC_MEDIA / s["media"]).read_text(encoding="utf-8"))
            frames |= {start + c["start"] + c["frames"] + 6 for c in block["cams"] if c["start"] + c["frames"] + 6 < n}
        for f in sorted(frames):
            if f < tlj["totalFrames"]:
                t = f / tlj["fps"]
                items.append({"frame": f, "label": f"{int(t // 60):02d}:{t % 60:04.1f}  {s['visual']}  {s['id']}",
                              "words": said(f)})
    (work / "storyboard.json").write_text(json.dumps(items, indent=1), encoding="utf-8")
    (work / "storyboard_frames.txt").write_text(",".join(str(i["frame"]) for i in items), encoding="utf-8")
    print(f"storyboard: {len(items)} frames")


if __name__ == "__main__":
    cmd, slug = sys.argv[1], sys.argv[2]
    {"prepare": prepare, "thumbnails": make_thumbnails, "finalize": finalize, "storyboard": storyboard}[cmd](slug)
