"""YouTube Analytics on the PC: where viewers leave each video, mapped back to the script.

    python tools/yt_analytics.py auth                      # once: opens the browser, saves a token outside the repo
    python tools/yt_analytics.py videos                    # channel uploads with views, average % watched
    python tools/yt_analytics.py retention dubai-islands   # retention curve -> episodes/<slug>/retention.md
    python tools/yt_analytics.py retention --all           # every episode whose YouTube title matches an upload

Credentials live in %USERPROFILE%\\.yt-pipeline\\ (client_secret.json from Google Cloud, token.json written by
`auth`), never in the repo or the chat. Read-only scopes: the tool cannot change anything on the channel.

The retention curve comes from the Analytics API (audienceWatchRatio per 1 % of the video, plus YouTube's
comparison with similar videos). Each drop is mapped to the narration around it: the episode's timeline is
estimated from the script (tools/episode_check.py) and stretched to the real video length, so the sentence
named at a drop is right to within a few seconds. Data appears about 2-3 days after upload.
"""
import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "pipeline"))
sys.path.insert(0, str(ROOT / "tools"))

HOME = Path.home() / ".yt-pipeline"
SECRET = HOME / "client_secret.json"
TOKEN = HOME / "token.json"
SCOPES = ["https://www.googleapis.com/auth/yt-analytics.readonly",
          "https://www.googleapis.com/auth/youtube.readonly"]
LESSONS = "## Lessons for the next script"


def creds():
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    c = Credentials.from_authorized_user_file(str(TOKEN), SCOPES) if TOKEN.exists() else None
    if c and c.valid:
        return c
    if c and c.expired and c.refresh_token:
        c.refresh(Request())
        TOKEN.write_text(c.to_json(), encoding="utf-8")
        return c
    sys.exit("No valid token: run `python tools/yt_analytics.py auth` first.")


def auth():
    from google_auth_oauthlib.flow import InstalledAppFlow
    if not SECRET.exists():
        sys.exit(f"Put the OAuth client file (Desktop app) from Google Cloud at {SECRET}")
    flow = InstalledAppFlow.from_client_secrets_file(str(SECRET), SCOPES)
    c = flow.run_local_server(port=0, prompt="consent", access_type="offline")
    HOME.mkdir(exist_ok=True)
    TOKEN.write_text(c.to_json(), encoding="utf-8")
    print(f"Token saved to {TOKEN} (read-only access to YouTube data and analytics).")


def services():
    from googleapiclient.discovery import build
    c = creds()
    return (build("youtube", "v3", credentials=c, cache_discovery=False),
            build("youtubeAnalytics", "v2", credentials=c, cache_discovery=False))


def iso_seconds(d: str) -> int:
    m = re.fullmatch(r"P(?:(\d+)D)?T?(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", d)
    days, h, mi, s = (int(x or 0) for x in m.groups())
    return ((days * 24 + h) * 60 + mi) * 60 + s


def uploads(yt) -> list[dict]:
    ch = yt.channels().list(part="contentDetails", mine=True).execute()["items"][0]
    pl = ch["contentDetails"]["relatedPlaylists"]["uploads"]
    ids, token = [], None
    while True:
        r = yt.playlistItems().list(part="contentDetails", playlistId=pl, maxResults=50, pageToken=token).execute()
        ids += [i["contentDetails"]["videoId"] for i in r["items"]]
        token = r.get("nextPageToken")
        if not token:
            break
    out = []
    for k in range(0, len(ids), 50):
        r = yt.videos().list(part="snippet,contentDetails,statistics", id=",".join(ids[k:k + 50])).execute()
        for v in r["items"]:
            out.append({"id": v["id"], "title": v["snippet"]["title"], "published": v["snippet"]["publishedAt"][:10],
                        "seconds": iso_seconds(v["contentDetails"]["duration"]),
                        "views": int(v["statistics"].get("viewCount", 0))})
    return out


def _query(ya, vid: str, published: str, metrics: str, dimensions: str | None = None) -> dict:
    kw = {"ids": "channel==MINE", "startDate": published, "endDate": dt.date.today().isoformat(),
          "metrics": metrics, "filters": f"video=={vid}"}
    if dimensions:
        kw["dimensions"] = dimensions
    return ya.reports().query(**kw).execute()


def video_stats(ya, vid: str, published: str) -> dict:
    out = {}
    r = _query(ya, vid, published, "views,averageViewDuration,averageViewPercentage")
    if r.get("rows"):
        out = dict(zip([h["name"] for h in r["columnHeaders"]], r["rows"][0]))
    try:  # thumbnail impressions and click-through rate, where the API offers them
        r = _query(ya, vid, published, "videoThumbnailImpressions,videoThumbnailImpressionsClickRate")
        if r.get("rows"):
            out.update(dict(zip([h["name"] for h in r["columnHeaders"]], r["rows"][0])))
    except Exception:
        pass
    return out


def curve(ya, vid: str, published: str) -> list[tuple[float, float, float]]:
    """[(fraction of the video, share of viewers still watching, retention relative to similar videos)]."""
    r = _query(ya, vid, published, "audienceWatchRatio,relativeRetentionPerformance", "elapsedVideoTimeRatio")
    return [(row[0], row[1], row[2]) for row in r.get("rows", [])]


def script_times(slug: str, real_seconds: float):
    """[(start s, end s, 'cXXpYY', text)] for every paragraph, estimated and stretched to the real length."""
    from config import FPS
    from episode_check import fake_timings
    from schema import load_script
    import timeline as tl
    script = load_script(ROOT / "episodes" / slug / "script.json")
    if script.legacy_length:  # rendered before 2026-11-08, with a full-screen card at every chapter after the first
        for ch in script.chapters[1:]:
            if ch.card is None:
                ch.card = True
    durations, words = fake_timings(script)
    lay = tl.layout(script, durations, words)
    total = lay["total_frames"] / FPS
    k = real_seconds / total
    flat = [(ci, pi, p) for ci, ch in enumerate(script.chapters) for pi, p in enumerate(ch.paragraphs)]
    out = []
    for n, ((ci, pi, p), para) in enumerate(zip(flat, lay["paragraphs"])):
        end = lay["paragraphs"][n + 1]["start"] if n + 1 < len(lay["paragraphs"]) else total
        out.append((para["start"] * k, end * k, f"c{ci + 1:02d}p{pi + 1:02d}", p.text))
    return out, [(c["title"], c["start"] * k) for c in lay["chapters"]]


def mmss(s: float) -> str:
    return f"{int(s // 60)}:{int(s % 60):02d}"


def find_video(slug: str, vids: list[dict]) -> dict | None:
    meta = json.loads((ROOT / "episodes" / slug / "script.json").read_text(encoding="utf-8")).get("youtube") or {}
    if meta.get("video_id"):
        return next((v for v in vids if v["id"] == meta["video_id"]), None)
    title = (meta.get("title") or "").strip().lower()
    return next((v for v in vids if v["title"].strip().lower() == title), None) if title else None


def drops(pts: list[tuple], T: float) -> list[tuple[float, float, float]]:
    """Steepest falls over ~2 % of the video after the first 3 % (the intro has its own checkpoint), spread out."""
    falls = sorted(((a[1] - b[1], a[0] * T, b[0] * T) for a, b in zip(pts, pts[2:]) if a[0] >= 0.03), reverse=True)
    picked = []
    for f in falls:
        if f[0] <= 0.005 or len(picked) == 6:
            break
        if all(abs(f[1] - q[1]) > T * 0.04 for q in picked):
            picked.append(f)
    return sorted(picked, key=lambda x: x[1])


STAT_NAMES = {"views": "Views", "averageViewDuration": "Average view duration (s)",
              "averageViewPercentage": "Average % watched", "videoThumbnailImpressions": "Thumbnail impressions",
              "videoThumbnailImpressionsClickRate": "Impressions click-through rate"}


def report(slug: str, v: dict, ya) -> Path:
    pts = curve(ya, v["id"], v["published"])
    if not pts:
        raise RuntimeError(f"{slug}: no retention data yet (it appears about 2-3 days after upload)")
    stats = video_stats(ya, v["id"], v["published"])
    T = v["seconds"]
    paras, chapters = script_times(slug, T)

    def para_at(t):
        return next((p for p in paras if p[0] <= t < p[1]), paras[-1])

    def watching(sec):
        return min(pts, key=lambda p: abs(p[0] - sec / T))[1]

    lines = [f"# {slug} - audience retention", "",
             f"Video: https://youtu.be/{v['id']} \"{v['title']}\" ({mmss(T)}), published {v['published']}, "
             f"read {dt.date.today().isoformat()} (tools/yt_analytics.py).", ""]
    if stats:
        lines += ["| Metric | Value |", "|---|---|"]
        for key, val in stats.items():
            if key == "videoThumbnailImpressionsClickRate":
                shown = f"{val:.1f} %" if val > 1 else f"{val:.1%}"
            elif key == "averageViewPercentage":
                shown = f"{val:.1f} %"
            else:
                shown = f"{val:,.0f}"
            lines.append(f"| {STAT_NAMES.get(key, key)} | {shown} |")
        lines.append("")
    lines += ["## Checkpoints", "", "| Time | Still watching |", "|---|---|"]
    for sec in (30, 60, 120, 300, T * 0.5, T * 0.9):
        if sec < T:
            lines.append(f"| {mmss(sec)} | {watching(sec):.0%} |")
    lines += ["", "Values above 100 % mean re-watching or skipping into that point.", "",
              "## Where viewers leave (steepest drops after the intro)", "",
              "| From | To | Lost | Chapter | Paragraph | Narration there |", "|---|---|---|---|---|---|"]
    for drop, t0, t1 in drops(pts, T):
        ch = max((c for c in chapters if c[1] <= t0), key=lambda c: c[1], default=("", 0))[0]
        p = para_at(t0)
        lines.append(f"| {mmss(t0)} | {mmss(t1)} | {drop:.1%} | {ch} | {p[2]} | {p[3][:140]} |")
    rises = sorted(((b[1] - a[1], a[0] * T) for a, b in zip(pts, pts[2:]) if b[1] - a[1] > 0.01), reverse=True)[:3]
    if rises:
        lines += ["", "## Re-watched or skipped to", ""]
        for gain, t in rises:
            p = para_at(t)
            lines.append(f"- {mmss(t)} (+{gain:.0%}) {p[2]}: {p[3][:120]}")
    weak = [p for p in pts if p[2] < 0.35]
    if weak:
        lines += ["", f"YouTube rates {len(weak)} of {len(pts)} points well below similar videos "
                      f"(relativeRetentionPerformance < 0.35)."]
    lines += ["", "## Curve (every 5 %)", "", "| % of video | Time | Watching | vs similar videos |", "|---|---|---|---|"]
    for p in pts[::5]:
        lines.append(f"| {p[0]:.0%} | {mmss(p[0] * T)} | {p[1]:.0%} | {p[2]:.2f} |")
    out = ROOT / "episodes" / slug / "retention.md"
    old = out.read_text(encoding="utf-8") if out.exists() else ""
    body = old.split(LESSONS, 1)[1].lstrip("\n") if LESSONS in old else (
        "(Claude writes these from the tables above: what the drops have in common and the rule it suggests. "
        "Rules that repeat across episodes go to docs/script-rules.md.)\n")
    out.write_text("\n".join(lines) + f"\n\n{LESSONS}\n\n" + body, encoding="utf-8")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["auth", "videos", "retention"])
    ap.add_argument("slug", nargs="?")
    ap.add_argument("--all", action="store_true")
    a = ap.parse_args()
    if a.cmd == "auth":
        return auth()
    yt, ya = services()
    vids = uploads(yt)
    if a.cmd == "videos":
        for v in sorted(vids, key=lambda v: v["published"]):
            s = video_stats(ya, v["id"], v["published"])
            ctr = s.get("videoThumbnailImpressionsClickRate")
            print(f"{v['published']}  {v['id']}  {mmss(v['seconds']):>6}  {v['views']:>6} views  "
                  f"{s.get('averageViewPercentage', 0):5.1f} % watched  "
                  f"{'' if ctr is None else f'CTR {ctr}  '}{v['title']}")
        return
    if not a.all and not a.slug:
        ap.error("retention needs an episode slug or --all")
    slugs = sorted(d.name for d in (ROOT / "episodes").iterdir() if (d / "script.json").exists()) if a.all else [a.slug]
    for slug in slugs:
        v = find_video(slug, vids)
        if v is None:
            if not a.all:
                print(f"{slug}: no upload matches its youtube.title; add \"video_id\" under \"youtube\" in script.json")
            continue
        try:
            print(f"{slug}: {report(slug, v, ya).relative_to(ROOT)}")
        except RuntimeError as exc:
            print(exc)


if __name__ == "__main__":
    main()
