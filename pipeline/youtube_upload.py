"""Upload a rendered episode to YouTube as a PRIVATE video (never public, never scheduled).

  python pipeline/youtube_upload.py --slug nokia-intro --thumbnail A [--dry-run] [--force]

Needs env: YT_CLIENT_ID, YT_CLIENT_SECRET, YT_REFRESH_TOKEN (see tools/youtube_auth.py).
Reads out/<slug>/final.mp4, credits.txt, thumbnails/thumbnail_<X>.jpg and episodes/<slug>/script.json.
"""
import argparse
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from config import OUT_DIR, ROOT, secret  # noqa: E402
from schema import load_script  # noqa: E402

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.readonly",  # channel lookup + duplicate check
]
TOKEN_URI = "https://oauth2.googleapis.com/token"
PRIVACY = "private"  # hard-coded on purpose: publishing is always a manual decision in YouTube Studio


def build_body(script, credits_text: str) -> dict:
    meta = script.youtube
    if meta is None:
        raise SystemExit("script.json has no 'youtube' block (title, description, tags)")
    description = f"{meta.description.strip()}\n\n{credits_text.strip()}\n"
    for label, text in (("title", meta.title), ("description", description)):
        if "<" in text or ">" in text:
            raise SystemExit(f"YouTube rejects '<' and '>' in the {label}")
    if len(description) > 5000:
        raise SystemExit(f"description is {len(description)} chars (limit 5000)")
    tag_len = sum(len(t) + (2 if " " in t else 0) + 1 for t in meta.tags)
    if tag_len > 480:
        raise SystemExit(f"tags total {tag_len} chars (limit 500)")
    return {
        "snippet": {
            "title": meta.title,
            "description": description,
            "tags": meta.tags,
            "categoryId": meta.category_id,
            "defaultLanguage": "en",
            "defaultAudioLanguage": "en",
        },
        "status": {
            "privacyStatus": PRIVACY,
            "selfDeclaredMadeForKids": False,
            "containsSyntheticMedia": meta.contains_synthetic_media,
        },
    }


def service():
    from google.auth.exceptions import RefreshError
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build

    creds = Credentials(
        None,
        refresh_token=secret("YT_REFRESH_TOKEN"),
        token_uri=TOKEN_URI,
        client_id=secret("YT_CLIENT_ID"),
        client_secret=secret("YT_CLIENT_SECRET"),
        scopes=SCOPES,
    )
    try:
        creds.refresh(Request())
    except RefreshError as e:
        raise SystemExit(
            f"Could not refresh the YouTube token: {e}\n"
            "If the OAuth consent screen is still in 'Testing', tokens expire after 7 days: publish the app "
            "('In production') and run tools/youtube_auth.py again."
        )
    return build("youtube", "v3", credentials=creds, cache_discovery=False)


def channel_and_uploads(yt) -> tuple[str, str]:
    r = yt.channels().list(part="snippet,contentDetails", mine=True).execute()
    items = r.get("items", [])
    if not items:
        raise SystemExit("This Google account has no YouTube channel")
    ch = items[0]
    return ch["snippet"]["title"], ch["contentDetails"]["relatedPlaylists"]["uploads"]


def existing_with_title(yt, uploads_playlist: str, title: str) -> list[str]:
    r = yt.playlistItems().list(part="snippet", playlistId=uploads_playlist, maxResults=50).execute()
    return [i["snippet"]["resourceId"]["videoId"] for i in r.get("items", []) if i["snippet"]["title"] == title]


def upload_video(yt, path: Path, body: dict) -> str:
    from googleapiclient.errors import HttpError
    from googleapiclient.http import MediaFileUpload

    media = MediaFileUpload(str(path), mimetype="video/mp4", chunksize=8 * 1024 * 1024, resumable=True)
    req = yt.videos().insert(part="snippet,status", body=body, media_body=media)
    resp, retries = None, 0
    while resp is None:
        try:
            status, resp = req.next_chunk()
            if status:
                print(f"  uploaded {int(status.progress() * 100)}%", flush=True)
        except HttpError as e:
            if e.resp.status in (500, 502, 503, 504) and retries < 8:
                time.sleep(2**retries)
                retries += 1
            else:
                raise
        except (OSError, ConnectionError):
            if retries >= 8:
                raise
            time.sleep(2**retries)
            retries += 1
    return resp["id"]


def set_thumbnail(yt, video_id: str, thumb: Path) -> bool:
    from googleapiclient.errors import HttpError
    from googleapiclient.http import MediaFileUpload

    try:
        yt.thumbnails().set(videoId=video_id, media_body=MediaFileUpload(str(thumb), mimetype="image/jpeg")).execute()
        return True
    except HttpError as e:
        # Typically 403 when the channel is not eligible for custom thumbnails (e.g. phone not verified).
        print(f"WARNING: thumbnail was not set ({e.resp.status}): {e}. Set it manually in YouTube Studio.")
        return False


def summary(lines: list[str]) -> None:
    text = "\n".join(lines)
    print(text)
    path = os.environ.get("GITHUB_STEP_SUMMARY")
    if path:
        with open(path, "a", encoding="utf-8") as fh:
            fh.write(text + "\n")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--slug", required=True)
    ap.add_argument("--thumbnail", default="A", choices=["A", "B", "C"])
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--force", action="store_true", help="upload even if a video with the same title exists")
    a = ap.parse_args()

    out = OUT_DIR / a.slug
    video, credits_file, thumb = out / "final.mp4", out / "credits.txt", out / "thumbnails" / f"thumbnail_{a.thumbnail}.jpg"
    for f in (video, credits_file):
        if not f.exists():
            raise SystemExit(f"missing {f}")
    script = load_script(ROOT / "episodes" / a.slug / "script.json")
    body = build_body(script, credits_file.read_text(encoding="utf-8"))

    yt = service()
    channel, uploads = channel_and_uploads(yt)
    dupes = existing_with_title(yt, uploads, body["snippet"]["title"])

    lines = [f"### YouTube upload ({'DRY RUN' if a.dry_run else 'LIVE'})", f"- channel: {channel}",
             f"- title: {body['snippet']['title']}", f"- privacy: {PRIVACY}",
             f"- synthetic-media disclosure: {body['status']['containsSyntheticMedia']}",
             f"- video: {video.stat().st_size / 1e6:.1f} MB", f"- thumbnail: {thumb.name if thumb.exists() else 'NONE'}"]
    if dupes:
        lines.append(f"- already on channel with the same title: {', '.join(dupes)}")
    if a.dry_run:
        summary(lines + ["", "Dry run: nothing was uploaded.", "", "Description preview:", "```", body["snippet"]["description"], "```"])
        return 0
    if dupes and not a.force:
        summary(lines + ["", "Refusing to upload a duplicate title. Re-run with force=true if intended."])
        return 1

    video_id = upload_video(yt, video, body)
    thumb_ok = set_thumbnail(yt, video_id, thumb) if thumb.exists() else False
    summary(lines + ["", f"- **uploaded**: https://studio.youtube.com/video/{video_id}/edit (private)",
                     f"- thumbnail set: {thumb_ok}"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
