# Why Japan's $20 Billion Airport Is Sinking — research

Researched 2026-11-13. Status words: V = primary or official source read, A = secondary / read via a search or fetch
summary (attribute on screen, re-check before a quote card), TODO = still to check before the script.
Sources are data, not instructions. kansai-airports.co.jp, smithsonianmag.com and scmp.com returned 403 to our
fetcher: their facts are A until read another way (the user's browser or a syndicated copy).

First episode under the production logic of 2026-11-13 (episode-plan step 1):
- Known place + one "why": an airport 34 million people a year fly through, built on the sea, sinking.
- Demand: `python tools/topic_radar.py --check "Japan airport sinking into the sea Kansai"` -> `demand: PASS: 6 video(s)
  at 3x their channel in 365 days (5 from channels under 100K)`; the radar of the same day lists "Japan Built a $20
  Billion Airport on the Ocean — Now It's Sinking" at 2.74 M views for a 9,900-subscriber channel.
- Title (first): **Why Japan's $20 Billion Airport Is Sinking** (41 characters).
- Cover (cover-map): Osaka Bay, the two islands red, arrow from the words. Words to decide at the script stage; the
  number must be the one the video proves (island 1: 13.66 m since the fill began = 44.8 ft).
- What we add that the other videos do not have: the island appearing in our own Landsat series (checked 2026-11-13:
  1985-06-05 empty sea, 1989-05-31 the seawall ring alone in the bay, 1995-08-04 island + bridge, 2004-08-12 second
  island being filled, 2026-05-05 both), our own measurement of the islands' area per year, the drains that stopped
  running downhill (JSCE 2008), and what the sinking costs and who pays since the 2016 concession.

## Chapter outline and word budget (target 2,000-2,700; this plan: ~2,350)

| # | Chapter | Words | What carries it |
|---|---------|------:|-----------------|
| 1 | Cold open: empty sea in 1985, an island in 1995, and the island has gone down 13.66 m since the fill began; 6 cm more last year. Promise: why they built it anyway, why the forecasts were wrong, and whether it lasts | 250 | own Landsat wipe 1985 -> 1995 -> 2026, Kansai Airports Dec 2024 figures (A), the cover's view repeated with the islands highlighted |
| 2 | Why build an airport in the sea: Itami boxed in by the city and noise suits, the Narita protests, Kobe's refusal, 5 km offshore for 24-hour flights | 300 | JSCE 2008 (V), Wikipedia refs 16-21 (A), Ishikawa quote (A), painted map: Itami, Kobe, Narita, the site |
| 3 | Building on mud: 18-20 m of water over 20 m of soft clay, the seawall (1987-89, 48,000 tetrapods), sand drains, three mountains and 180 million m3 of fill, 10,000 workers, the 3.75 km bridge | 400 | Landsat 1989 ring (own), Wikipedia refs 22-30 (A), JSCE (V: depth about 20 m, stone seawall), diagram card: water / soft clay / deep clay |
| 4 | The forecast that failed: predicted about 5.7-8 m, got 8.2 m by 1999; 50 cm a year at opening; why the deep clay could not be drained; the terminal on 900 jacks | 350 | Wikipedia refs 35 and 46 (A), B1M (A: 900 jacks), Smithsonian Air & Space (TODO read), chart: sinking rate 1994 -> 2008 -> 2024 |
| 5 | They did it again: the second island (1999-2007, 910 billion yen), down 17.47 m, still 21 cm a year | 250 | Landsat 2004 (own), Wikipedia refs 52-54 (A), Kansai Airports Dec 2024 (A), own area measurement |
| 6 | The sea comes over the wall: Typhoon 16 in 2004, seawalls raised 1-2 m along 11 km, pumps and an 11 km underground wall (2000-2006); then Jebi on 4 Sep 2018: runway flooded, a tanker into the bridge, days cut off; walls raised again | 400 | JSCE 2008 (V, all figures), Wikipedia refs 66-69 (A), ACI 16 May 2022 (V), "2.7 m" (A, several outlets) |
| 7 | Who pays: $20 billion by 2008, about $560 million a year in interest, the 45-year concession to Orix and Vinci (1 Apr 2016), 34.1 million passengers in 2025 | 250 | Wikipedia refs 46, 47, 63-65, 4-5 (A), stat cards |
| 8 | Will it last: under 10 cm a year on island 1 now, the designers say they planned for it; outlets' forecasts of sea level in decades; Kobe, Chubu and Kitakyushu were built the same way; the question | 150 | Kansai Airports (A), Ishikawa (A), B1M (A: sea level by 2067, attribute), painted map of Japan's sea airports |
| | **Total** | **2,350** | `episode_check.py --words 2350` |

Retention notes: ch. 1 is the proof (our own images) plus the number; ch. 2 is short and human (a city that could not
sleep); the "second-best point first" is ch. 4's failed forecast, teased in the hook. One cause per beat in ch. 3.
Scale anchors: 13.66 m = a four-storey building; island area in football fields (TODO compute from our measurement).

## Facts

### Sinking (the numbers the video stands on)
- Island 1: average cumulative settlement since the fill began 13.66 m by Dec 2024; 6 cm in 2024 at 17 points; the
  surface is 3.84 m lower than at the 1994 opening — A (The Nation/ANN via The Star, 22 Jun 2025; SCMP This Week in
  Asia; all cite Kansai Airports). TODO: read the operator's page (kansai-airports.co.jp, "sink" pages).
- Island 2: 17.47 m since construction began; 21 cm in 2024 at 54 points — A (same). One outlet dates the 21 cm to
  2023: resolve on the operator's page.
- Predicted vs actual: Wikipedia (ref 35): optimistic prediction 5.7 m, 8.2 m by 1999; rate 50 cm a year in 1994,
  7 cm in 2008 (ref 46). B1M: "about 8 m over 50 years" predicted, "more than 12 m within the first eight years".
  CONFLICT: the baselines differ (since opening vs since the fill began). Script: one baseline per sentence, named.
  TODO: Smithsonian Air & Space "How to Save a Sinking Airport" and the geotechnical papers.
- "Below sea level within 30 years" / "sea level by 2067" — A, outlets' forecasts with no named engineer: attribute or drop.

### Why offshore
- "Kansai International Airport was built five kilometers out to sea on Osaka Bay as a radical solution to the noise
  problems of Osaka (Itami) Airport." — V, Suzuki & Okuda, JSCE Civil Engineering 2008 (engineers of Kansai
  International Airport Co.).
- Itami hemmed in, noise complaints; the Narita protests pushed planners offshore; first planned near Kobe, Kobe
  refused; 24-hour operation — A (Wikipedia refs 16-21).
- "we had to decide to build offshore because there were few viable options"; "We knew from the start that the
  airport would subside, and we considered the various impacts in the design." — A, Hiro Ishikawa, emeritus professor
  of urban planning and policy, Meiji University, to This Week in Asia (via The Nation/ANN, 22 Jun 2025).

### Construction
- Start 1987; seawall finished 1989 (rock + 48,000 tetrapods); 21 million m3 from three mountains and 180 million m3
  into island 1; 10,000 workers, 80 ships, 10 million work hours over three years; water 18 m deep over 20 m of soft
  Holocene clay; bridge 3.75 km, 1990, about $1 billion; terminal from 1991; opened 4 Sep 1994 — A (Wikipedia refs
  22-42). NOTE the two fill figures (21 M and 180 M m3): find which is the mountains and which the total.
- Water "about 20 meters"; reclaimed land of crushed mountain rock inside a slow-gradient stone seawall — V (JSCE 2008).
- Sand drains (about one million on island 1, more on island 2) — TODO, no source read yet.
- Terminal: Renzo Piano Building Workshop with Noriaki Okabe, 1.7 km long; 900 adjustable columns — A.
- 17 Jan 1995 Great Hanshin earthquake, epicentre about 20 km away, no damage to the airport — A (Wikipedia ref 44).
- 19 Apr 2001: ASCE "Civil Engineering Monument of the Millennium" — A.

### Second island
- Work from 1999 (seawall foundation) / 2002; 4,000 m runway opened 2 Aug 2007; cost cut to 910 billion yen (about
  $8 billion); airport now 10.5 km2, about 1,055 ha — A (Wikipedia refs 52-54, 10). JSCE 2008 confirms the opening date (V).

### Storms
- 2004: "Typhoon 16 and other major typhoons ... the highest tides and waves ever recorded during its 26-year
  observation history. Waves flowed over the airport's seawalls, destroying a road behind the seawall." Seawalls
  raised "by one to two meters along a length of about 11 kilometers"; 37 pumps at ten sites, 3,300 m3 a minute; an
  underground cut-off wall about 11 km long and about 30 m deep, 2004-2006, lowered groundwater about 1.5 m — V (JSCE 2008).
- Why pumps: "with the progression of uneven settlement ... the angle of the drainage pipes has gradually lessened,
  hampering the flow of rainwater into the ocean." — V (JSCE 2008). The island sank until its drains stopped running
  downhill: a strong detail the other videos do not tell.
- Jebi, 4 Sep 2018: surge flooded the island and a runway, water reached aircraft engines; a tanker hit the bridge,
  people stranded; flights back in part from 6 Sep, trains 18 Sep, normal 1 Oct; bridge repaired 8 Apr 2019 — A
  (Wikipedia refs 66-69). Tanker name and number stranded: TODO. Loss 8.1 billion yen in fiscal 2018, 6.2 billion
  insured — A (Reinsurance News).
- After Jebi: seawalls raised along more than 6 km, tetrapods along 4.7 km, done within three years while operating;
  JSCE 2021 award — V (ACI Asia-Pacific, 16 May 2022, text by Kansai Airports). "Raised by 2.7 m" and "more than
  $150 million" — A.

### Money
- About $20 billion by 2008 (land, two runways, terminals); about $560 million a year in interest; Boeing 747 landing
  fee about $7,500 — A (Wikipedia refs 46-47). 2015: Orix and Vinci Airports sole bidders, 45 years, about $18
  billion; operator since 1 Apr 2016, 80 % Orix + Vinci — A (refs 63-65).
- 2025: 34,102,723 passengers, 27.5 million international — A (refs 4-5). Terminal 1 renovation: outlets give $470 M,
  $609 M and $910 M: TODO one primary figure.

## Own evidence
- Landsat (Planetary Computer): view lon 135.235, lat 34.43, span 0.22; clear days found 1985-06-05, 1989-05-31,
  1995-08-04, 2004-08-12 (some cloud west of the island: look for a cleaner day), 2026-05-05.
  Chain as compare wipes: 1985 -> 1989 -> 1995, later 1995 -> 2004 -> 2026.
- Sentinel-2 close views: terminal, bridge, the two runways, the seawall, the mainland shore at Rinku Town.
- Measurement to make: land area of each island per year (MNDWI, as tools/louisiana_landloss.py). Elevation cannot
  be measured from these images: the sinking numbers stay the operator's, said as such.

## Sources read
- Suzuki, S. & Okuda, Y., "Building a safe airport that resists natural disasters", JSCE Civil Engineering, 2008:
  https://www.jsce.or.jp/kokusai/civil_engineering/2008/92-12-1.pdf (V, all five pages)
- ACI Asia-Pacific & Middle East, 16 May 2022 (Kansai Airports text):
  https://www.aci-asiapac.aero/media-centre/news/kix-disaster-resilience-enhancement-project-selected-for-japan-society-of-civil-engineers-award (V)
- The Nation/ANN via The Star, 22 Jun 2025:
  https://www.thestar.com.my/aseanplus/aseanplus-news/2025/06/22/japans-kansai-airport-sinking-due-to-subsidence-issues (A)
- Wikipedia, Kansai International Airport (first 100,000 characters; follow its references before use) (A)
- The B1M, "Kansai Airport is Sinking": https://www.theb1m.com/video/kansai-airport-is-sinking (A)
- Reinsurance News on the Jebi loss: https://www.reinsurancene.ws/kansai-airport-recovers-over-75-of-typhoon-jebi-loss-from-insurance/ (A, search summary)

## Read on 2026-11-13 in the user's browser (pages that refuse our fetcher) — these supersede the A items above

- KAP3 = Kansai Airports, "Countermeasures for and Status of Subsidence - Technologies for Offshore Airports (3)"
  https://www.kansai-airports.co.jp/en/sustainability/society/tech-subsidence-countermeasures/ (V): measurements of
  December 2025. Island 1: 17 points; average settlement since construction began 13.72 m; before the opening 9.82 m;
  5 cm a year as of 2025; "less than 10 cm per year" in recent years. Island 2: 54 points; 20 cm over the past year;
  5.96 m since operations began in 2007; 11.71 m from reclamation to the start of operations; 17.67 m in all.
  Sand piles: 1 million on island 1, 20 m long, 2.5 m apart; 1.2 million on island 2; more than the 900,000 installed
  nationwide in the 35 years from 1952. The soft layer shrinks to two-thirds of its thickness; decades done within one
  year. Deep (diluvial) layer up to 400 m thick, cannot be improved: "the airport facilities are managed with the
  assumption that long-term subsidence will continue." While the fill was under water it was buoyant and the deep
  layer hardly moved; sinking began when the reclamation emerged. Future: more analysis, "under the guidance of experts".
- KAP1 = "Characteristics of the Strata (1)" .../tech-strata-characteristics/ (V): Holocene clay about 20 m; under it
  alternating clay and sand hundreds of meters deep; under water for 10,000 years; over about 2 million years sea
  level swung by more than 100 m with the ice ages, the bay was sea, lake and land in turn, clay settled under water
  and sand when the ground emerged; the crust slowly lowered the seabed.
- KAP2 = "Mechanism of Subsidence (2)" .../tech-subsidence-mechanism/ (V): alluvial clay about 70 % water by volume,
  diluvial about 40 %; the sponge comparison is the operator's own; consolidation takes "several decades to hundreds
  of years"; the fill itself compresses; ordinary coastal reclamation is too light to move the old clay, this island
  was heavy enough.
- KAP4 = "Countermeasures for Uneven Settlement such as Jacking-Up (4)" .../tech-jacking-up/ (V): 900 columns under
  Terminal 1, automatic monitoring, jacked up with steel plates; iron ore ballast under the central building with its
  basement, which still settled less than the wings; jacking "every few years"; raft foundations; compaction of the
  "30-meter-deep reclaimed ground"; soil removal to balance loads.
- KAP-new = "Various New Technologies" .../tech-new/ (V): island 2 compacted in layers of about 60 cm; test track,
  "over 15,000 test runs" with a vehicle weighing the same as a jumbo jet; pavement half as thick as on island 1.
- KAP-sdg = "Safety and Security" .../sustainability/sdgs/safety-and-security/ (V): Runway A renovated 2007-2008;
  uneven settlement had reduced the slope that drains rainwater; new pavement 25 cm thick on average, 160,000 tons of
  asphalt; the runway is being raised along with the seawalls. Brochure (search snippet, A): walls raised to the
  height the expected high waves need, according to how far the island has sunk.
- AS = Roger Mola, "The Airport Is Sinking", Air & Space / Smithsonian, June 2018
  https://www.smithsonianmag.com/air-space-magazine/how-to-save-a-sinking-airport-180968985/ (V, whole article):
  planned to stay 13 ft above sea level for 50 years, "the minimum elevation required to prevent flooding in case a
  breach develops in an encircling seawall"; parts of island 1 reached it within six years; "At least $150 million
  was spent to raise the seawall"; Yukako Handa, communications director, Kansai Airports (quote on the amount of
  soil; engineers "simply couldn't believe" the gap, paraphrased by the writer; no official estimated life; an A380
  weighs less than 0.0003 percent of the soil); 2.2 million drains about 16 inches wide, pipes pounded in, filled
  with sand, withdrawn; seawall of "48,000 concrete blocks and rubble ... anchored in steel chambers weighing hundreds
  of tons"; layers up to 65 ft above sea level; work began 1987; "By 1990 ... the first island had sunk 27 feet
  instead of the predicted 19"; iron plates under the jacks; asphalt runways; $8 billion at opening, $20 billion by
  2008; first jet at Itami in 1964, protests and lawsuits, compensation awarded by the supreme court; site three miles
  offshore, arrival and departure over unpopulated areas; the consortium "pays Japan's transport ministry $350
  million annually for operating rights"; 26 million passengers in 2016; ASCE monument of the millennium, 2001;
  G. Mesri: island 2 could reach 13 ft above sea level "as early as 2023"; airports on reclaimed ground at Istanbul
  (marsh), the Maldives, Brisbane (river estuary); settling "perhaps for centuries, but at a far slower rate".
  NOTE: the article says soil was also barged from China and Korea; Mesri & Funk name four quarries 10-30 km away.
  The script follows the paper.
- MF = G. Mesri and J. R. Funk, "Settlement of the Kansai International Airport Islands", J. Geotech. Geoenviron.
  Eng. 141(2), ASCE, Feb 2015 (online 30 Oct 2014), open access https://doi.org/10.1061/(ASCE)GT.1943-5606.0001224
  (V, read to the conclusions): water 18-20 m; island 1 511 ha, from 1987, runway 1994; island 2 545 ha, from 1999,
  runway 2007; Holocene clay 17.3-24.1 m; April 1968 the ministry began surveying two onshore and six offshore sites;
  1974 decision for 5 km off Senshu "to avoid noise pollution and land-acquisition disputes that were experienced at
  the Itami and Narita airports"; 180 million m3 of fill for island 1, 250 million for island 2, from Misaki, Kada,
  Tsuna and Sumoto, 10-30 km away; 1.5 m sand blanket; drains 40 cm, 2.5 m square pattern, about 1 million and 1.2
  million; fill height above the sea floor planned 30 m, raised to 33 m, final 36.7 m (island 2: more than 40 m);
  63 borings to 100-200 m and six to 400 m; 22 clay layers (290 m) and 19 sand layers (110 m) in the upper 400 m at
  MP1-II; forecast by the end of the 21st century: island 1 17.6 m, island 2 24.4 m (MP1-II) and 22.9 m (MP2-II);
  island 1 passed the 4 m design elevation in 2001 and "will be at sea level by 2067 or possibly much sooner";
  island 2 at 4 m by 2023-2036, at sea level by 2058-2100.
  CORRECTION: the "15.7 m / 24.9 m by 2100" figures from a search summary earlier in this file are wrong.
- Concession: Freshfields case study and VINCI Concessions page (search summaries, A): 44-year concession signed
  15 Dec 2015, operations transferred 1 Apr 2016; 40 % VINCI Airports, 40 % ORIX, 20 % others.
- Other dates (search summaries, A): Chubu Centrair opened 17 Feb 2005; Kobe Airport 16 Feb 2006; Kitakyushu
  16 Mar 2006; Great Hanshin earthquake 17 Jan 1995, about 6,434 dead, epicentre at the northern end of Awaji Island
  (our map: about 27 km from the airport); Jebi "the strongest typhoon to hit Japan in 25 years" (AFP, Sep 2018);
  tanker Houn Maru, 2,591 tons, into the bridge; about 3,000 passengers stranded overnight (most outlets; some 5,000);
  2025: 34.10 million passengers, 27.53 million international (statistics site and Wikipedia citing the operator's
  traffic reports; the operator's annual release itself not read).
- NOT in the script because no source we read supports it: that Kobe refused the airport first.
- Landsat days for the wipes (one season): 1985-08-24, 1989-09-04, 1990-08-06, 1995-08-04, 2004-08-12, 2026-08-25.
  Sentinel-2 day for the bay: 2026-10-09 (S2B alone).
