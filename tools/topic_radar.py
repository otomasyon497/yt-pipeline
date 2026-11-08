"""Topic radar: recent English long videos near the channel's topics that beat their channel's size.

    python tools/topic_radar.py            # writes docs/topic-radar-<date>.md and prints it
    python tools/topic_radar.py --days 60

A lead, not a verdict: it shows that a subject drew viewers, never how many people search for it or where they live.
Every lead still goes through .claude/skills/episode-plan (research depth, real pictures) and the user's choice. Other
channels' videos only show interest in a subject; script, pictures and angle stay our own.
Read-only, uses the analytics token. Quota: search.list 1 unit in the search bucket (100 calls a day).
"""
import argparse
import datetime as dt
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "pipeline"))
import yt_analytics as t  # noqa: E402

QUERIES = {
    "water": ["river dispute dam countries explained", "why is this lake disappearing satellite", "aquifer running out water crisis explained",
              "dam that could start a war", "sea drying up what happened"],
    "megaprojects": ["failed megaproject explained", "artificial island project what happened", "new canal project geopolitics explained",
                     "new capital city project explained"],
    "borders": ["strange border explained geography", "disputed territory map explained", "why this country wants this land map"],
    "land": ["sinking city explained satellite", "coastline disappearing country losing land", "desert expansion satellite images explained"],
    "trade": ["shipping chokepoint strait explained map", "why this port matters geopolitics map"],
}
# Exam-prep and news channels fill these results; their numbers say little about a documentary audience.
NOISE = re.compile(r"\b(upsc|ias|ssc|testbook|adda247|studyiq|drishti|vajiram|sanskriti|gs booster|exam|mains|prelims|hindi|news|tv|live)\b", re.I)
LONG = 480  # seconds
TOO_LONG = 90 * 60  # streams
MIN_VIEWS = 20000
SUB_FLOOR = 1000  # a very small channel's ratio would run away


def english(title: str) -> bool:
    letters = [c for c in title if c.isalpha()]
    return bool(letters) and sum(c.isascii() for c in letters) / len(letters) > 0.95


def search(yt, after: str) -> dict[str, str]:
    ids: dict[str, str] = {}
    for theme, queries in QUERIES.items():
        for q in queries:
            for length in ("medium", "long"):
                r = yt.search().list(part="id", q=q, type="video", order="viewCount", publishedAfter=after, maxResults=25,
                                     relevanceLanguage="en", regionCode="US", videoDuration=length).execute()
                for i in r["items"]:
                    ids.setdefault(i["id"]["videoId"], theme)
    return ids


def details(yt, ids: list[str]) -> tuple[list[dict], dict[str, int]]:
    videos, channels = [], set()
    for k in range(0, len(ids), 50):
        for v in yt.videos().list(part="snippet,statistics,contentDetails", id=",".join(ids[k:k + 50])).execute()["items"]:
            videos.append(v)
            channels.add(v["snippet"]["channelId"])
    subs, channels = {}, list(channels)
    for k in range(0, len(channels), 50):
        for c in yt.channels().list(part="statistics", id=",".join(channels[k:k + 50])).execute()["items"]:
            subs[c["id"]] = int(c["statistics"].get("subscriberCount", 0) or 0)
    return videos, subs


def score(videos: list[dict], subs: dict[str, int], themes: dict[str, str], now) -> tuple[list[dict], int]:
    out, dropped = [], 0
    for v in videos:
        sn = v["snippet"]
        views = int(v["statistics"].get("viewCount", 0))
        secs = t.iso_seconds(v["contentDetails"]["duration"])
        lang = sn.get("defaultAudioLanguage") or sn.get("defaultLanguage") or "en"
        if (views < MIN_VIEWS or not LONG <= secs <= TOO_LONG or not lang.startswith("en") or not english(sn["title"])
                or NOISE.search(sn["channelTitle"]) or NOISE.search(sn["title"])):
            dropped += 1
            continue
        age = max(1, (now - dt.datetime.fromisoformat(sn["publishedAt"].replace("Z", "+00:00"))).days)
        s = subs.get(sn["channelId"], 0)
        out.append({"ratio": views / max(s, SUB_FLOOR), "views": views, "subs": s, "per_day": views // age, "age": age,
                    "min": secs // 60, "title": sn["title"], "channel": sn["channelTitle"], "id": v["id"], "theme": themes[v["id"]]})
    return sorted(out, key=lambda x: -x["ratio"]), dropped


def own_search_terms(ya, days: int) -> list[tuple[str, int]]:
    """What people typed before watching our videos. Empty while the channel is too small for YouTube to report it."""
    end = dt.date.today()
    r = ya.reports().query(ids="channel==MINE", startDate=str(end - dt.timedelta(days=days)), endDate=str(end), metrics="views",
                           dimensions="insightTrafficSourceDetail", filters="insightTrafficSourceType==YT_SEARCH",
                           sort="-views", maxResults=25).execute()
    return [(row[0], int(row[1])) for row in r.get("rows", [])]


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=90)
    a = ap.parse_args()
    yt, ya = t.services()
    now = dt.datetime.now(dt.timezone.utc)
    ids = search(yt, (now - dt.timedelta(days=a.days)).strftime("%Y-%m-%dT%H:%M:%SZ"))
    videos, subs = details(yt, list(ids))
    rows, dropped = score(videos, subs, ids, now)
    try:
        terms = own_search_terms(ya, a.days)
    except Exception as exc:
        terms = []
        print(f"own search terms unavailable: {str(exc)[:160]}")

    lines = [f"# Topic radar, {now.date()}", "",
             f"Last {a.days} days: {len(ids)} videos found, {dropped} filtered out (short, under {MIN_VIEWS:,} views, exam or news, "
             "not English). Leads only: views show interest, not search demand or the audience's country.", "",
             "| Views / subs | Views | Subs | Views a day | Min | Theme | Title | Channel |", "|---|---|---|---|---|---|---|---|"]
    for r in rows[:40]:
        title = r["title"].replace("|", "/")
        lines.append(f"| {r['ratio']:.1f} | {r['views']:,} | {r['subs']:,} | {r['per_day']:,} | {r['min']} | {r['theme']} | "
                     f"[{title}](https://youtu.be/{r['id']}) | {r['channel'].replace('|', '/')} |")
    lines += ["", "## What people searched before watching us", ""]
    lines += [f"- {term}: {views} views" for term, views in terms] or ["Nothing reported yet."]
    out = ROOT / "docs" / f"topic-radar-{now.date()}.md"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    print(f"\nWritten to {out}")


if __name__ == "__main__":
    main()
