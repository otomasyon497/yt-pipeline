# Retention read, 2026-11-23

Source: YouTube Analytics API, `audienceWatchRatio` by `elapsedVideoTimeRatio` (filter `video==ID`, 2026-10-01 to
2026-11-23), mapped to paragraphs with `tools/yt_analytics.py` `script_times()`. Views: Maine 144, GERD 142,
Mongolia 113, Kansai 56, Colorado 44 (Colorado's curve is too thin to read beyond the first minute).

| Video | ~0:45 | 3:00 | 6:00 | 10:00 | end |
|---|---|---|---|---|---|
| Why Almost Nobody Lives in Northern Maine | 69 % | 54 % | 54 % -> 38 % | 19 % | 15 % |
| Why Mongolia Is the Emptiest Country on Earth | 83 % | 59 % | 27 % | 22 % | 20 % |
| Egypt Called This Dam an Existential Threat (GERD) | 60 % | 33 % | 27 % | 15 % | 12 % |
| Why Japan's $20 Billion Airport Is Sinking | 56 % | 29 % | 26 % | 21 % | 15 % |
| The US Cut Arizona's Water (Colorado) | 25 % | 12 % | 4 % | - | - |

## Drops and what was said there
- Maine 5:48, -15 points: c03p03, the Acadian families of June 1785 (settlement history inside the border chapter).
- Maine 8:46, -12: c04p04, the potato country around Presque Isle; 9:34, -8: Idaho passing Maine in 1957.
- Mongolia 0:36, -15: c01p02, borders, distance to the sea and three census figures in a row, still inside the hook.
- Mongolia 4:15, -15: c02p07, Roy Chapman Andrews' dinosaur eggs (1923), a side story at the end of the climate reason.
- GERD 0:47, -10: c01p03, "Egypt has called this dam an existential threat" (the news framing).
- Kansai 0:37, -15: c01p02, the operator's settlement figures; 1:33, -12: c02p02, Narita protests (background).

Lessons carried into docs/script-rules.md ("second read").
