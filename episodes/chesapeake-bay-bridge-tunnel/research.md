# Chesapeake Bay Bridge-Tunnel: research (round 1, 2026-11-22)

Status key: V = primary or official source read; A = secondary only (attribute or confirm); OWN = our calculation;
CHECK = not yet confirmed, do not script until it is.

## 1. Why there is a 17-mile gap of open water here (geology)
- V: About 35 million years ago (late Eocene) "a 2-mile-wide asteroid or comet" struck what is now the lower bay;
  "among the 20 largest known impact structures on Earth"; glassy melt particles fell "as far away as Texas and the
  Caribbean"; "Large tsunamis affected most of the North Atlantic basin." (USGS Fact Sheet 2015-3071, Powars et al.,
  https://www.usgs.gov/publications/chesapeake-bay-impact-structure)
- V: Buried "beneath 1,000 to 1,500 feet of rocky debris, sediment, and marine deposits"; identified by C. Wylie Poag
  (USGS) from cores (USGS and Virginia State Water Control Board) and seismic profiles (Texaco, USGS, National
  Geographic Society). (USGS image caption 2023, https://www.usgs.gov/media/images/chesapeake-bay-meteorite-impact-crater)
- V: Crater "approximately 200 km southeast of Washington, D.C.", buried 300-500 m beneath the southern bay and the
  peninsulas of SE Virginia; impactor 3-5 km (Poag, USGS FS 049-98, 1998). Impactor size differs by publication
  (2 mi / 2-3 mi / 3-5 km): say "a few miles wide".
- A: Diameter ~85 km (53 mi), centre near Cape Charles 37.28 N, 76.02 W (Earth Impact Database via Wikipedia). CHECK EID.
- A: "The impact crater created a long-lasting topographic depression that determined the course of local streams and
  the eventual location of the Chesapeake Bay" (Wikipedia; same idea in Poag FS 049-98 per search snippet). CHECK the
  USGS wording before scripting the causal claim.
- V: Deep groundwater in the crater is 100-145-million-year-old Early Cretaceous North Atlantic seawater, about twice as
  salty as today's sea (Sanford et al. 2013, Nature 503:252; USGS 70057876,
  https://www.usgs.gov/centers/chesapeake-bay-activities/science/oldest-large-body-ancient-seawater-identified-under).
- A (NPS / USGS FS 102-98 via search): ~18,000 years ago sea level ~100 m lower; by ~10,000 years ago the ancient
  Susquehanna valley was flooded; bay took its present shape ~3,000 years ago; old river channel still the bay's deep
  trough. CHECK https://www.nps.gov/cajo/learn/nature/chesapeake-climate-history.htm and chesapeakebay.net geology.

## 2. The sinking shore (sea level), OWN from NOAA
NOAA CO-OPS sea-level trends API (fetched 2026-11-22,
https://api.tidesandcurrents.noaa.gov/dpapi/prod/webapi/product/sealvltrends.json):
- Sewells Point, Norfolk (8638610): +1.90 +/- 0.04 in/decade, 1927-2025 (= 4.8 mm/yr; ~18.6 in over 98 years).
- Highest of all 23 US Atlantic gauges whose records begin by 1935 (next: Sandy Hook 1.68, Atlantic City 1.67;
  Boston 1.17, The Battery 1.16, Key West 1.04, Portland 0.78). OWN ranking, method: API list, station ids
  8410000-8725000, startDate year <= 1935, sort by trend.
- Chesapeake Channel (8638901, the gauge on the bridge-tunnel, combined with 8638863): +2.42 +/- 0.11 in/decade,
  1975-2025 (~1 ft in 50 years). Kiptopeke (Eastern Shore end, 8632200): +1.58 in/decade since 1951.
- V: Virginia has "the highest rates of relative sea level rise along the entire Atlantic Coast"; causes: groundwater
  withdrawal and aquifer compaction, post-glacial adjustment (forebulge collapse) (USGS Land Subsidence on the Virginia
  Coastal Plain).
- V: Hampton Roads subsidence 1940-1971 averaged 2.2 mm/yr (1.1-4.8); GPS 2006-2011 3.1 mm/yr; extensometers Franklin
  1.5 and Suffolk 3.7 mm/yr (1979-1995); causes include "ongoing shifts associated with the Chesapeake Bay meteor impact
  crater"; Sewells Point >200 flood hours/yr in recent years vs >50 h only 7 times 1927-1990 (Bekaert et al. 2017,
  Sci Rep 7:14752). Say the crater is "one of the causes" only, as the paper does.

## 3. The Navy
- V: The Naval Station Norfolk land was the 1907 Jamestown Exposition site; officers judged it ideal for a base (CNIC,
  https://cnrma.cnic.navy.mil/Installations/NAVSTA-Norfolk/About/); base established 1917 (proclamation 28 Jun 1917, CHECK
  history.navy.mil page). "Largest naval base in the world": Navy/CNIC wording CHECK; Bekaert 2017 says it.
- A: The Navy objected to bridging Thimble Shoal Channel: a collapse (possibly by sabotage) could cut the base off from
  the Atlantic (Wikipedia citing Forster; virginiaplaces: "objected to any bridge across the channel"). Maryland wanted
  the Chesapeake Channel kept open (virginiaplaces). CHECK a primary (CBBT history page, 1950s press). Attribute if not.
- V: Hampton Roads Bridge-Tunnel 1957 (3.5 mi) was the model (ASCE 2021; virginiaplaces).

## 4. Before 1964: the ferry
- A: Virginia Ferry Corporation, Little Creek - Cape Charles (moved to Kiptopeke 1951); up to 90 one-way trips a day
  (Wikipedia) ; ferry of up to 60 cars took 90 minutes for 18 miles (virginiaplaces). Ferry Commission created 1954,
  bought VFC 1956 (dates differ). CHECK Encyclopedia Virginia / CBBT history.

## 5. Building it (1960-1964)
- V: $200 M revenue bonds sold to private investors in 1960, paid back by tolls, no local/state/federal tax money (CBBT
  history; Encyclopedia Virginia). Construction began Oct 1960 (ASCE; CBBT says Sep), opened 15 Apr 1964, 42 months.
- V: 17.6 mi shore to shore, 23 mi with approaches; >12 mi trestle, two one-mile tunnels, two bridges, ~2 mi causeway,
  four islands ~5.25 acres each (CBBT history; ASCE). 1965 ASCE "Outstanding Civil Engineering Achievement" and one of
  "Seven Engineering Wonders of the Modern World" (>100 projects) (CBBT).
- A: Designed by Sverdrup & Parcel; contractors Tidewater Construction and Merritt-Chapman & Scott; seven workers killed
  (Wikipedia). CHECK deaths in a contemporary source.
- A: Tube sections steel, 300 ft long, 35 ft across, built in Orange, Texas, 37 per tunnel, two broke free in the Gulf
  and were recovered; 858 spans 30 ft above water; longest pile 172 ft; bedrock >6,000 ft down; granite 2-4 t from
  Lunenburg County (virginiaplaces). Rival says 2,600 piles; virginiaplaces says 4,805: CHECK.
- A: Ash Wednesday storm March 1962 destroyed the "Big D" pile-driving platform (virginiaplaces; Wikipedia; rival says no
  one died and 3.5-month delay: CHECK). NWS/NOAA page on the 1962 storm for dates.

## 6. The bay pushes back
- A: Dec 1967 coal barge Mohawk broke anchor, hit the trestle, closed ~2 weeks; 21 Jan 1970 USS Yancey dragged anchors
  in a gale and knocked out ~375 ft of trestle (Hampton Roads Naval Museum blog 2023: six other ships dragged anchor
  that night; five spare 75-ft spans stockpiled); 1972 barge, 2 weeks (Wikipedia refs: Daily Press 2002, Washington Post
  1984, DANFS). CHECK DANFS / HRNM blog text.
- A: Vehicles over the side: "17th over-the-side accident since 1984" (2023); "By July 2023, a total of 20 people had
  died in over-the-side accidents"; Feb 2026 Perdue truck through the southbound guardrail (virginiaplaces). Counts
  differ: say "more than a dozen".
- A: Wind restrictions start at 40 mph; trucks banned at 60 (virginiaplaces); exact levels CHECK cbbt.com.
- V: Parallel trestles opened 19 Apr 1999 (1995 contract $197,185,777); tunnels left single-tube "due to financial
  constraints" (CBBT history).

## 7. Chessie
- V (CBBT news "project milestone"): mining began Feb 2023; May 2023 Chessie struck "a large ship's anchor"
  "manufactured in England at the turn of the 20th century"; eight more months of work to remove it; tunnelling resumed
  May 2024 at ~50 ft/day; breakthrough 27 Jan 2025 after "more than 6,300 feet" at Two Island; ~10,000 segments; TBM by
  Herrenknecht, 43 ft cutterhead, 308 ft long; completion forecast "early 2028"; two southbound lanes.
- V: 2016 contract $756,987,318; funding 37 % toll bonds, 30 % TIFIA loan, 29 % CBBT general fund, 4 % VTIB (CBBT).
- A: Chesapeake Channel parallel tunnel "in 25-35 years" (virginiaplaces) / 2035-2040 (Wikipedia). CHECK CBBT.

## 8. Traffic
- A: >140 million vehicles by Jan 2021 (Wikipedia); 3.5-4 M a year (virginiaplaces, inconsistent); saves ~90-95 mi.
  CHECK CBBT annual report.

## Gaps to fill in round 2
EID crater entry; USGS wording on crater -> bay location; NPS/CBP bay-formation dates; CBBT history page for ferry,
Navy, deaths, 1962 storm; NWS 1962 storm; DANFS Yancey; CBBT wind policy page; Naval Station Norfolk official "largest";
CBBT traffic; pictures (Commons/NARA/LoC 1960s construction photos, Sentinel views of the islands, NASA crater figure).

# Round 2 (2026-11-22)
- V (NPS Captain John Smith Chesapeake NHT, "Chesapeake climate history", updated 17 Sep 2024): "about 35 million years
  ago, a large bolide collided with the Earth near what is now the lower Delmarva peninsula"; "This large depression
  helped determine the location of the Chesapeake Bay when it began forming millions of years later." Glaciers began to
  melt 18,000 years ago; the Susquehanna valley "gradually filled with water and became a wide Bay"; modern shape
  "about 3,000 years ago". -> script: the crater did NOT dig the bay; it left a low spot the rivers bent toward.
- A (virginiaplaces chesgeo): ~9-10,000 years ago the rising ocean submerged the mouths of the James and Susquehanna;
  old Susquehanna paleochannels (Exmore, Cape Charles channels); "Later rivers curved towards the low spot of the impact".
- V (CBBT weather page, "may change at any time"): Advisory 35 mph: limit 45, no passing; Level 1 at 40 mph: no
  motorcycles, campers, anything towed, box/rental trucks, buses, empty tractor-trailers; Level 2 at 50 mph: only cars,
  pickups without cargo, minivans, SUVs; Level 3 at 60+ mph: closed.
- A (Hampton Roads Naval Museum blog, 13 Jul 2023, from the 1971 ruling): 21 Jan 1970 gusts 35-50 knots; Yancey struck
  the trestle at 1:37 and 3:30 am; "A 400-foot gap" (Wikipedia: 375 ft: say "about 400 feet"); "6 other ships dragged
  anchor that night"; five spare 75-ft spans stockpiled; reopening reported for ~5 Mar 1970; Yancey was the 4th vessel to
  strike the bridge (1966, 1967 x2). No injuries reported.
- V (Encyclopedia Virginia): private ferries until the crossing; 1954 Chesapeake Bay Ferry Commission; "More than eighty
  million vehicles" (old figure: do not use).
- Failed (do not retry): chesapeakebay.net (403), history.navy.mil (refused, TLS), cnrma.cnic.navy.mil (403),
  weather.gov akq 1962 page (404), ENR (403), WHRO (DNS), pubs.usgs.gov PDFs (403).
- Still CHECK: Navy objection primary (attribute to "accounts of the project" or CBBT if not found), 7 deaths, Big D /
  1962 storm details, Naval Station Norfolk founding and "largest" wording.

# Gate-1 outline (draft, ~2,850 words, 8 chapters)
Working title: "Why This American Highway Dives Under the Sea" (alt: "Why Virginia Built a Highway Into the Atlantic").
Cover idea: aerial photo of an island where the road drops into the tunnel; words "THE ROAD / GOES / UNDER".
1. Cold open (~250): drive out 17 miles from shore; the road drops onto a 5-acre island and into the sea; ships pass
   over the cars. Two questions: why is there 17 miles of open water here, and why does the road go under? Open loop:
   the gauge on this bridge-tunnel shows the sea about a foot higher than in 1975.
2. A hole older than the bay (~400): 35 Ma impact, among the 20 largest on Earth; buried 1,000-1,500 ft; the low spot
   set where the bay formed; Ice Age, Susquehanna valley drowned ~10,000 years ago; shape ~3,000 years ago; the deep
   channels ships use follow old river valleys (CHECK wording). Map: crater ring + bay + old channels.
3. Cut off (~300): the Eastern Shore of Virginia, a peninsula within sight of Norfolk; private ferries, 90 minutes,
   1954 commission; HRBT 1957 shows a bridge can dive under a channel.
4. The Navy's veto (~350): Hampton Roads, the Navy's Atlantic base (Jamestown Exposition site, 1917 CHECK); the deep
   Thimble Shoal Channel; a fallen bridge could bottle up the fleet (attributed); Maryland's Chesapeake Channel: two
   tunnels, four islands.
5. Building land in the sea (~450): $200 M of bonds, no tax money; islands of sand and granite; steel tubes from Orange,
   Texas; piles to 172 ft, bedrock >6,000 ft down (the crater fill); March 1962 storm wrecks Big D; open 15 Apr 1964,
   42 months; 1965 "Seven Engineering Wonders".
6. The bay pushes back (~400): Yancey 1970, a 400-ft gap, six other ships dragging anchor; wind rules at 35/40/50/60
   mph; trucks over the side (say "more than a dozen"); 1999 second trestle, tunnels still one tube.
7. Chessie and the anchor (~300): $757 M contract, Feb 2023 start, May 2023 the anchor from early-1900s England, 8
   months lost, breakthrough 27 Jan 2025 after 6,300 ft, opening forecast early 2028; Chesapeake Channel tube decades away.
8. The sinking ground (~400): Sewells Point +1.90 in/decade since 1927, highest of 23 long-record US Atlantic gauges
   (OWN); the bridge-tunnel's own gauge +2.42 in/decade since 1975; land sinks (pumped aquifers, post-glacial settling,
   the crater among the causes); 145-million-year-old seawater still trapped below. Closing question for comments:
   should the next tube be built for the sea of 2100?
