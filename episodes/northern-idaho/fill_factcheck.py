"""Fill Source/Status of episodes/northern-idaho/factcheck.md (first matching rule wins)."""
import re, sys
sys.stdout.reconfigure(encoding="utf-8")
p = r'C:\projeler\yt-pipeline\episodes\northern-idaho\factcheck.md'
V, A, O = "verified", "attributed", "own"
RULES = [
    (r"White Bird Canyon|17 JUNE 1877|fled east over the Lolo Trail", "R16 US Army (White Bird Canyon, 17 Jun 1877); NPS Bear Paw (1,170 mi, 126 days)", V),
    (r"cut Montana Territory", "R6 Wikipedia Idaho Territory / Montana Territory (1864)", V),
    (r"6.3 MILLION|six point three", "R21 SPLC Keenan v. Aryan Nations", V),
    (r"Pulaski tool|tool Pulaski designed", "R23 USFS history (Pulaski tool from 1911)", V),
    (r"traffic light|Seattle and Boston", "R19 ITD 2005; Jalopnik; Wikipedia I-90 in Idaho", V),
    (r"fires joined into one", "R10 Wikipedia Great Fire of 1910", V),
    (r"seventy-three men", "R8 MSHA Sunshine Mine Disaster", V),
    (r"We added up the 2020", "M1 own count geo/measure_population.py", O),
    (r"mills that replaced the mines", "Framing / summary of R11", V),
    (r"^Reason (one|two|three|four|five|six)\.|So why does|There are six reasons|answer runs through|Even the map looks strange|really the answer|So we have mountains|What is left is|If you lived in|which brings us to|But to understand why|was not the only industry|The territory still had|What they did have|The one place in the north|is cut off from the rest|does not belong to anyone|was settled first|paid its wages for a century|Because a wall|Because its capital|Because most of its|it is a different place|land stayed with the government", "Framing / summary of facts cited elsewhere in this table", V),
    (r"one Idahoan in five|1 IN 5|47 %|six per cent of its land|Two in three|2 IN 3|fifteen miles of just three|quarter of the state|Vermont and New Hampshire|crowd into one corner|full in one place|full in one corner", "M1 own count geo/measure_population.py (2020 census block groups; Census county land)", O),
    (r"Idaho County|eight thousand square|8,477|sixteen thousand|16,541|2 PER SQ MI|New Jersey|Grangeville", "M1 Census 2020 (Idaho County 16,541; 8,477 sq mi land); NJ land 7,354 sq mi; Grangeville ~3,100 (2020 census)", V),
    (r"route planner|four hundred and twenty|seventy miles longer|423 MI|about the same time", "M3 own route test geo/drive_osrm.txt (OSRM / OpenStreetMap)", O),
    (r"forty-five miles|45 MILES|chimney", "R14 International Boundary Commission (45 mi); Britannica", V),
    (r"Pacific time|Mountain time|different clock|clocks", "R2 49 CFR 71 (Salmon River time-zone line)", V),
    (r"Seattle|Spokane, just across|its big city|watches its television|shops there", "Framing: Spokane is the region's metro (Spokane-Coeur d'Alene CSA, Census); Pacific time as Seattle (49 CFR 71)", V),
    (r"Frank Church|two and a half million|2\.37|largest single block|River of No Return Wilderness", "R1 USFS (2,366,757 acres; largest contiguous wilderness in the lower 48)", V),
    (r"Selway|Gospel|roadless forest", "R1 USFS EDW wilderness boundaries; Wikipedia (3.3 M acre roadless area)", V),
    (r"River of No Return|freight boats|broke them up|sold the wood", "R22 USFWS National Wild and Scenic Rivers; Britannica (one-way scows)", V),
    (r"Hells Canyon|7,993|eight thousand feet|deepest river gorge", "R22 USFS Hells Canyon NRA (7,993 ft)", V),
    (r"Clearwater, the Salmon River and the Bitterroot|roughest country", "R1 relief: Clearwater, Salmon River, Bitterroot ranges (Geography of Idaho, Wikipedia)", V),
    (r"White Bird|1975|forty years|one road between|two lanes|US Highway 95|US 95", "R2 Wikipedia US 95 in Idaho; White Bird Hill Summit (old grade the only link ~40 years; new grade 1975)", V),
    (r"Lochsa|Lolo|1962|Lewis and Clark", "R2 ISHS ref 286; Wikipedia US 12 (finished 1962)", V),
    (r"sixty-two per cent|62 %|Nevada and Utah|federal land", "R1 CRS 2012 via Ballotpedia (61.65 %; NV 80 %, UT 63 %)", V),
    (r"seven million acres|7 MILLION|two national forests|national forests? (cover|run)|Idaho Panhandle and the Nez", "R23 USFS LAR table 28 (2.94 M + 4.07 M acres)", V),
    (r"timber and water", "R23 national forests set aside for timber and watershed (Organic Act 1897)", V),
    (r"1910|Big Burn|three million acres|3 MILLION|Connecticut|eighty-five|~85|hurricane-force|twentieth of August|20 AUGUST|dry year|hundreds of small fires", "R10 Wikipedia Great Fire of 1910; PBS; NWCG; HistoryLink (3 M acres; ~85 dead; CT 3.56 M acres)", V),
    (r"Wallace burned|mayor of Wallace|Trains carried|soldiers pulled", "R19 Wikipedia Great Fire of 1910; Spokesman-Review 2010 (evacuation trains)", V),
    (r"Pulaski|forty-five men|45 MEN|40 OF 45|mine tunnel|gunpoint|wet blankets|five or six", "R10 Wikipedia; PBS American Experience 'The Big Burn'", V),
    (r"1935|ten o'clock|10 AM|stop every fire|half axe|AXE \+ HOE|wildland firefighters", "R23 USFS history (10 a.m. policy 1935; Pulaski tool from 1911)", V),
    (r"Elias Pierce|1860|thousands of miners|tent town|They called it Lewiston", "R4 NPS Nez Perce NHP (gold 1860; ~15,000 miners; Lewiston)", V),
    (r"Nez Perce land|ninety per cent|-90 %|1863 the United States|thief|never signed", "R4 NPS Treaty of 1863 (90 % reduction)", V),
    (r"1877|White Bird Canyon|cavalry|eleven hundred and seventy|1,170|hundred and twenty-six|Chief Joseph|forty miles short|four states", "R16 US Army; NPS Bear Paw", V),
    (r"Idaho Territory|first capital|Boise Basin|BOISE BASIN|voters lived in the south|1864|DEC 1864|1865|Fort Lapwai|seal|archives|1866|supreme court|Lewiston refused|carried off by soldiers", "R5 ISHS ref 344; Wikipedia Idaho Territory; Lewiston Tribune", V),
    (r"Montana Territory|Bitterroot Mountains|narrow strip|Then the shape", "R6 Wikipedia Idaho Territory / Montana Territory (1864, Bitterroot crest)", V),
    (r"three hundred miles away|run from Boise", "Geography: Coeur d'Alene - Boise ~280 mi straight line (own measure)", O),
    (r"1887|Washington Territory|Grover Cleveland|telegram|let the bill die|president's desk|Olympia", "R15 Wikipedia Idaho Territory; Spokesman-Review 2015 (pocket veto, 1887)", V),
    (r"University of Idaho|1889|Moscow, in the north|push to join Washington", "R15 University of Idaho catalog; Wikipedia (30 Jan 1889)", V),
    (r"1890|became a state|still argue|have gone to Washington", "R15 statehood 3 Jul 1890; secession proposals recur (Spokesman-Review)", A),
    (r"1880s prospectors|South Fork|Wallace, Kellogg and Mullan|Silver Valley|narrow canyon", "R7 Wikipedia Silver Valley; ISU Digital Geology", V),
    (r"billion ounces|1 BILLION|richest silver districts|Since 1884", "R7 ISU (1.18 bn oz); Mining.com (1.2 bn)", A),
    (r"Interstate 90 once ran|1991|traffic light|Seattle and Boston|viaduct|funeral", "R19 ITD 2005; Jalopnik; Wikipedia I-90 in Idaho", V),
    (r"1892|1899|dynamite|3,000 LB|Wardner|seized a train|union men|men underground\.|miners' union", "R7 Wikipedia 1899 Coeur d'Alene labor confrontation; ISHS ref 210", V),
    (r"Steunenberg|martial law|MARTIAL LAW|bullpen|Federal troops|Caldwell|1905|30 DEC", "R7 Wikipedia; ISHS ref 447; Idaho PTV", V),
    (r"Harry Orchard|HARRY ORCHARD|Haywood|1907|ACQUITTED|labour history", "R7 famous-trials.com Haywood chronology; Wikipedia", V),
    (r"Sunshine|1972|173|ninety-one|91 MINERS|carbon monoxide|never found|1977", "R8 MSHA Sunshine Mine Disaster; Spokesman-Review 2022", V),
    (r"Bunker Hill smelter|baghouse|1973|SEPT 1973|kept the smelter running|melted lead ore", "R9 EPA Bunker Hill Superfund site documents", V),
    (r"blood lead|HIGHEST EVER|Lead dust", "R9 EPA (children's blood lead among the highest ever measured in the US)", V),
    (r"1981|Superfund|SUPERFUND|seven thousand|7,000", "R9 EPA (NPL 1983; 7,000+ properties) [closure 1981 per Wikipedia; some sources 1982]", V),
    (r"1968|tailings|seventy-five million|75 MILLION|bed of Lake Coeur", "R17 USGS OFR 93-656; NASEM 2022", V),
    (r"thirty-eight hundred|twenty-three hundred|Kellogg, people|3811|2314|3,811|-39 %", "R20 US Census via Wikipedia Kellogg (3,811 in 1970; 2,314 in 2020)", V),
    (r"Silver Mountain|gondola|3\.1|1990", "R20 Silver Mountain Resort; Shoshone News-Press 2020", V),
    (r"Potlatch|1906|white pine sawmill|1983|whole town", "R11 Idaho Capital Sun 2022 / Intermountain Histories", V),
    (r"Orofino, Pierce and St\. Maries|fewer of them|machines replaced|from Canada|Less federal land", "R11 NPR 2016; Idaho Capital Sun 2022", A),
    (r"plywood|215|2016|six months", "R11 Spokesman-Review 2000; NPR 2016", V),
    (r"young left|grew older|argued about it|worth more standing|more logging", "Framing: two-sided question (Idaho Capital Sun 2022)", V),
    (r"Kootenai is growing|seventeen thousand|\+9\.9|ten per cent|newcomers|Southern California|arriving faster", "R13 Census QuickFacts Kootenai (171,362 -> 188,323); Census migration via CdA Press / KREM", A),
    (r"Lewiston, at the southern end|seaport|Barges|eight locks|465|wheat, peas", "R18 Port of Lewiston", V),
    (r"Aryan Nations|Hayden Lake|six point three|\$6\.3|bankrupt|torn down|problem with its name", "R21 SPLC Keenan v. Aryan Nations; ABC News 2001", V),
    (r"Interstate 90, half an hour|airport|not really cut off", "Geography: Coeur d'Alene - Spokane ~33 mi on I-90 (own measure)", O),
    (r"Mullan Road|1859|1862", "R3 Kootenai County; Wikipedia Mullan Road", V),
    (r"Pend Oreille|1,150|eleven hundred and fifty|largest lake|ice age", "R12 NAVSEA Bayview (1,150 ft)", V),
    (r"1942|Navy|training base|Japanese bombers|three hundred thousand|293,381|second-largest|two and a half years|Farragut|submarines", "R12 Idaho Military Museum; NPS; NAVSEA ARD", V),
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
