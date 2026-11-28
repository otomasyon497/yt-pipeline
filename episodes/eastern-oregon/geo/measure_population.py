"""M1/M2: how many Oregonians live east of the Cascades, on how much of the land, and how empty the inside is.

Inputs (public domain, US Census Bureau):
  .cache/geo/census/CenPop2020_Mean_BG41.txt   2020 census population per block group, with its centre of population
  .cache/geo/cb_2023_us_county_5m.zip          county boundaries + land area (ALAND)
Eastern Oregon = the 18 counties east of the Cascade crest (the usual definition, e.g. Oregon Blue Book regions
"Central" + "Eastern" + Klamath/Lake); "far east" = the 8 counties east of the John Day / Deschutes country.
Run: venv python -I episodes/eastern-oregon/geo/measure_population.py   -> measure_population.txt
"""
import csv, io, zipfile
from pathlib import Path
import shapefile
from pyproj import Geod

ROOT = Path(__file__).resolve().parents[3]
G = ROOT / ".cache/geo"
EAST = {"001": "Baker", "013": "Crook", "017": "Deschutes", "021": "Gilliam", "023": "Grant", "025": "Harney",
        "027": "Hood River", "031": "Jefferson", "035": "Klamath", "037": "Lake", "045": "Malheur", "049": "Morrow",
        "055": "Sherman", "059": "Umatilla", "061": "Union", "063": "Wallowa", "065": "Wasco", "069": "Wheeler"}
FAR = {"001", "023", "025", "045", "049", "059", "061", "063"}   # Baker Grant Harney Malheur Morrow Umatilla Union Wallowa
WILLAMETTE = {"005": "Clackamas", "009": "Columbia", "039": "Lane", "043": "Linn", "047": "Marion", "051": "Multnomah",
              "053": "Polk", "067": "Washington", "071": "Yamhill", "003": "Benton"}
geod = Geod(ellps="WGS84")

z = zipfile.ZipFile(G / "cb_2023_us_county_5m.zip")
r = shapefile.Reader(shp=io.BytesIO(z.read("cb_2023_us_county_5m.shp")), dbf=io.BytesIO(z.read("cb_2023_us_county_5m.dbf")))
f = [x[0] for x in r.fields[1:]]
land = {}
for sr in r.iterShapeRecords():
    a = dict(zip(f, sr.record))
    if a["STATEFP"] == "41":
        land[a["COUNTYFP"]] = a["ALAND"] / 1e6

rows = list(csv.DictReader(open(G / "census/CenPop2020_Mean_BG41.txt", encoding="utf-8-sig")))
pop = {}
for x in rows:
    pop[x["COUNTYFP"]] = pop.get(x["COUNTYFP"], 0) + int(x["POPULATION"])
SQ = 2.58999
tot, totl = sum(pop.values()), sum(land.values())


def grp(name, cs):
    p, l = sum(pop[c] for c in cs), sum(land[c] for c in cs)
    return p, l, (f"{name}: {p:,} people = {p/tot*100:.1f} % of Oregon; land {l:,.0f} km2 ({l/SQ:,.0f} sq mi) = "
                  f"{l/totl*100:.1f} %; {p/l:.1f}/km2 ({p/l*SQ:.1f}/sq mi)")


out = [f"Oregon 2020: {tot:,} people, {totl:,.0f} km2 land ({totl/SQ:,.0f} sq mi), {tot/totl*SQ:.1f}/sq mi"]
ep, el, s = grp("East of the Cascades (18 counties)", EAST); out.append(s)
out.append(grp("  same without Deschutes (Bend)", set(EAST) - {"017"})[2])
out.append(grp("Far east (8 counties)", FAR)[2])
out.append(grp("Willamette Valley + Portland (10 counties)", WILLAMETTE)[2])
for c in sorted(EAST, key=lambda c: -pop[c]):
    out.append(f"  {EAST[c]:<11} {pop[c]:>8,}  {land[c]:>7,.0f} km2 ({land[c]/SQ:>6,.0f} sq mi)  {pop[c]/land[c]*SQ:6.1f}/sq mi"
               f"  {pop[c]/ep*100:5.1f} % of the east")
# M2: the east's people who live within 25 km of Bend, Redmond, Klamath Falls, Hermiston, Pendleton
towns = {"Bend": (-121.315, 44.058), "Redmond": (-121.174, 44.272), "Klamath Falls": (-121.781, 42.225),
         "Hermiston": (-119.289, 45.840), "Pendleton": (-118.788, 45.672)}
bgs = [x for x in rows if x["COUNTYFP"] in EAST]
near = sum(int(x["POPULATION"]) for x in bgs
           if min(geod.inv(float(x["LONGITUDE"]), float(x["LATITUDE"]), a, b)[2] for a, b in towns.values()) <= 25000)
out.append(f"east's people within 25 km of Bend, Redmond, Klamath Falls, Hermiston or Pendleton: {near:,} = {near/ep*100:.1f} %")
# the empty southeast: Harney + Lake + Malheur
se = {"025", "037", "045"}
out.append(grp("Southeast (Harney + Lake + Malheur)", se)[2])
Path(__file__).with_suffix(".txt").write_text("\n".join(out) + "\n", encoding="utf-8"); print("\n".join(out))
