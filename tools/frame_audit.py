"""Second-by-second audit of a finished render, required before any YouTube upload (the user's rule, 2026-11-09).

    python -I tools/frame_audit.py <slug>                    # frames, contact sheets, automatic checks -> <video dir>/audit/
    python -I tools/frame_audit.py <slug> --approve "note"   # after looking at EVERY sheet: records the approval
    python -I tools/frame_audit.py <slug> --approve "note" --accept-flags "why the remaining flags are fine"

Run it with %USERPROFILE%\\.yt-pipeline\\venv (numpy, Pillow). Reads %USERPROFILE%\\Videos\\yt-pipeline\\<slug>\\<slug>.mp4 and,
when the release carried it, timeline.json next to it (shot ids, kinds, on-screen texts and word timings per second).

What it does, from the first second to the last:
1. One frame per second (Remotion's ffmpeg), contact sheets of 30 s (6 x 5) with time, shot id, kind and the words
   spoken at that second under every frame: the visual review looks at every one of them, not only at known problems.
2. Automatic checks: black or blank frames; frozen picture (no change for more than HOLD s); flashes (a jump in
   brightness inside one shot); dark map stretches; soft frames (sharpness far below the video's median); duration against the timeline;
   quote and document cards on screen for less than DOC_MIN s; the same photo used twice within REPEAT_S s; audio
   peaks, clipping, silent gaps and level.
3. audit.json with the video's fingerprint. tools/yt_upload.py refuses a video without an approved audit of that
   exact file, so a re-render needs a new audit.
"""
import argparse
import datetime as dt
import json
import re
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
from video_fingerprint import fingerprint  # noqa: E402  (shared with tools/yt_upload.py)

ROOT = Path(__file__).resolve().parents[1]
FFMPEG = ROOT / "remotion/node_modules/@remotion/compositor-win32-x64-msvc/ffmpeg.exe"
VIDEOS = Path.home() / "Videos" / "yt-pipeline"
TILE_W, TILE_H, BAR, COLS, ROWS = 480, 270, 44, 6, 5  # landscape; vertical Shorts switch to 216 x 384, 10 x 3
HOLD = 8.0  # s without any change -> frozen
DOC_MIN = 3.0  # s a quote / document card must stay on screen
DARK, DARK_RUN = 22.0, 3  # mean brightness (0-255) under DARK for DARK_RUN s on a map -> dark
REPEAT_S = 90.0  # the same photo twice within this many seconds
SOFT = 0.30  # sharpness below this share of the median -> soft


def font(size):
    for name in ("arial.ttf", "DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            pass
    return ImageFont.load_default()


def dims(video: Path) -> tuple[int, int]:
    err = subprocess.run([str(FFMPEG), "-hide_banner", "-i", str(video)], capture_output=True, text=True, errors="replace").stderr
    m = re.search(r"Video:.*?(\d{3,5})x(\d{3,5})", err)
    return (int(m.group(1)), int(m.group(2))) if m else (1920, 1080)


def extract(video: Path, out: Path) -> list[Path]:
    out.mkdir(parents=True, exist_ok=True)
    for old in out.glob("f_*.jpg"):
        old.unlink()
    # -r 1 on the output keeps one frame per second without the fps filter (not in Remotion's ffmpeg build)
    subprocess.run([str(FFMPEG), "-v", "error", "-y", "-i", str(video), "-an", "-r", "1", "-s", f"{TILE_W}x{TILE_H}",
                    "-q:v", "3", str(out / "f_%05d.jpg")], check=True)
    return sorted(out.glob("f_*.jpg"))


def audio(video: Path) -> dict:
    raw = subprocess.run([str(FFMPEG), "-v", "error", "-i", str(video), "-vn", "-ac", "2", "-ar", "16000", "-c:a", "pcm_s16le",
                          "-f", "wav", "-"], capture_output=True).stdout
    raw = raw[raw.find(b"data") + 8:]
    raw = raw[:len(raw) // 4 * 4]
    if not raw:
        return {"error": "no audio stream"}
    a = np.frombuffer(raw, np.int16).reshape(-1, 2).astype(np.float32) / 32768
    m, sr, w = a.mean(1), 16000, 6400  # 0.4 s windows
    n = len(m) // w
    rms = np.sqrt((m[:n * w].reshape(n, w) ** 2).mean(1))
    lvl = 20 * np.log10(np.maximum(rms, 1e-9))
    gaps, start = [], None
    for i, quiet in enumerate(list(lvl < -45) + [False]):
        if quiet and start is None:
            start = i
        if not quiet and start is not None:
            if (i - start) * 0.4 >= 1.6:
                gaps.append([round(start * 0.4, 1), round((i - start) * 0.4, 1)])
            start = None
    active = m[:n * w][np.repeat(lvl > -50, w)]
    return {"seconds": round(len(m) / sr, 2), "peak_dbfs": round(float(20 * np.log10(max(np.abs(a).max(), 1e-9))), 2),
            "clipped_samples": int((np.abs(a) > 0.999).sum()),
            "rms_active_dbfs": round(float(20 * np.log10(max(np.sqrt((active ** 2).mean()) if len(active) else 0, 1e-9))), 1),
            "silent_gaps": gaps}


def sharpness(g: np.ndarray) -> float:
    lap = 4 * g[1:-1, 1:-1] - g[:-2, 1:-1] - g[2:, 1:-1] - g[1:-1, :-2] - g[1:-1, 2:]
    return float(lap.var())


def mmss(t: float) -> str:
    return f"{int(t // 60)}:{int(t % 60):02d}"


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("slug")
    ap.add_argument("--video")
    ap.add_argument("--approve", help="record that every contact sheet was looked at; give a short note")
    ap.add_argument("--accept-flags", help="why the remaining automatic flags are fine (required to approve with flags)")
    a = ap.parse_args()
    folder = VIDEOS / a.slug
    video = Path(a.video) if a.video else folder / f"{a.slug}.mp4"
    out = folder / "audit"
    report_json = out / "audit.json"

    if a.approve:
        if not report_json.exists():
            sys.exit("No audit yet: run the audit first, then look at every sheet.")
        rep = json.loads(report_json.read_text(encoding="utf-8"))
        if rep["fingerprint"] != fingerprint(video):
            sys.exit("The video changed since the audit: run the audit again.")
        if rep["flags"] and not a.accept_flags:
            sys.exit(f"{len(rep['flags'])} automatic flag(s) open (see {out / 'report.md'}): fix them, or pass --accept-flags with the reason.")
        rep.update(approved=True, approved_at=dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
                   note=a.approve, accepted_flags=a.accept_flags)
        report_json.write_text(json.dumps(rep, indent=1, ensure_ascii=False), encoding="utf-8")
        print(f"Approved: {video.name} ({len(rep['sheets'])} sheets reviewed). Upload is unlocked for this exact file.")
        return

    if not video.exists():
        sys.exit(f"Missing {video}")
    tl_path = video.parent / "timeline.json"
    tl = json.loads(tl_path.read_text(encoding="utf-8")) if tl_path.exists() else None
    fps = tl["fps"] if tl else 24
    shots = sorted(tl["shots"], key=lambda s: s["startFrame"]) if tl else []
    words = tl["words"] if tl else []

    def shot_at(t):
        f = t * fps
        cur = None
        for s in shots:
            if s["startFrame"] <= f:
                cur = s
            else:
                break
        return cur

    def words_at(t):
        f0, f1 = (t - 1.2) * fps, (t + 1.2) * fps
        return " ".join(w["text"] for w in words if f0 <= w["start"] <= f1)

    global TILE_W, TILE_H, COLS, ROWS
    vw, vh = dims(video)
    if vh > vw:
        TILE_W, TILE_H, COLS, ROWS = 216, 384, 10, 3
    print(f"{video.name}: {vw}x{vh}, extracting one frame per second ...", flush=True)
    frames = extract(video, out / "frames")
    flags = []
    grays, lum, sharp = [], [], []
    for p in frames:
        g = np.asarray(Image.open(p).convert("L"), dtype=np.float32)
        grays.append(g[::2, ::2])
        lum.append(float(g.mean()))
        sharp.append(sharpness(g))
    med_sharp = float(np.median(sharp)) if sharp else 0
    n = len(frames)

    # 1. black / blank frames (the first and last second may fade)
    for i in range(1, max(1, n - 1)):
        if lum[i] < 10 and float(grays[i].std()) < 5:
            flags.append({"t": i, "kind": "black", "detail": f"mean luma {lum[i]:.0f}"})
    # 2. frozen picture
    run = 0
    for i in range(1, n):
        if float(np.abs(grays[i] - grays[i - 1]).mean()) < 0.6:
            run += 1
            if run + 1 == int(HOLD) + 1:
                flags.append({"t": i - run, "kind": "frozen", "detail": f"no visible change for more than {HOLD:.0f} s"})
        else:
            run = 0
    # 3. flashes inside one shot
    for i in range(1, n):
        s0, s1 = shot_at(i - 1), shot_at(i)
        if abs(lum[i] - lum[i - 1]) > 70 and (not tl or (s0 and s1 and s0["id"] == s1["id"])):
            flags.append({"t": i, "kind": "flash", "detail": f"brightness {lum[i - 1]:.0f} -> {lum[i]:.0f} inside one shot"})
    # 4. soft frames (maps flying through coarse imagery, upscaled photos)
    for i in range(n):
        if med_sharp and sharp[i] < SOFT * med_sharp and lum[i] > 25:
            s = shot_at(i)
            flags.append({"t": i, "kind": "soft", "detail": f"sharpness {sharp[i] / med_sharp:.2f} of median"
                          + (f" ({s['visual']} {s['id']})" if s else "")})
    # 4b. dark stretches: map pictures the eye cannot read (Louisiana 12:33, six seconds of near-black marsh)
    run = 0
    for i in range(n + 1):
        s = shot_at(i) if i < n else None
        if i < n and lum[i] < DARK and (not tl or (s and s["visual"] == "map")):
            run += 1
            continue
        if run >= DARK_RUN:
            flags.append({"t": i - run, "kind": "dark", "detail": f"{run} s under brightness {DARK:.0f} (mean {np.mean(lum[i - run:i]):.0f})"})
        run = 0
    # 5. duration, document cards, repeated photos (timeline)
    if tl:
        want = tl["totalFrames"] / fps
        if abs(want - n) > 1.5:
            flags.append({"t": 0, "kind": "duration", "detail": f"video {n} s, timeline {want:.1f} s"})
        for k, s in enumerate(shots):
            if s["visual"] == "document":
                end = shots[k + 1]["startFrame"] if k + 1 < len(shots) else tl["totalFrames"]
                on = (end - s["startFrame"]) / fps
                if on < DOC_MIN:
                    flags.append({"t": round(s["startFrame"] / fps), "kind": "document", "detail": f"{s['id']} on screen {on:.1f} s"})
        seen = {}
        for s in shots:
            m = s.get("media")
            key = m if isinstance(m, str) else (json.dumps(m, sort_keys=True) if m and s["visual"] in ("photo", "film") else None)
            if not key or s["visual"] not in ("photo", "film"):
                continue
            t = s["startFrame"] / fps
            if key in seen and t - seen[key][0] < REPEAT_S:
                flags.append({"t": round(t), "kind": "repeat", "detail": f"{s['id']} shows the same {s['visual']} as {seen[key][1]} "
                              f"{t - seen[key][0]:.0f} s earlier"})
            seen[key] = (t, s["id"])
    # 6. audio
    au = audio(video)
    if "error" in au:
        flags.append({"t": 0, "kind": "audio", "detail": au["error"]})
    else:
        if au["clipped_samples"]:
            flags.append({"t": 0, "kind": "audio", "detail": f"{au['clipped_samples']} clipped samples"})
        if au["peak_dbfs"] > -0.3:
            flags.append({"t": 0, "kind": "audio", "detail": f"peak {au['peak_dbfs']} dBFS"})
        if not -24 <= au["rms_active_dbfs"] <= -14:
            flags.append({"t": 0, "kind": "audio", "detail": f"speech level {au['rms_active_dbfs']} dBFS (expected about -18)"})
        for start, length in au["silent_gaps"]:
            if 1 < start < au["seconds"] - 3:
                flags.append({"t": round(start), "kind": "silence", "detail": f"{length} s without sound"})

    # contact sheets: every second, with what the timeline says is on screen and being said
    f_small, f_time = font(15), font(22)
    sheets = []
    per = COLS * ROWS
    flagged = {}
    for fl in flags:
        flagged.setdefault(int(fl["t"]), []).append(fl["kind"])
    for k in range(0, n, per):
        im = Image.new("RGB", (COLS * TILE_W, ROWS * (TILE_H + BAR)), (12, 12, 12))
        d = ImageDraw.Draw(im)
        for j, p in enumerate(frames[k:k + per]):
            t = k + j
            x, y = (j % COLS) * TILE_W, (j // COLS) * (TILE_H + BAR)
            im.paste(Image.open(p), (x, y))
            s = shot_at(t)
            head = f"{mmss(t)}  {s['id']} {s['visual']}" if s else mmss(t)
            box_col = (200, 30, 30) if t in flagged else (0, 0, 0)
            d.rectangle([x, y, x + min(210, TILE_W), y + 28], fill=box_col)
            d.text((x + 5, y + 3), head[:26], fill=(255, 220, 0), font=f_time if not s else f_small)
            if t in flagged:
                d.text((x + 5, y + TILE_H - 22), "FLAG: " + ", ".join(flagged[t]), fill=(255, 80, 80), font=f_small)
            say = words_at(t) if words else ""
            cut = 62 if TILE_W >= 400 else 26
            d.text((x + 5, y + TILE_H + 4), say[:cut], fill=(230, 230, 230), font=f_small)
            d.text((x + 5, y + TILE_H + 22), say[cut:2 * cut], fill=(230, 230, 230), font=f_small)
        name = f"sheet_{k // per + 1:02d}_{mmss(k).replace(':', 'm')}s.jpg"
        im.save(out / name, quality=82)
        sheets.append(name)

    rep = {"slug": a.slug, "video": video.name, "fingerprint": fingerprint(video), "seconds": n,
           "audited_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"), "timeline": bool(tl),
           "median_sharpness": round(med_sharp, 1), "audio": au, "flags": flags, "sheets": sheets,
           "approved": False, "approved_at": None, "note": None}
    report_json.write_text(json.dumps(rep, indent=1, ensure_ascii=False), encoding="utf-8")
    lines = [f"# Frame audit: {video.name}", "", f"{n} s, one frame per second, {len(sheets)} sheets of {per} s in {out}.",
             f"Timeline: {'yes' if tl else 'no (shot ids and words not shown)'}. Audio: {au}", "",
             "## Automatic flags", ""]
    lines += [f"- {mmss(fl['t'])} {fl['kind']}: {fl['detail']}" for fl in flags] or ["None."]
    lines += ["", "## Visual review (fill in while looking at every sheet)", ""] + [f"- [ ] {s}" for s in sheets]
    (out / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines[:8 + len(flags)]))
    print(f"\nNext: look at all {len(sheets)} sheets in {out}, fix what is wrong, then --approve.")


if __name__ == "__main__":
    main()
