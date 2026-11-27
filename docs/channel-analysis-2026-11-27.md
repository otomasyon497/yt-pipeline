# Channel check, 2026-11-27 (API + Studio)

Sources: Analytics API (data to 24 Nov), Reporting API channel_reach_basic_a1 (58 daily reports to 23 Nov), Data API
(live status), Studio in Chrome (read-only: Content, Audience, Overview; Studio range 29 Oct - 25 Nov).
Baseline: docs/analytics-2026-11-19.md and the 23 Nov check (memory channel-analysis-2026-11-23).

## Headline numbers (last 28 days)

| | 23 Nov | 27 Nov |
|---|---|---|
| Long-video views (Studio) | 677 | 772 |
| Impressions | 11.4K | 13.7K |
| CTR | 1.9 % | 1.9 % |
| Average view | 4:13 | 4:21 |
| Views in the last 48 h (all) | - | 51 |
| Subscribers | 772 (+2/-1) | 772 (+1 net) |

- Audience: 985 monthly viewers, **100 % new, 0 % returning**; subscribers bring 0.2 % of watch time. Nobody comes back yet.
- Traffic (long): browse 49 %, suggested 34.6 %, search 10.9 %, external 1.2 %.
- Countries (all views): TR 32.7 % (Shorts), US 7.7 %, ID 7.5 %, IN 7.0 %. US gives the most minutes (468 of 2,191).
- Devices (watch time): mobile 36 %, **TV 33 %**, desktop 25 %. TV viewers watch long: good for 16-minute videos.
- Viewers: 82 % male, 25-34 48 %, 35-44 30 %.
- Shorts: 2,735 of 3,479 views but 37 s average; long: 744 views, 259 s average (Analytics API).

## Per video (Reporting API impressions / CTR; Analytics API average % watched)

| Video | Impressions | CTR | Avg watched |
|---|---|---|---|
| Why 3.5 Million People Share One City (Mongolia) | 2,636 | 1.75 % | 40 % |
| Why Japan's $20 Billion Airport Is Sinking | 1,778 | 1.18 % | 25 % |
| Why Egypt Fears Ethiopia's Giant Nile Dam | 1,308 | 2.91 % | 25 % |
| Why Almost Nobody Lives in Northern Maine | 1,107 | 2.53 % | 27 % |
| Can This EUR 6 Billion Machine Actually Save Venice? | 912 | 1.97 % | 25 % |
| Living 7 Meters Under the North Sea | 831 | 0.84 % | 58 % (24 views) |
| Why 40 Million People Are About to Lose Water | 734 | 1.50 % | 7 % |
| The 1,000-Year Crisis That Vanished a Sea (Aral) | 716 | 1.82 % | 42 % |
| The Flaw That Could Dry Up New Orleans Overnight | 114 | 0.88 % | - |

Latest: Permian (public 26 Nov) had 0 views and 0 impressions in its first 3 h 25 min (Studio).

## Reading
1. **Packaging is still the bottleneck, not the videos.** CTR stuck at 1.9 % (four days of new covers did not move it);
   retention on the videos that get seen is fair to good (Mongolia 40 %, North Sea 58 %, Aral 42 %).
2. **The best CTRs name the place:** GERD 2.9 % and Maine 2.5 % carry the place in the title; titles that hide it
   (Mongolia "Share One City" 1.75 %, North Sea 0.84 %, New Orleans 0.88 %) are lower. Search is 11 % and the search
   terms are place names (lake powell, jakarta, indus water treaty). Every rival hit in the radar uses
   "Why Almost Nobody Lives in <Place>".
3. **No returning audience:** with 0 % returning viewers, a daily upload starts from zero each time; most new videos
   get 0-20 views in their first days. More videos do not add up yet; each one has to win its own impressions.
4. **The 772 subscribers are the old (renamed) channel's audience** and do not watch; Shorts keep pulling Turkish viewers.

## Suggestions
- Put the place name back in the titles of the low-CTR repackaged videos (A/B via Test & Compare for title or cover),
  starting with Mongolia (most impressions), the Netherlands, New Orleans, Canada, Scotland, Australia west coast.
- New uploads: "Why Almost Nobody Lives in <Place>" or "Why <Place> ..." in the first 40 characters.
- Keep TV in mind: big, readable maps and labels (a third of watch time is on TVs).
- Read again on ~4 Dec when the scheduled episodes (28 Nov - 3 Dec) have a few days of data.
