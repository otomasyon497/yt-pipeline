# Research: Canadian Shield (round 1, 2026-11-24)

Each fact has its source; secondary sources are marked. Round 2 opens the primary pages marked (check).

## Size and people
- R1 Shield ~5 million km2, about half of Canada's land (The Canadian Encyclopedia, "Canadian Shield").
  https://thecanadianencyclopedia.ca/en/article/shield (check wording)
- R2 Finland 5,637,214 people at the end of December 2024 (Statistics Finland, preliminary).
  https://stat.fi/en/publication/clmrja5eq4gl80avy7bbj9jui (check Dec release)
- R3 Fennoscandian (Baltic) Shield covers most of Finland and Sweden and eastern Norway (Britannica, "continental
  shield"; check a GTK page for "Finland's bedrock is part of the Fennoscandian Shield").
- TODO round 2 OWN MEASUREMENT: population on the Shield = 2021 census dissemination-area points (StatCan, CSV/
  shapefile) inside the Shield polygon (GSC/NRCan "Geological provinces" or Natural Earth / CEC ecoregions
  Boreal+Taiga Shield). StatCan pages refuse our fetch tool (403): download the data files directly.
  Same for Ontario north share (rival: 94/6).

## Cold: Hudson Bay
- R4 Churchill annual mean -6.9 C, January -26.7 C, July 12.0 C (StatCan table of ECCC normals 1971-2000).
  https://www150.statcan.gc.ca/n1/pub/16-201-x/2007000/5212433-eng.htm  Round 2: ECCC 1991-2020 normals Churchill A
  (5060600), FMI normals Helsinki/Stockholm (SMHI); Canadian Ice Service Hudson Bay freeze/break-up dates.

## Farming the Shield: the Clay Belt
- R5 Matheson Fire, 29 July 1916: ~223 dead officially (true toll unknown; an older NRCan page says 282); settlers'
  clearing fires in a dry summer merged; Nushka/Matheson destroyed (CBC 2016; Alexander 2010 review, frames.gov;
  Ontario Heritage Trust plaque). https://www.cbc.ca/news/canada/sudbury/100-years-great-matheson-fire-1916-1.3689061
  https://heritagetrust.on.ca/plaques/great-fire-of-1916 ; Great Fire of 1922 (Haileybury) in the Lesser Clay Belt.

## Rail to the bay
- R6 Hudson Bay line to Churchill: flooding in May 2017 washed out the ~400 km track in about 20 places; Omnitrax
  refused to repair without government help; line reopened 1 Nov 2018 after 18 months; first VIA passenger train
  4 Dec 2018; federal $117 M for buying and repairing it (CBC; Canada.ca RRCI evaluation).
  https://www.canada.ca/en/prairies-economic-development/corporate/transparency/audit-evaluation/evaluation-restoring-rail-service-churchill-initiative.html

## Towns switched off
- R7 Schefferville: IOC announced closure of its mine on 2 November 1982 (Canadian Historical Review abstract,
  doi 10.3138/chr-2022-0010); company president then Brian Mulroney; 244 people in 2021 (StatCan via TCE/Wikipedia).
  Round 2: 1981 census population.
- R8 Pine Point NWT: peak 1,915 people (1976), mine closed 1987, town closed 1988, houses sold and moved to Hay
  River / Fort Resolution, 9 people in 1991 (Wikipedia; Canadian Mining Journal). Secondary: check NWT archives.

## Power for the south
- R9 James Bay Project: announced by Premier Bourassa on 30 April 1971 ("project of the century", ~$6 B); Phase I
  cost $13.7 B; Cree/Inuit injunction 1973 overturned; James Bay and Northern Quebec Agreement signed 11 Nov 1975,
  $225 M compensation, first modern treaty (The Canadian Encyclopedia).
  https://thecanadianencyclopedia.ca/en/article/james-bay-project
- R10 Churchill Falls: 1969 contract, Hydro-Québec buys ~4,800 MW at about 0.2 cents/kWh; MOU 12 Dec 2024 would
  raise it to ~4 cents (2024 $); definitive agreement dated 17 Aug 2026 replaces the 1969 contract (NL Government
  releases, Hydro-Québec PDF). https://www.gov.nl.ca/releases/2024/exec/1212n01/ (check 2026 terms)

## Round 2 (2026-11-24)
### Own measurements
- R11 OWN (geo/measure_population.py, output geo/measure_population.txt): Kontur Population Canada 2023-11-01
  (CC BY 4.0, modelled 400 m hexagons from GHSL/Microsoft buildings/census, total 38,810,039) inside the Boreal
  Shield + Taiga Shield ecozones (AAFC Ecological Framework of Canada): 3,373,306 people = 8.69 %; area
  3,442,863 km2. Boreal Shield alone 3,321,861. Hudson Plain 14,116 people on 434,895 km2. Say "fewer than one
  Canadian in ten lives on the Shield" and "about 3.4 million people". The ecozones cover the Shield's forest belt
  (3.4 M km2); the geological Shield (~5 M km2, R1) also runs under the Arctic tundra, where ~50,000 people live
  (Southern + Northern Arctic ecozones), so the share does not change.
  Rejected: Natural Earth "CANADIAN SHIELD" polygon is too coarse (contains Montreal) -> 14.85 %, wrong.
- R12 OWN (data/era5_normals.py -> data/era5_normals.json): ERA5 reanalysis via Open-Meteo, daily means 1991-2020,
  ~25 km cells: Churchill (58.8 N) annual -6.0 C, Jan -25.8, Jul 12.0, 214 days a year below 0 C; Helsinki (60.2 N)
  6.0 / -3.8 / 17.9, 93 days; Stockholm 7.2 / -1.4 / 17.8; Oulu (65.0 N) 3.3 / -7.8 / 16.6, 136 days;
  Timmins (48.5 N) 2.7 / -15.4 / 18.3, 147 days; Thunder Bay (48.4 N) 3.8 / -13.0; Schefferville (54.8 N) -4.4.
  Cross-check: StatCan/ECCC 1971-2000 Churchill annual -6.9, Jan -26.7, Jul 12.0 (R4): consistent.
  Key line: Oulu, near the Arctic Circle, is warmer on average than Timmins, at the latitude of Paris (48.9 N).
### Finland
- R13 Finland's bedrock belongs to the Fennoscandian Shield, Precambrian (Archean in the east/north, mostly ~3,000-
  1,400 Ma) (Geology of Finland, citing GTK; secondary: check a GTK page).
- R14 Oulu ~216,000 people (2024, Statistics Finland via city/citypopulation); 217,556 on 31 Dec 2025 (City of Oulu).
- R15 Why Europe at these latitudes is milder: Seager et al. 2002 (QJRMS): mainly mean winds carrying warm maritime
  air from the Atlantic; the ocean current's share is debated (Smithsonian, Scientific American). Script: "winds off
  a warm ocean", no "the Gulf Stream heats Finland".
### Hudson Bay ice
- R16 Corridor to Churchill 1981-2014 average break-up 16 July, freeze-up 19 November (study cited by PBI/Arctic
  journal); polar bears ashore ~4 months, fasting (NASA Earth Observatory "Surviving summer in Hudson Bay").
  Script: "frozen for about eight months a year" -> check: 19 Nov to 16 Jul = ~8 months. OWN arithmetic.
### Clay Belt
- R17 Alfred Barlow's 1899 report promoted the Clay Belt; Ontario's 1900 exploration survey (ten parties);
  pamphlet c. 1901 "The great claybelt of Northern Ontario, containing over 15,000,000 acres" (Canadiana);
  long winters and erratic rain in a short season meant most farms yielded little (TCE "Canadian Clay Belt").
- R18 Great Fire of 1922, 4-5 Oct, Lesser Clay Belt (Timiskaming): ~43 dead (Ontario Heritage Trust plaque),
  90 % of Haileybury destroyed in 3-6 hours, 3,500 homeless (marker), 1,680 km2, snow and rain ended it.
### Rail and port
- R19 Hudson Bay Railway reached Churchill 29 March 1929 (crew of 3,000 on frozen muskeg, Manitoba plaque); port
  works finished 1931 (TCE/MHS). Churchill line washout 2017 (R6).
### Towns
- R20 Schefferville founded by IOC 1953-54 (TCE/Wikipedia), peak ~5,000 late 1960s (Wikipedia; secondary),
  mine closure announced 2 Nov 1982 (CHR), operations ended 1983 (TCE), 244 people 2021.
### Power
- R21 La Grande complex ~17,418 MW in 11 stations, close to half of Hydro-Québec's capacity (BAnQ/Hydro-Québec doc);
  Robert-Bourassa 5,616 MW (HQ annual report 2023); HQ installed in Québec 37,436 MW (2023).
- R22 Churchill Falls: 1969 contract 0.2 cents/kWh; DCIA 17 Aug 2026; new price starts 1.8 cents/kWh in 2027,
  rising to 2077 (CP24/BLG on the DCIA); NL House of Assembly voted to proceed 17 Sept 2026 (BLG). Definitive
  agreements not confirmed signed: say "a new deal agreed in 2026".
### Round 3 (narration additions)
- R23 Churchill Polar Bear Alert program since 1983; holding facility opened 1982 (PBI; Wikipedia "Polar bear
  jail"; Manitoba brochure). Western Hudson Bay bears 1,185 (1987) -> 618 (2021) (PBI), not used.
- R24 2021 census CMAs: Greater Sudbury 170,605, Saguenay 161,567, Thunder Bay 123,258 (StatCan Daily 2022-02-09
  table t005b via search; check).
- R25 Caniapiscau, Sept-Oct 1984: caribou of the George River herd drowned at Limestone Falls (Chute du Calcaire);
  Quebec officials' early estimates at least 10,000 (up to 22,000) (NYT via search; Time; SI 15 Oct 1984);
  Wikipedia 9,600; Inuit blamed water releases from the reservoir, Hydro-Québec blamed heavy rain; fence later
  built on the east bank (Nunatsiaq). Script: "thousands", "first estimated at least ten thousand".
- R26 Mercury: impoundment raised fish mercury 2-8x unflooded levels; back to baseline after ~20-30 years in
  piscivores; Cree advisories and a fish consumption guide with the Cree Board of Health (Hydro-Québec synthesis
  1978-2012; HQ mercury page). https://www.hydroquebec.com/data/developpement-durable/pdf/executive_summary_synthesis_1978-2012.pdf
- R27 Dominion Lands Act 1872 (royal assent 14 Apr 1872): 160-acre quarter section for a $10 fee, live on and
  cultivate it (TCE "Dominion Lands Policy"; Saskatchewan Archives; Wikipedia).
- R28 Kapuskasing: Ontario's returned-soldier land settlement scheme near Kapuskasing, discontinued in 1920 (Ontario
  Heritage Trust plaque "Founding of Kapuskasing"); farmers left for Toronto/Montreal or the prairies (Wikipedia
  "Clay Belt", citing Pugh 1975). https://www.heritagetrust.on.ca/plaques/founding-of-kapuskasing
- R29 James Bay injunction: Malouf judgment Nov 1973, overturned on appeal (TCE): script says "soon overturned".

## Gate-1 outline (draft, ~2,750 words, 7 reasons)
Title: "Why Almost Nobody Lives on Half of Canada" (41 chars). Cover: lakes-and-rock aerial, "HALF OF CANADA / EMPTY".
- Hook (~230): half of Canada; [own share] of Canadians live on it. But Finland stands on the same kind of rock,
  scraped by the same ice, and 5.6 M people live there. Teasers: a town that burned in a day, a town packed onto
  trucks, a railway that vanished for 18 months. Question. "The first reason is under your feet."
- 1 The rock with no soil (~330): Precambrian core, ice sheet pushed the soil south (brief; rivals cover it).
- 2 The freezer in the middle (~420): Hudson Bay; Churchill vs Helsinki at the same latitude (chart); sea ice; this
  is the main difference from Finland, which faces a warm Atlantic-fed Baltic.
- 3 The farm dream that burned (~420): Clay Belt, settlers, 1916 Matheson fire, 1922.
- 4 Canada had somewhere better to go (~330): prairies, southern Ontario; Finland had no other land (own: Finland
  ~100 % shield vs Canada ~50 %).
- 5 Towns that live as long as the mine (~400): Schefferville, Pine Point.
- 6 One line to the sea (~330): Churchill rail washout 2017-18.
- 7 The empty half lights the full half (~400): James Bay 1971/1975, Churchill Falls 1969-2026.
- Ending (~120) + question: "Would you move to a town on the Shield if the job paid double?"
