"""Measure that music is ducked under narration, using the real pipeline mix_audio().

Synthetic stand-ins: "narration" = 1 kHz tone bursts, "music" = steady 200 Hz + 330 Hz tones.
We decode the mixed output and compare the 200 Hz level inside bursts vs inside silences.
Exit code 1 if the music is not at least MIN_DUCK_DB quieter while narration plays.
"""
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
import soundfile as sf

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "pipeline"))
import media  # noqa: E402

SR = 24000
TOTAL = 24.0
MIN_DUCK_DB = 6.0
BURSTS = [(4, 7), (10, 13), (16, 19)]  # narration on
SPEECH_WINDOWS = [(4.5, 6.8), (10.5, 12.8), (16.5, 18.8)]
SILENCE_WINDOWS = [(8.0, 9.8), (14.0, 15.8), (20.2, 21.4)]  # after the 600 ms release, before the fade-out


def band_db(x: np.ndarray, sr: int, freq: float) -> float:
    spec = np.abs(np.fft.rfft(x * np.hanning(len(x))))
    k = int(freq * len(x) / sr)
    return 20 * np.log10(spec[k - 2:k + 3].max() + 1e-12)


def main() -> int:
    tmp = Path(tempfile.mkdtemp())
    t = np.arange(int(TOTAL * SR)) / SR
    narr = np.zeros_like(t, dtype=np.float32)
    for a, b in BURSTS:
        m = (t >= a) & (t < b)
        narr[m] = 0.1 * np.sin(2 * np.pi * 1000 * t[m])  # about -20 dBFS, like real speech
    sf.write(tmp / "narr.wav", narr, SR, subtype="PCM_16")
    tm = np.arange(10 * SR) / SR
    music = (0.25 * np.sin(2 * np.pi * 200 * tm) + 0.25 * np.sin(2 * np.pi * 330 * tm)).astype(np.float32)
    sf.write(tmp / "music.wav", music, SR, subtype="PCM_16")

    out = tmp / "mix.m4a"
    media.mix_audio(tmp / "narr.wav", tmp / "music.wav", TOTAL, out)
    dec = tmp / "mix.wav"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(out), "-ar", "48000", "-ac", "1", str(dec)], check=True)
    x, sr = sf.read(dec, dtype="float32")

    def level(win):
        a, b = win
        return band_db(x[int(a * sr):int(b * sr)], sr, 200)

    speech = [level(w) for w in SPEECH_WINDOWS]
    silence = [level(w) for w in SILENCE_WINDOWS]
    print("music (200 Hz) level while narration plays :", [f"{v:.1f} dB" for v in speech])
    print("music (200 Hz) level during silences       :", [f"{v:.1f} dB" for v in silence])
    duck = float(np.mean(silence) - np.mean(speech))
    print(f"average ducking: {duck:.1f} dB (required >= {MIN_DUCK_DB})")
    return 0 if duck >= MIN_DUCK_DB else 1


if __name__ == "__main__":
    sys.exit(main())
