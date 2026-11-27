"""Fill Source/Status of episodes/florida-keys/factcheck.md from research.md rules (first matching rule wins)."""
import re, sys
sys.stdout.reconfigure(encoding="utf-8")
p = r'C:\projeler\yt-pipeline\episodes\florida-keys\factcheck.md'
V, A, O = "verified", "attributed", "own"
RULES = [
    (r"roadblock of 1982|storm of 1935 showed", "Summary of R4/R8", V),
    (r"677|six hundred and seventy-seven|likely to be replaced", "R6 FDOT early estimate $677 M; replacement likely (Miami Herald 2024; WUSF 2024)", A),
    (r"thirty-seven of the forty-four|37 OF 44|new Seven Mile Bridge opened", "R6 37 of 44 bridges replaced; new Seven Mile Bridge 1982 (Florida Memory; Wikipedia)", V),
    (r"footpath|still there, beside|span is missing", "R6 Old Seven Mile Bridge: 2.2 mi restored to Pigeon Key (2022); swing span removed (Wikipedia)", V),
    (r"^Reason (one|two|three|four|five|six)\.$|sea decided which|road exists because the sea|one narrow strip|door was tested|threat to it now|somebody shut it", "Framing / summary of facts cited elsewhere in this table", V),
    (r"Hemingway|murdered the vets|New Masses|SEPT 1935", "Hemingway, 'Who Murdered the Vets?', New Masses 17 Sep 1935 (Wikipedia 1935 Labor Day hurricane)", V),
    (r"350|718|away in Miami", "R4 ~350 of 718 camp veterans in Miami for a ball game (myfloridahistory.org)", V),
    (r"24\.5|twenty-four and a half|twenty-four hours|2025-190|half an hour", "R9 F.S. 380.0552(9)(a)2 (2025): 24.5 h; was 24 h; ch. 2025-190", V),
    (r"April 1982|Border Patrol|searched", "R8 roadblock south of Florida City, April 1982; injunction refused (Florida Historical Society)", V),
    (r"twelve hundred|1,179", "R10 Monroe County: 1,179 homes destroyed (666 of them mobile homes)", V),
    (r"1913|foot higher|twice as fast|2\.4|\+1 FT|thirty years|NOAA|tide records|1913-22|2016-25", "M1 own calculation geo/measure_sealevel.py from NOAA CO-OPS 8724580", O),
    (r"hundred miles out|New York is from Philadelphia", "FDOT/Monroe County: Overseas Highway ~110 mi Florida City-Key West (113 mi Key Largo-Key West); NYC-Philadelphia ~95 mi by road", V),
    (r"more than four hundred|408|later counts", "R4 NWS official estimate 408; FERA/VA counts 423-488", V),
    (r"left the United States|Conch Republic|23 APR|twenty-third of April|proclamation|roadblock came down|still celebrate", "R8 Florida Historical Society; Wikipedia Conch Republic (secession 23 Apr 1982, roadblock removed)", V),
    (r"1\.8 BILLION|one point eight billion|150 miles of county|hundred and fifty miles", "R12 Monroe County roads study (2021): ~$1.8 B for ~155 mi (Miami Herald)", A),
    (r"biggest in Florida|18,080|17,201|eighteen thousand|Jacksonville|1890", "R2 Census 1890: Key West 18,080, Jacksonville 17,201 (Census twps0076 FL table)", V),
    (r"deep, sheltered harbour|Straits of Florida|ninety miles", "R2 Key West harbour on the Straits; Havana ~90 mi (NOAA charts)", V),
    (r"wrecked on the reef|federal court|salvaged", "R2/rivals: federal wrecking court at Key West (Wikipedia Key West; Leonard Sinclair, Paul McAllister)", V),
    (r"cigars|cigar|Tampa", "Ybor moved cigar making to Tampa 1885-86 (Wikipedia Ybor City; Key West)", V),
    (r"Navy kept a base|Navy had closed", "R15 Navy base closed 1930/31 (Florida Trend); Naval Station Key West", V),
    (r"Lighthouses", "Reef lights from the 1850s cut wrecks (Wikipedia Key West; Florida Keys lighthouses)", V),
    (r"Panama Canal|1905 the United States began|closest deep-water|canal opened in 1914|1914", "R2 Panama Canal construction 1904-14 (US began May 1904; Flagler's decision 1905); KWAHS FEC timeline", V),
    (r"Flagler|Florida East Coast", "R1/R2 Wikipedia Overseas Railroad; Library of Congress", V),
    (r"128|hundred and twenty-eight", "R1 1912 FEC booklet: Homestead-Key West 128.4 mi", A),
    (r"Work began in 1905|Thousands of men", "R1 Wikipedia Overseas Railroad (work began 1905)", V),
    (r"Lake Surprise|lake no map", "R1 Lake Surprise, Key Largo: unexpected lake, fill sank (Geography Docs; keyshistory.org)", A),
    (r"October 1906|OCT 1906|hundred workers|1909 and 1910|1909|1910", "R1 1906 hurricane, quarter boat no. 4, ~100 dead; 1909, 1910 storms (Wikipedia Overseas Railroad)", A),
    (r"Long Key Viaduct|two miles|concrete arches|arches", "R1 Long Key Viaduct ~2.15 mi (LOC caption 2.7 mi incl. approaches); FEC logo", V),
    (r"Bahia Honda|steel truss|sixty-five feet", "R5 Bahia Honda Rail Bridge: deepest channel, truss, road on top 65 ft (Wikipedia; NRHP)", V),
    (r"Seven Mile|Pigeon Key|five-acre|Knight", "R1/R6 Pigeon Key ~5 acres, construction camp (Pigeon Key Foundation; Wikipedia)", V),
    (r"Trumbo|hundred and thirty acres", "R18 Trumbo Point ~134 acres of fill (Key West marker 477; USGS PP 1751)", V),
    (r"came and went by the thousand|few stayed", "R1 high turnover of workers (Wikipedia Overseas Railroad; Standiford)", A),
    (r"twenty-second of January 1912|22 JAN 1912|eighty-two|died the next year|first train", "R1 first train 22 Jan 1912, Flagler 82; died 20 May 1913 (LOC; Wikipedia)", V),
    (r"1915|freight cars|Havana|car ferry|wagon loaded", "R2 FEC car ferries Key West-Havana from 1915 (FreightWaves; Wikipedia)", V),
    (r"business did not come|Freight on the single|ships kept going", "R2 freight disappointing (Wikipedia Overseas Railroad)", A),
    (r"1928|Lower Matecumbe|No Name|forty miles, a trip|four hours|ferry", "R18 1928 road; ferry Lower Matecumbe-No Name Key ~40 mi, ~4 h (keyshistory.org osh1ferries)", V),
    (r"two half-links", "Framing of R1 + R18", V),
    (r"July 1934|relief|80 %|handed its powers|tourists", "R15 July 1934 city handed powers to Gov. Sholtz; FERA; ~80 % on relief (Florida Trend; KWAHS)", V),
    (r"veterans|In 1934, the federal|camps", "R4 WWI veterans in FERA road camps, Windley Key and Lower Matecumbe (NOAA AOML; myfloridahistory.org)", V),
    (r"350|718|away in Miami", "R4 ~350 of 718 camp veterans in Miami for a ball game (myfloridahistory.org)", V),
    (r"Labor Day|second of September 1935|892|lower pressure|millibars", "R4 landfall 2 Sep 1935 near Long Key, 892 mb, lowest US landfall (NOAA AOML; Landsea 2014)", V),
    (r"185|eighty-five miles", "R4 185 mph 1-min winds (Landsea et al. 2014)", V),
    (r"train|drawbridge|Miami River|locomotive", "R4 rescue train held at Miami River drawbridge; cars swept off at Islamorada; locomotive 447 stayed; all aboard lived (myfloridahistory.org)", V),
    (r"forty miles of track|40 mi|bankrupt|did not rebuild", "R4 ~40 mi of track lost; FEC in receivership since 1931, did not rebuild (Hopkins, Tequesta 1986)", V),
    (r"640|six hundred and forty|1936", "R4 $640,000 (Wilkinson, keyshistory.org; Fla. Sup. Ct. 1936)", A),
    (r"1938|Overseas Highway opened|Concrete decks|drive to Key West", "R5 Overseas Highway opened 1938 on the railbed (Wikipedia; FL State Parks)", V),
    (r"Hemingway|murdered the vets|New Masses|SEPT 1935", "Hemingway, 'Who Murdered the Vets?', New Masses 17 Sep 1935 (Wikipedia 1935 Labor Day hurricane)", V),
    (r"memorial|remains of some", "R4 Florida Keys Memorial, Islamorada, 1937, crypt (NRHP; myfloridahistory.org)", V),
    (r"no fresh water|nothing to drink|coral reef|full of holes|Rain sinks", "R7 Key Largo limestone porous (USGS PP 1751); tDAR cisterns", V),
    (r"drank rain|cistern", "R7 tDAR 'No fresh water except that furnished by the rains: cisterns in Key West'", V),
    (r"1941|Florida City|353|wells", "R7 Navy bought 353 acres at Florida City 18 Aug 1941 (keyshistory.org fkaa)", V),
    (r"hundred and thirty miles|130", "R7 pipeline 128-130 mi (Wilkinson; Time)", V),
    (r"twenty-second of September 1942|22 SEP 1942|six days", "R7 first water 22 Sep 1942; ~6 days in transit (Wilkinson, keyshistory.org)", V),
    (r"1940|fourteen thousand|forty-eight thousand|14,078|47,921|29,957|1950|1960", "R17 Census: 1940 14,078; 1950 29,957; 1960 47,921", V),
    (r"seventeen million|17 MILLION|thousand miles of pipe", "R7 FKAA: ~17 M gal/day, 1,086 mi of pipe (Keys Weekly)", A),
    (r"quarter of a mile|nine in ten|49 %|93 %|within a mile|within one mile|every block of the 2020", "M3 own count geo/measure_road.py (2020 census blocks vs US 1)", O),
    (r"four million|4 MILLION|seawater|quarter of what|2025, makes|Two plants", "R18 Kermit H. Lewin RO plant, Stock Island, May 2025, 4 MGD; ran after Irma (Keys Weekly; WGCU)", V),
    (r"125,000|hundred and twenty-five thousand|4,588|four and a half thousand|May 1980|Mariel", "R16 Mariel: >125,000 (Britannica); 4,588 on 11 May 1980 (Miami Herald)", V),
    (r"April 1982|Border Patrol|searched|federal court", "R8 roadblock south of Florida City, April 1982; injunction refused (Florida Historical Society)", V),
    (r"queue ran for miles|Tourists stayed away", "R8 Wikipedia Conch Republic: long traffic backup, tourism hurt", A),
    (r"24\.5|twenty-four and a half|twenty-four hours|2025-190|half an hour", "R9 F.S. 380.0552(9)(a)2 (2025): 24.5 h; was 24 h; ch. 2025-190", V),
    (r"building permits|new homes|permits capped", "R9 permit allocations tied to clearance time (F.S. 380.0552; ch. 2025-190 s.22)", V),
    (r"mobile homes do not count|ordered out first", "R9 F.S. 380.0552(9)(a)2.a: mobile home residents not permanent residents; county phased evacuation", V),
    (r"Irma|sixth of September|6 SEP|tenth of September|Cudjoe|category four|evening", "R10 NHC TCR AL112017; Monroe County Irma page (visitors 7 a.m., residents 7 p.m., 6 Sep)", V),
    (r"twelve hundred|1,179", "R10 Monroe County: 1,179 homes destroyed", V),
    (r"forty-two bridges|washed out|mile 74|Two short stretches", "R10 all 42 bridges inspected; two 300-ft washouts near mile 74 (CBS/NBC 2017)", V),
    (r"within days|cheapest|never came back", "R10 return 12 Sep; Irma destroyed mostly mobile and older homes (Monroe County; Forgotten Road)", A),
    (r"fifteen hundred random|Four-fifths|Nine-tenths|twenty feet|three feet|81 %|Under 3|Under 5|Under 10|land stands", "M2 own sample geo/measure_height.py (USGS 3DEP)", O),
    (r"1913|foot higher|twice as fast|2\.4|\+1 FT|thirty years|NOAA|tide records|1913-22|2016-25", "M1 own calculation geo/measure_sealevel.py from NOAA CO-OPS 8724580", O),
    (r"2019|ninety-four|94 DAYS|Stillwright", "R18 Stillwright Point 94 days (Keys Weekly; WLRN)", V),
    (r"Twin Lakes|twenty-two million|22 MILLION|Less than a mile", "R12 Twin Lakes $21.97 M for 4,633 ft (Monroe County slides)", V),
    (r"thirty-seven of the forty-four|37 OF 44|early 1980s|1982", "R6 37 of 44 bridges replaced; new Seven Mile Bridge 1982 (Florida Memory; Wikipedia)", V),
    (r"677|six hundred and seventy-seven", "R6 FDOT early estimate $677 M (Miami Herald 2024)", A),
    (r"2023|elkhorn|staghorn|functionally extinct|97\.8|150\+", "R18 Science 2025 (U. Miami Rosenstiel; NBC): 97.8-100 % died; hottest in 150+ years", V),
    (r"eighty thousand|80,000", "R13 Census: 82,874 (2020), 80,406 (2025 est.)", V),
    (r"federal grants|paid for by", "R12 county assessments + FEMA/state grants (Miami Herald; Monroe County)", A),
    (r"footpath|Pigeon Key|span is missing|first two miles", "R6 Old Seven Mile Bridge restored 2.2 mi to Pigeon Key (2022); swing span removed (Wikipedia)", V),
    (r"only way out|one road|one door|only road|single road|hang on", "Framing: US 1 is the only road (Monroe County EM)", V),
    (r"storm of 1935|roadblock of 1982|rebuilt this road twice", "Summary of R4/R5/R6/R8", V),
    (r"Would you keep paying", "Question to the viewer (pinned comment)", V),
    (r"US 1|Overseas Highway", "Monroe County / FDOT: US 1 Overseas Highway", V),
]
CAPTION = "Caption of a Commons photo or a map label; place and date from the file description (visuals.md) or our own drawing"
out, miss = [], []
for line in open(p, encoding='utf-8').read().splitlines():
    cells = line.split("|")
    if len(cells) >= 8 and cells[1].strip().isdigit():
        kind, claim = cells[3].strip(), cells[4].strip()
        if kind == "on screen":
            src, st = CAPTION, V
        else:
            hit = next(((s, t) for r, s, t in RULES if re.search(r, claim, re.I)), None)
            if not hit:
                miss.append(claim); src, st = "", ""
            else:
                src, st = hit
        cells[5], cells[6] = f" {src} ", f" {st} "
        line = "|".join(cells)
    out.append(line)
open(p, 'w', encoding='utf-8').write("\n".join(out) + "\n")
print("unmatched:", len(miss)); [print("  ", m) for m in miss]
