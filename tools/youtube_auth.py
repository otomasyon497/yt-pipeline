"""One-time YouTube OAuth setup. Run this on YOUR PC (it opens a browser for Google consent).

  pip install google-auth-oauthlib
  python tools/youtube_auth.py "C:\\path\\to\\client_secret.json"

It stores YT_CLIENT_ID, YT_CLIENT_SECRET and YT_REFRESH_TOKEN directly as GitHub secrets through the
gh CLI. Nothing secret is printed or written to disk by this script.
"""
import argparse
import json
import subprocess
import sys

from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.readonly",
]


def set_secret(repo: str, name: str, value: str) -> None:
    subprocess.run(["gh", "secret", "set", name, "--repo", repo], input=value, text=True, check=True)
    print(f"  set secret {name}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("client_secret_json")
    ap.add_argument("--repo", default="otomasyon497/yt-pipeline")
    a = ap.parse_args()

    with open(a.client_secret_json, encoding="utf-8") as fh:
        client = json.load(fh)["installed"]  # a 'Desktop app' OAuth client

    flow = InstalledAppFlow.from_client_secrets_file(a.client_secret_json, SCOPES)
    creds = flow.run_local_server(port=0, access_type="offline", prompt="consent")
    if not creds.refresh_token:
        print("Google returned no refresh token. Revoke this app at myaccount.google.com/permissions and retry.")
        return 1

    set_secret(a.repo, "YT_CLIENT_ID", client["client_id"])
    set_secret(a.repo, "YT_CLIENT_SECRET", client["client_secret"])
    set_secret(a.repo, "YT_REFRESH_TOKEN", creds.refresh_token)
    print("Done. You can delete the client_secret.json file or keep it somewhere safe outside the repo.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
