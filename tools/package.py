"""Packaging set for a long video: three covers for YouTube's Test & Compare, title candidates linted against them,
and one sheet that shows everything at the size a phone shows it (user's decision 2026-11-23, CTR 1.9 %).

    %USERPROFILE%\\.yt-pipeline\\venv\\Scripts\\python.exe tools/package.py <slug>

episodes/<slug>/cover_photo.json is cover A (see tools/cover_photo.py). Its optional "variants" list holds covers B
and C as overrides of A: a different photo, other words, other colours. Every variant must still be something the
video shows (honest covers). Titles come from script.json youtube.title (the one uploaded) plus
youtube.title_candidates; each is linted with .claude/skills/yt-package/title.py against every cover's words.

    "variants": [{"photo": "File:....jpg", "focus": [0.5, 0.5], "lines": [{"t": "...", "color": "yellow"}]},
                 {"lines": [...], "text_at": [0.55, 0.06]}]

Writes to %USERPROFILE%\\Videos\\yt-pipeline\\<slug>\\: cover_A.jpg, cover_B.jpg, cover_C.jpg, cover.jpg (= A, the one
yt_upload.py sets), package_sheet.jpg and package.txt (the titles and what to upload in Studio's Test & Compare).
"""
import importlib.util
import json
import shutil
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import cover_photo  # noqa: E402

spec = importlib.util.spec_from_file_location("title_lint", ROOT / ".claude" / "skills" / "yt-package" / "title.py")
title_lint = importlib.util.module_from_spec(spec)
spec.loader.exec_module(title_lint)

FEED = (360, 202)    # a phone's home feed, full width
SIDE = (168, 94)     # suggested videos next to / under the player


def covers(cfg: dict) -> list[dict]:
    base = {k: v for k, v in cfg.items() if k != "variants"}
    return [base] + [{**base, **v} for v in cfg.get("variants", [])][:2]


def words(c: dict) -> str:
    return " ".join(ln["t"] for ln in c["lines"])


def sheet(imgs: list[Image.Image], labels: list[str], titles: list[str]) -> Image.Image:
    pad, colw = 24, 640
    f = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 22) if Path("C:/Windows/Fonts/segoeui.ttf").exists() \
        else ImageFont.load_default()
    rows_h = 40 + 360 + FEED[1] + 2 * pad
    th = 34 * len(titles) + pad
    out = Image.new("RGB", (pad + len(imgs) * (colw + pad), rows_h + th), (24, 24, 28))
    d = ImageDraw.Draw(out)
    for i, (im, lab) in enumerate(zip(imgs, labels)):
        x = pad + i * (colw + pad)
        d.text((x, 8), lab, fill=(240, 240, 240), font=f)
        out.paste(im.resize((colw, 360), Image.LANCZOS), (x, 40))
        out.paste(im.resize(FEED, Image.LANCZOS), (x, 40 + 360 + pad))
        out.paste(im.resize(SIDE, Image.LANCZOS), (x + FEED[0] + pad, 40 + 360 + pad))
        d.text((x + FEED[0] + pad, 40 + 360 + pad + SIDE[1] + 6), "168 px", fill=(150, 150, 150), font=f)
    y = rows_h
    for t in titles:
        d.text((pad, y), t, fill=(230, 230, 230), font=f)
        y += 34
    return out


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    slug = sys.argv[1]
    ep = ROOT / "episodes" / slug
    cfg = json.loads((ep / "cover_photo.json").read_text(encoding="utf-8"))
    yt = json.loads((ep / "script.json").read_text(encoding="utf-8")).get("youtube", {})
    titles = [yt["title"]] + [t for t in yt.get("title_candidates", []) if t != yt.get("title")]
    out = cover_photo.VIDEOS / slug
    out.mkdir(parents=True, exist_ok=True)
    cs = covers(cfg)
    imgs, labels = [], []
    for name, c in zip("ABC", cs):
        im = cover_photo.build(c)
        im.save(out / f"cover_{name}.jpg", quality=92)
        imgs.append(im)
        labels.append(f"{name}: {words(c)}")
    shutil.copyfile(out / "cover_A.jpg", out / "cover.jpg")
    report, lines = [], []
    for t in titles:
        rs = [title_lint.check(t, words(c)) for c in cs]
        best = max(rs, key=lambda r: r["score"])
        issues = [k for k, _ in best["issues"]]
        lines.append(f"{best['score']:>3}  {t}  ({len(t)} ch, best with cover {'ABC'[rs.index(best)]})  "
                     f"issues: {', '.join(issues) or 'none'}")
        report.append((best["score"], t, rs))
    sheet(imgs, labels, lines).save(out / "package_sheet.jpg", quality=88)
    txt = [f"PACKAGE {slug}", "", "Covers (Studio > the video > Thumbnail > Test & Compare: upload all three):"]
    txt += [f"  cover_{n}.jpg  {lab[3:]}" for n, lab in zip("ABC", labels)]
    txt += ["", "Titles (score with the best cover; uploaded title first):"] + [f"  {ln}" for ln in lines]
    for _, t, rs in report:
        dup = [f"{n}" for n, r in zip("ABC", rs) if any(k == "duplicate" for k, _ in r["issues"])]
        if dup:
            txt.append(f"  ! '{t}' repeats words of cover {', '.join(dup)}")
    if len(cs) < 3:
        txt.append(f"  ! only {len(cs)} cover(s): add 'variants' to cover_photo.json")
    (out / "package.txt").write_text("\n".join(txt) + "\n", encoding="utf-8")
    print("\n".join(txt))
    print(f"\nsheet: {out / 'package_sheet.jpg'}")


if __name__ == "__main__":
    main()
