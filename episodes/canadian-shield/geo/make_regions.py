"""Writes the painted-map regions of this episode (venv python: shapely, pyproj, pyshp).

Source: Ecological Framework of Canada (AAFC / CanSIS, open licence), ecozones (ecozone_shp.zip) and ecoregions
(ecoregion_shp.zip) from https://sis.agr.gc.ca/cansis/nsdb/ecostrat/ , downloaded 2026-11-24 into a scratch folder.
  shield.geojson     Boreal Shield + Taiga Shield ecozones ("The Canadian Shield"); written by measure_population.py
  mixedwood.geojson  Mixedwood Plain ecozone ("Great Lakes-St Lawrence lowlands")
  prairie.geojson    Prairie ecozone ("The Prairies")
  claybelt.geojson   Abitibi Plains ecoregion (96), the core of the Great Clay Belt (approx.)
  hudsonbay_low.geojson  Hudson Plain ecozone ("Hudson Bay Lowlands")
Run: venv python -I geo/make_regions.py <ecozones.shp> <ecoregions.shp>
"""
import json, sys
from pathlib import Path
import numpy as np, shapefile, shapely
from shapely.geometry import shape, mapping
from shapely.ops import unary_union
from pyproj import Transformer

HERE = Path(__file__).parent
CREDIT = "Ecological Framework of Canada (AAFC)"
aea = Transformer.from_crs(4326, 3978, always_xy=True)


def area(g):
    return shapely.transform(g, lambda xy: np.column_stack(aea.transform(xy[:, 0], xy[:, 1]))).area / 1e6


def load(path, field):
    out = {}
    for sr in shapefile.Reader(path, encoding="latin-1").shapeRecords():
        out.setdefault(sr.record[field], []).append(shape(sr.shape.__geo_interface__).buffer(0))
    return {k: unary_union(v) for k, v in out.items()}


def write(name, label, g, tol=0.03):
    g = shapely.make_valid(g.simplify(tol))
    (HERE / name).write_text(json.dumps({"type": "FeatureCollection", "features": [
        {"type": "Feature", "properties": {"name": label, "credit": CREDIT}, "geometry": mapping(g)}]}), encoding="utf-8")
    print(f"{name}: {area(g):,.0f} km2")


zones = {k.strip(): v for k, v in load(sys.argv[1], "ZONE_NAME").items()}
regions = load(sys.argv[2], "ECOREGION")
write("mixedwood.geojson", "Great Lakes-St Lawrence lowlands", zones["MixedWood Plain"])
write("prairie.geojson", "The Prairies", zones["Prairie"])
write("hudsonbay_low.geojson", "Hudson Bay Lowlands", zones["Hudson Plain"])
write("claybelt.geojson", "The Great Clay Belt (approx.)", regions[96], tol=0.01)

# hudsonbay.geojson: Natural Earth marine polygon "Hudson Bay" (public domain), added after the storyboard refused the name
sys.path.insert(0, str(HERE.parents[2] / "pipeline"))
import geo  # noqa: E402
hb = unary_union([g for pp, g in geo.ne_geoms("ne_10m_geography_marine_polys") if (pp.get("name") or pp.get("NAME")) == "Hudson Bay"])
(HERE / "hudsonbay.geojson").write_text(json.dumps({"type": "FeatureCollection", "features": [
    {"type": "Feature", "properties": {"name": "Hudson Bay", "credit": "Natural Earth"}, "geometry": mapping(shapely.make_valid(hb.simplify(0.03)))}]}), encoding="utf-8")
print(f"hudsonbay.geojson: {area(hb):,.0f} km2")
