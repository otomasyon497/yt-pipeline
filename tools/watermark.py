"""YouTube video watermark for "Ink & Orbit": the profile picture's idea in flat shapes, on a transparent background.

The profile picture's photo globe turns to mud at the size a watermark plays at, so this one is drawn: a disc split by
the amber wipe line (paper with ink lines | orbit blue), the amber orbit ring and the satellite. A navy edge keeps it
readable over bright and dark footage. Needs only Pillow.
Usage: python tools/watermark.py <out.png> [--preview <frame.png> ... --sheet <sheet.jpg>]
"""
import argparse
import math
from pathlib import Path

from PIL import Image, ImageDraw

NAVY, CREAM, AMBER = (11, 15, 26), (244, 241, 234), (245, 166, 35)  # remotion/src/theme.ts
INK, BLUE = (24, 32, 52), (38, 104, 186)
SIZE, K = 600, 4
N = SIZE * K
C = N / 2
R = 0.335 * N  # globe
RX, RY, TILT = 0.462 * N, 0.135 * N, -20.0  # orbit ring (tilt in degrees)
RING, EDGE = 0.042 * N, 0.018 * N  # ring width, navy edge


def disc(radius: float) -> Image.Image:
    m = Image.new("L", (N, N), 0)
    ImageDraw.Draw(m).ellipse((C - radius, C - radius, C + radius, C + radius), fill=255)
    return m


def ring(width: float) -> Image.Image:
    m = Image.new("L", (N, N), 0)
    w = round(width)
    ImageDraw.Draw(m).ellipse((C - RX - w / 2, C - RY - w / 2, C + RX + w / 2, C + RY + w / 2), outline=255, width=w)
    return m.rotate(-TILT, resample=Image.BICUBIC, center=(C, C))


def half_plane(front: bool) -> Image.Image:
    """The ring's lower half passes in front of the globe, the upper half behind it."""
    m = Image.new("L", (N, N), 0)
    d = ImageDraw.Draw(m)
    a = math.radians(TILT)
    ux, uy = math.cos(a), math.sin(a)
    nx, ny = -uy, ux  # towards the viewer's lower side of the tilted ring
    if not front:
        nx, ny = -nx, -ny
    L = 2 * N
    d.polygon([(C + ux * L, C + uy * L), (C - ux * L, C - uy * L),
               (C - ux * L + nx * L, C - uy * L + ny * L), (C + ux * L + nx * L, C + uy * L + ny * L)], fill=255)
    return m


def masked(a: Image.Image, b: Image.Image) -> Image.Image:
    return Image.composite(a, Image.new("L", (N, N), 0), b)


def draw() -> Image.Image:
    img = Image.new("RGBA", (N, N), (*NAVY, 0))
    front, back = half_plane(True), half_plane(False)

    def paint(color, mask):
        img.paste((*color, 255), (0, 0), mask)

    # behind the globe
    paint(NAVY, masked(ring(RING + 2 * EDGE), back))
    paint(AMBER, masked(ring(RING), back))

    # the globe: paper with ink lines on the left, orbit blue on the right
    paint(NAVY, disc(R + EDGE))
    left = Image.new("L", (N, N), 0)
    ImageDraw.Draw(left).rectangle((0, 0, C, N), fill=255)
    right = Image.new("L", (N, N), 0)
    ImageDraw.Draw(right).rectangle((C, 0, N, N), fill=255)
    paint(BLUE, masked(disc(R), right))
    paper = Image.new("RGBA", (N, N), (*CREAM, 255))
    d = ImageDraw.Draw(paper)
    w = round(0.016 * N)
    for k in (0.42, 0.8):  # meridians: half ellipses opening towards the wipe line
        d.ellipse((C - R * k, C - R, C + R * k, C + R), outline=INK, width=w)
    for dy in (-0.42, 0.42):  # parallels
        y = C + dy * R
        d.line((C - R, y, C, y), fill=INK, width=w)
    img.paste(paper, (0, 0), masked(disc(R), left))

    # the wipe line
    bar = 0.024 * N
    over = R + 0.055 * N
    edge = Image.new("L", (N, N), 0)
    ImageDraw.Draw(edge).rounded_rectangle((C - bar - EDGE, C - over - EDGE, C + bar + EDGE, C + over + EDGE), radius=bar + EDGE, fill=255)
    paint(NAVY, edge)
    line = Image.new("L", (N, N), 0)
    ImageDraw.Draw(line).rounded_rectangle((C - bar, C - over, C + bar, C + over), radius=bar, fill=255)
    paint(AMBER, line)

    # in front of the globe
    paint(NAVY, masked(ring(RING + 2 * EDGE), front))
    paint(AMBER, masked(ring(RING), front))

    # the satellite, on the ring's upper right
    t = math.radians(-11)  # far enough from the globe that the arc between them reads as ring, not as a stray bit
    a = math.radians(TILT)
    ex, ey = RX * math.cos(t), RY * math.sin(t)
    sx, sy = C + ex * math.cos(a) - ey * math.sin(a), C + ex * math.sin(a) + ey * math.cos(a)
    for color, r in ((NAVY, 0.058 * N), (CREAM, 0.04 * N)):
        d = ImageDraw.Draw(img)
        d.ellipse((sx - r, sy - r, sx + r, sy + r), fill=(*color, 255))
    return img.resize((SIZE, SIZE), Image.LANCZOS)


def sheet(mark: Image.Image, frames: list[Path], out: Path) -> None:
    """Each frame at 1280 wide with the mark in the corner at three sizes, plus 1:1 crops of the corners."""
    rows = []
    for f in frames:
        fr = Image.open(f).convert("RGB")
        fr = fr.resize((1280, fr.height * 1280 // fr.width), Image.LANCZOS)
        row = Image.new("RGB", (1280 + 3 * 200, fr.height), (40, 40, 40))
        row.paste(fr, (0, 0))
        base = fr.copy()
        for i, px in enumerate((48, 64, 96)):
            m = mark.resize((px, px), Image.LANCZOS)
            pad = 16
            pos = (1280 - px - pad, fr.height - px - pad)
            tile = base.copy()
            tile.paste(m, pos, m)
            if i == 1:
                row.paste(tile, (0, 0))
            crop = tile.crop((1280 - 200, fr.height - 200, 1280, fr.height))
            row.paste(crop, (1280 + i * 200, fr.height - 200))
        rows.append(row)
    s = Image.new("RGB", (rows[0].width, sum(r.height for r in rows)))
    y = 0
    for r in rows:
        s.paste(r, (0, y))
        y += r.height
    s.save(out, quality=92)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("out", type=Path)
    ap.add_argument("--preview", nargs="*", type=Path, default=[])
    ap.add_argument("--sheet", type=Path)
    args = ap.parse_args()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    mark = draw()
    mark.save(args.out, optimize=True)
    print(args.out, mark.size, f"{args.out.stat().st_size / 1000:.0f} KB")
    if args.preview and args.sheet:
        sheet(mark, args.preview, args.sheet)
