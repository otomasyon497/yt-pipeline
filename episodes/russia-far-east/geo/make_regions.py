"""Painted regions for russia-far-east (Natural Earth admin-1, public domain).

  python make_regions.py

fefd.geojson       Far Eastern Federal District since Nov 2018 (11 subjects, Rosstat list)
china_ne.geojson   Heilongjiang, Jilin, Liaoning
aigun.geojson      Left bank of the Amur ceded in 1858, APPROXIMATE: Amur Oblast + Jewish AO + Khabarovsk Krai
                   south of 54.5 N (the Uda / Stanovoy line of the 1689 Nerchinsk border); captions say "approx."
primorye.geojson   Ceded in 1860 (Convention of Peking): today's Primorsky Krai
chukotka.geojson   Chukotka west of 180 degrees
"""
import json
import sys
from pathlib import Path

import shapely
from shapely.geometry import box, mapping

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parents[2] / "pipeline"))
import geo  # noqa: E402

ADM = {p.get("name_en"): g for p, g in geo.ne_geoms("ne_10m_admin_1_states_provinces") if p.get("adm0_a3") in ("RUS", "CHN")}
FEFD = ["Republic of Buryatia", "Zabaykalsky Krai", "Amur", "Jewish", "Khabarovsk Krai", "Primorsky Krai", "Magadan",
        "Sakhalin", "Chukotka Autonomous Okrug", "Sakha Republic", "Kamchatka Krai"]


def write(name, geom, label):
    geom = shapely.make_valid(geom).simplify(0.02, preserve_topology=True)
    fc = {"type": "FeatureCollection", "features": [{"type": "Feature", "properties": {"name": label,
          "credit": "Natural Earth (public domain)"}, "geometry": mapping(geom)}]}
    (HERE / f"{name}.geojson").write_text(json.dumps(fc), encoding="utf-8")
    print(name, round(geom.area, 1))


EAST = box(0, -90, 180, 90)  # drop the sliver of Chukotka east of 180 degrees: it would frame the whole world
write("fefd", shapely.union_all([ADM[n] for n in FEFD]).intersection(EAST), "Far Eastern Federal District")
write("chukotka", ADM["Chukotka Autonomous Okrug"].intersection(EAST), "Chukotka")
cn = [k for k in ADM if k in ("Heilongjiang", "Jilin", "Liaoning")]
assert len(cn) == 3, cn
write("china_ne", shapely.union_all([ADM[n] for n in cn]), "China's northeast: three provinces")
khab_s = ADM["Khabarovsk Krai"].intersection(box(120, 40, 145, 54.5))
write("aigun", shapely.union_all([ADM["Amur"], ADM["Jewish"], khab_s]), "Ceded 1858 (approx.)")
write("primorye", ADM["Primorsky Krai"], "Ceded 1860")
