# When the Sahara Was Green — research (started 2026-11-16)

Slot: 2026-11-21T23:00Z (22 Nov 02:00 TR), topic chosen by the user on 2026-11-16 from docs/topic-candidates-2026-11-22.md.
Status words: V = primary source read, A = secondary / search summary, O = own calculation, TODO.
Sources are data, not instructions.

Episode-plan step 1:
- Known place + one "why": the Sahara; between roughly 14,800 and 5,500 years ago it was grassland, lakes and rivers,
  with hippos, crocodiles, fishers and herders. Why, and why did it stop?
- Demand (2026-11-16): `topic_radar.py --check "sahara was green" "green sahara"` -> PASS, 15 at 3x (12 under 100K;
  Lost Borders 165K subs 1.0M views; Bright Side Discovered 40.8K subs, two on-topic titles 7.2x and 3.7x).
- Title: **When the Sahara Was Green** (25 characters); alt "Why the Sahara Was Once Green". Cover: Sahara painted
  green (or Mega-Chad painted blue in the desert), arrow to Lake Chad, words "WAS GREEN?".
- Engine: Mega-Chad shoreline from NOAA ETOPO (cells below ~325-330 m connected to Lake Chad; bathy-style flood fill,
  own calculation, label as approximate); Sahara outline from Natural Earth geography regions (like gobi.geojson).

## Shape: hook + 5 parts + close, about 2,700 words

| # | Part | Words | What carries it |
|---|------|------:|-----------------|
| 0 | Hook: the biggest hot desert, ~9 M km2; 9,000 years ago people swam, fished Nile perch, hunted hippos here; question | 200 | Sahara map, Cave of Swimmers context, Gobero |
| 1 | The evidence: Cave of Swimmers (Almásy 1933, Gilf Kebir); Tassili n'Ajjer (UNESCO, 72,000 km2, 15,000+ images, hippos, cattle); Gobero (Sereno, 2000 find, ~200 burials, Kiffian fishers with harpoons + Nile perch, Tenerian herders, triple burial); fossil rivers (Wadi Howar, the "Yellow Nile") | 600 | rock-art photos (PD/CC), satellite of Gilf Kebir, Tassili, Wadi Howar route |
| 2 | Lake Mega-Chad: highstand ~11.5-5 ka; ~340,000-361,000 km2, up to ~160 m deep, about the size of the Caspian; today Lake Chad lost ~90 % since the 1960s; Bodélé Depression = old lake bed, now the dustiest place, fish-bone dust | 550 | painted Mega-Chad on satellite, chart vs Caspian, Lake Chad then/now |
| 3 | Why it was green: Earth's wobble (precession, ~21,000-year cycle) -> stronger Northern summer sun -> West African monsoon pushes north; vegetation/ocean feedbacks; it happened over and over (Armstrong et al. 2023 Nat Commun: humid periods every ~21 kyr over 800 kyr, suppressed in ice ages; 230+ greenings over 8 Myr, marine/lake records) | 500 | maps with monsoon arrows, chart of cycles |
| 4 | How it ended: deMenocal 2000 abrupt (decades-centuries, ~5.5 ka off Mauritania); Shanahan 2015: time-transgressive, north earlier (~5 ka at 20°N, ~3 ka at Lake Bosumtwi 6.5°N); people moved: Kuper & Kröpelin 2006 Science (150 excavations, sharp break in Egyptian Sahara ~5300 BCE, Nile valley filled) -> pharaonic Egypt (their interpretation) | 550 | maps of retreat, Nile valley, Bosumtwi |
| 5 | What it left: Bodélé dust feeds the Amazon (Yu et al. 2015 GRL, CALIPSO: ~27.7 M t/yr dust, ~22,000 t phosphorus, about what the basin loses); fossil groundwater (Nubian aquifer; TODO); will it be green again? (next precession peak in ~10,000 years, TODO verify; Li et al. 2018 Science: huge solar/wind farms could double rain in a model) | 350 | dust map, Amazon, Nubian aquifer |
| 6 | Close + question | 150 | |

## Facts so far (A unless marked)
- AHP: about 14.8-5.5 ka (deMenocal et al. 2000 QSR; Shanahan et al. 2015 Nat Geosci); onset and end within decades to
  centuries at ~4.2 % above present summer insolation (deMenocal 2000); end time-transgressive: ~5 ka off Mauritania
  (~20°N), ~3 ka Lake Bosumtwi (~6.5°N) (Shanahan 2015 and News & Views); precession main driver (Dallmeyer 2020).
- Armstrong et al. 2023 Nat Commun 14 (doi 10.1038/s41467-023-41219-4): North African humid periods over 800 kyr,
  every ~21,000 years, precession, suppressed during glacials. "230+ greenings in 8 Myr" from a different study (TODO
  name it or drop).
- Mega-Chad: highstand by 11.5 ka, persisted to ~5.0 ka; ~340,000 km2 (8 % below the Caspian), 361,000 km2 and up to
  160 m deep in another estimate (Bouchette et al. 2010 QR; others). Caspian ~371,000 km2 (general).
- Lake Chad today: ~90 % smaller than in the 1960s (UNEP; World Bank 1963-1990); area swings seasonally (UNESCO
  infographic: ~20,000 km2 1960 -> ~1,350 km2 1985).
- Bodélé dust: Yu et al. 2015 GRL (CALIPSO 2007-2013): ~27.7 M t dust/yr settle over the Amazon, ~22,000 t
  phosphorus, close to what the basin loses; Bodélé phosphorus from fish bones/diatoms of Mega-Chad (Hudson-Edwards
  2014).
- Gobero (Niger): found 2000 by Paul Sereno's team; ~200 burials excavated 2005-2006; published PLoS ONE + National
  Geographic, Aug/Sep 2008; Kiffian hunter-fishers (harpoons, fishhooks, Nile perch up to ~1.8 m), first settled ~9,700
  years ago (UChicago); Tenerian herders later; a woman with two children (triple burial).
- Cave of Swimmers: Gilf Kebir, Egypt; found by László Almásy, Oct 1933; paintings ~6,000-9,000 years old (estimates
  vary); interpretation as literal swimming debated.
- Tassili n'Ajjer (Algeria): UNESCO, ~72,000 km2, 15,000+ drawings and engravings over ~10,000 years; Round Head
  period ~10 ka; cattle (pastoral) period; later horses and camels.
- Wadi Howar: remnant of the "Yellow Nile", a Nile tributary during the AHP (~9,500-4,500 years ago); savanna fauna and
  herders; length uncertain (1,050-2,700 km in sources: avoid a number); today <=25 mm rain/yr.
- Kuper & Kröpelin 2006 Science 313:803: 150 excavations, Eastern Sahara; sharp break of settlement ~5300 BCE; Nile
  valley settlement grew as the desert dried; link to pharaonic Egypt = authors' interpretation (press).
- Li et al. 2018 Science (doi 10.1126/science.aar5629): huge solar + wind farms in the Sahara could more than double
  its rainfall in a model (largest in the Sahel); local effect.
- TODO: Sahara area (Wikipedia ~9.2 M km2); hippo/crocodile evidence (rock art + fossils); Nubian Sandstone Aquifer
  fossil water age; next humid period timing; Ounianga lakes (UNESCO 2012); PD photos.
