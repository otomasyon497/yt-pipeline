# Music

Put background tracks from the YouTube Audio Library here (`.mp3`, `.wav`, `.m4a`, `.ogg`, `.flac`).

- `"music": "auto"` in script.json picks one track (stable per episode slug).
- `"music": "some-file.mp3"` picks a specific file. `"music": "none"` disables music.
- If the track requires attribution, add it to `credits.json` so it lands in credits.txt:

```json
{ "some-file.mp3": "\"Track Title\" by Artist - Music provided by YouTube Audio Library" }
```

Check each track's licence in the Audio Library (some need attribution, some are for YouTube use only).
The music is ducked under the narration automatically.
