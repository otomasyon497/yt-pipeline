# colorado-river: outline (target 16-18 min, about 2,400 words)

Working title: "America's Two Biggest Reservoirs Hit Record Lows. Now the States Are Suing." (to test with yt-package
in step 5)
Central question: the river was divided in 1922 for more water than it carries. Now that the reservoirs are nearly
empty, who gives up water first: the farms, the cities, or the states upstream?
Answer at the end: for 2027 and 2028 Washington has decided (the Lower Basin pays); after that the Compact itself is
contested, a court or the Supreme Court may decide, and October's rain did not change the arithmetic.

## 0. Cold open (about 1:10, no card)
- HERO: Sentinel-2 wipe of Lake Powell at Bullfrog Bay, 2019 vs September 2026: blue bays turn into red rock.
- 15 Sep 2026: Lake Powell's lowest level since it filled. 22 Oct: Lake Mead's. Together: less water than at any time
  since 1963.
- 21 Aug 2026: Washington orders Arizona, California and Nevada to give up 1.25 million acre-feet a year; the four
  states upstream are asked for nothing. Three days later Nevada sues. Title.

## 1. The Promise of 1922 (about 2:30, curious)
- Map: the basin from the Rockies to the Gulf of California; seven states and Mexico; Lees Ferry as the line
  between the Upper and Lower Basin.
- Santa Fe, 1922 (photo): 7.5 million acre-feet a year for each basin; the Upper Basin must not let ten-year flow at
  Lee Ferry fall below 75 million. 1944: 1.5 million for Mexico.
- Chart: they counted on about 16.4 million a year; the long average is about 14.8; since 2000 about 12.4.
- Hoover Dam (1936) and Glen Canyon Dam (1963) build two lakes that held about three and a half years of the
  river at their 1983 peak (OWN CALC: 52.5 million acre-feet / 14.76 average).
- Bridge: for decades the two lakes hid the gap. Then the gap started to show.

## 2. Where the Water Goes (about 2:30, curious)
- Camera follows the water: Lake Havasu, the CAP canal 336 miles to Phoenix and Tucson; the Colorado River Aqueduct
  to Los Angeles; the All-American Canal to the Imperial Valley; Las Vegas's intakes; Morelos Dam; the dry delta.
- Richter et al. 2024: agriculture is 74 % of direct human use; alfalfa and other cattle feed 46 %.
- Las Vegas uses about 40 % less river water than 25 years ago with 800,000 more people.
- ASK 1: "Hay and alfalfa for cattle use more of the river than all its cities and industries combined (46 % vs
  about 26 % of direct use). Waste, or exactly what senior water rights are for?"

## 3. Twenty-Six Dry Years (about 2:30, tension)
- Charts: Lake Mead 1935-2026 and Lake Powell 1980-2026 (1983 peak, 2022 and 2026 records).
- OWN CALC: the two lakes held 46.5 million acre-feet in January 2000 and 12.0 million in September 2026: 74 % gone.
  Lake Powell's surface is 63 % smaller.
- Satellite: MODIS wipe of Lake Powell, September 2000 vs 2026; Sentinel-2 wipe of Lake Mead's Overton Arm.
- Winter 2025-26: the lowest snowpack on record; April-July inflow 18 % of average.
- Bridge: low in Lake Powell there is a number engineers fear, and in September the lake was 27 feet above it.

## 4. The Line at 3,490 (about 2:30, tension)
- Glen Canyon Dam: 1,320 megawatts. Below 3,490 ft the turbines stop and water can leave only through four outlet
  tunnels never meant for long use (Reclamation memo). Dead pool 3,370 ft.
- What was done in 2026: the smallest release since 1966 (6.0 million acre-feet, OWN CHECK) and up to 1 million
  acre-feet from Flaming Gorge.
- OWN MAP: Lake Powell's shore at 3,490 and 3,370 ft from USGS survey data.
- Lake Mead: Las Vegas's intakes at 1,050 and 1,000 ft and the deep "third straw"; Reclamation's October forecasts
  put Mead between about 1,008 and 1,016 ft next summer.
- One content-tied subscribe line.

## 5. Washington Steps In (about 2:30, tension -> curious)
- Missed deadlines; the Final EIS (31 Jul); the Record of Decision (21 Aug).
- Chart: the cuts: Arizona -760,000 (27 %), California -440,000 (10 %), Nevada -50,000, Mexico -250,000 (Minute 334);
  the Upper Basin 0.
- OWN CALC: Mead and Powell lost 638,000 acre-feet to evaporation in 2026: 84 % of Arizona's cut, twice Nevada's
  whole allocation.
- The Compact fight: Upper Basin "75 million is our obligation" vs Lower Basin "82.5 with Mexico". OWN CALC: 80.0
  million passed the dam in the last ten years. Kuhn: the "first tripwire".
- Both sides in their words: Upper Basin governors (mandatory, uncompensated cuts to 1800s water rights; Flaming
  Gorge water) vs Lombardo and Hobbs ("draconian").
- ASK 2: "Should the four states upstream share the cuts, even if the Compact may not require it?"

## 6. Into Court (about 1:45, tension)
- 24 Aug: Nevada sues; 16 Oct: Arizona and CAP move to join. Burgum: "you can't be injured in theory".
- Nevada's worst case after 2028: more than 70 % of its water.
- Experts on a Supreme Court Compact case: years, and "everybody loses".
- ASK 3: "Should judges decide how the river is shared, or should the states be forced back to the table?"

## 7. Rain in October (about 1:30, calm)
- 20-22 Oct: 65,000 cubic feet per second into Lake Powell, the second-highest October flow since 1963; Powell up
  17 ft. The forecasts and the arithmetic are unchanged.
- Close at the delta (S2): the river that used to reach the sea now rarely does (Richter et al. 2024).
- ASK 4 / pinned comment: "Who should give up water first: the farms, the cities, or the states upstream?"

## Features this needs (step 4)
- Lake Powell shoreline at a given elevation from the USGS topobathymetric DEM (bathy.py, new basin "powell";
  NGVD29 -> NAVD88 +2.91 ft); test ScienceBase access from Actions first.
- Canal lines (CAP, Colorado River Aqueduct, All-American Canal) and the Colorado / Green rivers in lines.json.
- Basin outline as a "file:" GeoJSON from the USGS Watershed Boundary Dataset (regions 14 and 15).
- tools/colorado_numbers.py: reproduce the own calculations from Reclamation's CSVs.
