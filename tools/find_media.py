"""Find real, reusable pictures of a subject: public domain, CC0 or CC BY only.

    python tools/find_media.py "Great Salt Lake flood 1986" [--kind image|video|all] [--max 12] [--out build/media/x]

Searches Wikimedia Commons (licence metadata checked), the NASA Image and Video Library (NASA's own media are public
domain; items naming another owner are dropped), the Internet Archive (public-domain mark, CC0 or CC BY licence URLs,
and the Prelinger collection) and the Library of Congress photos (only "No known restrictions"). Writes candidates.md
(a table with the reference to put in script.json) and sheet.jpg (numbered thumbnails) to look at before choosing.
Commons files and NASA items can go straight into `photo` / `film`; Internet Archive and Library of Congress items
are listed for checking (upload them to Commons or add a fetcher before using them).
"""
import argparse
import io
import re
import sys
from pathlib import Path

import requests
from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "pipeline"))
from commons import _allowed, _clean  # noqa: E402  (same licence rule as the pipeline)

UA = {"User-Agent": "yt-pipeline/1.0 (https://github.com/otomasyon497/yt-pipeline)"}


def _json(url, **params):
    r = requests.get(url, params=params, headers=UA, timeout=60)
    r.raise_for_status()
    return r.json()


def commons(q, kind, n):
    ft = {"image": " filetype:bitmap", "video": " filetype:video", "all": ""}[kind]
    d = _json("https://commons.wikimedia.org/w/api.php", action="query", generator="search", gsrnamespace=6,
              gsrlimit=n * 3, gsrsearch=q + ft, prop="imageinfo", iiprop="url|extmetadata|size|mediatype",
              iiurlwidth=320, format="json")
    out = []
    for p in sorted(d.get("query", {}).get("pages", {}).values(), key=lambda p: p.get("index", 0)):
        ii = p.get("imageinfo", [{}])[0]
        m = ii.get("extmetadata", {})
        short = _clean(m.get("LicenseShortName", {}).get("value", ""))
        if not _allowed(m.get("License", {}).get("value", ""), short) or p["title"].lower().endswith((".pdf", ".djvu")):
            continue
        out.append({"source": "Commons", "kind": "video" if ii.get("mediatype") == "VIDEO" else "image",
                    "title": p["title"][5:], "licence": short, "date": _clean(m.get("DateTimeOriginal", {}).get("value", ""))[:20],
                    "ref": p["title"], "url": ii.get("descriptionurl", ""), "thumb": ii.get("thumburl"),
                    "size": f"{ii.get('width')}x{ii.get('height')}"})
    return out[:n]


def nasa(q, kind, n):
    mt = {"image": "image", "video": "video", "all": "image,video"}[kind]
    d = _json("https://images-api.nasa.gov/search", q=q, media_type=mt, page_size=n * 2)
    out = []
    for it in d["collection"]["items"]:
        data = it["data"][0]
        text = " ".join(str(data.get(k, "")) for k in ("description", "secondary_creator", "photographer"))
        if re.search(r"©|\bcopyright", text, re.I):
            continue
        out.append({"source": "NASA", "kind": data.get("media_type", ""), "title": data.get("title", ""),
                    "licence": "Public domain (NASA)", "date": data.get("date_created", "")[:10],
                    "ref": f"nasa:{data['nasa_id']}", "url": f"https://images.nasa.gov/details/{data['nasa_id']}",
                    "thumb": (it.get("links") or [{}])[0].get("href"), "size": data.get("center", "")})
    return out[:n]


def archive(q, kind, n):
    mt = {"image": "image", "video": "movies", "all": "(movies OR image)"}[kind]
    d = _json("https://archive.org/advancedsearch.php", q=f"({q}) AND mediatype:{mt}",
              **{"fl[]": ["identifier", "title", "licenseurl", "year", "mediatype", "collection"]}, rows=n * 4, output="json")
    out = []
    for doc in d["response"]["docs"]:
        lic = str(doc.get("licenseurl", "")).lower()
        cols = doc.get("collection", [])
        cols = cols if isinstance(cols, list) else [cols]
        ok = ("publicdomain" in lic or "/zero/" in lic or re.search(r"/licenses/by/\d", lic) or "prelinger" in cols)
        if not ok:
            continue
        ident = doc["identifier"]
        out.append({"source": "Internet Archive", "kind": "video" if doc.get("mediatype") == "movies" else "image",
                    "title": str(doc.get("title", ident))[:120], "licence": lic or "Prelinger (public domain)",
                    "date": str(doc.get("year", "")), "ref": f"https://archive.org/details/{ident}",
                    "url": f"https://archive.org/details/{ident}", "thumb": f"https://archive.org/services/img/{ident}",
                    "size": ""})
    return out[:n]


def loc(q, kind, n):
    if kind == "video":
        return []
    d = _json("https://www.loc.gov/photos/", q=q, fo="json", c=n * 2)
    out = []
    for r in d.get("results", [])[: n * 2]:
        try:
            item = _json(r["url"], fo="json").get("item", {})
        except requests.RequestException:
            continue
        rights = " ".join(item.get("rights_advisory", []) if isinstance(item.get("rights_advisory"), list)
                          else [str(item.get("rights_advisory", ""))])
        if "no known restrictions" not in rights.lower():
            continue
        imgs = r.get("image_url") or []
        out.append({"source": "Library of Congress", "kind": "image", "title": str(r.get("title", ""))[:120],
                    "licence": "No known restrictions", "date": str(r.get("date", "")), "ref": r["url"], "url": r["url"],
                    "thumb": imgs[0] if imgs else None, "size": ""})
    return out[:n]


def sheet(items, path):
    tiles = []
    for i, it in enumerate(items, 1):
        try:
            im = Image.open(io.BytesIO(requests.get(it["thumb"], headers=UA, timeout=30).content)).convert("RGB")
        except Exception:
            im = Image.new("RGB", (320, 200), (40, 40, 40))
        im.thumbnail((320, 200))
        tile = Image.new("RGB", (320, 222), (17, 20, 27))
        tile.paste(im, ((320 - im.width) // 2, 0))
        ImageDraw.Draw(tile).text((4, 204), f"{i}. {it['source']} {it['kind']}"[:52], fill=(245, 166, 35))
        tiles.append(tile)
    if not tiles:
        return
    cols = 5
    rows = (len(tiles) + cols - 1) // cols
    out = Image.new("RGB", (320 * cols, 222 * rows), (17, 20, 27))
    for i, t in enumerate(tiles):
        out.paste(t, ((i % cols) * 320, (i // cols) * 222))
    out.save(path, quality=85)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("query")
    ap.add_argument("--kind", choices=["image", "video", "all"], default="all")
    ap.add_argument("--max", type=int, default=10, help="per source")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    out = Path(a.out or Path("build/media") / re.sub(r"[^a-z0-9]+", "-", a.query.lower()).strip("-"))
    out.mkdir(parents=True, exist_ok=True)
    items = []
    for name, fn in (("Commons", commons), ("NASA", nasa), ("Internet Archive", archive), ("Library of Congress", loc)):
        try:
            got = fn(a.query, a.kind, a.max)
        except Exception as exc:  # one source down should not stop the others
            print(f"  {name}: {exc}")
            continue
        print(f"  {name}: {len(got)}")
        items += got
    lines = [f"# Media candidates: {a.query}", "", "| # | source | kind | title | licence | date | reference |", "|---|---|---|---|---|---|---|"]
    for i, it in enumerate(items, 1):
        lines.append(f"| {i} | {it['source']} | {it['kind']} | {it['title'].replace('|', '/')} | {it['licence']} | "
                     f"{it['date']} | `{it['ref']}` |")
    (out / "candidates.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    sheet(items, out / "sheet.jpg")
    print(f"{len(items)} candidates -> {out / 'candidates.md'}, {out / 'sheet.jpg'}")


if __name__ == "__main__":
    main()
