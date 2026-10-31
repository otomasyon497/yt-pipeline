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

# Long-form layout. Narration flows paragraph by paragraph; shots cut on anchor words and each shot
# is drawn TRANSITION_FRAMES longer so the next one can dissolve in over it.
TRANSITION_FRAMES = 10
LEAD_IN = 0.4  # seconds of picture before the first word
PARA_PAUSE = 0.55  # after every paragraph
CHAPTER_PAUSE = 0.9  # extra pause at the end of a chapter
CARD_SEC = 2.6  # chapter title card (no narration)
CUT_LEAD = 0.1  # cuts land slightly before their anchor word
MIN_SHOT = 1.2  # shortest allowed shot (later anchors are pushed back if needed)
END_PAD = 2.5  # after the last word (music fade-out)

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

# Thumbnails (YouTube: 1280x720, JPEG/PNG, < 2 MB)
THUMB_WIDTH = 1280
THUMB_HEIGHT = 720
THUMB_STYLE = "high contrast, dramatic lighting, cinematic, rich colors, no text, no watermark, no logos, no people"
