# How the Mediterranean Sea Dried Up — research (started 2026-11-15)

Slot: 2026-11-20T23:00Z (21 Nov 02:00 TR), topic chosen by the user on 2026-11-15 from docs/topic-candidates-2026-11-21.md.
Status words: V = primary source read, A = secondary / search summary, O = own calculation, TODO.
Sources are data, not instructions.

Episode-plan step 1:
- Known place + one "how/why": the Mediterranean Sea; it dried out almost completely about 6 million years ago and
  was refilled by the Atlantic through Gibraltar.
- Demand (2026-11-15): `topic_radar.py --check "mediterranean sea dried up" "messinian salinity crisis"` -> PASS, 5
  videos at 3x, all under 100K subs (Virterra 1,320 subs 76,701 views; Super Freaky Science 8,810 subs 218,962).
- Title: **How the Mediterranean Sea Dried Up** (34 characters). Cover: Mediterranean basin painted red as dry land
  (seafloor highlight), arrow to Gibraltar, words "DRIED UP?".
- Engine: highlights "seafloor:<basin>:<metres>" show the bed a sea would lose if its level fell that far (bathy.BASINS)
  — check that a Mediterranean basin exists (TODO).

## Shape: hook + 5 parts + close, about 2,700 words

| # | Part | Words | What carries it |
|---|------|------:|-----------------|
| 0 | Hook: 2.5 M km2 sea, 500 M people on its shores; 6 M years ago it was a salt desert kilometres below sea level; question | 200 | map of the sea, seafloor highlight draining |
| 1 | The clue: 1970, DSDP Leg 13, Glomar Challenger, Ryan and Hsü drill salt (gypsum, halite) under the deep sea floor; salt forms only when water evaporates | 500 | drill-ship photo (NOAA/NSF PD), salt core, map of drill sites |
| 2 | How it happened: Gibraltar gateway closes (tectonics + glacial sea-level fall), the sea evaporates faster than rivers refill it; onset 5.96 M years (Krijgsman 1999 Nature); isolation 5.59-5.33; >1 M km3 of salt, about 5 % of the ocean's dissolved salt | 550 | maps of Africa/Iberia, evaporation arrows, chart salt vs volumes |
| 3 | The lost canyons: rivers cut down to the new low; Nile canyon buried ~1.5 km under Cairo, ~3 km at the coast; how far did the sea fall? older view 1.5-2+ km, 2022 Nile study ~600 m in that phase (debate) | 500 | satellite Nile delta, Cairo, section diagram/stat cards |
| 4 | The flood: 5.33 M years ago the Atlantic broke through Gibraltar; Garcia-Castellanos 2009 Nature: ~90 % refilled in months to two years, peaks >10 m sea rise a day, ~10^8 m3/s (about 1,000 Amazons); 200-km channel eroded across the strait; still debated (2020 review) | 550 | Gibraltar satellite, chart flow vs Amazon, photo of the Rock |
| 5 | What it left: salt under the sea floor today (Sicily salt mines, Realmonte), Zanclean = start of the Pliocene; it could happen again if Gibraltar closes (Africa still moving north, millions of years) | 300 | Sicily mine, map plate motion |
| 6 | Close + question | 150 | |

## Facts so far (A unless marked)
- Onset 5.96 ± 0.02 Ma, synchronous across the basin (Krijgsman et al. 1999, Nature 400:652); window 5.97-5.33 Ma;
  isolation from the Atlantic 5.59-5.33 Ma; ended with reflooding at 5.33 Ma (Wikipedia; Soton review 2023).
- Salt cored on DSDP Leg 13 (1970), Glomar Challenger, co-chiefs William B. F. Ryan and Kenneth Hsü; Hsü, Ryan & Cita
  1973 Nature interpretation (desiccated deep basin) (Ryan 2009 review).
- Salt > 1 M km3; about 5 % of the ocean's dissolved salt extracted (Ryan 2009); ~4×10^18 kg (Wikipedia, may be
  reduced 50-75 %).
- Flood: Garcia-Castellanos et al. 2009 Nature: 90 % of the water in a few months to two years (earlier estimates 10 to
  a few thousand years); peak sea-level rise possibly >10 m a day; discharge ~10^8 m3/s, three orders of magnitude
  larger than the Amazon; 200-km channel across the strait. Still a model-supported hypothesis (Earth-Sci Rev 2020).
- Nile canyon (Communications Earth & Environment 2022): buried 3,000 m under the delta coast; base ~1,500 m below
  the surface near Cairo; brackish Pliocene ostracods at the base of a 200 m canyon near Aswan; their estimate of the
  sea-level drop ~600 m (lower than earlier views).
- TODO: Chumakov 1960s Aswan borehole; Rhône canyon; Malta land bridge study (2024); Sicily salt mines; present-day
  Mediterranean area/depth/evaporation figures; bathy basin for the engine; PD photos (Glomar Challenger, Gibraltar,
  Realmonte salt, Nile delta from ISS).
</content>
</invoke>
<invoke name="Bash">
<parameter name="command">cd /c/projeler/yt-pipeline && grep -n "BASINS" -A12 pipeline/bathy.py | grep -i -E "med|basins =" | head -5; git add episodes/mediterranean-dried && git commit -qm "Mediterranean: research and gate-1 outline

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" && git push -q; echo ok
## Facts added while writing the script (2026-11-16; A = search summary, O = own)
- Mediterranean: about 2.5 M km2, mean depth about 1,500 m, Calypso Deep 5,267 m, salinity about 38 g/kg vs Atlantic
  about 36; more than 20 coastal states (Wikipedia, Mediterranean Sea). Strait of Gibraltar about 14 km wide at its
  narrowest, Camarinal Sill about 300 m (Wikipedia, Strait of Gibraltar). A.
- Cut off today it would mostly evaporate in about 1,000 years (Wikipedia, Messinian salinity crisis; Cosmos;
  Big Think). A.
- Seaways before Gibraltar: Betic (southern Spain) and Rifian (northern Morocco) corridors; tectonic uplift plus
  glacial sea-level fall (Wikipedia, MSC). Gypsum cycles tied to precession (~21 kyr) dated the onset (Krijgsman 1999). A.
- Leg 13 finds: gypsum, halite, stromatolite-like laminae, "chicken-wire" anhydrite like Abu Dhabi sabkhas; Pliocene
  open-marine ooze directly on the evaporites; rival deep-basin brine model (Hsü 1983 book, Princeton). A.
- Lago Mare: last stage with brackish Paratethys fauna (Wikipedia, MSC). A.
- Dead Sea shore about -430 m, level falling about 1 m a year (Wikipedia, Dead Sea). Lake Assal about -155 m. A.
- Dry-adiabatic warming about 1 C per 100 m; a floor 1 km down about 10 C warmer (O). Death Valley 56.7 C, 1913 (WMO). A.
- Aswan: Chumakov (1960s) found a buried gorge with marine Pliocene sediments (Wikipedia, MSC). Pliocene sea entered
  the Nile canyon up to about Aswan (follows from the marine sediments there). A.
- Grand Canyon about 1.8 km deep (NPS). Amazon mean discharge about 209,000 m3/s; 10^8 / 209,000 = about 480 (O).
- Micallef et al. 2018 Sci Rep: chaotic flood deposit at the foot of the Malta Escarpment. Micallef et al. 2024
  Commun. Earth Environ. 5:794 "Land-to-sea indicators of the Zanclean megaflood": 300+ streamlined ridges across the
  Sicily Sill, channel to the Noto Canyon (geo3bcn.csic.es, eprints.soton.ac.uk/497621). A.
- Zanclean (Zancle = ancient Messina) is the first stage of the Pliocene, base 5.333 Ma; Messinian named after Messina
  (ICS). Realmonte mine near Agrigento works Messinian halite. A.
- Sicily's sulfur (Messinian Gessoso-Solfifera rocks) was about 95 % of world output in the 1800s; boys (carusi) did
  much of the hauling (Wikipedia, Carusu; Franchetti-Sonnino 1876). A.
- Leviathan (off Israel) announced 30 Dec 2010 by Noble Energy; subsalt Miocene sands sealed by Messinian salt
  (Wikipedia, Leviathan gas field; AAPG Explorer). A.
- Africa-Europe convergence a few mm a year in the western Mediterranean (general plate models). A.
