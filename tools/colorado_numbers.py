"""Reproduce the colorado-river episode's own numbers from Reclamation's public daily data (stdlib only).

Usage: python tools/colorado_numbers.py [CACHE_DIR]
Downloads (or reuses) the daily CSVs for Lake Powell (919) and Lake Mead (921) from
https://www.usbr.gov/uc/water/hydrodata/reservoir_data/<id>/csv/<parameter>.csv
(49 = pool elevation ft, 17 = storage acre-feet, 89 = surface area acres, 42 = total release cfs) and prints:
record lows, combined storage since 2000, Lake Powell's surface area, water-year releases from Glen Canyon Dam and the
ten-year total that the Compact's Lee Ferry test counts. The evaporation figures come from Reclamation's October 2026
24-Month Study (a PDF table), so they are constants here.
"""
import csv
import sys
import urllib.request
from datetime import date
from pathlib import Path

BASE = "https://www.usbr.gov/uc/water/hydrodata/reservoir_data/{id}/csv/{p}.csv"
POWELL, MEAD = 919, 921
CFS_DAY_AF = 1.98347  # one cubic foot per second for a day, in acre-feet
ACRE_KM2 = 0.0040468564224
AF_M3 = 1233.48184
# Reclamation, October 2026 Most Probable 24-Month Study (6 maf scenario), water year 2026 evaporation losses.
EVAP_WY2026_AF = {"Lake Mead": 457_000, "Lake Powell": 181_000}
CUTS_2027_AF = {"Arizona": 760_000, "California": 440_000, "Nevada": 50_000}  # Interior, 21 Aug 2026
NEVADA_ALLOCATION_AF = 300_000


def series(cache: Path, rid: int, p: int) -> dict[date, float]:
    path = cache / f"r{rid}_{p}.csv"
    if not path.exists():
        cache.mkdir(parents=True, exist_ok=True)
        req = urllib.request.Request(BASE.format(id=rid, p=p), headers={"User-Agent": "yt-pipeline"})
        path.write_bytes(urllib.request.urlopen(req, timeout=120).read())
    out = {}
    with open(path, newline="") as f:
        rows = csv.reader(f)
        next(rows)
        for row in rows:
            try:
                out[date.fromisoformat(row[0])] = float(row[1])
            except (ValueError, IndexError):
                pass
    return out


def lowest(s: dict[date, float], start: date, end: date | None = None) -> tuple[float, date]:
    return min((v, d) for d, v in s.items() if d >= start and (end is None or d < end))


def water_year_af(cfs: dict[date, float], wy: int) -> float:
    return sum(v for d, v in cfs.items() if (d.year == wy and d.month < 10) or (d.year == wy - 1 and d.month >= 10)) * CFS_DAY_AF


def main(cache: Path) -> None:
    pe, ps, pa, pr = (series(cache, POWELL, p) for p in (49, 17, 89, 42))
    me, ms = (series(cache, MEAD, p) for p in (49, 17))
    last = max(pe)
    print(f"Data through {last}: Powell {pe[last]:.2f} ft, Mead {me[max(me)]:.2f} ft\n")

    print("1. Record lows")
    for name, s, start in (("Lake Powell", pe, date(1980, 1, 1)), ("Lake Mead", me, date(1938, 1, 1))):
        v, d = lowest(s, start)
        v0, d0 = lowest(s, start, date(2026, 1, 1))
        print(f"   {name}: {v:,.2f} ft on {d} (before 2026: {v0:,.2f} ft on {d0})")

    print("\n2. Combined storage (Powell + Mead)")
    comb = {d: ps[d] + ms[d] for d in set(ps) & set(ms)}
    start = date(2000, 1, 1)
    low, low_d = lowest(comb, date(1966, 1, 1))
    peak, peak_d = max((v, d) for d, v in comb.items())
    lost = comb[start] - low
    print(f"   {start}: {comb[start] / 1e6:.2f} MAF; low {low / 1e6:.2f} MAF on {low_d}; peak {peak / 1e6:.2f} MAF on {peak_d}")
    print(f"   lost {lost / 1e6:.1f} MAF = {lost / comb[start]:.0%} (about {lost * AF_M3 / 1e9:.1f} km3); low = {low / peak:.0%} of the peak")

    print("\n3. Lake Powell's surface (Reclamation area series)")
    a0, a1 = pa[start], pa[low_d] if low_d in pa else pa[max(d for d in pa if d <= low_d)]
    print(f"   {start}: {a0:,.0f} acres ({a0 * ACRE_KM2:,.0f} km2); {low_d}: {a1:,.0f} acres ({a1 * ACRE_KM2:,.0f} km2): "
          f"{1 - a1 / a0:.0%} smaller")

    print("\n4. Glen Canyon Dam releases by water year (Oct-Sep)")
    wy = {y: water_year_af(pr, y) for y in range(1966, last.year + (1 if last.month >= 10 else 0))}
    for y in range(2017, max(wy) + 1):
        print(f"   WY {y}: {wy[y] / 1e6:.2f} MAF")
    smallest = min(wy, key=wy.get)
    print(f"   smallest since 1966: WY {smallest} ({wy[smallest] / 1e6:.2f} MAF)")
    ten = sum(wy[y] for y in range(max(wy) - 9, max(wy) + 1))
    print(f"   ten years WY {max(wy) - 9}-{max(wy)}: {ten / 1e6:.1f} MAF (Upper Basin reading 75, Lower Basin reading 82.5)")

    print("\n5. Evaporation vs the 2027 cuts (Reclamation 24-Month Study, October 2026)")
    evap = sum(EVAP_WY2026_AF.values())
    print(f"   WY 2026 evaporation, Mead + Powell: {evap:,} AF = {evap / CUTS_2027_AF['Arizona']:.0%} of Arizona's cut, "
          f"{evap / sum(CUTS_2027_AF.values()):.0%} of the Lower Basin cut, {evap / NEVADA_ALLOCATION_AF:.1f} x Nevada's allocation")


if __name__ == "__main__":
    main(Path(sys.argv[1]) if len(sys.argv) > 1 else Path.home() / ".cache" / "yt-pipeline" / "usbr")
