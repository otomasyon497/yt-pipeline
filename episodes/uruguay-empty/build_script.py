"""Builds script.json for uruguay-empty.  python build_script.py

Same production logic as episodes/scottish-highlands (hand-placed shots, a photo or map frame at most twice, 60 s
apart, every reason opens on a painted map). The narration lives in drafts/narration.md; every sentence comes from
research.md. Photos and satellite tests: visuals.md. Regions: geo/make_regions.py. Glass-negative scans from the
Centro de Fotografía de Montevideo carry "#crop=" (pipeline/commons.py) to cut their black frames.
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
SU = "2024-12-15/2025-02-28"    # southern summer 2024-25: scratch uysat.py 2026-11-26, clear on every view tested
W23 = "2023-06-01/2023-07-31"   # winter 2023, the drought: Paso Severino 2023-07-14


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
URU = {"lon": -55.8, "lat": -32.8, "span": 17.0}        # the whole country
REGION = {"lon": -55.5, "lat": -31.5, "span": 16.0}    # Uruguay, Rio Grande do Sul, Buenos Aires
PLATA = {"lon": -57.4, "lat": -34.4, "span": 4.6}      # the River Plate: Buenos Aires, Colonia, Montevideo
SAM = {"lon": -58.0, "lat": -27.0, "span": 38.0}       # southern South America
ATL = {"lon": -30.0, "lat": 8.0, "span": 120.0}        # Europe to the River Plate
SCOAST = {"lon": -56.0, "lat": -34.3, "span": 3.4}     # the southern coast around Montevideo
RS_V = {"lon": -53.7, "lat": -30.9, "span": 22.5}       # Rio Grande do Sul with northern Uruguay
NORTH = {"lon": -56.0, "lat": -31.4, "span": 4.2}      # northern Uruguay, the Brazilian border
CENTRE = {"lon": -56.4, "lat": -33.0, "span": 4.0}     # the middle of the country
WEST = {"lon": -57.9, "lat": -33.0, "span": 3.6}       # the Uruguay River towns
WORLD = {"lon": -30.0, "lat": 10.0, "span": 160.0}     # where the emigrants went

UY_RED, UY_ALT = "Uruguay@red", "Uruguay@alt"
BR_ALT, AR_ALT = "Brazil@alt", "Argentina@alt"
RS_RED, RS_ALT = "Rio Grande do Sul@red", "Rio Grande do Sul@alt"
COAST_RED, INT_ALT, INT_RED = "file:coast6.geojson@red", "file:interior.geojson@alt", "file:interior.geojson@red"
MVD30 = "file:mvd30.geojson@red"
ENG = "file:england.geojson@alt"
SUD_RED, NOR_BLUE = "file:rs_sudoeste.geojson@red", "file:rs_nordeste.geojson@blue"

# ------------------------------------------------------------------ sources (research.md)
OWN_POP = "Own count: Kontur Population 2023 (geo/measure_population.py)"
OWN_AREA = "Own measurement: Natural Earth polygons"
INE = "INE Uruguay, census 2023"
DICOSE = "MGAP DICOSE declaration 2025 (via Montevideo Portal)"
IBGE = "IBGE, census 2022"

# ------------------------------------------------------------------ photos (visuals.md; crops checked: scratch uyphotos sheet)
G = "#crop=0.07,0.07,0.06,0.16"   # Centro de Fotografía glass negatives: black frame and grey strip
PH_TACUA = "Countryside of Tacuarembó Department.jpg"
PH_TACUA_RIO = "Río Tacuarembó, Departamento de Tacuarembó.jpg"
PH_RUTA30 = "Ruta 30, cerca de Tranqueras.JPG"
PH_RN_LAND = "Paisaje del departamento de Río Negro.jpg"
PH_RN_RIVER = "Río Negro, Uruguay.jpg"
PH_EUCA_ROW = "Countryside in Montevideo, Uruguay.jpg"
PH_FIELD = "Field (2884212928).jpg"
PH_OVINOS = "Ovinos.jpg"
PH_WIND1 = "Windmills in northern Uruguay 1.jpg"
PH_WIND2 = "Windmills in northern Uruguay 2.jpg"
PH_CARACOLES = "Sierra de los Caracoles wind farm.JPG"
PH_BONETE = "Represa Rincón del Bonete 2026.jpg"
PH_ISS = "ISS022-E-78437 - View of Uruguay.jpg"
PH_HERD_1918 = "A herd of cattle in Uruguay LCCN2016819438.jpg#crop=0.2,0.22,0.2,0.2"
PH_TABLADA1 = "La Tablada - 23407FMHGE.tif" + G
PH_TABLADA2 = "La Tablada - 23410FMHGE.tif" + G
PH_TABLADA3 = "La Tablada - 23412FMHGE.tif" + G
PH_TABLADA4 = "La Tablada - 20425FMHGE.tif" + G
PH_BRANDING = "C34f334. Marcando un caballo.jpg"
PH_SHEARING = "C34f335. Esquila.jpg"
PH_SHEEP_PEN = "C34f337. Corral con ovejas.jpg"
PH_GAUCHO_1868 = "Gaucho 1868c.jpg"
PH_LAROCHE = "Ernesto Laroche - Paisaje de campo con tajamar.jpg"
PH_ESCENA = "Escena campestre.jpg"
PH_PG17 = "El Embajador de los Estados Unidos, Lou Rinaldi, participó en Tacuarembó del desfile de la 39a Fiesta de la Patria Gaucha en 14 Marzo 2026 - 17.jpg"
PH_PG23 = "El Embajador de los Estados Unidos, Lou Rinaldi, participó en Tacuarembó del desfile de la 39a Fiesta de la Patria Gaucha en 14 Marzo 2026 - 23.jpg"
PH_PG33 = "El Embajador de los Estados Unidos, Lou Rinaldi, participó en Tacuarembó del desfile de la 39a Fiesta de la Patria Gaucha en 14 Marzo 2026 - 33.jpg"
PH_PG34 = "El Embajador de los Estados Unidos, Lou Rinaldi, participó en Tacuarembó del desfile de la 39a Fiesta de la Patria Gaucha en 14 Marzo 2026 - 34.jpg"
PH_PG42 = "El Embajador de los Estados Unidos, Lou Rinaldi, participó en Tacuarembó del desfile de la 39a Fiesta de la Patria Gaucha en 14 Marzo 2026 - 42.jpg"
PH_PG60 = "El Embajador de los Estados Unidos, Lou Rinaldi, participó en Tacuarembó del desfile de la 39a Fiesta de la Patria Gaucha en 14 Marzo 2026 - 60.jpg"
PH_SALADERO = "Faenas de saladero.tif#crop=0.07,0.07,0.07,0.3"   # book page: caption cut
PH_LIEBIG_1907 = "Saladero Liebig's - Fray Bentos - Río Negro.tif#crop=0.07,0.07,0.07,0.3"
PH_LIEBIG_PAN = "Vista panorámica - Saladero Liebig's - Río Negro.tif#crop=0.07,0.07,0.07,0.3"
PH_LIEBIG_1919 = "Frigorífico Liebig - 01792FMHGE.tif" + G
PH_LIEBIG_POSTER = "Liebig Poster french 1890.jpg"
PH_ANGLO = "El Frigorífico ANGLO en acción.jpg"
PH_ANGLO_PLANT = "Fray Bentos industrial plant.jpg"
PH_ANGLO_OLD = "2007 08 Uruguay - Fray Bentos - Anglo Factory - Old Area.JPG"
PH_ANGLO_PIER = "Muelle - Barrio Anglo 1.jpg"
PH_CASA_GRANDE = "Casa Grande, Fray Bentos.jpg"
PH_SWIFT_1918 = "Frigorífico Swift - 01890FMHGE.tif" + G
PH_SWIFT_1949 = "Frigorífico Swift - 08190FMHGE.tif" + G
PH_SWIFT_1958 = "Frigorífico Swift - 09587FMHGE.tif" + G
PH_CERRO_1865 = "Cerro de Montevideo desde la ciudad. Año 1865.jpg"
PH_PANTANOSO = "Arroyo Pantanoso - 04317FMHGE.tif" + G
PH_PORT_1931 = "Vista aérea del puerto de Montevideo y la Ciudad Vieja - 0102FMHE.tif" + G
PH_PORT_1931B = "Vista aérea del puerto y la Ciudad Vieja - 0103FMHE.tif" + G
PH_PORT_AIR = "Vista aérea del Puerto y la Ciudad Vieja - 0017FMHE.tif" + G
PH_OLDTOWN_1936 = "Vista aérea de la Ciudad Vieja - 0311FMHE.tif" + G
PH_OLDTOWN_AIR = "Vista aérea de la Ciudad Vieja - 0310FMHE.tif" + G
PH_BAY_AIR = "Vista aérea de la bahía de Montevideo - 0016FMHE.tif" + G
PH_PORT_1919 = "Ciudad Vieja y puerto de Montevideo - 02493FMHGE.tif" + G
PH_POCITOS_1919 = "Rambla de Pocitos - 01778FMHGE.tif" + G
PH_WILSON_1922 = "Rambla Wilson - 03340FMHGE.tif" + G
PH_PERU_1944 = "Rambla República del Perú - 07994FMHGE.tif" + G
PH_STATION_1900 = "Estación Central de Ferrocarriles - 03428FMHGE.tif" + G
PH_STATION_1917 = "Estación Central de Ferrocarriles Gral - 01210FMHGE.tif" + G
PH_SALTO_STATION = "Salto Uruguay train station 1.jpg"
PH_SALTO_1919 = "Ciudad de Salto - 01794FMHGE.tif" + G
PH_IMM_HOTEL = "Hotel de Inmigrantes - 0522FMHB.tif" + G
PH_LAZARETO = "Instalaciones del lazareto de inmigrantes - 02627FMHGE.tif" + G
PH_FLORES_PIER = "Isla de Flores - 02626FMHGE.tif" + G
PH_IMM_PIER_1904 = "C25f241. Muelle de entrada para control de inmigrantes.jpg"
PH_BA_HOTEL = "Hotel de Inmigrantes Argentina 1912.jpg"
PH_BA_SHIP = "L'Atlantique des Messageries Maritimes à Buenos Aires c. 1910.jpg"
PH_BA_CROWD = "The immigration offices and statistics from 1857 to 1903 - information for the Universal Exhibition of St. Louis (U.S.A.) (1904) (14780946871).jpg"
PH_BA_1931 = "Inmigrantes en la zona puerto ba 1931.jpg"
PH_MVD_AIR1 = "GRU - MVD flight (2026-06-21) (13644).jpg"
PH_MVD_AIR2 = "GRU - MVD flight (2026-06-21) (33670).jpg"
PH_MVD_AIR3 = "GRU - MVD flight (2026-06-21) (34806).jpg"
PH_MVD_AIR4 = "GRU - MVD flight (2026-06-21) (54649).jpg"
PH_MVD_AIR5 = "GRU - MVD flight (2026-06-21) (86584).jpg"
PH_MVD_AIR6 = "GRU - MVD flight (2026-06-21) (99393).jpg"
PH_MVD_WALK = "Montevideo walking MRD 07.jpg"
PH_RAMBLA = "Rambla - Montevideo (4278689373).jpg"
PH_RAMBLA_FR = "Rambla Francia MRD 01.jpg"
PH_OLDTOWN_NOW = "Montevideo old town from air.JPG"
PH_PUNTA_CARRETAS = "Punta Carretas from air.JPG"
PH_PLAZA = "Plaza Independencia, Montevideo.jpg"
PH_PLAZA2 = "PlazaIndependencia2.jpg"
PH_PORT_NOW = "Puerto de Montevideo, Uruguay.jpg"
PH_SKYLINE = "Montevideo skyline (282952662).jpg"
PH_OSE = "Edificio OSE Montevideo.JPG"
PH_COLONIA = "Colonia Del Sacramento, Uruguay (Unsplash).jpg"
PH_COLONIA2 = "Colonia del sacramento.JPG"
PH_COLONIA_DUSK = "Anochecer en Colonia del Sacramento.jpg"
PH_BLANES_33 = "Juan Manuel Blanes - El Juramento de los Treinta y Tres Orientales.jpg"
PH_ARTIGAS = "Juan Manuel Blanes - Artigas en la Ciudadela.jpg"
PH_ARTIGAS_PY = "Eduardo Carbajal - 1873 - Artigas en el Paraguay.jpg"
PH_RIVERA = "Johann Moritz Rugendas – General Fructuoso Rivera (1846).jpg"
PH_SIEGE_PLAN = "PlanoMontevideoSitioGrande.JPG"
PH_PORT_1789 = "BERRA(1882) p365 PLANO DEL PUERTO DE MONTEVIDEO IN 1789.jpg"
PH_SARAVIA = "Aparicio Saravia a caballo.jpg"
PH_SARAVIA_1903 = "Desfile militar de Aparicio Saravia el 30 de marzo de 1903.jpg"
PH_BATLLE = "José Batlle y Ordóñez (1904).jpg"
PH_BATLLE2 = "José Batlle y Ordóñez 2.jpg"
PH_HUELGA = "Plaza Huelga General de 1973 A.jpg"
PH_SILENCIO = "Marcha del silencio, Montevideo, Uruguay 2024 (1).jpg"
PH_SEVERINO22 = "Reserva Paso Severino (Uruguay) Junio 2022.jpg"
PH_SEVERINO23 = "Reserva Paso Severino (Uruguay) Junio 2023.jpg"
PH_WATER_AID = "Donación de equipos para tratamiento de agua (53115826372).jpg"
PH_UPM = "UPM 2 psdlt.jpg"
PH_UPM2 = "Planta de celulosa UPM 2.jpg"
PH_UPM3 = "Planta de celulosa de UPM II 26.jpg"
PH_SERRA = "Serra Gaúcha de Bento Gonçalves.jpg"
PH_GRAMADO = "Bairro Planalto em Gramado.jpg"
PH_VINE = "Grape vine in Gramado.jpg"
PH_SALTON = "RenatoSoares Passeios e Experiencias nas Vinicolas Salton Bento Goncalves RS (40913639972).jpg"
PH_CAXIAS_HILLS = "Caxias do Sul - RS, Brazil - panoramio.jpg"
PH_CAXIAS_1971 = "Caxias do Sul, Fundo Correio da Manhã.tif"
PH_CAXIAS_1932 = "Amadeo Rossi & Cia - Caxias do Sul, RS - 1932.jpg"
PH_SAOLEO_1924 = "Centenário alemão em São Leopoldo.jpg"
PH_JAGUARY = "Planta Geral da Colonia Jaguary.png"
PH_BENTO = "Bento Gonçalves - RS, Brazil - panoramio (1).jpg"
PH_BORDER = "Border between Rivera and Santana do Livramento.jpg"
PH_PLAZA_INT = "Plaza Internacional.jpg"
PH_DURAZNO = "Casa de la Cultura, Durazno, Uruguay.jpg"
PH_BA_LCCN = "Immigrant Hotel, Buenos Aires, Argentina LCCN 91739070.tif#crop=0.05,0.07,0.08,0.11"
PH_BA_HOTEL2 = "Hotel de Inmigrantes c. 1912 - Google Arts & Culture.jpg"
PH_BAY_SHIPS = "Vista aérea de la bahía de Montevideo - 0086FMHE.tif" + G
PH_CERRO_AIR = "Vista aérea del Cerro - 0152FMHE.tif" + G
PH_RIVERA_BLANES = "Juan Manuel Blanes - Retrato del General Fructuoso Rivera.png"
PH_CAMPO_VACAS = "C48f515. Campo con vacas.jpg"
PH_OXO = "Oxo P-FG-ES-05537.jpg"
PH_LAZARETO2 = "Instalaciones del lazareto de inmigrantes - 0762FMHB.tif" + G
PH_WIND_RIVERA = "La Embajadora Kelly Keiderling visita Rivera.jpg"
PH_UPM_II = "Planta de celulosa de UPM II 12.jpg"
PH_GAUCHO_PORTRAIT = "Portrait of a Gaucho (5464643263).jpg"
PH_MOLLES = "Tropa de ganado en Molles.tif#crop=0.05,0.05,0.05,0.22"
PH_WAGON = "El Libro Del Centenario Del Uruguay-page 466-recorte3.tif#crop=0.02,0.02,0.02,0.12"
PH_SAOLEO_1971 = "São Leopoldo (RS).tif"
PH_CAXIAS_1883 = "Igreja de Caxias do Sul em 1883. (6615475477).jpg"
PH_RAMBLA_1948 = "Rambla República Argenitna - 08278FMHGE.tif" + G
PH_RAMBLA_1930 = "Rambla Presidente Wilson - 05453FMHGE.tif" + G
PH_MVD_PC = "Montevideo from Punta Carretas.JPG"
PH_PORT_NOW2 = "Puerto de Montevideo.jpg"
PH_BORDABERRY = "Asunción a la Presidencia de la Republica de Juan María Bordaberry - 11442FMHGE (cropped).tif"
PH_SILENCIO3 = "Marcha del silencio, Montevideo, Uruguay 2024 (3).jpg"
PH_STATION_2008 = "Estación Central General Artigas 2008 (2978564213).jpg"
PH_EST_PARAISO = "El Uruguay a través de un siglo page 461 recorte 02.tif#crop=0.03,0.03,0.03,0.13"
PH_EST_PINO = "El Uruguay a través de un siglo page 489 recorte 01.tif#crop=0.03,0.03,0.03,0.13"
PH_SALADERO_SALTO = "Saladero en Salto.jpg"  # the chimney of an old saladero

# ------------------------------------------------------------------ places, routes and arrows
MVD = place("Montevideo", -56.19, -34.90, "Montevideo", "capital")
BA = place("Buenos Aires", -58.38, -34.60, "Buenos Aires", "capital")
COLONIA = place("Colonia del Sacramento", -57.84, -34.47, "Colonia del Sacramento", "site")
AGRACIADA = place("Agraciada", -58.33, -33.80, "Agraciada beach", "site", icon="ship")
MASOLLER = place("Masoller", -55.99, -31.08, "Masoller", "site", icon="conflict")
FRAY = place("Fray Bentos", -58.31, -33.12, "Fray Bentos", "site", icon="factory")
CERRO = place("Cerro", -56.26, -34.89, "The Cerro plants", "site", icon="factory")
PDT = place("Paso de los Toros", -56.52, -32.82, "Paso de los Toros", "site", icon="factory")
SEVERINO = place("Paso Severino", -56.31, -34.23, "Paso Severino reservoir", "site", icon="water")
DURAZNO = place("Durazno", -56.52, -33.38, "Durazno", "city")
TRINIDAD = place("Trinidad", -56.90, -33.52, "Trinidad (Flores)", "city")
SALTO = place("Salto", -57.96, -31.38, "Salto", "city")
PAYSANDU = place("Paysandú", -58.08, -32.32, "Paysandú", "city")
RIVERA = place("Rivera", -55.55, -30.90, "Rivera", "city")
TACUAREMBO = place("Tacuarembó", -55.98, -31.71, "Tacuarembó", "city")
MELO = place("Melo", -54.18, -32.37, "Melo", "city")
PORTO_ALEGRE = place("Porto Alegre", -51.23, -30.03, "Porto Alegre", "city")
SAO_LEO = place("São Leopoldo", -51.15, -29.76, "São Leopoldo", "site", icon="farm")
CAXIAS = place("Caxias do Sul", -51.18, -29.17, "Caxias do Sul", "city")
BAGE = place("Bagé", -54.10, -31.33, "Bagé", "city")
RIO = place("Rio de Janeiro", -43.20, -22.90, "Rio de Janeiro", "city")
LONDON = place("London", -0.13, 51.51, "London", "capital")
GENOA = place("Genoa", 8.93, 44.41, "Genoa", "port")
VIGO = place("Vigo", -8.72, 42.24, "Vigo", "port")
MADRID = place("Madrid", -3.70, 40.42, "Spain", "capital")
NEWYORK = place("New York", -74.0, 40.71, "United States", "city")
HAVANA = place("Havana", -82.37, 23.11, "Cuba", "city")
L_BRAZIL = place("Brazil", -53.2, -28.6, "BRAZIL", "label")
L_ARG = place("Argentina", -60.3, -31.8, "ARGENTINA", "label")
AMER = {"lon": -62.0, "lat": -6.0, "span": 70.0}       # the River Plate to Cuba

RAIL = [{"from": [-56.19, -34.90], "via": [[-56.25, -34.45], [-56.52, -33.38], [-56.52, -32.82], [-55.98, -31.71]], "to": [-55.55, -30.90],
         "mode": "line", "label": "Railways to the port (approx.)", "color": "accent", "seconds": 3.0},
        {"from": [-56.19, -34.90], "via": [[-56.75, -34.30], [-57.45, -33.25]], "to": [-58.08, -32.32],
         "mode": "line", "color": "accent", "seconds": 3.0},
        {"from": [-56.19, -34.90], "via": [[-55.25, -34.37], [-54.95, -33.23]], "to": [-54.18, -32.37],
         "mode": "line", "color": "accent", "seconds": 3.0},
        {"from": [-56.19, -34.90], "via": [[-56.75, -34.35]], "to": [-57.84, -34.47],
         "mode": "line", "color": "accent", "seconds": 2.5}]
CATTLE_X = [{"from": [-58.45, -34.40], "to": [-57.30, -33.55], "color": "red", "label": "Cattle sent across", "bend": 0.15}]
HUNTERS = [{"from": [-58.40, -34.55], "to": [-56.80, -32.80], "color": "red", "label": "Hide hunters", "bend": 0.12},
           {"from": [-52.50, -30.20], "to": [-55.40, -32.20], "color": "red", "bend": -0.12}]
SHIPS = [{"from": [8.5, 43.8], "to": [-57.9, -34.7], "color": "red", "label": "Emigrant ships", "bend": 0.12},
         {"from": [-9.2, 42.0], "to": [-57.9, -34.9], "color": "red", "bend": 0.10}]
SHIPS_PAST = [{"from": [-54.0, -35.6], "to": [-58.2, -34.7], "color": "red", "label": "Most ships sail on to Buenos Aires", "bend": 0.15}]
LEAVERS = [{"from": [-56.19, -34.90], "to": [-58.3, -34.6], "color": "red", "label": "Emigrants", "bend": 0.3},
           {"from": [-56.19, -34.90], "to": [-3.7, 40.4], "color": "red", "bend": 0.12},
           {"from": [-56.19, -34.90], "to": [-74.0, 40.7], "color": "red", "bend": -0.12}]
INVASION = [{"from": [-53.0, -30.0], "to": [-56.0, -33.0], "color": "red", "label": "Portuguese troops, 1816", "bend": 0.1}]
LANDING = [{"from": [-58.55, -33.70], "to": [-58.33, -33.80], "color": "red", "label": "The Thirty-Three", "bend": 0.2}]
WATER_LINE = {"from": [-56.31, -34.23], "via": [[-56.40, -34.52]], "to": [-56.19, -34.85], "mode": "line",
              "label": "Water to the capital (approx.)", "color": "blue", "seconds": 3.0}

chapters = []
heads = iter(HEADS)


def chapter(*paras):
    title, mood = next(heads)
    chapters.append({"title": title, "mood": mood, "paragraphs": list(paras)})


# ================================================================== Hook
chapter(
    P("P0",
      m(0, v(URU, highlight=[UY_RED])),
      photo("It has soft green", PH_TACUA, "Tacuarembó, northern Uruguay"),
      photo("no deserts and no", PH_RN_LAND, "Río Negro department"),
      stat("And it has fewer", "3.5 MILLION", "People in Uruguay, census 2023", INE),
      m("England has more than", v(ATL, highlight=[UY_RED, ENG]))),
    P("P1",
      photo(0, PH_TABLADA1, "Cattle at La Tablada market, Montevideo, 1920"),
      photo("Ranchers in Uruguay declare", PH_PG23, "Tacuarembó, 2026"),
      stat("The last count came", "11.8 MILLION", "Cattle declared in Uruguay, 2025", DICOSE),
      chart("That is more than", "Uruguay, 2023-2025 (millions)", "", [["People", 3.5], ["Cattle", 11.8]], f"{INE}; {DICOSE}", highlight=1)),
    P("P2",
      photo(0, PH_MVD_AIR3, "Montevideo from the air, 2026"),
      m("We measured where Uruguayans", v(SCOAST, highlight=[MVD30])),
      sat("using a population map", -56.18, -34.88, 0.3, "Montevideo"),
      stat("Almost half of them", "49 %", "Uruguayans living within 30 km of Plaza Independencia", OWN_POP),
      photo("one square in central", PH_PLAZA, "Plaza Independencia, Montevideo"),
      stat("Half the country lives", "0.14 %", "Share of the land where half of Uruguayans live", OWN_POP)),
    P("P3",
      m(0, v(REGION, highlight=[UY_ALT, RS_RED])),
      photo("the same grass rolls", PH_PLAZA_INT, "The border at Rivera and Santana do Livramento"),
      stat("It holds nearly eleven", "10.9 MILLION", "People in Rio Grande do Sul, census 2022", IBGE),
      photo("The answer runs through", PH_HERD_1918, "A herd of cattle in Uruguay, about 1918-1920"),
      photo("a country designed in", PH_PORT_1931, "The port of Montevideo, 1931"),
      photo("a law that fenced", PH_EST_PINO, "Prize cattle at an estancia, 1910"),
      photo("ships that sailed past", PH_BAY_SHIPS, "Ships off Montevideo"),
      photo("and families that shrank", PH_PLAZA2, "Plaza Independencia"),
      photo("The first reason arrived", PH_TACUA_RIO, "The Tacuarembó River")),
)

# ================================================================== 1. The Cows Came First
chapter(
    P("P4",
      m(0, v(SAM, highlight=[UY_RED])),
      photo("On the far bank", PH_COLONIA, "The River Plate at Colonia"),
      m("the governor of Buenos", v(PLATA, places=[BA])),
      sat("had a plan for", -57.30, -33.60, 0.4, "The eastern bank of the river")),
    P("P5",
      stat(0, "1611 AND 1617", "Dates usually given for Hernandarias's cattle", "INAC; Library of Congress country study"),
      m("Hernandarias sent cattle across", v(PLATA, places=[BA], arrows=CATTLE_X)),
      photo("Nobody herded them.", PH_LAROCHE, "Ernesto Laroche, countryside painting, 1906"),
      sat("The grass was endless", -56.00, -32.30, 0.3, "Open grassland, central Uruguay")),
    P("P6",
      m(0, v(REGION, highlight=[UY_RED], places=[BA])),
      stat("the herds had grown", "MILLIONS", "Wild cattle on the eastern bank by the early 1700s", "Library of Congress country study"),
      photo("The land the Spanish", PH_MOLLES, "A cattle drive at Molles, 1907"),
      photo("one vast wild ranch.", PH_ESCENA, "Country scene, 19th century"),
      m("Hunters rode in from", v(REGION, highlight=[UY_RED], places=[L_BRAZIL], arrows=HUNTERS)),
      photo("which were shipped to", PH_GAUCHO_1868, "A gaucho, about 1868"),
      photo("Often the hide was", PH_BRANDING, "Branding a horse, Uruguay, 1904")),
    P("P6b",
      photo(0, PH_SALADERO, "Work at a saladero, Uruguay, 1907"),
      photo("Their workers cut the", PH_LIEBIG_1907, "The Liebig saladero at Fray Bentos, 1907"),
      photo("The product was called", PH_SALADERO_SALTO, "Chimney of an old saladero, Salto"),
      m("Ships carried it to", v(AMER, highlight=[UY_RED], places=[RIO]), step("where it fed enslaved", places=[HAVANA])),
      photo("It was the country's", PH_LIEBIG_PAN, "Fray Bentos, 1907"),
      photo("It did not need", PH_RN_LAND, "Río Negro department")),
    P("P7",
      photo(0, PH_FIELD, "Uruguayan countryside"),
      photo("and men on horseback", PH_GAUCHO_PORTRAIT, "A gaucho"),
      m("When Spain and Portugal", v(PLATA, places=[BA, COLONIA])),
      sat("Portugal founded Colonia del", -57.845, -34.47, 0.08, "Colonia del Sacramento"),
      photo("right across the river", "Uruguay - Colonia del Sacramento 06.jpg", "Colonia del Sacramento"),
      photo("Spain answered with a", PH_CERRO_AIR, "Montevideo Bay and the Cerro from the air"),
      sat("It became a city", -56.205, -34.905, 0.08, "Montevideo's old town")),
    P("P8",
      photo(0, PH_OLDTOWN_NOW, "Montevideo's old town"),
      photo("A single family could", PH_TACUA, "Tacuarembó"),
      photo("The cattle did the", PH_HERD_1918, "Cattle in Uruguay, about 1918-1920"),
      m("So when the time", v(URU, places=[MVD, COLONIA])),
      sat("A port, a few", -56.52, -33.38, 0.15, "Durazno and its pastures")),
)

# ================================================================== 2. A Country With One Door
chapter(
    P("P8b",
      m(0, v(URU, highlight=[UY_RED])),
      stat("In 1815, during the", "10 SEP 1815", "Artigas's land regulation", "Reglamento Provisorio, 1815"),
      photo("the leader of the", PH_ARTIGAS, "Artigas, painted by Juan Manuel Blanes"),
      photo("It ordered the land", PH_LAROCHE, "Countryside, painted by Ernesto Laroche, 1906"),
      photo("divided up and given", PH_EST_PARAISO, "An estancia house, 1910"),
      stat("Its most famous line", "MOST UNFORTUNATE FIRST", "Its principle: the most unfortunate should be the most privileged (1815)", "Reglamento Provisorio, 1815 (text: La Izquierda Diario)"),
      m("A year later, Portuguese", v(REGION, highlight=[UY_RED], arrows=INVASION)),
      photo("Artigas was driven into", PH_ARTIGAS_PY, "Artigas in Paraguay, by Eduardo Carbajal, 1873")),
    P("P9",
      m(0, v(SAM, highlight=[UY_RED]), step("After Artigas fell, the", places=[RIO])),
      stat("first by Portugal and", "CISPLATINE PROVINCE", "The eastern bank under Portugal, then the Empire of Brazil", "MEC Uruguay; Wikipedia"),
      stat("At dawn on the", "19 APRIL 1825", "Thirty-three exiles land at Agraciada", "MEC Uruguay"),
      m("crossed the Uruguay River", v(WEST, places=[AGRACIADA], arrows=LANDING)),
      sat("a beach called Agraciada.", -58.335, -33.80, 0.1, "Agraciada, on the Uruguay River"),
      m("They raised the countryside", v(URU, places=[AGRACIADA]), step("against Brazil.", highlight=[UY_RED])),
      m("Argentina joined in, and", v(REGION, highlight=[UY_RED]), step("went to war over", places=[L_BRAZIL, L_ARG])),
      m("Britain, whose merchants wanted", v(ATL, places=[LONDON, MVD]))),
    P("P10",
      stat(0, "27 AUG 1828", "Peace convention signed in Rio de Janeiro", "Preliminary Peace Convention, 1828"),
      m("The disputed land would", v(REGION, places=[L_BRAZIL, L_ARG]), step("It would be a", highlight=[UY_RED])),
      photo("A buffer.", PH_COLONIA_DUSK, "Colonia del Sacramento")),
    P("P11",
      m(0, v(URU, places=[MVD])),
      photo("the harbour at Montevideo.", PH_PORT_1919, "Montevideo's old town and port, 1919"),
      photo("The customs house, the", PH_OLDTOWN_1936, "Montevideo's old town, 1936"),
      photo("And the countryside around", PH_PG17, "Riders in Tacuarembó, 2026")),
    P("P12",
      m(0, v(URU, highlight=[UY_RED])),
      stat("On the eleventh of", "11 APRIL 1831", "Rivera's army attacks the Charrúa at Salsipuedes", "INDDHH Uruguay"),
      photo("attacked the Charrúa, the", PH_RIVERA_BLANES, "Fructuoso Rivera, by Juan Manuel Blanes"),
      stat("Rivera's own report counted", "~40 / 300", "Dead and prisoners in Rivera's own report", "INDDHH Uruguay"),
      photo("who were handed out", PH_OLDTOWN_AIR, "Montevideo's old town")),
    P("P13",
      photo(0, PH_GAUCHO_PORTRAIT, "A gaucho"),
      stat("From 1839 to 1851,", "1839-1851", "The Guerra Grande", "Library of Congress country study"),
      m("pulled in Argentina, Brazil,", v(REGION, highlight=[UY_RED], places=[L_BRAZIL, L_ARG])),
      sat("For about eight years,", -56.19, -34.89, 0.15, "Montevideo, besieged 1843-1851"),
      photo("The interior was fought", PH_PG42, "Riders, Tacuarembó"),
      photo("and the herds were", PH_MOLLES, "A cattle drive at Molles, 1907")),
    P("P14",
      stat(0, "1869", "Uruguay's first railway opens", "Rail transport in Uruguay (Wikipedia)"),
      photo("built and owned mostly", PH_STATION_1900, "Central Station, Montevideo, about 1900"),
      m("Look at the network", v(URU, places=[MVD, RIVERA, PAYSANDU, MELO]), step("The lines reach out", routes=RAIL)),
      photo("and every one of", PH_WAGON, "A cattle wagon of the Central Uruguay Railway, 1925"),
      photo("runs back to the", PH_PORT_1931B, "Montevideo's port, 1931")),
    P("P15",
      photo(0, PH_STATION_1917, "Central Station, Montevideo, 1917"),
      photo("But a railway can", PH_SALTO_STATION, "The old station at Salto"),
      sat("Because by then, the", -55.95, -31.85, 0.2, "Ranch land near Tacuarembó")),
)

# ================================================================== 3. The Fences
chapter(
    P("P16",
      m(0, v(URU, highlight=[INT_RED])),
      photo("Boundaries were streams, stone", PH_FIELD, "Old stone huts on the grassland"),
      photo("Cattle wandered, and so", PH_PG34, "Riders, Tacuarembó")),
    P("P17",
      photo(0, PH_SHEARING, "Sheep shearing, Uruguay, 1904"),
      stat("On the twenty-seventh of", "27 JULY 1875", "The Rural Code comes into force", "IMPO, Código Rural"),
      photo("It was written by", PH_SHEEP_PEN, "A sheep pen, 1904"),
      sat("Landowners now had to", -56.70, -33.40, 0.25, "Fenced pastures, central Uruguay"),
      stat("From 1876, imports of", "1876", "Fencing wire imports take off", "Montevideo Portal history series")),
    P("P18",
      sat(0, -56.15, -33.60, 0.4, "Estancias of central Uruguay"),
      photo("And a fence changes", PH_RUTA30, "Fenced grassland, Rivera"),
      photo("A ranch without fences", PH_PG60, "Riders, Tacuarembó"),
      photo("A fenced one needs", PH_EST_PINO, "Prize cattle at an estancia, 1910")),
    P("P19",
      photo(0, PH_ESCENA, "Rural Uruguay, 19th century"),
      photo("Workers who had lived", PH_BRANDING, "Ranch work, 1904"),
      sat("Many drifted to clusters", -55.95, -31.85, 0.1, "Small settlements on the ranch roads, Tacuarembó"),
      stat("They called them pueblos", "PUEBLOS DE RATAS", "\"Rat towns\": the ranchers' name for the shack settlements", "Udelar studies (Redalyc)")),
    P("P20",
      photo(0, PH_TABLADA4, "La Tablada cattle market, Montevideo"),
      photo("The last great revolt", PH_PG42, "Riders, Tacuarembó"),
      photo("In 1904, the rebel", PH_SARAVIA, "Aparicio Saravia"),
      photo("led thousands of riders", PH_SARAVIA_1903, "Saravia's riders, March 1903"),
      m("He was shot at", v(NORTH, places=[MASOLLER])),
      stat("on the first of", "1 SEP 1904", "Battle of Masoller: Uruguay's last civil war", "Encyclopedia.com; Wikipedia"),
      sat("It was Uruguay's last", -55.99, -31.08, 0.12, "Masoller today"),
      photo("The age of the", PH_GAUCHO_1868, "A gaucho, about 1868")),
    P("P20b",
      m(0, v(WEST, places=[FRAY])),
      sat("on the Uruguay River.", -58.33, -33.12, 0.08, "Fray Bentos and the old plant"),
      photo("It boiled down beef", PH_OXO, "Liebig's OXO, advertising"),
      photo("and later canned corned", PH_LIEBIG_1919, "The Fray Bentos plant, 1919"),
      photo("Thousands worked there, and", PH_ANGLO, "The old plant at Fray Bentos"),
      stat("today the site is", "UNESCO 2015", "Fray Bentos Industrial Landscape, World Heritage", "UNESCO 39 COM 8B.39")),
    P("P20c",
      photo(0, PH_SWIFT_1918, "The Swift plant on the Cerro, 1918"),
      sat("took over plants on", -56.25, -34.885, 0.12, "The Cerro and Montevideo Bay"),
      photo("the hill across the", PH_CERRO_AIR, "The Cerro from the air"),
      photo("Cattle were raised in", PH_TABLADA3, "La Tablada cattle market, 1920"),
      photo("and turned into jobs", PH_PANTANOSO, "Meat plants by the Pantanoso creek, 1926"),
      photo("The work went to", PH_SWIFT_1958, "The Cerro plants, 1958")),
    P("P21",
      photo(0, PH_OLDTOWN_1936, "Montevideo, 1936"),
      m("Europe's great wave of", v(ATL, highlight=[UY_RED, "Italy@alt", "Spain@alt"]))),
)

# ================================================================== 4. The Ships Went to Buenos Aires
chapter(
    P("P22",
      m(0, v(ATL, places=[GENOA, VIGO, BA], arrows=SHIPS)),
      stat("some six million Europeans", "~6 MILLION", "Europeans to Argentina, about 1870-1930", "bpb country profile Argentina"),
      photo("Italians and Spaniards above", PH_BA_LCCN, "The Immigrants' Hotel, Buenos Aires, early 1900s"),
      photo("offered free lodging on", PH_BA_HOTEL2, "The Immigrants' Hotel, Buenos Aires, about 1912"),
      m("free train tickets inland", v(SAM, highlight=["Argentina@red"]))),
    P("P23",
      m(0, v(PLATA, places=[BA, MVD], arrows=SHIPS_PAST)),
      photo("Estimates for the half", PH_BAY_SHIPS, "Ships in Montevideo Bay"),
      chart("run from under three", "Immigrants, about 1880-1930", "", [["Argentina", 6000], ["Uruguay, high estimate", 579], ["Uruguay, low estimate", 273]], "bpb; Immigration to Uruguay (Wikipedia)", highlight=0, reveal=None),
      photo("And most of the", PH_FLORES_PIER, "Immigrants at the Isla de Flores quarantine station, 1921"),
      photo("stayed exactly where the", PH_IMM_PIER_1904, "The immigrants' pier, Montevideo, 1904"),
      stat("In 1889, almost half", "47 %", "Foreign-born share of Montevideo, 1889 census", "Beretta Curi (SciELO)")),
    P("P23b",
      photo(0, PH_LAZARETO2, "The immigrant quarantine station, Isla de Flores"),
      photo("nearly half of all", PH_PORT_1919, "Montevideo, 1919"),
      stat("Even in 1908, when", "1 IN 6", "Uruguayans born abroad, 1908 census", "Immigration to Uruguay (Wikipedia)"),
      photo("about one person in", PH_SALTO_1919, "Salto, 1919"),
      photo("Most of them lived", PH_POCITOS_1919, "The Rambla at Pocitos, 1919")),
    P("P24",
      sat(0, -56.70, -33.40, 0.4, "Estancias of central Uruguay"),
      photo("The good land was", PH_TABLADA4, "La Tablada, Montevideo"),
      photo("by families who did", PH_EST_PARAISO, "An estancia, 1910"),
      photo("An Italian peasant could", PH_LAZARETO, "The immigrant quarantine station, 1921"),
      photo("He could not find", PH_RN_RIVER, "The Río Negro")),
    P("P25",
      m(0, v(RS_V, highlight=[RS_RED], places=[SAO_LEO])),
      photo("In 1824, the first", PH_SAOLEO_1924, "Centenary of German settlement, São Leopoldo, 1924"),
      photo("in the forested hills", PH_SAOLEO_1971, "São Leopoldo, 1971"),
      m("From 1875, Italians followed,", v(RS_V, highlight=[NOR_BLUE], places=[CAXIAS])),
      photo("about a hundred thousand", PH_CAXIAS_HILLS, "The hills around Caxias do Sul"),
      photo("most of them to", PH_CAXIAS_1883, "Caxias do Sul in 1883"),
      photo("the city of Caxias", PH_CAXIAS_1932, "Caxias do Sul, 1932"),
      photo("They were given family-sized", PH_JAGUARY, "Plan of the Jaguari colony lots, 1898"),
      photo("cleared the forest and", PH_VINE, "Vineyards in the Serra Gaúcha, Gramado"),
      sat("then towns, then cities.", -51.18, -29.17, 0.25, "Caxias do Sul")),
    P("P26",
      m(0, v(RS_V, highlight=[RS_ALT]), step("into its official regions", highlight=[SUD_RED, NOR_BLUE])),
      sat("on the open pampa", -54.67, -30.98, 0.25, "The Campanha near Dom Pedrito"),
      photo("In the northeast, the", PH_SERRA, "Serra Gaúcha, Bento Gonçalves"),
      chart("In Uruguay's interior, away", "People per km², 2023", "", [["Old colonies, Brazil", 47.0], ["Campanha, Brazil", 10.9], ["Uruguay's interior", 6.9]], OWN_POP, highlight=2)),
    P("P27",
      photo(0, PH_BORDER, "The border at Rivera"),
      sat("On the Brazilian side,", -55.53, -30.90, 0.12, "Rivera and Santana do Livramento"),
      photo("The people are where", PH_GRAMADO, "Gramado, in the old colony hills"),
      photo("Uruguay never had that", PH_PG33, "Tacuarembó")),
    P("P28",
      photo(0, PH_PLAZA2, "Montevideo"),
      photo("Uruguay's were not.", PH_MVD_WALK, "Montevideo")),
)

# ================================================================== 5. Small Families, Early
chapter(
    P("P29",
      m(0, v(SAM, highlight=[UY_RED])),
      photo("Demographers count it among", PH_WILSON_1922, "The Rambla, Montevideo, 1922"),
      photo("to see both death", PH_RAMBLA_1948, "The Rambla, Montevideo, 1948"),
      stat("at least thirty years", "30+ YEARS", "Uruguay's head start in the demographic transition", "Pellegrino 2013; Cabella et al.")),
    P("P30",
      photo(0, PH_PORT_AIR, "Montevideo from the air"),
      photo("A large share of", PH_RAMBLA_1930, "Montevideo, 1930"),
      photo("with jobs, schools and", PH_PERU_1944, "Montevideo, 1944"),
      photo("In the early nineteen", PH_BATLLE, "José Batlle y Ordóñez, 1904"),
      stat("Divorce became legal in", "1907", "Uruguay's divorce law", "Ramos Palomo & Ortega Muñoz; LOC"),
      photo("a wife could end", PH_POCITOS_1919, "Pocitos, Montevideo, 1919")),
    P("P31",
      chart(0, "Children per woman", "", [["Uruguay, 1950", 2.7], ["Uruguay, 2021", 1.4]], "Cabella et al.; Nathan, Pardo & Cabella", highlight=0),
      photo("Most of Latin America", PH_RAMBLA, "The Rambla, Montevideo"),
      m("Brazil and Argentina grew", v(SAM, highlight=[UY_RED], places=[L_BRAZIL, L_ARG]))),
    P("P31b",
      chart(0, "Uruguayans aged 65 or older (%)", "", [["1963", 7.9], ["2023", 15.7], ["2070 (projected)", 32.5]], "INE Uruguay projections", highlight=2),
      photo("In the 2023 census", PH_RAMBLA_FR, "The Rambla, Montevideo"),
      photo("and the statistics office", PH_MVD_AIR1, "Montevideo")),
    P("P32",
      photo(0, PH_MVD_PC, "Montevideo from Punta Carretas"),
      stat("By 2021, the rate", "1.4", "Children per woman in Uruguay, 2021", "Cabella et al."),
      photo("far below the two", PH_SKYLINE, "Montevideo"),
      photo("Every new generation is", PH_PUNTA_CARRETAS, "Punta Carretas, Montevideo")),
    P("P33",
      photo(0, PH_PORT_NOW, "The port of Montevideo"),
      m("Its people left.", v(WORLD, places=[MVD], arrows=LEAVERS))),
)

# ================================================================== 6. The Ones Who Left
chapter(
    P("P34",
      m(0, v(URU, highlight=[UY_RED], places=[MVD])),
      photo("In 1973, the military", PH_BORDABERRY, "Juan María Bordaberry takes office, 1 March 1972"),
      photo("Over the next twelve", PH_HUELGA, "Square of the 1973 General Strike, Montevideo"),
      photo("By the time democracy", PH_SILENCIO3, "Silent march for the disappeared, Montevideo, 2024"),
      stat("about three hundred and", "380,000", "Uruguayans who left by 1985", "Wilson Center"),
      photo("In a nation of", PH_SILENCIO, "Silent march for the disappeared, Montevideo, 2024")),
    P("P35",
      stat(0, "2002", "Banking crisis", "Pellegrino & Vigorito 2005"),
      photo("Banks closed their doors,", PH_OLDTOWN_NOW, "Montevideo's old town"),
      stat("about a hundred thousand", "~100,000", "Uruguayans who left, 1999-2002", "Pellegrino & Vigorito 2005"),
      photo("Studies found that the", PH_MVD_AIR2, "Montevideo")),
    P("P36",
      m(0, v(WORLD, places=[MVD, MADRID, NEWYORK], arrows=LEAVERS)),
      photo("Today there are hundreds", PH_PORT_NOW2, "The port of Montevideo")),
    P("P37",
      stat(0, "3,499,451", "People counted in the 2023 census", INE),
      photo("only a little more", PH_MVD_AIR4, "Montevideo"),
      photo("The national statistics office", PH_MVD_AIR5, "Montevideo"),
      m("Even Montevideo is getting", v(SCOAST, highlight=["Montevideo@red"])),
      stat("The capital lost about", "-5 %", "Montevideo department, 2011-2023", f"{INE}; El Observador"),
      sat("as families moved out", -54.95, -34.92, 0.2, "Maldonado and Punta del Este")),
    P("P37b",
      m(0, v(SCOAST, places=[SEVERINO, MVD])),
      photo("after a record drought,", PH_SEVERINO22, "Paso Severino from orbit, June 2022"),
      photo("fell to a few", PH_SEVERINO23, "Paso Severino from orbit, June 2023"),
      m("More than half the", v(SCOAST, places=[SEVERINO, MVD], routes=[WATER_LINE])),
      sat("the water company mixed", -56.31, -34.23, 0.25, "Paso Severino, July 2023", date=W23),
      photo("and people in Montevideo", PH_OSE, "Headquarters of OSE, the water company"),
      sat("The crisis ended only", -56.31, -34.23, 0.35, "Paso Severino, summer 2025")),
    P("P38",
      photo(0, PH_TACUA_RIO, "The Tacuarembó River"),
      photo("and many of those", PH_STATION_2008, "The old Central Station, Montevideo, 2008"),
      m("But the interior is", v(URU, highlight=[INT_RED])),
      sat("Something is growing on", -55.90, -31.80, 0.35, "Tree plantations near Tacuarembó")),
)

# ================================================================== Ending
chapter(
    P("P38b",
      m(0, v(URU, highlight=[COAST_RED])),
      chart("seven in ten Uruguayans", "Six coastal departments", "%", [["Share of people", 69.9], ["Share of land", 18.0]], OWN_POP, highlight=0),
      m("In Durazno and Flores,", v(CENTRE, highlight=["Durazno@red", "Flores@red"], places=[DURAZNO, TRINIDAD])),
      photo("there are fewer than", PH_DURAZNO, "Durazno"),
      stat("Montevideo, the smallest department", "1.3 MILLION", "People in Montevideo department (Kontur 2023)", OWN_POP)),
    P("P39",
      m(0, v(URU, places=[MVD, TACUAREMBO, RIVERA])),
      sat("Long straight rows of", -55.55, -31.55, 0.15, "Plantations in Rivera"),
      photo("planted where cattle used", PH_EUCA_ROW, "Eucalyptus and pasture"),
      stat("More than a million", "1.1 MILLION HA", "Pine and eucalyptus plantations in Uruguay, 2023", "Dialogue Earth; UPM")),
    P("P39b",
      photo(0, PH_OVINOS, "Sheep in Uruguay"),
      chart("In the late 1980s,", "Sheep in Uruguay (millions)", "", [["About 1990", 25.0], ["2025", 4.75]], "MercoPress", highlight=1),
      photo("By 2025, the flock", PH_SHEEP_PEN, "A sheep pen, 1904"),
      sat("as pasture went to", -57.90, -33.50, 0.2, "Crop fields, Soriano")),
    P("P40",
      m(0, v(CENTRE, highlight=[UY_ALT], places=[PDT, DURAZNO])),
      sat("started a new pulp", -56.55, -32.84, 0.12, "The UPM mill at Paso de los Toros"),
      photo("It can produce two", PH_UPM, "UPM mill, Paso de los Toros"),
      stat("from trees grown on", "2.1 MILLION T", "Pulp a year from the Paso de los Toros mill", "UPM"),
      photo("And on the hilltops,", PH_WIND1, "Wind turbines in northern Uruguay"),
      stat("In 2024, almost all", "99 %", "Renewable share of Uruguay's electricity, 2024 (wind 28 %)", "MIEM via trade.gov"),
      photo("more than a quarter", PH_WIND2, "Wind turbines, northern Uruguay")),
    P("P41",
      sat(0, -58.255, -33.105, 0.1, "The UPM mill at Fray Bentos"),
      photo("cover a great deal", PH_UPM_II, "The UPM mill at Paso de los Toros"),
      photo("The interior is producing", PH_UPM3, "UPM pulp mill, Paso de los Toros"),
      sat("and it is still", -55.95, -31.85, 0.25, "The interior near Tacuarembó")),
    P("P42",
      photo(0, PH_TABLADA1, "Cattle, La Tablada, 1920"),
      photo("The country was built", PH_BAY_AIR, "Montevideo Bay from the air"),
      photo("Fences closed the land,", PH_RUTA30, "Fenced grassland, Rivera"),
      photo("the ships sailed past", PH_BA_LCCN, "Buenos Aires"),
      photo("the families were small,", PH_WILSON_1922, "Montevideo, 1922"),
      photo("and in hard times", PH_SILENCIO, "Montevideo, 2024"),
      photo("None of these alone", PH_PG60, "Tacuarembó"),
      m("Together, they made a", v(URU, highlight=[COAST_RED, INT_ALT])),
      photo("and keeps its interior", PH_RN_RIVER, "The Río Negro")),
    P("P43",
      photo(0, PH_MVD_AIR6, "Montevideo"),
      photo("with more cows than", PH_TABLADA3, "Cattle at La Tablada, 1920"),
      m("Tell me in the", v(URU, highlight=[INT_RED], places=[TACUAREMBO, DURAZNO])),
      ask=("Would you trade a", "City flat or a house in Uruguay's interior?")),
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



TITLE = "Why Uruguay Has More Cows Than People"
script = {
    "title": TITLE,
    "voice": "am_michael",
    "voice_speed": 1.15,
    "music": "procedural",
    "map_style": "satellite",
    "look": "none",
    "photo_upscale": True,
    "sources": ["episodes/uruguay-empty/research.md and factcheck.md", "Contains modified Copernicus Sentinel data 2026",
                "Where Uruguayans live: own count, Kontur Population 2023 (CC BY 4.0) (geo/measure_population.py)",
                "Departments and England: Natural Earth; Rio Grande do Sul regions: IBGE mesorregiões (geo/make_regions.py)",
                "Railway, ship and water arrows drawn through main points (approximate)"],
    "thumbnail": {"text": "MORE COWS THAN PEOPLE"},
    "chapters": chapters,
    "youtube": {
        "title": TITLE,
        "title_candidates": [TITLE, "Why Almost Nobody Lives in Uruguay's Interior", "Why Half of Uruguay Lives in One City"],
        "description": "Uruguay is bigger than England, with mild winters, good rain and endless grass, yet it has fewer than 3.5 million people and almost 12 million cattle. Half of all Uruguayans live within 30 km of one square in Montevideo. Across the border, the same grass in southern Brazil holds nearly 11 million. We follow the answer from orbit and the archives: cattle set loose in the 1600s, a buffer state with one port, the Rural Code and the fences of 1875, the emigrant ships that sailed on to Buenos Aires, families that shrank decades early, the exiles of 1973 and 2002, and the eucalyptus, pulp mills and wind farms on the old ranches.",
        "tags": ["Uruguay", "Montevideo", "Uruguay geography", "cattle", "gaucho", "Rio Grande do Sul", "Fray Bentos",
                 "River Plate", "Buenos Aires", "immigration", "estancia", "UPM pulp mill", "geography", "satellite images"],
        "pinned_comment": "Would you trade a city flat for a house in Uruguay's quiet interior, with more cows than neighbours?",
    },
}
out = HERE / "script.json"
out.write_text(json.dumps(script, ensure_ascii=False, indent=1) + chr(10), encoding="utf-8")
words = sum(len(p["text"].split()) for c in chapters for p in c["paragraphs"])
shots = [s for c in chapters for p in c["paragraphs"] for s in p["shots"]]
kinds = {k: sum(1 for s in shots if s["type"] == k) for k in ("map", "photo", "stat", "document", "chart")}
print(f"{words} words, {len(chapters)} chapters, {len(shots)} shots {kinds}")
