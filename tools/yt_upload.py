"""Upload a finished episode to Ink & Orbit as a PRIVATE video; the user reviews and publishes it in Studio.

    python tools/yt_upload.py auth                     # once: sign in, pick the channel (a separate write token)
    python tools/yt_upload.py indus-waters --dry-run   # show what would be sent, change nothing
    python tools/yt_upload.py indus-waters             # upload video and thumbnail, then read the privacy back
    python tools/yt_upload.py ogallala-aquifer --publish-at 2026-11-10T15:00:00Z   # private, goes public at that time

Reads %USERPROFILE%\\Videos\\yt-pipeline\\<slug>\\ (<slug>.mp4, youtube.txt, cover.jpg [else thumbnail_D.jpg] or cover_short.jpg).
A video goes up only with an approved second-by-second audit of that exact render (tools/frame_audit.py).
Private is fixed in the code on purpose, there is no option for anything else; --publish-at only schedules a private
video for a time the user chose (used to replace a scheduled upload). Left for Studio: publishing, the pinned
comment (the API cannot pin), end screens, a Short's cover if YouTube refuses it here.
The write token is its own file, so the read-only analytics token stays read-only. Quota: 1 unit per upload in the
upload bucket (100 a day), about 50 for a thumbnail.
"""
import argparse
import json
import re
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HOME = Path.home() / ".yt-pipeline"
SECRET = HOME / "client_secret.json"
TOKEN = HOME / "token_upload.json"
VIDEOS = Path.home() / "Videos" / "yt-pipeline"
CHANNEL_ID = "UC1h2p6x09doXZRvG4d4M0Sg"  # Ink & Orbit
SCOPES = ["https://www.googleapis.com/auth/youtube.upload",
          "https://www.googleapis.com/auth/youtube.readonly",  # readonly: channel check, duplicates, reading the result
          "https://www.googleapis.com/auth/youtube",  # 2026-11-11, user's consent: change publishAt after upload (reschedule)
          "https://www.googleapis.com/auth/youtube.force-ssl"]  # 2026-11-11, user's consent: post the episode's comment
PRIVACY = "private"
CATEGORY_EDUCATION = "27"
RETRY_STATUS = (500, 502, 503, 504)


def auth() -> None:
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    if not SECRET.exists():
        sys.exit(f"Put the OAuth client file (Desktop app) from Google Cloud at {SECRET}")
    c = InstalledAppFlow.from_client_secrets_file(str(SECRET), SCOPES).run_local_server(
        port=0, prompt="select_account consent", access_type="offline")
    items = build("youtube", "v3", credentials=c, cache_discovery=False).channels().list(part="snippet", mine=True).execute().get("items", [])
    if not items or items[0]["id"] != CHANNEL_ID:
        got = items[0]["snippet"]["title"] if items else "no channel"
        sys.exit(f"Signed in as '{got}', not Ink & Orbit ({CHANNEL_ID}); token not saved. Run auth again and pick that channel.")
    TOKEN.write_text(c.to_json(), encoding="utf-8")
    print(f"Upload token for '{items[0]['snippet']['title']}' saved to {TOKEN}.")


def service():
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    if not TOKEN.exists():
        sys.exit("No upload token: run `python tools/yt_upload.py auth` first.")
    c = Credentials.from_authorized_user_file(str(TOKEN), SCOPES)
    if not c.valid:
        c.refresh(Request())
        TOKEN.write_text(c.to_json(), encoding="utf-8")
    return build("youtube", "v3", credentials=c, cache_discovery=False)


def parse_youtube_txt(path: Path) -> dict:
    """TITLE / DESCRIPTION / TAGS / PINNED COMMENT sections, as pipeline/youtube_meta.py writes them."""
    m = re.fullmatch(r"TITLE\n(?P<title>.*?)\n\nDESCRIPTION\n(?P<description>.*?)\nTAGS\n(?P<tags>.*?)\n(?:\nPINNED COMMENT[^\n]*\n(?P<pinned>.*?)\n?)?",
                     path.read_text(encoding="utf-8").replace("\r\n", "\n"), re.S)
    if not m:
        sys.exit(f"{path}: not in the expected format")
    return {"title": m["title"].strip(), "description": m["description"].strip(),
            "tags": [t.strip() for t in m["tags"].split(",") if t.strip()], "pinned": (m["pinned"] or "").strip()}


def audit_status(folder: Path, video: Path) -> str | None:
    """None when tools/frame_audit.py approved this exact file; otherwise the reason (the user's rule, 2026-11-09:
    every render is checked second by second, start to end, before it goes to YouTube)."""
    rep_path = folder / "audit" / "audit.json"
    if not rep_path.exists():
        return f"no frame audit: run tools/frame_audit.py {folder.name}, review every sheet, then --approve"
    rep = json.loads(rep_path.read_text(encoding="utf-8"))
    sys.path.insert(0, str(ROOT / "tools"))
    from video_fingerprint import fingerprint  # the same fingerprint the audit recorded
    if rep.get("fingerprint") != fingerprint(video):
        return "the audit belongs to another render of this video: audit the new file"
    if not rep.get("approved"):
        return f"the audit is not approved yet ({len(rep.get('flags', []))} automatic flag(s), {len(rep.get('sheets', []))} sheets to review)"
    return None


def check(meta: dict) -> None:
    """YouTube's limits (videos reference): refuse here instead of after a long upload."""
    errors = []
    if not meta["title"] or len(meta["title"]) > 100:
        errors.append(f"title is {len(meta['title'])} characters (1-100)")
    if len(meta["description"].encode("utf-8")) > 5000:
        errors.append(f"description is {len(meta['description'].encode('utf-8'))} bytes (limit 5000)")
    for label in ("title", "description"):
        if "<" in meta[label] or ">" in meta[label]:
            errors.append(f"YouTube refuses '<' and '>' in the {label}")
    tag_len = sum(len(t) + (2 if " " in t else 0) for t in meta["tags"]) + max(0, len(meta["tags"]) - 1)
    if tag_len > 500:
        errors.append(f"tags count as {tag_len} characters (limit 500)")
    if errors:
        sys.exit("Not uploading: " + "; ".join(errors))


def body_of(meta: dict, publish_at: str | None = None) -> dict:
    body = {
        "snippet": {"title": meta["title"], "description": meta["description"], "tags": meta["tags"],
                    "categoryId": CATEGORY_EDUCATION, "defaultLanguage": "en", "defaultAudioLanguage": "en"},
        # containsSyntheticMedia False: the channel's checked answer for our usual episode (PROGRESS.md, Decisions).
        "status": {"privacyStatus": PRIVACY, "selfDeclaredMadeForKids": False, "containsSyntheticMedia": False},
    }
    if publish_at:  # YouTube keeps the video private until then; publishAt is only allowed on private videos
        body["status"]["publishAt"] = publish_at
    return body


def future_utc(text: str) -> str:
    import datetime as dt
    t = dt.datetime.fromisoformat(text.replace("Z", "+00:00"))
    if t.tzinfo is None:
        sys.exit("--publish-at needs a time zone, e.g. 2026-11-10T15:00:00Z")
    t = t.astimezone(dt.timezone.utc)
    if t <= dt.datetime.now(dt.timezone.utc) + dt.timedelta(minutes=30):
        sys.exit(f"--publish-at {t:%Y-%m-%dT%H:%M}Z is not at least 30 minutes ahead")
    return t.strftime("%Y-%m-%dT%H:%M:%S.000Z")


def existing_with_title(yt, title: str) -> list[str]:
    ch = yt.channels().list(part="contentDetails", mine=True).execute()["items"][0]
    pl, found, token = ch["contentDetails"]["relatedPlaylists"]["uploads"], [], None
    while True:
        r = yt.playlistItems().list(part="snippet", playlistId=pl, maxResults=50, pageToken=token).execute()
        found += [i["snippet"]["resourceId"]["videoId"] for i in r.get("items", []) if i["snippet"]["title"] == title]
        token = r.get("nextPageToken")
        if not token:
            return found


def upload(yt, video: Path, body: dict) -> str:
    from googleapiclient.errors import HttpError
    from googleapiclient.http import MediaFileUpload
    media = MediaFileUpload(str(video), mimetype="video/mp4", chunksize=8 * 1024 * 1024, resumable=True)
    req = yt.videos().insert(part="snippet,status", body=body, media_body=media)
    resp, retries, shown = None, 0, -10
    while resp is None:
        try:
            status, resp = req.next_chunk()
            retries = 0
            if status and int(status.progress() * 100) >= shown + 10:
                shown = int(status.progress() * 100)
                print(f"  {shown} %", flush=True)
        except HttpError as e:
            if e.resp.status not in RETRY_STATUS or retries >= 8:
                raise
            time.sleep(2 ** retries)
            retries += 1
        except OSError:
            if retries >= 8:
                raise
            time.sleep(2 ** retries)
            retries += 1
    return resp["id"]


def set_thumbnail(yt, vid: str, thumb: Path) -> bool:
    from googleapiclient.errors import HttpError
    from googleapiclient.http import MediaFileUpload
    try:
        yt.thumbnails().set(videoId=vid, media_body=MediaFileUpload(str(thumb), mimetype="image/jpeg")).execute()
        return True
    except HttpError as e:
        print(f"WARNING: thumbnail not set ({e.resp.status}): {e.reason}. The video is up; set it by hand in Studio.")
        return False


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("slug", help="episode folder name, `auth`, or `reschedule` (with --video ID --publish-at TIME)")
    ap.add_argument("--video", help="reschedule / comment: the video id")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--force", action="store_true", help="upload even if a video with this title exists")
    ap.add_argument("--publish-at", help="schedule the private video, e.g. 2026-11-10T15:00:00Z (the user's chosen time)")
    ap.add_argument("--slug-of", help="comment: the episode whose youtube.pinned_comment to post")
    a = ap.parse_args()
    if a.slug == "auth":
        return auth()
    if a.slug == "comment":  # python tools/yt_upload.py comment --video ID --slug-of SLUG ; the API cannot pin, Studio does
        if not (a.video and a.slug_of):
            sys.exit("comment needs --video ID and --slug-of SLUG")
        text = json.loads((ROOT / "episodes" / a.slug_of / "script.json").read_text(encoding="utf-8"))["youtube"]["pinned_comment"]
        yt = service()
        st = yt.videos().list(part="status", id=a.video).execute()["items"][0]["status"]
        if st["privacyStatus"] != "public":
            sys.exit(f"{a.video} is {st['privacyStatus']}: comments open once it is public")
        mine = yt.commentThreads().list(part="snippet", videoId=a.video, searchTerms=text[:40], maxResults=20).execute().get("items", [])
        if any(t["snippet"]["topLevelComment"]["snippet"].get("authorChannelId", {}).get("value") == CHANNEL_ID for t in mine):
            return print(f"{a.video}: our comment is already there")
        r = yt.commentThreads().insert(part="snippet", body={"snippet": {"channelId": CHANNEL_ID, "videoId": a.video,
                                       "topLevelComment": {"snippet": {"textOriginal": text}}}}).execute()
        return print(f"{a.video}: comment posted ({r['id']}); pin it in Studio")
    if a.slug == "reschedule":
        if not (a.video and a.publish_at):
            sys.exit("reschedule needs --video ID and --publish-at TIME")
        yt = service()
        st = yt.videos().list(part="status", id=a.video).execute()["items"][0]["status"]
        if st["privacyStatus"] != "private":
            sys.exit(f"{a.video} is already {st['privacyStatus']}: not touched")
        st["publishAt"] = future_utc(a.publish_at)
        r = yt.videos().update(part="status", body={"id": a.video, "status": st}).execute()["status"]
        return print(f"{a.video}: privacy {r['privacyStatus']}, publishAt {r.get('publishAt')}")

    folder = VIDEOS / a.slug
    video = folder / f"{a.slug}.mp4"
    txt = folder / "youtube.txt"
    for need in (video, txt):
        if not need.exists():
            sys.exit(f"Missing {need}: run tools/fetch_episode.ps1 {a.slug}")
    script = json.loads((ROOT / "episodes" / a.slug / "script.json").read_text(encoding="utf-8"))
    short = script.get("format") == "short"
    # Long videos: cover.jpg (the hand-made public-domain photo cover, see thumbnails/make_thumbs.py) wins over the
    # pipeline's own Landsat split, which is a blur on a phone; without it an upload silently got the old style.
    thumb = folder / ("cover_short.jpg" if short else "cover.jpg")
    if not short and not thumb.exists():
        thumb = folder / "thumbnail_D.jpg"
        print("  NOTE: no cover.jpg; falling back to the pipeline's thumbnail_D.jpg (old style)")
    meta = parse_youtube_txt(txt)
    check(meta)
    publish_at = future_utc(a.publish_at) if a.publish_at else None
    body = body_of(meta, publish_at)
    print(f"{a.slug}: {video.stat().st_size / 1e6:.0f} MB, {'Short' if short else 'long'}, privacy {PRIVACY}"
          f"{', public at ' + publish_at if publish_at else ''}")
    print(f"  title: {meta['title']}")
    print(f"  description: {len(meta['description'].encode('utf-8'))} bytes, {len(meta['tags'])} tags, category {body['snippet']['categoryId']}")
    print(f"  thumbnail: {thumb.name if thumb.exists() else 'NONE FOUND'}")
    print(f"  by hand in Studio: {'pin: ' + meta['pinned'] if meta['pinned'] else 'no pinned comment'}")
    blocked = audit_status(folder, video)
    print(f"  frame audit: {'approved' if blocked is None else 'NOT OK: ' + blocked}")
    if blocked and not a.dry_run:
        sys.exit("Not uploading: " + blocked)
    if a.dry_run and not TOKEN.exists():
        print("Dry run: no upload token yet, so duplicates were not checked. Nothing was sent.")
        return

    yt = service()
    ch = yt.channels().list(part="snippet", mine=True).execute()["items"][0]
    if ch["id"] != CHANNEL_ID:
        sys.exit(f"This token belongs to '{ch['snippet']['title']}', not Ink & Orbit. Nothing was sent.")
    dupes = existing_with_title(yt, meta["title"])
    if dupes:
        print(f"  same title already on the channel: {', '.join(dupes)}")
    if a.dry_run:
        print("Dry run: nothing was sent.")
        return
    if dupes and not a.force:
        sys.exit("Not uploading a duplicate. Use --force if it is meant.")

    vid = upload(yt, video, body)
    print(f"Uploaded: https://studio.youtube.com/video/{vid}/edit")
    thumb_ok = thumb.exists() and set_thumbnail(yt, vid, thumb)
    got = yt.videos().list(part="status", id=vid).execute()["items"][0]["status"]
    print(f"  thumbnail set: {thumb_ok}; YouTube says: privacy {got['privacyStatus']}, processing {got.get('uploadStatus')}, "
          f"publishAt {got.get('publishAt')}")
    if publish_at and not got.get("publishAt"):
        print("WARNING: YouTube did not keep the schedule; set it in Studio.")
    if got["privacyStatus"] != PRIVACY:
        sys.exit(f"WARNING: the video is {got['privacyStatus']}, not {PRIVACY}. Check it in Studio now.")


if __name__ == "__main__":
    main()
