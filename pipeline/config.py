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

# Video format: "long" (16:9 documentary) or "short" (9:16 YouTube Short). run.py sets YTP_FORMAT from the
# episode's script.json before any module imports the values below.
FORMAT = os.environ.get("YTP_FORMAT") or "long"
if FORMAT not in ("long", "short"):
    raise ValueError(f"YTP_FORMAT must be 'long' or 'short', not {FORMAT!r}")
SHORT = FORMAT == "short"
SHORT_MAX_SEC = 180  # YouTube files square / vertical uploads up to 3 minutes as Shorts
# Long-form length (the user's requirement, 2026-11-08: 15-20 minutes, consistently). prepare stops outside it.
LONG_MIN_SEC = 15 * 60
LONG_MAX_SEC = 20 * 60 + 30
# Effective pace of a finished long-form episode, pauses and beats included (neom-the-line: 1,354 words in 610 s).
# tools/episode_check.py uses it to estimate the length from a script or an outline before any rendering.
WORDS_PER_SEC = 2.65  # was 2.22 (episode 6); Louisiana ran 2.46 and Kansai 2.74 words a second at speed 1.08
# (2026-11-13: the old value passed a 14.1-minute script as 16.7)
_WORDS_PER_SEC_EP6 = 2.22
# A before/after wipe must finish this long before the next cut (neom 05:38: a stat card cut a wipe in half).
WIPE_CLEAR_SEC = 1.0

# 24 fps is a deliberate render-time optimisation (20% fewer frames than 30 fps).
FPS = 24
WIDTH, HEIGHT = (1080, 1920) if SHORT else (1920, 1080)
UI_SCALE = 1.4 if SHORT else 1.0  # map labels, markers and lines: a Short is watched on a phone held upright

# Layout. Narration flows paragraph by paragraph; shots cut on anchor words and each shot
# is drawn a few frames longer so the next one can dissolve in over it (3B: tighter pacing).
TRANSITION_FRAMES = 8
CARD_TRANSITION_FRAMES = 12  # chapter cards punch in (scale + fade)
LEAD_IN = 0.15 if SHORT else 0.4  # seconds of picture before the first word
PARA_PAUSE = 0.25 if SHORT else 0.38  # after every paragraph (0.45 until 2026-11-04: tighter pace, user)
CHAPTER_PAUSE = 0.6  # extra pause at the end of a chapter (0.75 until 2026-11-04)
CARD_SEC = 1.8  # chapter title card (no narration; 2.4 until 2026-11-05)
CUT_LEAD = 0.1  # cuts land slightly before their anchor word
MIN_SHOT = 1.2  # shortest allowed shot (later anchors are pushed back if needed)
END_PAD = 1.6 if SHORT else 2.5  # after the last word (long: music fade-out; short: room for a closing loop wipe)

CACHE_DIR = Path(os.environ.get("YTP_CACHE_DIR", ROOT / ".cache"))
BUILD_DIR = ROOT / "build"
OUT_DIR = ROOT / "out"
PUBLIC_MEDIA = ROOT / "remotion" / "public" / "media"
MUSIC_DIR = ROOT / "music"

# Voice
DEFAULT_VOICE = "am_michael"
SAMPLE_VOICES = ["bm_george", "am_michael", "am_onyx"]
SAMPLE_MIN_SECONDS = 10.0
PACE_SPEEDS = [1.0, 1.08, 1.15]  # pace samples: the opening narration at each speed (PACE_SAMPLES=1)
PACE_SAMPLE_SECONDS = 40.0
TTS_SPEED = 1.06 if SHORT else 1.08  # long form: 1.08 chosen by ear from the pace samples (2026-11-04)
TTS_SAMPLE_RATE = 24000

# Captions
WHISPER_MODEL = "base.en"

# Maps (3B). Styles: satellite (NASA Blue Marble), atlas (light vector + relief), midnight (dark vector + relief).
MAP_STYLE = os.environ.get("MAP_STYLE") or "satellite"
MAP_STYLES = ("satellite", "atlas", "midnight")
# px kept clear when framing. Long: the bottom holds the captions. Short: the hook line sits on top, and YouTube's own
# title and buttons cover the bottom and the right edge.
MAP_SAFE = ({"left": 60, "right": 150, "top": 300, "bottom": 480} if SHORT else
            {"left": 130, "right": 130, "top": 110, "bottom": 200})
# Map label area. Long: down to just under the framing area. Short: above the captions band (y ~1290-1400 of 1920).
LABEL_INSET = {"left": 40, "top": 400, "right": 150, "bottom": 670} if SHORT else {"left": 24, "top": 24, "right": 24}
MAP_DRIFT = 0.009  # slow push-in per second while the camera holds (keeps maps alive)

# Sound effects (procedural, see sfx.py): peak level in dBFS when the voice sits at -14 LUFS
# (sfx.build_track shifts it by the measured narration loudness, so the balance is independent of the TTS level).
SFX_LEVEL_DB = -17.0

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
