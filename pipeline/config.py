"""Global settings for the pipeline."""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def secret(name: str) -> str:
    """Read an env secret, tolerating pasted quotes (straight or curly) and stray whitespace."""
    value = os.environ.get(name, "").strip().strip("\"'“”‘’").strip()
    if not value:
        raise RuntimeError(f"{name} is not set")
    return value

# Video format. 24 fps is a deliberate render-time optimisation (20% fewer frames than 30 fps).
FPS = 24
WIDTH = 1920
HEIGHT = 1080

# Timing (frames). Each scene i occupies [start_i, start_i + duration_i) on the timeline and
# is drawn for TRANSITION_FRAMES longer so the next scene can dissolve in over its tail.
# Narration starts TRANSITION_FRAMES after the scene start, i.e. after the dissolve finished.
TRANSITION_FRAMES = 12
TAIL_FRAMES = 10  # silence after the last word of a scene
END_PAD_FRAMES = 36  # extra time after the final scene (music fade-out)

CACHE_DIR = Path(os.environ.get("YTP_CACHE_DIR", ROOT / ".cache"))
BUILD_DIR = ROOT / "build"
OUT_DIR = ROOT / "out"
PUBLIC_MEDIA = ROOT / "remotion" / "public" / "media"
MUSIC_DIR = ROOT / "music"

# Voice
DEFAULT_VOICE = "am_michael"
SAMPLE_VOICES = ["bm_george", "am_michael", "am_onyx"]
SAMPLE_MIN_SECONDS = 10.0
TTS_SPEED = 0.95
TTS_SAMPLE_RATE = 24000

# Captions
WHISPER_MODEL = "base.en"

# Pexels
PEXELS_BASE = "https://api.pexels.com/v1/videos"
PEXELS_HOURLY_SOFT_LIMIT = 150  # hard API limit is 200/hour; stay well below

# Cloudflare Workers AI
CF_MODEL_PRIMARY = os.environ.get("CF_IMAGE_MODEL", "@cf/black-forest-labs/flux-2-klein-4b")
CF_MODEL_FALLBACK = "@cf/black-forest-labs/flux-1-schnell"
# 1536x864 is exactly 16:9 and costs 3x2 = 6 output tiles (~156 neurons) instead of 12.
CF_IMAGE_WIDTH = 1536
CF_IMAGE_HEIGHT = 864
CF_DAILY_BUDGET_NEURONS = int(os.environ.get("CF_DAILY_BUDGET", "5000"))  # free tier = 10,000/day
CF_STYLE_SUFFIX = (
    "cinematic documentary photograph, 35mm film look, muted color grading, "
    "natural light, no text, no watermark, no logos"
)
