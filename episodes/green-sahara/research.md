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

## Facts added 2026-11-16 (A)
- Sahara about 9.2 M km2, the largest hot desert (Wikipedia; Geographical). Natural Earth label polygon is larger
  (~10.6 M km2): paint it, never quote its area.
- Hippo and crocodile remains reported at sites now far from water (Libya, Egypt, Niger) (popular sources; say "hippo
  and crocodile bones" without a distance). Rock art (Bubalus period) shows buffalo, elephant, rhino, hippo (Penn State).
- Nubian Sandstone Aquifer: ~2 M km2 under Egypt, Libya, Sudan, Chad; water ages ~4,000-20,000 years in places and up
  to hundreds of thousands deeper (81Kr 40,000-630,000 years, J. Hydrol. 2020); recharged in several humid episodes;
  little recharge today (Wikipedia, Fossil water). Volume: TODO or omit.
- Next green Sahara: next northern summer insolation maximum about 10,000 years from now (Live Science); strength
  depends on future greenhouse gases (Duque-Villegas et al. 2022 Clim. Past).
- Mega-Chad map: our ETOPO fill below 320 m gives ~331,000 km2 (own; make_regions.py).
- Drake & Bristow 2006 The Holocene "Shorelines in the Sahara": Landsat + SRTM mapped Megachad shorelines; beach
  terrace at 329 m (Hebil); peak before 7,000 years ago >173 m deep, >=400,000 km2 (their estimate). Others: 325 +- 5 m.
- Sand sheets and dunes ~25 % of the Sahara (Britannica; some say 1/8): say "only a fraction" or "about a quarter".
- Camel: common in the Sahara from about the early centuries AD (Roman era) (Britannica; Zerboni & Nicoll 2019).
- Guelta d'Archei (Ennedi, Chad): relict West African crocodiles, ~7-10 animals (George 1999; de Smet; IUCN outlook),
  isolated a few thousand years since the river network drained.
- Ounianga lakes (Chad): UNESCO 2012, 18 lakes fed by fossil groundwater (general, UNESCO page); Great Green Wall:
  African Union initiative launched 2007, ~8,000 km across the Sahel (general).
- Almásy portrayed in The English Patient (Ondaatje novel 1992, film 1996), which shows the Cave of Swimmers (general).
