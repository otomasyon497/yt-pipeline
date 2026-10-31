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


def mix_audio(narration_wav: Path, music: Path | None, total_sec: float, out_m4a: Path) -> None:
    """Narration (+ optional music ducked under it), fade-out, loudness-normalised to about -14 LUFS."""
    fade = f"afade=t=out:st={max(total_sec - 2.5, 0):.2f}:d=2.5,loudnorm=I=-14:TP=-1.5:LRA=11"
    if music is None:
        run(["ffmpeg", "-y", "-loglevel", "error", "-i", narration_wav, "-af", fade, "-ar", 48000,
             "-c:a", "aac", "-b:a", "192k", out_m4a])
        return
    graph = (
        "[1:a]volume=0.9,afade=t=in:d=2[m0];"
        "[0:a]asplit=2[n][sc];"
        "[m0][sc]sidechaincompress=threshold=0.02:ratio=10:attack=30:release=600[md];"
        "[md]volume=0.5[mv];"
        "[n][mv]amix=inputs=2:duration=first:dropout_transition=0:normalize=0[mx];"
        f"[mx]{fade}[out]"
    )
    run(["ffmpeg", "-y", "-loglevel", "error", "-i", narration_wav, "-stream_loop", "-1", "-i", music,
         "-filter_complex", graph, "-map", "[out]", "-t", f"{total_sec:.3f}", "-ar", 48000,
         "-c:a", "aac", "-b:a", "192k", out_m4a])


def mux(video: Path, audio: Path, out: Path) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    run(["ffmpeg", "-y", "-loglevel", "error", "-i", video, "-i", audio, "-map", "0:v:0", "-map", "1:a:0",
         "-c:v", "copy", "-c:a", "copy", "-shortest", "-movflags", "+faststart", out])
