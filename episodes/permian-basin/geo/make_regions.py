"""Writes the painted-map regions of permian-basin (venv python: pyshp, shapely, pyproj).

Source: EIA "Permian Basin: boundary, structure and tectonic features" shapefiles (December 2017), public domain:
https://www.eia.gov/maps/map_data/PermianBasin_Boundary_Structural_Tectonic.zip, unpacked to build/geo/eia_permian/x.
Outputs (lon/lat GeoJSON next to this file): basin_extent, delaware, cbp (Central Basin Platform), midland,
capitan_reef (line). Prints areas and the reef length for the fact check.
"""
import json
import sys
from pathlib import Path

import shapefile
import shapely
from pyproj import Transformer
from shapely.geometry import mapping, shape
from shapely.ops import transform, unary_union

HERE = Path(__file__).parent
SRC = HERE.parents[2] / "build" / "geo" / "eia_permian" / "x"
CREDIT = "EIA, Permian Basin boundary and tectonic features (2017)"
albers = Transformer.from_crs(4326, 5070, always_xy=True).transform


def read(name):
    prj = (SRC / f"{name}.prj").read_text()
    r = shapefile.Reader(str(SRC / name))
    to_ll = Transformer.from_crs(prj, 4326, always_xy=True).transform
    fields = [f[0] for f in r.fields[1:]]
    out = []
    for sr in r.shapeRecords():
        out.append((dict(zip(fields, sr.record)), transform(to_ll, shape(sr.shape.__geo_interface__))))
    return out


def write(fname, label, g, tol=0.005):
    g = shapely.make_valid(g.simplify(tol, preserve_topology=True))
    (HERE / fname).write_text(json.dumps({"type": "FeatureCollection", "features": [
        {"type": "Feature", "properties": {"name": label, "credit": CREDIT}, "geometry": mapping(g)}]}), encoding="utf-8")
    m = transform(albers, g)
    size = f"{m.length / 1609.344:,.0f} mi long" if g.geom_type.endswith("LineString") else f"{m.area / 2.59e6:,.0f} sq mi"
    print(f"{fname}: {label}, {size}, bounds {tuple(round(b, 2) for b in g.bounds)}")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--fields":
        for n in ("Permian_SubBasins_201712", "PermianBasin_Extent_201712", "Capitan_Reef_Trend_201712"):
            for rec, g in read(n):
                print(n, rec, g.geom_type)
        sys.exit()
    ext = unary_union([g for _, g in read("PermianBasin_Extent_201712")])
    write("basin_extent.geojson", "Permian Basin", ext)
    subs = read("Permian_SubBasins_201712")
    for key, fname, label in (("Delaware", "delaware.geojson", "Delaware Basin"), ("Central", "cbp.geojson", "Central Basin Platform"),
                              ("Midland", "midland.geojson", "Midland Basin")):
        gs = [g for rec, g in subs if any(key.lower() in str(v).lower() for v in rec.values())]
        write(fname, label, unary_union(gs))
    reef = unary_union([g for _, g in read("Capitan_Reef_Trend_201712")])
    write("capitan_reef.geojson", "Capitan Reef trend", reef, tol=0.002)
