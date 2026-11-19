"""Make instrumental music beds with ACE-Step 1.5 (MIT code and weights), for music/library/<mood>/.

Runs inside an ACE-Step checkout (the music_gen workflow clones it, pinned):
    python tools/music_gen.py --ace /path/to/ACE-Step-1.5 --out out/music --moods calm,curious,tension --seconds 150 --per-mood 2

DiT only (no language model, no lyrics): a caption per mood describes a documentary underscore. CPU works but is slow;
the workflow has hours. The beds are only candidates: listen to them, keep the good ones in music/library/<mood>/
(as .ogg) and they are used by episodes with "music": "library" (pipeline/music.py build_library).
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

CAPTIONS = {
    "calm": ("instrumental ambient documentary underscore, soft felt piano, warm sustained strings, gentle pads, "
             "slow and spacious, reflective, no drums, no vocals", 70, "A minor"),
    "curious": ("instrumental light documentary underscore, plucked strings and marimba ostinato, soft synth pads, "
                "curious and hopeful, steady gentle pulse, no vocals", 96, "D major"),
    "tension": ("instrumental dark cinematic documentary underscore, low string ostinato, pulsing synth bass, "
                "soft ticking percussion, distant booms, rising suspense, no vocals", 84, "D minor"),
}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ace", required=True, help="ACE-Step 1.5 checkout (project root)")
    ap.add_argument("--out", required=True)
    ap.add_argument("--moods", default="calm,curious,tension")
    ap.add_argument("--seconds", type=float, default=150.0)
    ap.add_argument("--per-mood", type=int, default=2)
    ap.add_argument("--steps", type=int, default=8)
    a = ap.parse_args()

    ace = Path(a.ace).resolve()
    out = Path(a.out).resolve()  # before the chdir below: a relative --out is meant from the caller's folder
    sys.path.insert(0, str(ace))
    os.chdir(ace)
    from acestep.handler import AceStepHandler  # noqa: E402
    from acestep.inference import GenerationConfig, GenerationParams, generate_music  # noqa: E402
    from acestep.llm_inference import LLMHandler  # noqa: E402

    out.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    dit = AceStepHandler()
    msg, ok = dit.initialize_service(project_root=str(ace), config_path="acestep-v15-turbo", device="cpu",
                                     offload_to_cpu=False)
    print(f"DiT init ({time.time() - t0:.0f}s): {msg}", flush=True)
    if not ok:
        sys.exit(1)
    llm = LLMHandler()  # not initialised: DiT-only generation (thinking off)

    log = []
    for mood in [m.strip() for m in a.moods.split(",") if m.strip()]:
        caption, bpm, key = CAPTIONS[mood]
        for k in range(a.per_mood):
            seed = 1000 * (list(CAPTIONS).index(mood) + 1) + k
            params = GenerationParams(task_type="text2music", caption=caption, lyrics="", instrumental=True,
                                      bpm=bpm, keyscale=key, duration=a.seconds, inference_steps=a.steps,
                                      seed=seed, thinking=False, use_cot_caption=False, use_cot_language=False,
                                      shift=3.0)
            config = GenerationConfig(batch_size=1, audio_format="wav", use_random_seed=False, seeds=[seed])
            t1 = time.time()
            res = generate_music(dit, llm, params=params, config=config, save_dir=str(out / "raw"))
            took = time.time() - t1
            if not res.success:
                print(f"{mood} #{k}: FAILED after {took:.0f}s: {res.status_message}", flush=True)
                log.append({"mood": mood, "seed": seed, "ok": False, "error": str(res.status_message)})
                continue
            src = Path(res.audios[0]["path"])
            dst = out / mood / f"ace-{mood}-{seed}.ogg"
            dst.parent.mkdir(parents=True, exist_ok=True)
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(src), "-af", "afade=t=in:d=1.5",
                            "-c:a", "libvorbis", "-q:a", "6", str(dst)], check=True)
            print(f"{mood} #{k}: {dst.name} ({took:.0f}s)", flush=True)
            log.append({"mood": mood, "seed": seed, "ok": True, "file": dst.name, "seconds": round(took),
                        "caption": caption, "bpm": bpm, "key": key, "model": "acestep-v15-turbo"})
    shutil.rmtree(out / "raw", ignore_errors=True)
    (out / "music_gen.json").write_text(json.dumps(log, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
