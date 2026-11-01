"""Natural Earth vector data (public domain): cached download, name lookup, Web Mercator helpers.

All map geometry handed to Remotion is in "unit Mercator" coordinates: x, y in [0, 1] for the whole
Web Mercator square (x = 0 at 180 W, y = 0 at about 85.05 N), the same projection as the GIBS imagery.
"""
import difflib
import json
import math
import re
import time
import unicodedata
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import numpy as np
import requests
import shapely
from shapely.geometry import shape

from config import CACHE_DIR, ROOT

NE_TAG = "v5.1.2"
NE_URL = "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/{tag}/geojson/{name}.geojson"
GEO_DIR = CACHE_DIR / "geo"
GAZETTEER = ROOT / "pipeline" / "gazetteer.json"
MAX_LAT = 85.0511287798

# Common names that Natural Earth spells differently -> ADM0_A3.
COUNTRY_ALIASES = {
    "usa": "USA", "us": "USA", "u s": "USA", "united states": "USA", "america": "USA",
    "uk": "GBR", "britain": "GBR", "great britain": "GBR",
    "south korea": "KOR", "korea": "KOR", "north korea": "PRK",
    "ivory coast": "CIV", "cote d ivoire": "CIV",
    "czech republic": "CZE", "czechia": "CZE",
    "drc": "COD", "dr congo": "COD", "congo kinshasa": "COD", "democratic republic of congo": "COD",
    "congo": "COG", "republic of the congo": "COG", "congo brazzaville": "COG",
    "turkiye": "TUR", "burma": "MMR", "holland": "NLD", "east timor": "TLS",
    "swaziland": "SWZ", "eswatini": "SWZ", "macedonia": "MKD", "north macedonia": "MKD",
    "vatican": "VAT", "uae": "ARE", "emirates": "ARE", "palestine": "PSX", "cape verde": "CPV",
}
# Shorter on-map labels where Natural Earth's NAME is abbreviated or long.
LABEL_OVERRIDES = {"USA": "United States", "COD": "DR Congo", "CAF": "Central African Rep.", "GBR": "United Kingdom",
                   "BIH": "Bosnia & Herz.", "DOM": "Dominican Rep.", "SSD": "South Sudan", "GNQ": "Eq. Guinea"}


def key(s: str) -> str:
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower().replace("&", " and ")
    s = re.sub(r"[^a-z0-9]+", " ", s).strip()
    return re.sub(r"^the ", "", s)


# ---------------------------------------------------------------- download / load

def ne_path(name: str) -> Path:
    path = GEO_DIR / "ne" / f"{name}.geojson"
    if path.exists():
        return path
    path.parent.mkdir(parents=True, exist_ok=True)
    url = NE_URL.format(tag=NE_TAG, name=name)
    for attempt in range(4):
        try:
            r = requests.get(url, timeout=300)
            r.raise_for_status()
            break
        except requests.RequestException:
            if attempt == 3:
                raise
            time.sleep(5 * (attempt + 1))
    tmp = path.with_suffix(".part")
    tmp.write_bytes(r.content)
    tmp.replace(path)
    print(f"  natural earth: downloaded {name} ({len(r.content) / 1e6:.1f} MB)")
    return path


@lru_cache(maxsize=None)
def ne_features(name: str) -> list[dict]:
    return json.loads(ne_path(name).read_text(encoding="utf-8"))["features"]


@lru_cache(maxsize=None)
def ne_geoms(name: str) -> list:
    """(properties, shapely geometry) for every feature with a geometry."""
    return [(f["properties"], shape(f["geometry"])) for f in ne_features(name) if f.get("geometry")]


# ---------------------------------------------------------------- Web Mercator (unit square)

def mx(lon):
    return (np.asarray(lon, dtype=float) + 180.0) / 360.0


def my(lat):
    lat = np.clip(np.asarray(lat, dtype=float), -MAX_LAT, MAX_LAT)
    s = np.sin(np.radians(lat))
    return 0.5 - np.log((1 + s) / (1 - s)) / (4 * math.pi)


def unmerc(x: float, y: float) -> tuple[float, float]:
    lon = x * 360.0 - 180.0
    lat = math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * y))))
    return lon, lat


def to_unit(geom):
    """lon/lat shapely geometry -> unit Mercator geometry."""
    return shapely.transform(geom, lambda c: np.column_stack([mx(c[:, 0]), my(c[:, 1])]))


# ---------------------------------------------------------------- countries

@dataclass
class Country:
    code: str  # ADM0_A3
    name: str  # label text
    label: tuple[float, float]  # lon, lat (Natural Earth's preferred label point)
    iso3: str  # ISO_A3_EH (or ADM0_A3)
    wb3: str  # World Bank code


@lru_cache(maxsize=None)
def _country_index() -> tuple[dict, dict]:
    """key(name or code) -> ADM0_A3, and ADM0_A3 -> Country (from the 10m layer)."""
    names, info = {}, {}
    for p, _ in ne_geoms("ne_10m_admin_0_countries"):
        code = p["ADM0_A3"]
        label = LABEL_OVERRIDES.get(code) or (p["NAME"] if "." not in p["NAME"] and len(p["NAME"]) <= 16 else p["NAME_LONG"])
        iso3 = p["ISO_A3_EH"] if p["ISO_A3_EH"] not in ("-99", None) else code
        wb3 = p["WB_A3"] if p["WB_A3"] not in ("-99", None) else iso3
        info[code] = Country(code, label, (p["LABEL_X"], p["LABEL_Y"]), iso3, wb3)
        for field in ("NAME", "NAME_LONG", "ADMIN", "NAME_EN", "FORMAL_EN", "NAME_SORT", "BRK_NAME", "GEOUNIT", "NAME_ALT"):
            if p.get(field):
                names.setdefault(key(p[field]), code)
        for field in ("ADM0_A3", "ISO_A3_EH", "ISO_A3"):
            if p.get(field) and p[field] != "-99":
                names.setdefault(key(p[field]), code)
    for alias, code in COUNTRY_ALIASES.items():
        if code in info:
            names[alias] = code
    return names, info


def country_code(name: str) -> str | None:
    names, _ = _country_index()
    return names.get(key(name))


def country(code: str) -> Country:
    return _country_index()[1][code]


@lru_cache(maxsize=None)
def country_geoms(lod: str) -> dict:
    """ADM0_A3 -> lon/lat geometry at a Natural Earth scale ('10m', '50m', '110m')."""
    return {p["ADM0_A3"]: g for p, g in ne_geoms(f"ne_{lod}_admin_0_countries")}


def country_geom(code: str, lod: str):
    geoms = country_geoms(lod)
    return geoms.get(code) or country_geoms("10m")[code]  # tiny countries are missing from 110m


def main_body(geom):
    """The country's largest polygon plus nearby islands (drops far overseas territories for framing)."""
    polys = list(getattr(geom, "geoms", [geom]))
    big = max(polys, key=lambda p: p.area)
    reach = math.dist(big.bounds[:2], big.bounds[2:]) * 0.35 + 1.0
    keep = [p for p in polys if p.area >= big.area * 0.002 and p.distance(big) <= reach]
    return shapely.union_all(keep)


# ---------------------------------------------------------------- admin-1 (states / provinces), loaded lazily

@lru_cache(maxsize=None)
def _admin1_index() -> dict:
    out = {}
    for p, g in ne_geoms("ne_10m_admin_1_states_provinces"):
        for field in ("name", "name_en", "name_alt"):
            for n in (p.get(field) or "").split("|"):
                if n:
                    out.setdefault(key(n), (p, g))
                    out.setdefault(key(f"{n}, {p.get('admin', '')}"), (p, g))
    return out


def admin1(name: str):
    """(label, lon/lat geometry, (lon, lat) label point) for a state/province name, or None."""
    hit = _admin1_index().get(key(name))
    if not hit:
        return None
    p, g = hit
    return p.get("name_en") or p["name"], g, (p.get("longitude"), p.get("latitude"))


# ---------------------------------------------------------------- places (gazetteer)

@dataclass
class Place:
    name: str
    lon: float
    lat: float
    kind: str  # city | capital | sea | site
    country: str = ""
    rank: float = 0.0  # larger wins when a name is ambiguous


@lru_cache(maxsize=None)
def _gazetteer() -> dict[str, list[Place]]:
    idx: dict[str, list[Place]] = {}

    def add(names, place):
        for n in {key(n) for n in names if n}:
            idx.setdefault(n, []).append(place)
            if place.country:
                idx.setdefault(key(f"{n}, {place.country}"), []).append(place)

    for p, g in ne_geoms("ne_10m_populated_places"):
        kind = "capital" if "capital" in (p.get("FEATURECLA") or "").lower() and "Admin-0" in p["FEATURECLA"] else "city"
        place = Place(p["NAME"], p["LONGITUDE"], p["LATITUDE"], kind, p.get("ADM0NAME") or "", float(p.get("POP_MAX") or 0))
        add([p["NAME"], p.get("NAMEASCII"), p.get("NAME_EN")], place)
    def prop(p: dict, name: str):
        return p.get(name) or p.get(name.upper()) or p.get(name.lower())

    for layer in ("ne_10m_geography_marine_polys", "ne_10m_geography_regions_points", "ne_10m_geography_regions_polys"):
        for p, g in ne_geoms(layer):
            if not prop(p, "name"):
                continue
            pt = g if g.geom_type == "Point" else g.representative_point()
            kind = "sea" if "marine" in layer else "site"
            rank = (1e9 if kind == "sea" else 1e8) / (1 + (prop(p, "scalerank") or 0))
            add([prop(p, "name"), prop(p, "name_en")], Place(prop(p, "name"), pt.x, pt.y, kind, "", rank))
    # Curated entries (canals, straits, landmarks Natural Earth lacks) always win.
    for name, v in json.loads(GAZETTEER.read_text(encoding="utf-8")).items():
        if name.startswith("_"):
            continue
        idx[key(name)] = [Place(name, v["lon"], v["lat"], v.get("kind", "site"), v.get("country", ""), 1e12)]
    return idx


def place(name: str) -> Place:
    hits = _gazetteer().get(key(name))
    if not hits:
        close = difflib.get_close_matches(key(name), list(_gazetteer()), n=5, cutoff=0.75)
        raise ValueError(f"place {name!r} not found in the gazetteer (close: {close}); give lon/lat or add it to pipeline/gazetteer.json")
    best = max(hits, key=lambda p: p.rank)
    others = {(h.country or h.kind) for h in hits if h is not best and h.rank > best.rank * 0.2 and h.kind == best.kind}
    if others:
        print(f"  note: place {name!r} is ambiguous, using {best.name} ({best.country or best.kind}); others: {sorted(others)}")
    return best
