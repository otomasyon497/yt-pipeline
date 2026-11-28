"""M1/M2: how many Idahoans live in the north, on how much of the land, and how empty the inside of the north is.

Inputs (public domain, US Census Bureau):
  .cache/geo/census/CenPop2020_Mean_BG16.txt   2020 census population per block group, with its centre of population
  .cache/geo/cb_2023_us_county_5m.zip          county boundaries + land area (ALAND)
North Idaho = the ten northern counties (Boundary, Bonner, Kootenai, Shoshone, Benewah, Latah, Clearwater, Nez Perce,
Lewis, Idaho), the usual "North Idaho" definition; roughly the land north of the Salmon River.
Run: venv python -I episodes/northern-idaho/geo/measure_population.py   -> measure_population.txt
"""
import csv, io, zipfile
from pathlib import Path
import shapefile
from shapely.geometry import shape, Point
from shapely.ops import unary_union
from pyproj import Geod

ROOT = Path(__file__).resolve().parents[3]
G = ROOT / ".cache/geo"
NORTH = {"021": "Boundary", "017": "Bonner", "055": "Kootenai", "079": "Shoshone", "009": "Benewah", "057": "Latah",
         "035": "Clearwater", "069": "Nez Perce", "061": "Lewis", "049": "Idaho"}
geod = Geod(ellps="WGS84")

z = zipfile.ZipFile(G / "cb_2023_us_county_5m.zip")
r = shapefile.Reader(shp=io.BytesIO(z.read("cb_2023_us_county_5m.shp")), dbf=io.BytesIO(z.read("cb_2023_us_county_5m.dbf")))
f = [x[0] for x in r.fields[1:]]
land, geoms = {}, {}
for sr in r.iterShapeRecords():
    a = dict(zip(f, sr.record))
    if a["STATEFP"] == "16":
        land[a["COUNTYFP"]] = a["ALAND"] / 1e6
        geoms[a["COUNTYFP"]] = shape(sr.shape.__geo_interface__)

rows = list(csv.DictReader(open(G / "census/CenPop2020_Mean_BG16.txt", encoding="utf-8-sig")))
pop = {}
for x in rows:
    pop[x["COUNTYFP"]] = pop.get(x["COUNTYFP"], 0) + int(x["POPULATION"])
tot, totl = sum(pop.values()), sum(land.values())
np_, nl = sum(pop[c] for c in NORTH), sum(land[c] for c in NORTH)
out = [f"Idaho 2020: {tot:,} people, {totl:,.0f} km2 land ({totl/2.58999:,.0f} sq mi)",
       f"North Idaho (10 counties): {np_:,} people = {np_/tot*100:.1f} %; land {nl:,.0f} km2 = {nl/totl*100:.1f} %",
       f"density: north {np_/nl:.1f}/km2 ({np_/nl*2.58999:.0f}/sq mi), rest of Idaho {(tot-np_)/(totl-nl):.1f}/km2"]
for c in sorted(NORTH, key=lambda c: -pop[c]):
    out.append(f"  {NORTH[c]:<11} {pop[c]:>8,}  {land[c]:>8,.0f} km2  {pop[c]/land[c]:6.1f}/km2  {pop[c]/np_*100:5.1f} % of the north")
k = pop["055"]
out.append(f"Kootenai alone: {k/np_*100:.1f} % of the north's people on {land['055']/nl*100:.1f} % of its land")
# block groups: how much of the north's land holds block groups under 1 person per km2
bgs = [x for x in rows if x["COUNTYFP"] in NORTH]
# M2: people living within 15 km of the two big towns' corridors is not used; instead the share of the north's
# people whose block-group centre lies within 25 km of Coeur d'Alene, Lewiston or Moscow
towns = {"Coeur d'Alene": (-116.78, 47.68), "Lewiston": (-117.02, 46.42), "Moscow": (-117.00, 46.73)}
near = 0
for x in bgs:
    lo, la = float(x["LONGITUDE"]), float(x["LATITUDE"])
    if min(geod.inv(lo, la, a, b)[2] for a, b in towns.values()) <= 25000:
        near += int(x["POPULATION"])
out.append(f"north's people within 25 km of Coeur d'Alene, Lewiston or Moscow: {near:,} = {near/np_*100:.1f} %")
# Idaho County (the big one in the middle): people and land
ic = "049"
out.append(f"Idaho County: {pop[ic]:,} people on {land[ic]:,.0f} km2 ({land[ic]/2.58999:,.0f} sq mi) = {pop[ic]/land[ic]:.1f}/km2; "
           f"its land = {land[ic]/totl*100:.1f} % of Idaho")
Path(__file__).with_suffix(".txt").write_text("\n".join(out) + "\n", encoding="utf-8"); print("\n".join(out))
