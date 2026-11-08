"""Upload a finished episode to Ink & Orbit as a PRIVATE video; the user reviews and publishes it in Studio.

    python tools/yt_upload.py auth                     # once: sign in, pick the channel (a separate write token)
    python tools/yt_upload.py indus-waters --dry-run   # show what would be sent, change nothing
    python tools/yt_upload.py indus-waters             # upload video and thumbnail, then read the privacy back

Reads %USERPROFILE%\\Videos\\yt-pipeline\\<slug>\\ (<slug>.mp4, youtube.txt, thumbnail_D.jpg or cover_short.jpg).
Private is fixed in the code on purpose, there is no option for anything else. Left for Studio: publishing, the pinned
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
          "https://www.googleapis.com/auth/youtube.readonly"]  # readonly: channel check, duplicates, reading the result
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


def body_of(meta: dict) -> dict:
    return {
        "snippet": {"title": meta["title"], "description": meta["description"], "tags": meta["tags"],
                    "categoryId": CATEGORY_EDUCATION, "defaultLanguage": "en", "defaultAudioLanguage": "en"},
        # containsSyntheticMedia False: the channel's checked answer for our usual episode (PROGRESS.md, Decisions).
        "status": {"privacyStatus": PRIVACY, "selfDeclaredMadeForKids": False, "containsSyntheticMedia": False},
    }


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
    ap.add_argument("slug", help="episode folder name, or `auth`")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--force", action="store_true", help="upload even if a video with this title exists")
    a = ap.parse_args()
    if a.slug == "auth":
        return auth()

    folder = VIDEOS / a.slug
    video = folder / f"{a.slug}.mp4"
    txt = folder / "youtube.txt"
    for need in (video, txt):
        if not need.exists():
            sys.exit(f"Missing {need}: run tools/fetch_episode.ps1 {a.slug}")
    script = json.loads((ROOT / "episodes" / a.slug / "script.json").read_text(encoding="utf-8"))
    short = script.get("format") == "short"
    thumb = folder / ("cover_short.jpg" if short else "thumbnail_D.jpg")
    meta = parse_youtube_txt(txt)
    check(meta)
    body = body_of(meta)
    print(f"{a.slug}: {video.stat().st_size / 1e6:.0f} MB, {'Short' if short else 'long'}, privacy {PRIVACY}")
    print(f"  title: {meta['title']}")
    print(f"  description: {len(meta['description'].encode('utf-8'))} bytes, {len(meta['tags'])} tags, category {body['snippet']['categoryId']}")
    print(f"  thumbnail: {thumb.name if thumb.exists() else 'NONE FOUND'}")
    print(f"  by hand in Studio: {'pin: ' + meta['pinned'] if meta['pinned'] else 'no pinned comment'}")
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
    print(f"  thumbnail set: {thumb_ok}; YouTube says: privacy {got['privacyStatus']}, processing {got.get('uploadStatus')}")
    if got["privacyStatus"] != PRIVACY:
        sys.exit(f"WARNING: the video is {got['privacyStatus']}, not {PRIVACY}. Check it in Studio now.")


if __name__ == "__main__":
    main()
