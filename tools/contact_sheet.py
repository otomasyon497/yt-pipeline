"""Storyboard contact sheets: every still with its time, shot and the narration at that moment.

  python tools/contact_sheet.py <storyboard.json> <stills dir> <out dir>
"""
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

COLS, ROWS, W, H, BAR = 4, 4, 480, 270, 46


def font(size: int):
    for name in ("DejaVuSans.ttf", "arial.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def main() -> None:
    items = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    stills, out = Path(sys.argv[2]), Path(sys.argv[3])
    out.mkdir(parents=True, exist_ok=True)
    f_big, f_small = font(17), font(14)
    first = next((p for it in items if (p := stills / f"frame_{it['frame']:05d}.jpg").exists()), None)
    portrait = first is not None and Image.open(first).height > Image.open(first).width  # a Short (9:16)
    cols, rows, w, h = (6, 2, 270, 480) if portrait else (COLS, ROWS, W, H)
    chars = 28 if portrait else 52
    per = cols * rows
    for page in range(0, len(items), per):
        sheet = Image.new("RGB", (cols * w, rows * (h + BAR)), (18, 20, 28))
        draw = ImageDraw.Draw(sheet)
        for k, it in enumerate(items[page:page + per]):
            x, y = (k % cols) * w, (k // cols) * (h + BAR)
            p = stills / f"frame_{it['frame']:05d}.jpg"
            if p.exists():
                sheet.paste(Image.open(p).convert("RGB").resize((w, h)), (x, y))
            draw.text((x + 6, y + h + 3), it["label"][:chars], fill=(245, 166, 35), font=f_big)
            draw.text((x + 6, y + h + 24), it["words"][:chars + 6], fill=(220, 220, 220), font=f_small)
        sheet.save(out / f"storyboard_{page // per + 1:02d}.jpg", quality=82)
    print(f"{len(items)} frames on {(len(items) + per - 1) // per} sheets")


if __name__ == "__main__":
    main()
