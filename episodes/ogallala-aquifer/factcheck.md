# ogallala-aquifer - fact-check

Status: verified (primary source) | attributed (secondary source, said in the script as "X reported") | own (our measurement or calculation, reproducible) | FIX (wrong, unsupported or quoted without the original text). Sources: R-items of research.md or a URL.

| # | Where | Kind | Claim | Source | Status |
|---|---|---|---|---|---|
| 1 | c01p01 | narration | This is the Texas Panhandle on August 17, 1986. | Landsat scene dates; R23 | own |
| 2 | c01p01 | narration | Each dark circle is one irrigated field. | Landsat scene dates; R23 | own |
| 3 | c01p01 | narration | Now the same place, on the same day of the year, in 2024. | Landsat scene dates; R23 | own |
| 4 | c01p02 | narration | In 1986 about one sixth of this land was actively green. | green_shares.json; tools/ogallala_green.py | own |
| 5 | c01p02 | narration | In 2024, more than half. | green_shares.json; tools/ogallala_green.py | own |
| 6 | c01p02 | stat card | 17% to 58%: Land actively green near Dalhart, Texas, 1986 and 2024 (Share of a 28-mile-wide box with NDVI over 0.5) | Our measurement, Landsat 5 and 9 | own |
| 7 | c01p03 | narration | Thirty miles away, near Stratford, nine percent became fifty-five. | green_shares.json; R18 (NASA) | own |
| 8 | c01p03 | narration | Those two pairs compare different satellites, but the older one alone shows the climb: near Dalhart, seventeen percent by 2010 had already reached forty-six. | green_shares.json; R18 (NASA) | own |
| 9 | c01p03 | narration | Researchers who mapped the whole Landsat record found the same pattern: irrigation grew across this aquifer, even where water was already short. | green_shares.json; R18 (NASA) | own |
| 10 | c01p03 | chart | Land actively green, summer: Stratford 1986 9, Stratford 2024 55.1, Dalhart 1986 17, Dalhart 2024 58.5 | Our measurement, Landsat 5 and 9 | own |
| 11 | c01p03 | on screen | Deines et al., 2019: 34 years of Landsat maps | green_shares.json; R18 (NASA) | own |
| 12 | c01p04 | narration | But the water for those circles comes from below, and on September 30, the state of Kansas told the farmers above it that their rescue plan was not good enough. | R13 | verified |
| 13 | c02p01 | narration | The man who said no is Earl Lewis, the chief engineer of Kansas's water division. | R13 | verified |
| 14 | c02p01 | narration | The plan came from Groundwater Management District 3, around Garden City. | R13 | verified |
| 15 | c02p01 | stat card | Sept 30, 2026: Earl Lewis, Kansas chief engineer, says no | Earl Lewis, Kansas chief engineer, High Plains Journal, Nov 7, 2026 | verified |
| 16 | c02p02 | narration | Kansas had set the rules three years earlier. | R13 | verified |
| 17 | c02p02 | narration | In 2023 the legislature passed a law, 34 to 6 in the Senate and 116 to 6 in the House: every district must file a plan by July 1, 2026. | R13 | verified |
| 18 | c02p02 | stat card | HB 2279: Every Kansas groundwater district must file a plan (Senate 34 to 6, House 116 to 6) | Earl Lewis, Kansas chief engineer, High Plains Journal, Nov 7, 2026 | verified |
| 19 | c02p03 | narration | Lewis had said what he wanted, in a letter the November before: groundwater levels that stop falling within twenty years. | R13 | verified |
| 20 | c02p03 | stat card | 20 years: What the chief engineer asked for | Earl Lewis, Kansas chief engineer, High Plains Journal, Nov 7, 2026 | verified |
| 21 | c02p04 | narration | District 3 filed on time. | R13 | verified |
| 22 | c02p04 | stat card | 60 years: Levels still falling under the district's plan | Earl Lewis, Kansas chief engineer, High Plains Journal, Nov 7, 2026 | verified |
| 23 | c02p06 | narration | The district's engineer says the state objected too late, and the district is appealing. | R14 | attributed |
| 24 | c02p06 | stat card | 3 years: How long the state sat in on the meetings, the district's engineer says | Kansas Public Radio, Oct 19, 2026 | attributed |
| 25 | c03p01 | narration | This is Stratford, Texas, in 1935. | Commons, NOAA photo | verified |
| 26 | c03p01 | on screen | Stratford, Texas, 1935 | Commons, NOAA photo | verified |
| 27 | c03p03 | on screen | Buried machinery, 1936 | Commons, Dust Bowl - Dallas, South Dakota 1936 | verified |
| 28 | c03p04 | narration | Pumps were reaching water in Texas so quickly that by 1951 wells had already dropped more than fifty feet in places. | R15 | verified |
| 29 | c03p04 | stat card | 50+ feet: Water-level declines in parts of Texas, 1938 to 1951 | USGS, SIR 2023-5143 | verified |
| 30 | c03p05 | narration | In 1947 a Colorado farmer named Frank Zybach watched workers hauling irrigation pipe by hand, and thought a sprinkler could walk by itself. | R11 | attributed |
| 31 | c03p06 | narration | He built one in 1948, near Strasburg, and patented it in 1952: a long arm of pipe on wheels, turning around a well. | R11 | verified |
| 32 | c03p06 | stat card | July 22, 1952: Frank Zybach's self-propelled sprinkler is patented | ASABE; National Inventors Hall of Fame | attributed |
| 33 | c03p07 | narration | Watch what that did to western Kansas, from 1986 to this summer. | Landsat scenes, Goodland; green_shares.json if complete | own |
| 34 | c04p02 | narration | It lies under parts of eight states, about 175,000 square miles, from South Dakota to Texas. | R1 | verified |
| 35 | c04p03 | narration | That water supplies about thirty percent of the groundwater used for irrigation in the United States. | R2, R16 | attributed |
| 36 | c04p03 | stat card | 30%: Of US irrigation groundwater | Steward et al., PNAS, 2013 | attributed |
| 37 | c04p04 | narration | In 2019 it still held about 2.9 billion acre-feet. | R1; tools/ogallala_numbers.py | own |
| 38 | c04p04 | narration | We added up the federal figures: about nine percent has gone since 1950. | R1; tools/ogallala_numbers.py | own |
| 39 | c04p04 | stat card | 2.91 billion: Acre-feet of recoverable water in 2019 | USGS, SIR 2023-5143 | verified |
| 40 | c04p04 | stat card | 9%: Of the aquifer's water gone since about 1950 (286.4 of about 3,196 million acre-feet) | Our calculation from USGS, SIR 2023-5143 | own |
| 41 | c04p05 | narration | Nine percent. | R1; tools/ogallala_numbers.py | own |
| 42 | c05p01 | narration | Because that average hides nearly everything. | R15 | verified |
| 43 | c05p01 | narration | This is the government's own map of the change, about 1950 to 2019. | R15 | verified |
| 44 | c05p02 | narration | Its average fell less than half a foot, and one well there rose eighty-six feet. | R15 | verified |
| 45 | c05p02 | chart | Average water-level change since about 1950: Nebraska 0.4, Kansas 27.3, Texas 44.1 | USGS, SIR 2023-5143 | verified |
| 46 | c05p03 | narration | Kansas fell an average of twenty-seven feet. | R15 | verified |
| 47 | c05p03 | narration | Texas, forty-four. | R15 | verified |
| 48 | c05p03 | chart | Average water-level decline since about 1950: Nebraska 0.4, Kansas 27.3, Texas 44.1 | USGS, SIR 2023-5143 | verified |
| 49 | c05p04 | narration | One Texas well dropped two hundred sixty-five feet: sixteen times the average for the whole aquifer. | R15; tools/ogallala_numbers.py | own |
| 50 | c05p04 | stat card | 265 feet: The largest decline at one well, in Texas (Sixteen times the aquifer's 16.5-foot average) | USGS, SIR 2023-5143 | verified |
| 51 | c05p05 | narration | Of 286 million acre-feet gone, Texas accounts for about fifty-nine percent. | R15; own shares | own |
| 52 | c05p05 | narration | Kansas, twenty-five. | R15; own shares | own |
| 53 | c05p05 | narration | Nebraska, under one. | R15; own shares | own |
| 54 | c05p05 | chart | Water lost since about 1950: Texas 169.6, Kansas 72, Nebraska 2.7 | USGS, SIR 2023-5143; shares are our calculation | verified |
| 55 | c05p06 | narration | From 2017 to 2019 the aquifer as a whole gained water: 1.6 million acre-feet. | R15 | verified |
| 56 | c05p06 | narration | But Nebraska gained 4.3 million, while Texas lost 2.7 million. | R15 | verified |
| 57 | c05p06 | stat card | +1.6 million: Acre-feet, the whole aquifer, 2017 to 2019 | USGS, SIR 2023-5143 | verified |
| 58 | c05p06 | chart | Change in stored water, 2017 to 2019: Nebraska gained 4.3, Texas lost 2.7 | USGS, SIR 2023-5143 | verified |
| 59 | c05p08 | narration | A Kansas study put numbers on that: recharge replaces about fifteen percent of what is pumped. | R2 | attributed |
| 60 | c05p08 | narration | If you drained the aquifer there, refilling it would take five hundred to thirteen hundred years. | R2 | attributed |
| 61 | c05p08 | stat card | 15%: Of current pumping is replaced by recharge, Kansas | Steward et al., PNAS, 2013 | attributed |
| 62 | c05p08 | stat card | 500-1,300 years: To refill a depleted aquifer in Kansas, on average | Steward et al., PNAS, 2013 | attributed |
| 63 | c05p09 | narration | That study also projected, in 2013, that nearly seventy percent of the water under Kansas would be gone in fifty years on existing trends. | R2 | attributed |
| 64 | c05p09 | stat card | 69%: Of Kansas's groundwater gone by about 2063 on 2013 trends (A projection) | Steward et al., PNAS, 2013 | attributed |
| 65 | c05p10 | narration | In some parts of Kansas, less than forty percent of the aquifer's original thickness remains. | R3 | verified |
| 66 | c05p10 | stat card | Under 40%: Of the original thickness left in some Kansas areas | Kansas Geological Survey, 2023 | verified |
| 67 | c06p02 | narration | In 1980 what was described as the world's largest beef plant opened at Holcomb, just outside Garden City. | R21 | attributed |
| 68 | c06p02 | narration | A 2021 Associated Press count put Kansas feedlots at 2.5 million cattle, eating more than 6.5 billion pounds of corn a year. | R21 | attributed |
| 69 | c06p02 | stat card | 2.5 million: Cattle in Kansas feedlots (Eating more than 6.5 billion pounds of corn a year) | Associated Press, 2021 | attributed |
| 70 | c06p03 | narration | In Kansas, this aquifer supplies seventy to eighty percent of the water residents use each day. | R16 | attributed |
| 71 | c06p03 | stat card | 70-80%: Of the water Kansas residents use each day | Stateline, Feb 1, 2024 | attributed |
| 72 | c06p04 | narration | Guymon, Oklahoma has about thirteen thousand people and eighteen wells. | R16 | attributed |
| 73 | c06p04 | narration | It has committed some four and a half million dollars to find new ones, with no guarantee of water. | R16 | attributed |
| 74 | c06p05 | narration | Its interim city manager said it plainly in 2024: "We're running out of water." | R16 | attributed |
| 75 | c06p06 | narration | Farther southwest, Clovis, New Mexico and its neighbors are building a pipeline of more than eight hundred million dollars, to bring in river water from a reservoir. | R16 | attributed |
| 76 | c06p06 | narration | The head of their water authority says these towns could not last long without it. | R16 | attributed |
| 77 | c06p06 | stat card | $800 million+: A pipeline to replace groundwater in eastern New Mexico | Stateline, Feb 1, 2024 | attributed |
| 78 | c06p07 | narration | On current trends, about a quarter of today's irrigated land on the aquifer could not be irrigated by 2100, and thirteen percent of that land may not suit dryland crops either. | R18 | attributed |
| 79 | c06p07 | stat card | 24%: Of irrigated land may lose irrigation by 2100 (A projection) | Deines et al., Agricultural Water Management, 2020 | attributed |
| 80 | c07p01 | narration | Since 1904, a landowner there may pump as much groundwater as they like, even if a neighbor's well runs dry. | R8 | verified |
| 81 | c07p01 | stat card | 1904: Texas adopts the rule of capture for groundwater | Houston & T.C. Ry. v. East | verified |
| 82 | c07p02 | narration | In 1999 landowners whose wells had gone dry took a bottled-water company to the Texas Supreme Court. | R8 | verified |
| 83 | c07p02 | narration | The court left the rule standing, and said changing it was a job for the legislature. | R8 | verified |
| 84 | c07p02 | stat card | 1999: Texas Supreme Court keeps the rule of capture | Sipriano v. Great Spring Waters of America | verified |
| 85 | c07p03 | narration | In 2001 the oilman T. | R19 | attributed |
| 86 | c07p03 | narration | His company leased about 150,000 acres in the Panhandle, and planned to sell water to Dallas-Fort Worth through a 385-mile pipeline. | R19 | attributed |
| 87 | c07p04 | stat card | 200,000: Acre-feet a year Pickens planned to sell | AAPG Explorer, July 2001 | attributed |
| 88 | c07p05 | narration | But look at the target for four Panhandle counties here: forty percent of the water left, after fifty years. | R20 | attributed |
| 89 | c07p05 | stat card | 40% left: After 50 years: the district's goal for four Panhandle counties (Dallam, Sherman, Hartley and Moore) | Texas Water Journal, on North Plains GCD | attributed |
| 90 | c08p01 | narration | Wells around there once drew about a thousand gallons a minute. | R17 | attributed |
| 91 | c08p01 | narration | In 2021 Tim Black's gave about fifty. | R17 | attributed |
| 92 | c08p01 | stat card | 1,000 to 50: Gallons a minute, wells near Muleshoe, Texas | Associated Press, 2021 | attributed |
| 93 | c08p03 | narration | An hour southwest of Amarillo, Chris Grotegrut has put about three quarters of his family's 11,000 acres back into native grass. | R17 | attributed |
| 94 | c08p03 | narration | That is the land's old cover, the one the plows removed before the Dust Bowl. | R17 | attributed |
| 95 | c08p03 | stat card | 75%: Of one family's 11,000 acres, back in native grass | Associated Press, 2021 | attributed |
| 96 | c08p04 | narration | This July our measurement near Dalhart fell to about fifteen percent, from one clear day. | green_shares.json | own |
| 97 | c08p04 | narration | One day is not a trend. | green_shares.json | own |
| 98 | c08p04 | stat card | 15%: Land actively green near Dalhart, July 30, 2026 (One clear day, not a trend) | Our measurement, Landsat 8 | own |
| 99 | c09p01 | narration | In 2013, farmers in Sheridan County, northwest Kansas, did something nobody made them do. | R3, R5 | verified |
| 100 | c09p01 | narration | They capped their own pumping for five years. | R3, R5 | verified |
| 101 | c09p02 | narration | The target was a twenty percent cut. | R16 | attributed |
| 102 | c09p02 | narration | They reached about twenty-three. | R16 | attributed |
| 103 | c09p02 | stat card | 23%: Average cut, first five years, Sheridan 6 (Target: 20%) | Stateline, Feb 1, 2024 | attributed |
| 104 | c09p03 | narration | From 2002 to 2012 levels fell about two feet a year. | R3 | verified |
| 105 | c09p03 | narration | From 2013 to 2022, about half a foot. | R3 | verified |
| 106 | c09p03 | chart | Average yearly water-level decline, Sheridan 6: 2002-2012 2, 2013-2022 0.5 | Kansas Geological Survey, 2023 | verified |
| 107 | c09p05 | narration | Wichita County has cut pumping by about forty percent. | R3, R16 | attributed |
| 108 | c09p05 | narration | Outside Garden City, Gina and Marc Gigot, whose father dug the well more than fifty years ago, had stopped growing corn on their farm by 2024. | R3, R16 | attributed |
| 109 | c09p05 | stat card | 40%: Pumping cut in Wichita County, Kansas | Kansas Geological Survey, 2023 | verified |
| 110 | c09p06 | narration | Even the Farm Bureau's president said in 2024, "we don't have decades." | R16 | attributed |
| 111 | c09p06 | on screen | Saving water, one nozzle at a time | R16 | attributed |
| 112 | c09p07 | narration | Because a cut that looks fine on a map hits people one field at a time. | Our framing | own |
| 113 | c10p01 | narration | A report to its legislature warned in 1955: "Ground-water mining is a serious problem." | R16 | attributed |
| 114 | c10p02 | narration | The state created its groundwater districts in 1972, and for decades its answer stayed local and voluntary, a policy often called planned depletion. | R13, R7, R16 | attributed |
| 115 | c10p02 | stat card | 1972: Kansas creates groundwater management districts | Earl Lewis, Kansas chief engineer, High Plains Journal, Nov 7, 2026 | verified |
| 116 | c10p03 | narration | In February, more than two hundred farmers came to hear District 3's plan: cut pumping five percent a year for twenty years, 27.7 percent in all, according to its engineer. | R6 | attributed |
| 117 | c10p03 | stat card | 27.7%: The district's first proposal, over twenty years | KCUR / HPPR, Feb 2, 2026 | attributed |
| 118 | c10p04 | narration | Three inches less water could mean about fifty fewer bushels of corn an acre, up to two hundred dollars. | R6 | attributed |
| 119 | c10p04 | stat card | $200 an acre: One farmer's estimate of the cost of three inches less | KCUR / HPPR, Feb 2, 2026 | attributed |
| 120 | c10p05 | narration | He said he would be dead in ten years. | R6 | attributed |
| 121 | c10p06 | narration | The plan filed in July gave some areas with deep water fifty years to cut thirty percent. | R14 | attributed |
| 122 | c10p06 | narration | The district also asked the state for ten million dollars a year to pay landowners for saving water. | R14 | attributed |
| 123 | c10p06 | stat card | $10 million: A year: what the district asked of the state | Kansas Public Radio, Oct 19, 2026 | attributed |
| 124 | c10p07 | narration | He says that in most of the district, after fifty years, groundwater would be on the verge of unusable, even under the district's own plan. | R13 | verified |
| 125 | c10p07 | stat card | 50 years: Then groundwater near unusable in most of the district, Lewis says | Earl Lewis, Kansas chief engineer, High Plains Journal, Nov 7, 2026 | verified |
| 126 | c10p08 | narration | Farmers and the Kansas Farm Bureau say the cuts go too far, some as deep as forty-four percent, and that they violate water rights. | R14 | attributed |
| 127 | c10p08 | stat card | 44%: Pumping cuts in some areas of northwest Kansas | Kansas Public Radio, Oct 19, 2026 | attributed |
| 128 | c10p09 | narration | Irrigation rights can make land worth almost twice as much, by the district's own testimony. | R14 | attributed |
| 129 | c10p09 | narration | The state denied the Bureau's request. | R14 | attributed |
| 130 | c10p09 | stat card | Nearly 2x: What irrigation rights can add to the value of land | Kansas Public Radio, Oct 19, 2026 | attributed |
| 131 | c10p10 | narration | So one Kansas district is told it does too little, and another that it does too much. | R13, R14 | verified |
| 132 | c11p01 | narration | District 3 will appeal to the Kansas Secretary of Agriculture, and hopes to start parts of its plan meanwhile. | R14 | attributed |
| 133 | c11p02 | narration | Every January, crews drive back out to about fourteen hundred wells. | R3, R4, R16 | attributed |
| 134 | c11p02 | narration | One of them, Brownie Wilson of the Kansas survey, feeds a steel tape down each well, and the wet part of the tape gives him the water level. | R3, R4, R16 | attributed |
| 135 | c11p02 | narration | Some of his wells have dropped more than a hundred feet since 2001. | R3, R4, R16 | attributed |
| 136 | c11p02 | stat card | 1,400 wells: Measured each January across western Kansas | Kansas Geological Survey, 2023 | verified |
| 137 | c11p02 | stat card | 100+ feet: Drop in some Kansas wells since 2001 (Brownie Wilson, Kansas Geological Survey) | Stateline, Feb 1, 2024 | attributed |
| 138 | c11p03 | narration | The Kansas survey says levels in the worst areas could hold steady for a decade or two, with pumping cuts of eighteen to thirty-two percent. | R3 | verified |
| 139 | c11p03 | stat card | 18-32%: Cuts that could hold levels for one to two decades | Kansas Geological Survey, 2023 | verified |
