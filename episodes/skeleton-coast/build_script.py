"""Builds script.json for skeleton-coast.  python build_script.py

Same production logic as episodes/wyoming-empty (hand-placed shots, a photo or map frame at most twice, 60 s apart,
every reason opens on a painted map). The narration lives in drafts/narration.md; every sentence comes from
research.md. Photos and satellite tests: visuals.md. Regions: geo/make_regions.py; measurements: geo/measure_*.py.
"""
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent.parent / "pipeline"))
from schema import Paragraph  # noqa: E402


def near(lon, lat, span):
    return {"lon": lon, "lat": lat, "span": span}


def place(name, lon, lat, label=None, kind="site", icon=None):
    d = {"name": name, "lon": lon, "lat": lat, "kind": kind, "label": label if label is not None else name}
    if icon:
        d["icon"] = icon
    return d


def m(at, *steps, text=None, cut=True):
    s = {"type": "map", "at": at, "map": {"steps": list(steps)}}
    if cut:
        s["map"]["cut"] = True
    if text:
        s["on_screen_text"] = text
    return s


def step(at, **kw):
    return {"at": at, **kw}


_uses: dict = {}


def fresh(view):
    """Wide views come back with new content; frame each use a little differently so no map frame is seen twice."""
    if view["span"] <= 2.5:
        return view
    key = (view["lon"], view["lat"], view["span"])
    k = _uses.get(key, 0)
    _uses[key] = k + 1
    if k == 0:
        return view
    dx, dy = [(0.05, 0.02), (-0.05, -0.02), (0.03, -0.04), (-0.03, 0.04), (0.07, 0.0), (-0.07, 0.0), (0.0, 0.05), (0.0, -0.05)][(k - 1) % 8]
    zoom = [1.08, 1.16, 1.24, 1.12, 1.2, 1.04, 1.28, 1.32][(k - 1) % 8] * (1.03 ** ((k - 1) // 8))  # out only: prefit snaps zoom-ins back
    return {"lon": round(view["lon"] + dx * view["span"], 3), "lat": round(view["lat"] + dy * view["span"], 3), "span": round(view["span"] * zoom, 3)}


def v(view, at=None, **kw):
    d = {"view": fresh(view), **kw}
    if at is not None:
        d["at"] = at
    return d


SAT_MIN_SPAN = 0.08

SU = "2025-05-01/2025-09-30"    # southern winter 2025: scratch sksat.py 2026-11-27


def sat(at, lon, lat, span, label=None, date=SU, **kw):
    return m(at, v(near(lon, lat, max(span, SAT_MIN_SPAN)), date=date, **kw), text=label)


def photo(at, name, text=None):
    d = {"type": "photo", "at": at, "photo": name if name.startswith("File:") else "File:" + name}
    if text:
        d["on_screen_text"] = text
    return d


def stat(at, value, label, source, note=None):
    s = {"value": value, "label": label, "source": source}
    if note:
        s["note"] = note
    return {"type": "stat", "at": at, "stat": s}


def chart(at, title, unit, data, source, reveal=None, highlight=0, kind="bar"):
    c = {"type": kind, "title": title, "unit": unit, "data": data, "source": source, "highlight": highlight}
    if reveal:
        c["reveal"] = reveal
    return {"type": "chart", "at": at, "chart": c}


TEXT = {}
HEADS = []
for line in (HERE / "drafts" / "narration.md").read_text(encoding="utf-8").splitlines():
    if line.startswith("## "):
        mt = re.match(r"## (?:\d+\. )?(.+?) \((\w+)\)", line)
        HEADS.append((mt.group(1), mt.group(2)))
    mp = re.match(r"(P\w+)(?: \([^)]*\))?: (.+)", line)
    if mp:
        TEXT[mp.group(1)] = mp.group(2).strip()


def P(key, *shots, ask=None):
    d = {"text": TEXT[key], "shots": list(shots)}
    if ask:
        d["ask"] = {"at": ask[0], "text": ask[1]}
    return d


# ------------------------------------------------------------------ views (painted views stay above 2.5 degrees)
AFR = {"lon": 18.0, "lat": -14.0, "span": 48.0}       # southern Africa
NAM = {"lon": 17.3, "lat": -22.6, "span": 13.0}       # Namibia
COAST = {"lon": 14.6, "lat": -22.8, "span": 11.0}     # the whole coast
CENT = {"lon": 14.8, "lat": -22.7, "span": 3.0}       # Walvis Bay - Swakopmund - Windhoek road
SOUTHV = {"lon": 15.7, "lat": -27.2, "span": 3.6}     # Lüderitz - Oranjemund
NORTHV = {"lon": 13.0, "lat": -19.2, "span": 5.2}     # the Skeleton Coast Park
ATL = {"lon": 3.0, "lat": 12.0, "span": 75.0}         # Europe to Namibia
GERM = {"lon": 16.0, "lat": -22.5, "span": 15.0}      # German South West Africa

COAST_RED = "file:coast30.geojson@red"
NA_ALT = "file:namibia.geojson@alt"
SKEL_RED = "file:skeleton_np.geojson@red"
SPERR_RED = "file:sperrgebiet.geojson@red"
NNP_ALT = "file:namib_naukluft.geojson@alt"
WB_RED = "file:walvis_enclave.geojson@red"
ES_RED = "file:empty_south.geojson@red"
EN_RED = "file:empty_north.geojson@red"

# ------------------------------------------------------------------ sources (research.md)
NSA = "Namibia Statistics Agency, 2023 census"
OWN_POP = "Own count: Kontur population 2023 (CC BY 4.0) vs the coastline (geo/measure_population.py)"

# ------------------------------------------------------------------ photos (visuals.md; PD / CC0 / CC BY)
PH_BOHLEN = "Eduard Bohlen anagoria.jpg"
PH_ZEILA = "Zeila (Ship).jpg"
PH_WRECK01 = "Skeleton Coast Wreck01.jpg"
PH_SUIDERKUS = "The Suiderkus (1976) Shipwreck (37762745461).jpg"
PH_SKCOAST = "Skeleton Coast (23910020708).jpg"
PH_DUNES = "Dune Formation Namib Skeleton Coast (37504515070).jpg"
PH_GATE = "Springbok Gate.jpg"
PH_SEALS = "Seals on the Skeleton Coast (5832914651).jpg"
PH_CAPECROSS = "Cape Cross Seal Colony confrontation.jpg"
PH_FOG = "Oceanic fog sossusvlei4.jpg"
PH_MODIS = "Namib desert MODIS.jpg"
PH_KUISEB = "Kuiseb Namibia anagoria.JPG"
PH_KUISEB_ISS = "Kuiseb River Nears the Ocean.jpg"
PH_WELW = "Welwitschia mirabilis 002.jpg"
PH_WB1 = "Walvis Bay (37714794876).jpg"
PH_WB2 = "Walvis Bay (37731160902).jpg"
PH_SANDWICH = "Sandwich Harbour, Walvis Bay (37731184332).jpg"
PH_MOLE = "Molo ve městě Swakopmund - Namibie - panoramio.jpg"
PH_MOLE2 = "Molo ve městě Swakopmund - Namibie - panoramio (2).jpg"
PH_JETTY = "Swakopmund Jetty.jpg"
PH_BRANDUNG = "Swakopmund Brandung.jpg"
PH_MISSION = "Mission Church and building - Rheinische Missionsgesellschaft - Swakopmund - 1938.jpg"
PH_RAILMAP = "Trasseführung der Bahnstrecke Swakopmund–Windhoek.jpg"
PH_CONTRACT = "Contract Frederiks-Vogelsang 1883 p1.jpg"
PH_MAP1885 = "Deutsche kolonien 1885 ausschnitt lüderitzland.jpg"
PH_MEDAL = "Lüderitz Territory (formerly Angra Pequena), today Lüderitz, Namibia German Medal 1884, obverse.jpg"
PH_KOL1 = "Abandoned building, Kolmannskuppe, Namibia.jpg"
PH_KOL2 = "01Kolmannskuppe.jpg"
PH_KOL3 = "Ghost Town (37464568170).jpg"
PH_KOL4 = "Ghost Town (37722079791).jpg"
PH_KOL5 = "Ghost Town (23869142088).jpg"
PH_LUD_WIDE = "Lüderitz, Namibia (55528882907).jpg"
PH_LUD_PORT = "Lüderitz - view from port.jpg"
PH_LUD_ART = "Lüderitz - Art Nouveau-style building.jpg"
PH_LUD_GRUN = "Lüderitz - Grunewald House.jpg"
PH_LUD_KELP = "Lüderitz - Kelp on beach.jpg"
PH_PENGUINS = "Penguins at Halifax Island (37051158333).jpg"
PH_VENTURA = "Lockheed PV-1 Ventura in flight, circa in late 1943 (NH 94917).jpg"
PH_ORANGE_ISS = "ISS-62 Orange River, Namibia and South Africa.jpg"
PH_ORANJE_DESERT = "Wild desert between Oranjemond and Rosh Pinah South Namibia (1).jpg"

# ------------------------------------------------------------------ places, routes and arrows
WALVIS = place("Walvis Bay", 14.505, -22.957, "Walvis Bay", "city")
SWAKOP = place("Swakopmund", 14.53, -22.68, "Swakopmund", "city")
LUDERITZ = place("Lüderitz", 15.16, -26.65, "Lüderitz", "city")
ORANJE = place("Oranjemund", 16.43, -28.55, "Oranjemund", "city")
WINDHOEK = place("Windhoek", 17.08, -22.56, "Windhoek", "capital")
CAPECROSS = place("Cape Cross", 13.95, -21.77, "Cape Cross", "site")
KOLMANS = place("Kolmanskop", 15.23, -26.70, "Kolmanskop", "site")
DUNEDIN = place("Dunedin Star", 12.20, -18.62, "Dunedin Star, 1942", "site", icon="conflict")
KUNENE = place("Kunene", 11.80, -17.26, "Kunene mouth", "site")
ROSSING = place("Rossing", 15.04, -22.48, "Rössing mine", "site", icon="factory")
HENTIES = place("Henties Bay", 14.28, -22.12, "Henties Bay", "city")
TORRA = place("Torra Bay", 13.30, -20.33, "Torra Bay", "site")
BERLIN = place("Berlin", 13.40, 52.52, "Berlin", "capital")
LISBON = place("Lisbon", -9.14, 38.72, "Lisbon", "capital")
CAPETOWN = place("Cape Town", 18.42, -33.92, "Cape Town", "city")
LUANDA = place("Luanda", 13.23, -8.84, "Luanda", "capital")
L_ATL = place("Atlantic", 9.0, -24.0, "ATLANTIC OCEAN", "label")

BENGUELA = [{"from": [14.0, -34.0], "to": [11.3, -18.5], "color": "blue", "label": "Benguela current", "bend": -0.08}]
RAIL1902 = [{"from": [14.53, -22.68], "via": [[15.85, -21.93], [16.91, -21.98]], "to": [17.08, -22.56], "mode": "line",
             "label": "Railway, 1902", "color": "accent", "seconds": 2.5}]
TUG = [{"from": [14.505, -22.957], "to": [12.25, -18.65], "color": "blue", "label": "Tug from Walvis Bay", "bend": 0.12}]
CONVOY = [{"from": [17.08, -22.56], "to": [12.25, -18.62], "color": "red", "label": "Police convoy", "bend": -0.12}]
TOBERLIN = [{"from": [13.95, -21.77], "to": [13.40, 52.52], "color": "red", "label": "To Berlin, 1893", "bend": 0.1}]
CAO = [{"from": [-9.14, 38.72], "to": [13.95, -21.77], "color": "blue", "label": "Diogo Cão, 1486", "bend": -0.12}]

chapters = []
heads = iter(HEADS)


def chapter(*paras):
    title, mood = next(heads)
    chapters.append({"title": title, "mood": mood, "paragraphs": list(paras)})


# ================================================================== Hook
chapter(
    P("P0",
      m(0, v(AFR, highlight=[COAST_RED], places=[CAPETOWN, LUANDA])),
      m("run for more than", v(NAM, highlight=[COAST_RED, NA_ALT])),
      photo("That is about as", PH_DUNES, "Where the Namib meets the Atlantic")),
    P("P1",
      sat(0, 14.55, -23.60, 0.6, "The dune sea meets the Atlantic"),
      stat("We counted where Namibians", "7 %", "Of Namibians live within 50 km of the sea", OWN_POP)),
    P("P2",
      m(0, v(COAST, highlight=[COAST_RED], places=[WALVIS, LUDERITZ])),
      photo("Namibia's Skeleton Coast?", PH_BOHLEN, "The Eduard Bohlen, wrecked 1909")),
    P("P3",
      sat(0, 14.50, -22.95, 0.25, "Walvis Bay"),
      photo("a rescue that wrecked", PH_ZEILA, "A wreck on the Skeleton Coast"),
      photo("and a diamond town", PH_KOL1, "Kolmanskop")),
    P("P4",
      m(0, v(COAST, arrows=BENGUELA))),
)

# ================================================================== 1. A Sea That Will Not Rain
chapter(
    P("P5",
      m(0, v(AFR, highlight=[COAST_RED], arrows=BENGUELA, places=[L_ATL])),
      photo("and cold water does", PH_BRANDUNG, "Cold surf at Swakopmund")),
    P("P6",
      m(0, v(COAST, arrows=BENGUELA)),
      photo("The air above it", PH_FOG, "Fog rolling over the Namib"),
      photo("and the clouds that", PH_MODIS, "The Namib from orbit")),
    P("P7",
      chart(0, "Rain in a year", "mm", [["Walvis Bay", 13], ["Windhoek", 360]], "Climate normals (Wikipedia / NMS)", highlight=0),
      photo("Windhoek, the capital, up", PH_WB1, "Walvis Bay")),
    P("P8",
      photo(0, PH_FOG, "Fog over the dunes"),
      photo("and the beetles and", PH_WELW, "Welwitschia, which lives on fog")),
    P("P9",
      sat(0, 14.55, -23.60, 0.6, "The Namib sand sea"),
      photo("In many places they", PH_SANDWICH, "Sandwich Harbour: dunes into the sea")),
    P("P9b",
      m(0, v(CENT, highlight=[NNP_ALT], places=[WALVIS])),
      sat("Its northern edge is", 14.70, -23.30, 0.4, "The Kuiseb: dunes stop at the riverbed"),
      photo("and the dunes stop", PH_KUISEB, "The Kuiseb")),
    P("P10",
      photo(0, PH_KUISEB_ISS, "The Kuiseb nearing the sea, from the ISS"),
      sat("and some years not", 11.80, -17.27, 0.2, "The Kunene, the only river that always flows")),
    P("P11",
      m(0, v(COAST, highlight=[COAST_RED])),
      photo("And the first Europeans", PH_SKCOAST, "The Skeleton Coast")),
)

# ================================================================== 2. No Harbour, No Water
chapter(
    P("P12",
      m(0, v(COAST, places=[CAPECROSS, WALVIS])),
      photo("and this coast had", PH_BRANDUNG, "Surf on the Namibian coast")),
    P("P13",
      m(0, v(ATL, places=[LISBON], arrows=CAO)),
      sat("landed at a headland", 13.95, -21.77, 0.08, "Cape Cross"),
      stat("and set up a", "1486", "Diogo Cão's stone cross at Cape Cross", "German Foreign Office; DHM")),
    P("P13b",
      photo(0, PH_CAPECROSS, "Cape fur seals at Cape Cross"),
      stat("In the breeding season", "210,000", "Seals at Cape Cross in the breeding season", "Namibia Ministry of Environment"),
      photo("the largest colony of", PH_SEALS, "Seals on the Skeleton Coast")),
    P("P14",
      m(0, v(ATL, places=[BERLIN], arrows=TOBERLIN)),
      stat("Namibia asked for it", "2019", "The cross is shipped back to Namibia", "Deutsches Historisches Museum; Bundestag")),
    P("P14b",
      photo(0, PH_SKCOAST, "The empty shore")),
    P("P15",
      sat(0, 14.43, -22.88, 0.12, "Pelican Point, the sandspit that shelters Walvis Bay"),
      photo("Walvis Bay, a deep", PH_WB2, "Walvis Bay")),
    P("P16",
      m(0, v(CENT, highlight=[WB_RED], places=[WALVIS])),
      stat("and in 1884 made", "1878", "Britain claims Walvis Bay; Cape Colony from 1884", "Britannica"),
      m("That same year, Germany", v(GERM, highlight=[NA_ALT, WB_RED]))),
    P("P16b",
      photo(0, PH_LUD_WIDE, "Lüderitz, the old Angra Pequena"),
      photo("In May 1883 he", PH_CONTRACT, "The first contract, 1883"),
      stat("for a hundred pounds", "£100 + 200 RIFLES", "Price of Angra Pequena, May 1883", "Wikipedia; Britannica")),
    P("P16c",
      photo(0, PH_MAP1885, "Lüderitzland on an 1885 map"),
      m("The contract meant German", v(SOUTHV, places=[LUDERITZ, ORANJE]))),
    P("P16d",
      photo(0, PH_ORANGE_ISS, "The Orange River from the ISS"),
      sat("The cove was renamed", 15.15, -26.65, 0.15, "Lüderitz")),
    P("P17",
      m(0, v(CENT, highlight=[WB_RED], places=[SWAKOP, WALVIS])),
      photo("but the only good", PH_WB1, "Walvis Bay")),
    P("P18",
      sat(0, 14.53, -22.68, 0.12, "Swakopmund"),
      photo("In 1903 they opened", PH_MOLE, "The Mole at Swakopmund today")),
    P("P19",
      photo(0, PH_MOLE2, "The Mole, long since filled with sand"),
      photo("and later onto a", PH_JETTY, "The Swakopmund jetty")),
    P("P19b",
      m(0, v(CENT, places=[SWAKOP, WINDHOEK], routes=RAIL1902)),
      photo("The line to Windhoek,", PH_RAILMAP, "The 1902 line, route map"),
      stat("opened in June 1902.", "382 KM", "Swakopmund-Windhoek railway, opened June 1902", "Wikipedia")),
    P("P19c",
      photo(0, PH_MISSION, "Swakopmund, 1938"),
      photo("and today it is", PH_BRANDUNG, "Swakopmund's sea front")),
    P("P20",
      m(0, v(CENT, highlight=[WB_RED], places=[WALVIS])),
      stat("When the British Cape", "1910", "Walvis Bay passes to the Union of South Africa", "Britannica")),
    P("P21",
      m(0, v(NAM, highlight=[NA_ALT, WB_RED])),
      stat("Its only deep-water port", "1 MAR 1994", "Walvis Bay handed over to Namibia", "Treaty on Walvis Bay")),
    P("P22",
      sat(0, 14.48, -22.95, 0.06, "The port of Walvis Bay"),
      m("And the rest of", v(NORTHV, highlight=[SKEL_RED]))),
)

# ================================================================== 3. The Coast of Wrecks
chapter(
    P("P23",
      m(0, v(NORTHV, highlight=[SKEL_RED], places=[DUNEDIN])),
      photo("The coast is dangerous", PH_WRECK01, "A wreck on the Skeleton Coast")),
    P("P24",
      photo(0, PH_BOHLEN, "The Eduard Bohlen, now inland in the dunes"),
      photo("Over the centuries hundreds", PH_ZEILA, "The Zeila"),
      photo("Their rusting hulls, with", PH_SUIDERKUS, "The Suiderkus, wrecked 1976")),
    P("P25",
      stat(0, "29 NOV 1942", "The Dunedin Star strikes a shoal", "Wikipedia; Marsh, Skeleton Coast")),
    P("P26",
      m(0, v(NORTHV, places=[DUNEDIN, KUNENE])),
      sat("Her captain ran her", 12.20, -18.60, 0.15, "The coast where the Dunedin Star was beached")),
    P("P27",
      photo(0, PH_SKCOAST, "The Skeleton Coast"),
      sat("The beach was dry,", 12.60, -19.20, 0.6, "Hundreds of kilometres from any town")),
    P("P28",
      m(0, v(COAST, places=[WALVIS, DUNEDIN], arrows=TUG)),
      stat("It too ran aground", "2 DEAD", "Crew of the tug Sir Charles Elliott who drowned", "Wikipedia")),
    P("P29",
      photo(0, PH_VENTURA, "A Lockheed Ventura, the type sent"),
      photo("It landed on the", PH_DUNES, "Soft sand on the Skeleton Coast")),
    P("P29b",
      stat(0, "4 AIRMEN", "The Ventura's crew, now stranded too", "SAAF Museum")),
    P("P30",
      m(0, v(NAM, places=[WINDHOEK, DUNEDIN], arrows=CONVOY)),
      stat("They reached Windhoek on", "24 DEC 1942", "Survivors and airmen reach Windhoek", "Wikipedia")),
    P("P31",
      photo(0, PH_WRECK01, "A wreck on the Skeleton Coast"),
      sat("That is the coast", 12.45, -19.00, 0.3, "The northern Skeleton Coast")),
    P("P31b",
      m(0, v(NORTHV, highlight=[SKEL_RED])),
      stat("proclaimed in 1971.", "1971", "Skeleton Coast Park proclaimed", "Namibia Ministry of Environment"),
      photo("Its southern half can", PH_GATE, "Springbok Gate, Skeleton Coast Park")),
    P("P31c",
      sat(0, 13.30, -20.33, 0.1, "Torra Bay")),
    P("P32",
      m(0, v(COAST, highlight=[SPERR_RED]))),
)

# ================================================================== 4. Diamonds Closed the Door
chapter(
    P("P32b",
      photo(0, PH_LUD_PORT, "Lüderitz bay"),
      sat("held prisoners on Shark", 15.15, -26.64, 0.06, "Shark Island, Lüderitz"),
      stat("Between September 1906 and", "1,032 OF 1,795", "Prisoners who died on Shark Island, Sep 1906 - Mar 1907", "Cited by NYRB; New Era")),
    P("P32c",
      stat(0, "2021", "Germany: genocide 'from today's perspective'", "German Federal Government"),
      photo("The talks about what", PH_LUD_KELP, "The shore at Lüderitz")),
    P("P33",
      m(0, v(SOUTHV, highlight=[SPERR_RED], places=[LUDERITZ, ORANJE])),
      photo("the most valuable land", PH_ORANJE_DESERT, "The desert of the Sperrgebiet")),
    P("P34",
      photo(0, PH_LUD_ART, "Lüderitz"),
      stat("near Lüderitz when he", "APRIL 1908", "Zacharias Lewala finds a diamond", "Wikipedia")),
    P("P35",
      m(0, v(SOUTHV, highlight=[SPERR_RED])),
      stat("about twenty-six thousand square", "~26,000 km²", "The Sperrgebiet, the forbidden area, 1908", "Wikipedia")),
    P("P36",
      photo(0, PH_KOL1, "Kolmanskop"),
      photo("At Kolmanskop there was", PH_KOL2, "Kolmanskop's houses"),
      photo("The hospital is said", PH_KOL3, "Inside Kolmanskop")),
    P("P37",
      photo(0, PH_KOL4, "Sand in the rooms"),
      stat("By 1956 Kolmanskop was", "1956", "Kolmanskop abandoned", "Wikipedia"),
      photo("which now fills its", PH_KOL5, "Kolmanskop today")),
    P("P38",
      sat(0, 16.48, -28.63, 0.15, "The Orange River mouth and Oranjemund"),
      photo("For decades nobody could", PH_ORANJE_DESERT, "Desert near Oranjemund")),
    P("P39",
      stat(0, "21 OCT 2017", "Oranjemund opens to the public", "Wikipedia; The Namibian")),
    P("P40",
      m(0, v(SOUTHV, highlight=[SPERR_RED], places=[ORANJE])),
      photo("Most of the old", PH_ORANGE_ISS, "The Orange River")),
    P("P41",
      sat(0, 16.48, -28.63, 0.3, "The mining coast at Oranjemund"),
      stat("It held more than", "2,000+ COINS", "Gold and silver coins of the Bom Jesus (lost 1533)", "Wikipedia")),
    P("P41b",
      stat(0, "17 TONNES", "Copper ingots from the Bom Jesus", "Wikipedia")),
    P("P42",
      m(0, v(COAST, places=[WALVIS, SWAKOP])),
      photo("So where do the", PH_WB2, "Walvis Bay")),
)

# ================================================================== 5. Where the People Are
chapter(
    P("P43",
      m(0, v(CENT, places=[WALVIS, SWAKOP, ROSSING])),
      sat("and those towns run", 14.53, -22.68, 0.12, "Swakopmund")),
    P("P43b",
      m(0, v(NAM, highlight=[NA_ALT])),
      m("and measured each small", v(NAM, highlight=[COAST_RED]))),
    P("P43c",
      chart(0, "Namibians living near the sea", "%", [["Within 5 km", 7.0], ["Within 50 km", 7.3], ["Within 100 km", 7.6]], OWN_POP, highlight=1),
      sat("Beyond the towns, almost", 14.90, -25.00, 0.6, "The empty coast south of Walvis Bay")),
    P("P44",
      m(0, v(COAST, highlight=[ES_RED])),
      stat("almost five hundred kilometres", "481 KM", "Of coast without a settled square", OWN_POP)),
    P("P45",
      m(0, v(COAST, highlight=[EN_RED], places=[KUNENE])),
      stat("the same is true", "347 KM", "Of empty coast up to the Kunene", OWN_POP)),
    P("P46",
      chart(0, "People, 2023 census", "", [["Walvis Bay", 102704], ["Swakopmund", 75921]], NSA, highlight=0),
      photo("Together they hold most", PH_WB1, "Walvis Bay")),
    P("P47",
      stat(0, "+59 %", "Growth of the Erongo region, 2011-2023", NSA)),
    P("P48",
      sat(0, 14.48, -22.95, 0.1, "Walvis Bay port"),
      photo("for fishing boats, ships", PH_WB2, "Walvis Bay")),
    P("P48b",
      sat(0, 14.485, -22.945, 0.06, "The 2019 container terminal on reclaimed land"),
      stat("It more than doubled", "750,000 TEU", "Container capacity a year after 2019", "Namport")),
    P("P48c",
      photo(0, PH_LUD_PORT, "Fishing harbour at Lüderitz"),
      stat("Fishing gives about sixteen", "~16,000", "Direct jobs in fishing", "New Era 2026; MSC")),
    P("P49",
      m(0, v(CENT, places=[ROSSING, SWAKOP])),
      sat("Rössing has been digging", 15.04, -22.48, 0.12, "The Rössing open pit"),
      stat("and in 2024 Namibia", "~12 %", "Namibia's share of world uranium, 2024", "World Nuclear Association")),
    P("P49b",
      sat(0, 14.70, -23.30, 0.25, "The Kuiseb, where Walvis Bay's water comes from"),
      stat("and the town has", "NO BACKUP", "Walvis Bay's only water source: the Kuiseb aquifer", "UN-Habitat; New Era")),
    P("P50",
      m(0, v(CENT, places=[SWAKOP, HENTIES])),
      stat("So in 2010 a", "2010", "First large seawater desalination plant in sub-Saharan Africa", "Orano; Wikipedia"),
      sat("It was the first", 14.29, -22.11, 0.1, "Henties Bay, north of the plant")),
    P("P51",
      stat(0, "17.6 MILLION m³", "Water from the Erongo desalination plant, 2025", "New Era")),
    P("P51b",
      sat(0, 15.03, -22.63, 0.15, "The Husab uranium mine"),
      stat("Walvis Bay counts a", "35,000 HOMES", "Housing backlog in Walvis Bay", "New Era 2025")),
    P("P52",
      m(0, v(CENT, places=[WALVIS, SWAKOP, ROSSING])),
      photo("But only where a", PH_JETTY, "Swakopmund")),
)

# ================================================================== 6. The Next Bet
chapter(
    P("P53",
      m(0, v(SOUTHV, highlight=[SPERR_RED], places=[LUDERITZ])),
      photo("and now someone wants", PH_LUD_WIDE, "Lüderitz")),
    P("P54",
      sat(0, 15.30, -26.75, 0.5, "The park around Lüderitz"),
      stat("and would cost around", "~$10 BILLION", "Hyphen's green hydrogen project", "Engineering News 2026")),
    P("P55",
      stat(0, "24 %", "Namibian state stake in the project", "Engineering News 2023"),
      photo("The decision on whether", PH_LUD_GRUN, "Lüderitz")),
    P("P56",
      photo(0, PH_LUD_ART, "Lüderitz"),
      photo("Conservationists warn about penguins", PH_PENGUINS, "African penguins at Halifax Island, off Lüderitz")),
    P("P56b",
      m(0, v(SOUTHV, places=[LUDERITZ, ORANJE])),
      stat("In 2022 Shell and", "2022", "Oil found offshore in the Orange Basin", "S&P Global"),
      sat("and a gas pipeline", 15.15, -26.65, 0.25, "Lüderitz")),
    P("P56c",
      photo(0, PH_KOL3, "Kolmanskop")),
    P("P56d",
      m(0, v(NORTHV, highlight=[SKEL_RED])),
      sat("taking seals, flamingos and", 12.70, -19.45, 0.15, "The Hoanib mouth, where the lions hunt"),
      photo("They are the only", PH_SEALS, "Seals, the lions' prey")),
    P("P56e",
      stat(0, "~100-110", "Desert lions in northwest Namibia", "Namibia Ministry of Environment, 2025")),
    P("P57",
      sat(0, 14.55, -23.60, 0.4, "The dune sea"),
      photo("Is it worth bringing", PH_DUNES, "The Namib")),
)

# ================================================================== Ending
chapter(
    P("P58",
      m(0, v(NAM, highlight=[COAST_RED]))),
    P("P59",
      photo(0, PH_FOG, "Fog"),
      photo("The one good harbour", PH_WB1, "Walvis Bay"),
      photo("Ships, tugs and even", PH_BOHLEN, "The Eduard Bohlen"),
      photo("Diamonds closed the south", PH_KOL1, "Kolmanskop"),
      sat("And the towns that", 15.04, -22.48, 0.2, "Rössing")),
    P("P60",
      m(0, v(COAST, highlight=[ES_RED, EN_RED], places=[WALVIS, SWAKOP]))),
    P("P60b",
      photo(0, PH_KOL5, "Kolmanskop"),
      sat("Where those were missing,", 12.60, -19.20, 0.5, "The empty Skeleton Coast")),
    P("P61",
      photo(0, PH_SKCOAST, "The Skeleton Coast"),
      m("or keep it the", v(COAST, highlight=[COAST_RED])),
      ask=("Should Namibia open its", "Open the empty coast to industry, or keep it as the desert made it?")),
)

def push_span(span):
    if span > 2.5:
        return max(2.55, round(span * 0.85, 3))
    if span > 2.0:
        return max(2.05, round(span * 0.75, 3))
    return max(0.08, round(span * 0.62, 3))


def word_at(text, at):
    if isinstance(at, int):
        return at
    ws, ph = text.split(), at.split()
    for i in range(len(ws)):
        if [w.strip(".,;:!?\"'()").lower() for w in ws[i:i + len(ph)]] == [w.strip(".,;:!?\"'()").lower() for w in ph]:
            return i
    raise ValueError(at)


BEAT_WORDS = 14
for ch in chapters:
    for para in ch["paragraphs"]:
        anchors = Paragraph.model_validate(para).anchor_indices()
        n = len(para["text"].split())
        for i, (sh, start) in enumerate(zip(para["shots"], anchors)):
            end = anchors[i + 1] if i + 1 < len(anchors) else n
            steps = (sh.get("map") or {}).get("steps", [])
            if sh["type"] != "map" or not steps or any(st.get("compare") for st in steps) or "view" not in steps[0]:
                continue
            if any(st.get(k) for st in steps for k in ("highlight", "routes", "arrows")):
                continue
            marks = [start] + [word_at(para["text"], st["at"]) for st in steps[1:] if st.get("at") is not None] + [end]
            last = steps[-1].get("view") or steps[0]["view"]
            for a, b in list(zip(marks, marks[1:])):
                k = (b - a) // (BEAT_WORDS + 1)
                if k == 0:
                    continue
                vw = dict(last)
                for j in range(1, k + 1):
                    vw = {"lon": vw["lon"], "lat": vw["lat"], "span": push_span(vw["span"]) if j % 2 or vw["span"] > 2.5 else round(vw["span"] * 1.6, 3)}
                    move = {"at": a + (b - a) * j // (k + 1), "view": vw}
                    for key in ("date", "layer"):
                        if steps[0].get(key):
                            move[key] = steps[0][key]
                    steps.append(move)
            steps[1:] = sorted(steps[1:], key=lambda st: word_at(para["text"], st["at"]) if st.get("at") is not None else 0)


def prefit_views():
    """Write the camera the pipeline would choose into the script (see scottish-highlands/build_script.py)."""
    import math
    import geo
    from maps import _arrow_hull, _inside_safe, _bounds_of, _span_for, fit, resolve_area, union_box, unit_pt, view_box

    def items_of(st):
        out = [("pt", (*unit_pt(pl["lon"], pl["lat"]), "site")) for pl in st.get("places", [])]
        for a in st.get("arrows", []):
            out.append(("line", _arrow_hull(unit_pt(*a["from"]), unit_pt(*a["to"]), a.get("bend", 0.2))))
        for r in st.get("routes", []):
            out.append(("line", [unit_pt(*q) for q in [r["from"], *r.get("via", []), r["to"]]]))
        for h in st.get("highlight", []):
            area = resolve_area(h.split("@")[0], HERE)
            if area:
                out.append(("geom", area[2]))
        return out

    def to_view(t):
        lat = math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * t["y"]))))
        span = t["w"] * 360
        lon = t["x"] * 360 - 180
        return {"lon": round(lon, 3), "lat": round(lat, 3), "span": round(span, 3)}

    n = 0
    for ch in chapters:
        for para in ch["paragraphs"]:
            for sh in para["shots"]:
                if sh["type"] != "map":
                    continue
                cur = None
                for st in sh["map"]["steps"]:
                    if st.get("compare"):
                        cur = None
                        continue
                    if st.get("view"):
                        cur = {"x": float(geo.mx(st["view"]["lon"])), "y": float(geo.my(st["view"]["lat"])), "w": st["view"]["span"] / 360.0}
                    items = items_of(st)
                    if cur is None or not items or _inside_safe(_bounds_of(items), cur, True, slack=0.0):
                        continue
                    span0 = cur["w"] * 360
                    cur = fit(union_box([_bounds_of(items), view_box(cur, 0.4)]), True, min(_span_for(items), span0))
                    st["view"] = to_view(cur)
                    n += 1
    print(f"prefit: {n} views widened to fit their content")


prefit_views()


TITLE = "Why Almost Nobody Lives on Namibia's Skeleton Coast"
script = {
    "title": TITLE,
    "voice": "am_michael",
    "voice_speed": 1.15,
    "music": "procedural",
    "map_style": "satellite",
    "look": "none",
    "photo_upscale": True,
    "sources": ["episodes/skeleton-coast/research.md and factcheck.md", "Contains modified Copernicus Sentinel data 2025",
                "Population near the sea and empty stretches: own count from Kontur Population 2023 (CC BY 4.0) (geo/measure_population.py)",
                "Parks: (c) OpenStreetMap contributors (ODbL); coast and borders: Natural Earth (geo/make_regions.py)",
                "Walvis Bay enclave drawn as an approximate area; current, railway, tug and convoy lines drawn through main points (approximate)"],
    "thumbnail": {"text": "EMPTY COAST"},
    "chapters": chapters,
    "youtube": {
        "title": TITLE,
        "title_candidates": [TITLE, "Why They Call It the Skeleton Coast", "Why Namibia's Coast Is Almost Empty"],
        "description": "Namibia's Atlantic coast runs for more than 1,300 km, yet only about one Namibian in fourteen lives within 50 km of the sea. We follow why: the cold Benguela sea that brings fog instead of rain, the one good harbour at Walvis Bay that stayed British and South African until 1994, Swakopmund's harbour that filled with sand, the Dunedin Star rescue of 1942 that cost a tug and a bomber, the diamond Sperrgebiet and the ghost town of Kolmanskop, Oranjemund closed until 2017, the uranium mines and the seawater plant that keep the coast towns alive, and the green hydrogen and oil bets on the empty south.",
        "tags": ["Skeleton Coast", "Namibia", "Walvis Bay", "Swakopmund", "Lüderitz", "Kolmanskop", "Namib Desert",
                 "Benguela Current", "Dunedin Star", "Sperrgebiet", "Oranjemund", "Cape Cross", "geography", "satellite images"],
        "pinned_comment": "Should Namibia open its empty coast to new industry, or keep it the way the desert made it?",
    },
}
out = HERE / "script.json"
out.write_text(json.dumps(script, ensure_ascii=False, indent=1) + chr(10), encoding="utf-8")
words = sum(len(p["text"].split()) for c in chapters for p in c["paragraphs"])
shots = [s for c in chapters for p in c["paragraphs"] for s in p["shots"]]
kinds = {k: sum(1 for s in shots if s["type"] == k) for k in ("map", "photo", "stat", "document", "chart")}
print(f"{words} words, {len(chapters)} chapters, {len(shots)} shots {kinds}")
