"""Document shots: a page of a public-domain PDF with the key line found and marked, or our own clipping card.

Only documents we may show in full belong here: U.S. federal government works are public domain (17 U.S.C. 105),
e.g. Interior's Records of Decision or Reclamation's studies. News articles and other copyrighted pages are not
screenshotted: quote a short line on a clipping card (`text`) with its source instead.
Rendering: pypdfium2 (Apache-2.0 / BSD-3, PDFium), page at about 1600 px wide; the highlight is searched in the page's
text layer and returned as line boxes in page fractions.
"""
import hashlib
import re
import time
from pathlib import Path

import requests

from config import CACHE_DIR

UA = {"User-Agent": "yt-pipeline/1.0 (https://github.com/otomasyon497/yt-pipeline)"}
PAGE_PX = 1600  # rendered page width


def _pdf(url: str) -> Path:
    path = CACHE_DIR / "documents" / f"{hashlib.sha1(url.encode()).hexdigest()}.pdf"
    if path.exists():
        return path
    for attempt in range(4):
        try:
            r = requests.get(url, headers=UA, timeout=120)
            r.raise_for_status()
            break
        except requests.RequestException:
            if attempt == 3:
                raise
            time.sleep(3 * (attempt + 1))
    if not r.content.startswith(b"%PDF"):
        raise ValueError(f"not a PDF: {url}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(r.content)
    return path


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", s.replace("­", "").replace("’", "'")).strip().lower()


def page_with_highlight(url: str, page_no: int, highlight: str | None, out_png: Path) -> dict:
    """Render page `page_no` (1-based) to `out_png`; return {"aspect": h/w, "rects": [[x0, y0, x1, y1], ...]} with one
    box per text line of the highlight, in fractions of the page (top-left origin)."""
    import pypdfium2 as pdfium  # local import: only episodes with document shots need it

    pdf = pdfium.PdfDocument(str(_pdf(url)))
    if not 1 <= page_no <= len(pdf):
        raise ValueError(f"{url}: page {page_no} does not exist ({len(pdf)} pages)")
    page = pdf[page_no - 1]
    pw, ph = page.get_size()  # points
    page.render(scale=PAGE_PX / pw).to_pil().convert("RGB").save(out_png, quality=92)
    rects: list[list[float]] = []
    if highlight:
        tp = page.get_textpage()
        n = tp.count_chars()
        chars = [tp.get_text_range(i, 1) for i in range(n)]
        # Map the normalised page text back to char indices, then find the normalised highlight in it.
        norm_text, index = [], []
        for i, ch in enumerate(chars):
            ch = " " if ch.isspace() or ch in "\r\n" else ch.replace("’", "'").lower()
            if ch == "­" or (ch == " " and norm_text and norm_text[-1] == " "):
                continue
            norm_text.append(ch)
            index.append(i)
        hay, needle = "".join(norm_text), _norm(highlight)
        pos = hay.find(needle)
        if pos < 0:
            raise ValueError(f"{url} p.{page_no}: highlight not found on the page: {highlight[:60]!r}")
        lines: list[list[float]] = []
        for k in range(pos, pos + len(needle)):
            l, b, r, t = tp.get_charbox(index[k])
            if r - l <= 0 or t - b <= 0:  # spaces have empty boxes
                continue
            box = [l / pw, 1 - t / ph, r / pw, 1 - b / ph]
            if lines:  # same line when the vertical centres are within half a line height
                last = lines[-1]
                if abs((box[1] + box[3]) - (last[1] + last[3])) / 2 < (last[3] - last[1]) * 0.5:
                    lines[-1] = [min(last[0], box[0]), min(last[1], box[1]), max(last[2], box[2]), max(last[3], box[3])]
                    continue
            lines.append(box)
        rects = [[round(v, 4) for v in box] for box in lines]
    return {"aspect": round(ph / pw, 4), "rects": rects}
