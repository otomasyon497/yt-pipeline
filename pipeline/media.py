"""ffmpeg helpers: normalise stock clips and mix the final audio."""
import subprocess
from pathlib import Path

from config import FPS, HEIGHT, WIDTH


def run(cmd: list) -> None:
    r = subprocess.run([str(c) for c in cmd], capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"ffmpeg failed ({r.returncode}):\n{r.stderr[-1500:]}")


def normalize_clip(src: Path, dst: Path, seconds: float) -> None:
    """Trim/loop `src` to exactly `seconds`, cover-crop to 1920x1080 at project fps, strip audio.

    Looping (-stream_loop) is only exercised when the stock clip is shorter than the scene.
    """
    dst.parent.mkdir(parents=True, exist_ok=True)
    vf = f"scale={WIDTH}:{HEIGHT}:force_original_aspect_ratio=increase,crop={WIDTH}:{HEIGHT},fps={FPS},setsar=1"
    run(["ffmpeg", "-y", "-loglevel", "error", "-stream_loop", "-1", "-i", src, "-t", f"{seconds:.3f}",
         "-vf", vf, "-an", "-c:v", "libx264", "-preset", "ultrafast", "-crf", "18", "-pix_fmt", "yuv420p", dst])


def mix_audio(narration_wav: Path, music: Path | None, total_sec: float, out_m4a: Path, sfx_wav: Path | None = None) -> None:
    """Narration (+ optional music ducked under it, + optional sound effects), fade-out, about -14 LUFS.

    Input order: 0 = narration, 1 = sfx (if any), then music (looped). Effects are not ducked: they are
    short and placed on visual events, at a fixed level under the voice (see sfx.py).
    """
    fade = f"afade=t=out:st={max(total_sec - 2.5, 0):.2f}:d=2.5,loudnorm=I=-14:TP=-1.5:LRA=11"
    inputs = ["-i", narration_wav]
    parts = ["[0:a]aresample=48000[n0]"]
    voice = "[n0]"
    if sfx_wav is not None:
        inputs += ["-i", sfx_wav]
        parts.append("[1:a]aresample=48000[fx]")
    if music is not None:
        m = 2 if sfx_wav is not None else 1
        inputs += ["-stream_loop", "-1", "-i", music]
        parts += [
            f"[{m}:a]aresample=48000,volume=0.9,afade=t=in:d=2[m0]",
            "[n0]asplit=2[n][sc]",
            "[m0][sc]sidechaincompress=threshold=0.02:ratio=10:attack=30:release=600[md]",
            "[md]volume=0.5[mv]",
        ]
        voice = "[n]"
    beds = ([voice] + (["[fx]"] if sfx_wav is not None else []) + (["[mv]"] if music is not None else []))
    if len(beds) > 1:
        parts.append(f"{''.join(beds)}amix=inputs={len(beds)}:duration=first:dropout_transition=0:normalize=0[mx]")
        parts.append(f"[mx]{fade}[out]")
    else:
        parts.append(f"{voice}{fade}[out]")
    run(["ffmpeg", "-y", "-loglevel", "error", *inputs, "-filter_complex", ";".join(parts), "-map", "[out]",
         "-t", f"{total_sec:.3f}", "-ar", 48000, "-c:a", "aac", "-b:a", "192k", out_m4a])


def mux(video: Path, audio: Path, out: Path) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    run(["ffmpeg", "-y", "-loglevel", "error", "-i", video, "-i", audio, "-map", "0:v:0", "-map", "1:a:0",
         "-c:v", "copy", "-c:a", "copy", "-shortest", "-movflags", "+faststart", out])
