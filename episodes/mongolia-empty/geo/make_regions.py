"""Writes the painted-map regions of this episode (venv python -I: shapely, pyproj).

gobi.geojson: Natural Earth "geography regions" polygon GOBI DESERT (a generalised label region, not a surveyed
boundary). Its area inside Mongolia is printed for the fact check.
"""
import json
import sys
from pathlib import Path

import shapely
from pyproj import Transformer
from shapely.geometry import mapping
from shapely.ops import transform

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parents[2] / "pipeline"))
import geo  # noqa: E402

fwd = Transformer.from_crs(4326, 6933, always_xy=True).transform  # equal-area
regions = {p.get("name") or p.get("NAME"): g for p, g in geo.ne_geoms("ne_10m_geography_regions_polys")}
g = shapely.make_valid(regions["GOBI DESERT"].simplify(0.02))
(HERE / "gobi.geojson").write_text(json.dumps({"type": "FeatureCollection", "features": [
    {"type": "Feature", "properties": {"name": "Gobi Desert", "credit": "Natural Earth (public domain)"}, "geometry": mapping(g)}]}), encoding="utf-8")
mn = [gg for p, gg in geo.ne_geoms("ne_10m_admin_0_countries") if (p.get("ADMIN") or p.get("NAME")) == "Mongolia"][0]
print(f"gobi: {transform(fwd, g).area / 1e6:,.0f} km2; inside Mongolia {transform(fwd, g.intersection(mn)).area / 1e6:,.0f} km2; Mongolia {transform(fwd, mn).area / 1e6:,.0f} km2")
