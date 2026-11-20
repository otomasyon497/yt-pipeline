# Mississippi: gate 1 outline (draft, 2026-11-20)

Title: **Why the Mississippi Wants to Leave New Orleans** (47 chars)
Cover (cover_photo.py): bright aerial of the Old River Control structures with the two rivers, words "IT WANTS / OUT".
Demand: PASS (5 videos at 3x). Competitors: competitors.md. Facts: research.md.

Word budget: ~2,850 words -> episode_check estimate 17.9 min; at Venice's real pace (2,671 w = 15.8 min) ~16.9 min.

| Part | Words | Carries it | Pictures |
|---|---|---|---|
| Hook: the river past New Orleans carries the water of ~40 % of the lower 48; "But" 300 miles upstream it is trying to leave; teasers (a fire on a log jam, a 1953 deadline, a night in April 1973 when the gates almost went); question by 0:30: why does the biggest river in North America want to abandon its own cities, and what holds it? | 250 | Corps brochure, NASA | painted map: the basin, then the lower river in red; Sentinel-2 of Old River |
| 1. Rivers like this do not stay put | 450 | delta cycle, "at least seven times", 200-mile arc, old bayous Lafourche and Teche | painted Louisiana with old channels as routes; Sentinel-2 of Bayou Lafourche towns on the ridge |
| 2. A shorter road next door | 400 | Turnbull's Bend, Red River capture, 142 vs 315 miles | painted map of both routes with lengths; Sentinel-2 Old River |
| 3. People opened the door | 450 | Shreve's cut 1831, the raft fire 1839, clearing to 1855, share 5 % -> 25-30 % | Sentinel-2: the oxbow left by the 1831 cut; chart of the Atchafalaya's share; Fisk 1952 plate |
| 4. The deadline and the gates | 450 | Fisk "1965-75", Corps "by 1990", 1954 law, 70/30, structures, lock | stat cards, Sentinel-2 close views of Low Sill / Overbank / Auxiliary / Murray / lock; USACE photos |
| 5. April 1973 | 400 | wet winter, wing wall, scour hole, 37 -> 22 ft head, Morganza first opened, Auxiliary 1986, Murray 1990 | archive photos (USACE), stat cards; Morganza 2011 satellite (EO-1 / Landsat) |
| 6. The river is already winning somewhere | 300 | Wax Lake / Atchafalaya deltas growing (only growing land) vs ~4,800 km2 lost; our Landsat measurement | Landsat wipe 1984 -> 2025 at Atchafalaya Bay; USGS land-loss chart |
| Ending: what leaving would look like (2023 salt wedge, the corridor, drinking water) + question | 250 | 2023 sill, Port of South Louisiana, New Orleans intakes | Sentinel-2 of the refinery corridor, sill photos, question card |

Question for the comments (draft): "Should the Corps keep holding the Mississippi in place forever, or let it move
and rebuild the coast?"

Open: the per-lobe delta ages (sources disagree: keep them off screen); the 1953 report wording (NASA attribution).
</content>
</invoke>
<invoke name="Bash">
<parameter name="command">cd /c/projeler/yt-pipeline; python tools/episode_check.py --words 2950; git add episodes/mississippi-old-river && git commit -qm "Mississippi: research.md (Corps brochure, Fisk 1952, NASA, USGS, USACE sill) and gate-1 outline

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" && git push -q && echo ok