"""Map blocks: consecutive map shots share one continuous camera (rendered by Remotion's `MapBlock`).

build_block() writes remotion/public/media/<block>.json (+ imagery) with everything pre-computed in unit
Mercator coordinates (see geo.py) and frames relative to the block start: camera keyframes, vector layers
per level of detail, highlights, places, routes, arrows, choropleths and true-size outlines.
"""
import calendar
import json
import math
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import requests
from PIL import Image, ImageDraw, ImageFilter
import searoute
import shapely
from shapely import affinity
from shapely.geometry import shape

import bathy
import geo
import gibs
import sentinel
from config import CACHE_DIR, FPS, HEIGHT, LABEL_INSET, MAP_DRIFT, MAP_SAFE, UI_SCALE, WIDTH

Q = 10_000_000  # unit Mercator -> int quantisation (0.07 px at a 1-degree view)
RHO = 1.25  # flight curvature (van Wijk & Nuij); sqrt(2) is d3's default, lower = less zoom-out mid-flight
LODS = [("10m", 25.0), ("50m", 110.0), ("110m", 1e9)]  # Natural Earth scale, widest view span (degrees) it serves
WORLD = {"x": 0.5, "y": 0.45, "w": 1.0}
DEFAULT_SPAN = {"city": 5.0, "capital": 6.0, "port": 4.0, "site": 5.0, "event": 5.0, "sea": 14.0}
SFX_GAIN = {"whoosh": -2.0, "whoosh_long": 0.0, "pop": -6.0, "thump": -4.0, "swoosh": -3.0}
WORLD_BANK = "https://api.worldbank.org/v2/country/all/indicator/{code}?date={year}&format=json&per_page=20000"
WORLD_BANK_CREDIT = "Data: World Bank, World Development Indicators (CC BY 4.0)."
_WORLD_IMAGES: dict[str, dict] = {}
MIN_VISIBLE = 1.6  # seconds an overlay stays up even if the next shot starts sooner
S2_MAX_SPAN = 2.0  # views narrower than this (degrees) get Sentinel-2 10 m imagery; wider mosaics mixed dates into a patchwork
S2_SEA_SPAN = 1.5  # wider than this: Sentinel-2 on land only (sea from Blue Marble, no patchwork of days)  # out_dir -> world image placements already written in this run


# ---------------------------------------------------------------- small geometry helpers

def unit_pt(lon: float, lat: float) -> tuple[float, float]:
    return float(geo.mx(lon)), float(geo.my(lat))


def view_box(v: dict, grow: float = 1.0) -> tuple[float, float, float, float]:
    w = v["w"] * grow
    h = w * HEIGHT / WIDTH
    return v["x"] - w / 2, v["y"] - h / 2, v["x"] + w / 2, v["y"] + h / 2


def unit_box_to_lonlat(b) -> tuple[float, float, float, float]:
    lon0, lat1 = geo.unmerc(max(b[0], 0.0), max(b[1], 0.0))
    lon1, lat0 = geo.unmerc(min(b[2], 1.0), min(b[3], 1.0))
    return lon0, lat0, lon1, lat1


def union_box(boxes):
    boxes = [b for b in boxes if b]
    if not boxes:
        return None
    return min(b[0] for b in boxes), min(b[1] for b in boxes), max(b[2] for b in boxes), max(b[3] for b in boxes)


def fit(bounds, captions: bool, min_span: float = 2.0) -> dict:
    """Camera (x, y, w) that shows unit-Mercator `bounds` inside the safe area (clear of captions)."""
    x0, y0, x1, y1 = bounds
    bottom = MAP_SAFE["bottom"] if captions else MAP_SAFE["top"]
    sw = WIDTH - MAP_SAFE["left"] - MAP_SAFE["right"]
    sh = HEIGHT - MAP_SAFE["top"] - bottom
    w = max((x1 - x0) * WIDTH / sw, (y1 - y0) * WIDTH / sh) * 1.16  # margin: the slow push-in eats ~10 % on long holds
    w = min(max(w, min_span / 360.0), 1.0)
    sx, sy = MAP_SAFE["left"] + sw / 2, MAP_SAFE["top"] + sh / 2
    return {"x": (x0 + x1) / 2 - (sx - WIDTH / 2) * w / WIDTH, "y": (y0 + y1) / 2 - (sy - HEIGHT / 2) * w / WIDTH, "w": w}


def flight_length(a: dict, b: dict) -> float:
    """Length S of the smooth zoom-and-pan path (same formula as remotion/src/map/camera.ts)."""
    dx, dy = b["x"] - a["x"], b["y"] - a["y"]
    w0, w1 = a["w"], b["w"]
    d2 = dx * dx + dy * dy
    if d2 < 1e-18:
        return abs(math.log(w1 / w0)) / RHO
    d1 = math.sqrt(d2)
    b0 = (w1 * w1 - w0 * w0 + RHO ** 4 * d2) / (2 * w0 * RHO ** 2 * d1)
    b1 = (w1 * w1 - w0 * w0 - RHO ** 4 * d2) / (2 * w1 * RHO ** 2 * d1)
    r0 = math.log(math.sqrt(b0 * b0 + 1) - b0)
    r1 = math.log(math.sqrt(b1 * b1 + 1) - b1)
    return abs(r1 - r0) / RHO


def encode(geom) -> list[list[int]]:
    """Rings / lines of a unit-Mercator geometry as flat int lists [x0, y0, x1, y1, ...] (x Q)."""
    out = []
    for g in getattr(geom, "geoms", [geom]):
        if g.is_empty:
            continue
        if g.geom_type == "Polygon":
            rings = [g.exterior, *g.interiors]
        elif g.geom_type == "LineString":
            rings = [g]
        else:
            out += encode(g)
            continue
        for ring in rings:
            a = np.asarray(ring.coords)[:, :2]
            if len(a) >= 2:
                out.append(np.round(a * Q).astype(np.int64).ravel().tolist())
    return out


def prepare_geom(geom_ll, region, w_finest: float, polygons: bool):
    """Clip a lon/lat geometry to a unit box, project, simplify to ~0.4 px at the finest view, drop specks."""
    if region is not None:
        lon0, lat0, lon1, lat1 = unit_box_to_lonlat(region)
        geom_ll = shapely.clip_by_rect(geom_ll, lon0, lat0, lon1, lat1)
    if geom_ll.is_empty:
        return None
    px = w_finest / WIDTH
    g = geo.to_unit(geom_ll).simplify(px * 0.4, preserve_topology=False)
    if polygons:
        parts = [p for p in getattr(g, "geoms", [g]) if p.geom_type == "Polygon" and p.area >= (1.2 * px) ** 2]
        g = shapely.MultiPolygon(parts) if parts else None
    return None if g is None or g.is_empty else g


# ---------------------------------------------------------------- name resolution

FILE_CREDITS: dict[str, str] = {}  # "file:<name>.geojson" -> its "credit" property


def resolve_area(name: str, episode_dir: Path | None = None):
    """('country' | 'admin1' | 'custom', id, lon/lat geom, label, (lon, lat)) or None.

    "file:<name>.geojson" loads your own polygons from episodes/<slug>/geo/ (historical borders, empires);
    the label comes from a "name" property or the file name. "seafloor:<basin>:<metres>" is the bed a lake or
    inland sea would lose if its level fell that far (bathy.py), labelled "-10 METRES".
    """
    if name.startswith("seafloor:"):
        try:
            _, basin, metres = name.split(":")
            drop = float(metres)
        except ValueError:
            raise ValueError(f"{name!r}: use seafloor:<basin>:<metres>, e.g. seafloor:caspian:10") from None
        g = bathy.exposed(basin, drop)
        biggest = max(getattr(g, "geoms", [g]), key=lambda p: p.area)
        pt = biggest.representative_point()
        return "custom", name, g, f"−{drop:g} metres", (pt.x, pt.y)
    if name.startswith("file:"):
        if episode_dir is None:
            raise ValueError(f"{name!r}: custom GeoJSON needs the episode folder")
        path = episode_dir / "geo" / name[5:]
        if not path.exists():
            raise ValueError(f"{name!r}: {path} does not exist")
        data = json.loads(path.read_text(encoding="utf-8"))
        feats = data["features"] if data.get("type") == "FeatureCollection" else [data]
        # Simplified or reprojected polygons (rounded coordinates) can self-touch; repair them before the union, and
        # keep only the polygonal parts make_valid returns.
        parts = []
        for f in feats:
            if f.get("geometry"):
                fixed = shapely.make_valid(shape(f["geometry"]))
                parts += [p for p in getattr(fixed, "geoms", [fixed]) if p.geom_type in ("Polygon", "MultiPolygon")]
        if not parts:
            raise ValueError(f"{name!r}: no polygons in {path}")
        g = shapely.union_all(parts)
        label = next((f.get("properties", {}).get("name") for f in feats if f.get("properties", {}).get("name")), None)
        # A "credit" property (data source and licence) goes into the video's credits when the area is shown.
        credit = next((f.get("properties", {}).get("credit") for f in feats if f.get("properties", {}).get("credit")), None)
        if credit:
            FILE_CREDITS[name] = credit
        pt = g.representative_point()
        return "custom", name, g, label or path.stem.replace("_", " ").title(), (pt.x, pt.y)
    code = geo.country_code(name)
    if code:
        c = geo.country(code)
        return "country", code, geo.country_geom(code, "10m"), c.name, c.label
    hit = geo.admin1(name)
    if hit:
        label, g, pt = hit
        return "admin1", name, g, label, pt if pt[0] is not None else (g.representative_point().x, g.representative_point().y)
    return None


def resolve_point(ref) -> tuple[float, float, str, str]:
    """(lon, lat, label, kind) for a PlaceRef: [lon, lat] or a gazetteer name / country."""
    if not isinstance(ref, str):
        return float(ref[0]), float(ref[1]), "", "site"
    area = resolve_area(ref) if geo.country_code(ref) else None
    if area:
        return area[4][0], area[4][1], area[3], "country"
    p = geo.place(ref)
    return p.lon, p.lat, p.name, p.kind


def lonlat_line_to_unit(coords) -> list[tuple[float, float]]:
    """Project a lon/lat polyline, unwrapping across the antimeridian so the line stays continuous."""
    a = np.asarray(coords, dtype=float)
    lon = np.degrees(np.unwrap(np.radians(a[:, 0])))
    return list(zip(((lon + 180.0) / 360.0).tolist(), geo.my(a[:, 1]).tolist()))


def great_circle(p0, p1, n: int = 72):
    lon0, lat0, lon1, lat1 = map(math.radians, (*p0, *p1))
    v0 = np.array([math.cos(lat0) * math.cos(lon0), math.cos(lat0) * math.sin(lon0), math.sin(lat0)])
    v1 = np.array([math.cos(lat1) * math.cos(lon1), math.cos(lat1) * math.sin(lon1), math.sin(lat1)])
    omega = math.acos(max(-1.0, min(1.0, float(v0 @ v1))))
    if omega < 1e-9:
        return [p0, p1]
    pts = []
    for t in np.linspace(0, 1, n):
        v = (math.sin((1 - t) * omega) * v0 + math.sin(t * omega) * v1) / math.sin(omega)
        pts.append((math.degrees(math.atan2(v[1], v[0])), math.degrees(math.asin(max(-1.0, min(1.0, v[2]))))))
    return pts


LINES = Path(__file__).with_name("lines.json")


def line_credit(path: str) -> str | None:
    """Credit line for a curated polyline whose source is not Natural Earth (lines.json "_credits")."""
    return json.loads(LINES.read_text(encoding="utf-8")).get("_credits", {}).get(path)


def route_coords(route) -> list[tuple[float, float]]:
    if route.path:
        lines = json.loads(LINES.read_text(encoding="utf-8"))
        if route.path not in lines:
            raise ValueError(f"route path {route.path!r} is not in pipeline/lines.json")
        return [tuple(p) for p in lines[route.path]]
    stops = [resolve_point(p)[:2] for p in [route.from_, *route.via, route.to]]
    coords: list[tuple[float, float]] = []
    for a, b in zip(stops, stops[1:]):
        if route.mode == "sea":
            seg = searoute.searoute(a, b, append_orig_dest=True, restrictions=sorted({"northwest", *route.avoid}))
            part = [tuple(c) for c in seg.geometry["coordinates"]]
        elif route.mode == "air":
            part = great_circle(a, b)
        else:
            part = [a, b]
        coords += part if not coords else part[1:]
    return coords


def world_bank(code: str, year: int) -> dict[str, float]:
    cache = CACHE_DIR / "worldbank" / f"{code}_{year}.json"
    if not cache.exists():
        r = requests.get(WORLD_BANK.format(code=code, year=year), timeout=90)
        r.raise_for_status()
        cache.parent.mkdir(parents=True, exist_ok=True)
        cache.write_text(r.text, encoding="utf-8")
    payload = json.loads(cache.read_text(encoding="utf-8"))
    rows = payload[1] if isinstance(payload, list) and len(payload) > 1 and payload[1] else []
    return {r["countryiso3code"]: float(r["value"]) for r in rows if r.get("value") is not None and r.get("countryiso3code")}


# ---------------------------------------------------------------- the block plan

@dataclass
class Element:
    kind: str
    data: dict
    start: int
    end: int = 10 ** 9
    geom: object = None  # lon/lat geometry, built into the JSON at the end (needs the final camera plan)
    sub: int = 0
    bounds: tuple | None = None  # unit-Mercator box the camera keeps in frame while the element is on screen


@dataclass
class Plan:
    style: str
    captions: bool
    frames: int
    cams: list = field(default_factory=list)  # {"start", "frames", "x", "y", "w"}
    elements: list = field(default_factory=list)
    layers: list = field(default_factory=list)  # {"f", "layer"}
    globe: dict | None = None
    events: list = field(default_factory=list)  # (frame, kind, gain_db)
    credits: set = field(default_factory=set)
    warnings: list = field(default_factory=list)
    episode_dir: Path | None = None

    @property
    def view(self):
        return self.cams[-1] if self.cams else None

    def clear(self, at: int, sub: int | None = None, grace: int = 0) -> None:
        """End overlays at frame `at`; with `grace`, anything that appeared less than `grace` frames ago stays a bit longer."""
        for e in self.elements:
            if e.end > at and (sub is None or e.sub == sub):
                e.end = max(at, e.start + grace)

    def move_to(self, target: dict, f: int, *, instant: bool = False) -> int:
        """Add a camera keyframe; returns the frame by which the move is mostly done."""
        cur = self.view
        if cur and abs(math.log(target["w"] / cur["w"])) < 0.05 and math.dist((cur["x"], cur["y"]), (target["x"], target["y"])) < cur["w"] * 0.03:
            return f
        if cur is None or instant:
            self.cams.append({"start": f, "frames": 0, **target})
            return f
        s = flight_length(cur, target)
        seconds = min(max(0.75 + 0.42 * s, 0.9), 2.8)
        start = max(f - round(0.25 * FPS), self.cams[-1]["start"] + 1, 0)
        frames = round(seconds * FPS)
        self.cams.append({"start": start, "frames": frames, **target})
        if s > 0.35:
            self.events.append((start, "whoosh", SFX_GAIN["whoosh"] + min(0.0, (s - 2.0) * 1.5)))
        return start + round(frames * 0.55)


def _inside_safe(bounds, view: dict, captions: bool, slack: float = 0.03) -> bool:
    """True if unit-Mercator `bounds` sit inside the view's safe area (clear of edges and captions)."""
    if bounds is None:
        return True
    k = view["w"] / WIDTH  # unit per pixel
    bottom = MAP_SAFE["bottom"] if captions else MAP_SAFE["top"]
    x0 = view["x"] + (MAP_SAFE["left"] - WIDTH / 2) * k
    x1 = view["x"] + (WIDTH / 2 - MAP_SAFE["right"]) * k
    y0 = view["y"] + (MAP_SAFE["top"] - HEIGHT / 2) * k
    y1 = view["y"] + (HEIGHT / 2 - bottom) * k
    pad = slack * view["w"]
    return bounds[0] >= x0 - pad and bounds[2] <= x1 + pad and bounds[1] >= y0 - pad and bounds[3] <= y1 + pad


def _bounds_of(items) -> tuple | None:
    boxes = []
    for kind, payload in items:
        if kind == "geom":
            boxes.append(geo.to_unit(payload).bounds)
        elif kind == "pt":
            boxes.append((payload[0], payload[1], payload[0], payload[1]))
        elif kind == "line":
            xs, ys = zip(*payload)
            boxes.append((min(xs), min(ys), max(xs), max(ys)))
    return union_box(boxes)


def _span_for(items) -> float:
    """Minimum span when framing: points alone get a sensible zoom instead of an infinite one."""
    kinds = [payload[2] for kind, payload in items if kind == "pt" and len(payload) > 2]
    if any(kind != "pt" for kind, _ in items):
        return 2.0
    return min((DEFAULT_SPAN.get(k, 5.0) for k in kinds), default=5.0)


def _step(plan: Plan, step, f: int, sub: int, sub_end: int, globe: bool, next_f: int | None = None,
          first: bool = False) -> None:
    if step.clear:
        plan.clear(f, sub)

    # Everything this step shows, resolved to geometry (used for auto-framing too).
    frame_items = []
    highlights = []
    for name in step.highlight:
        area = resolve_area(name, plan.episode_dir)
        if area is None:
            raise ValueError(f"map highlight {name!r} is not a country, state/province, file:<name>.geojson or seafloor:<basin>:<m>")
        if name.startswith("seafloor:"):
            plan.credits.add(bathy.CREDIT)
        if name in FILE_CREDITS:
            plan.credits.add(FILE_CREDITS[name])
        highlights.append(area)
        frame_items.append(("geom", geo.main_body(area[2]) if area[0] == "country" else area[2]))
    places = []
    for p in step.places:
        if p.lon is not None:
            lon, lat, label, kind = p.lon, p.lat, p.name, p.kind or "city"
        else:
            lon, lat, label, kind = resolve_point(p.name)
            label = p.name
            kind = p.kind or ("site" if kind == "country" else kind)
        x, y = unit_pt(lon, lat)
        places.append({"label": p.name if p.label is None else p.label, "marker": kind, "x": x, "y": y, "icon": p.icon})
        frame_items.append(("pt", (x, y, kind)))
    routes = []
    for r in step.routes:
        pts = lonlat_line_to_unit(route_coords(r))
        if r.path and (credit := line_credit(r.path)):
            plan.credits.add(credit)
        routes.append((r, pts))
        frame_items.append(("line", pts))
    arrows = []
    for a in step.arrows:
        p0, p1 = resolve_point(a.from_), resolve_point(a.to)
        arrows.append((a, unit_pt(*p0[:2]), unit_pt(*p1[:2])))
        frame_items.append(("line", _arrow_hull(unit_pt(*p0[:2]), unit_pt(*p1[:2]), a.bend)))
    true_size = None
    if step.true_size:
        code = geo.country_code(step.true_size.country)
        if not code:
            raise ValueError(f"true_size country {step.true_size.country!r} not found")
        body = geo.main_body(geo.country_geom(code, "50m"))
        to = resolve_point(step.true_size.to)[:2]
        c = body.centroid
        true_size = (code, body, (c.x, c.y), to)
        moved = affinity.translate(body, to[0] - c.x, to[1] - c.y)
        frame_items += [("geom", body), ("geom", moved)]

    # Camera
    target = None
    if step.view:
        target = {"x": float(geo.mx(step.view.lon)), "y": float(geo.my(step.view.lat)), "w": step.view.span / 360.0}
        if frame_items and not _inside_safe(_bounds_of(frame_items), target, plan.captions, slack=0.0):
            # Content wins over a hand-picked view: every arrow, route, area and marker of this step must show from
            # start to end, so zoom out around them and keep the middle of the requested view.
            target = fit(union_box([_bounds_of(frame_items), view_box(target, 0.4)]), plan.captions, _span_for(frame_items))
    elif step.world:
        target = dict(WORLD)
    elif step.focus:
        items = []
        for ref in step.focus:
            if not isinstance(ref, str):
                items.append(("pt", (*unit_pt(ref[0], ref[1]), "site")))
            elif (code := geo.country_code(ref)) is not None:
                items.append(("geom", geo.main_body(geo.country_geom(code, "10m"))))
            elif (p := _place_or_none(ref)) is not None:
                items.append(("pt", (*unit_pt(p.lon, p.lat), p.kind)))
            elif (area := resolve_area(ref, plan.episode_dir)) is not None:
                items.append(("geom", area[2]))
            else:
                raise ValueError(f"map focus {ref!r} is not a country, place or state/province")
        target = fit(_bounds_of(items), plan.captions, _span_for(items))
    elif plan.view is None:
        target = fit(_bounds_of(frame_items), plan.captions, _span_for(frame_items)) if frame_items else dict(WORLD)
    elif frame_items and not _inside_safe(_bounds_of(frame_items), plan.view, plan.captions):
        # The camera follows the new content and keeps what is on screen right now from earlier steps in frame
        # (overlays that are already out of view, e.g. a city from a world view, do not pull it back out).
        cur = view_box(plan.view)
        still = [e.bounds for e in plan.elements if e.end > f and e.bounds and e.bounds[0] < cur[2] and cur[0] < e.bounds[2]
                 and e.bounds[1] < cur[3] and cur[1] < e.bounds[3]]
        target = fit(union_box([_bounds_of(frame_items), *still]), plan.captions, _span_for(frame_items))

    if target is not None and step.date:
        target["date"] = step.date  # imagery of that day around this view (events)
    appear = f
    if globe and target is not None:
        g_frames = min(max(round(3.4 * FPS), 1), max(sub_end - f - 12, round(2.0 * FPS)))
        lon, lat = geo.unmerc(target["x"], target["y"])
        plan.globe = {"frames": f + g_frames, "toLon": lon, "toLat": lat, "fromLon": lon - 75.0, "fromLat": 18.0}
        plan.move_to(target, f + g_frames, instant=True)
        plan.events.append((f, "whoosh_long", SFX_GAIN["whoosh_long"]))
        appear = f + g_frames - 4
    elif target is not None:
        appear = plan.move_to(target, f)

    if step.compare:  # before/after wipe over the view the camera now holds
        c, cam = step.compare, plan.view
        # On the block's first step the 'before' image is there from frame 0, so the present-day imagery
        # underneath never shows before the wipe. hold: given seconds, else until the shot's next step
        # (the narration cue), else 1.8 s; frames counted from the element's start.
        start = 0 if first else max(0, appear - 8)
        hold = (round(c.hold * FPS) + appear - start if c.hold is not None
                else max(0, next_f - start) if next_f is not None else round(1.8 * FPS) + appear - start)
        plan.elements.append(Element("compare", {
            "cam": {"x": cam["x"], "y": cam["y"], "w": cam["w"]}, "before": c.before, "after": c.after,
            "source": c.source, "labelBefore": c.label_before, "labelAfter": c.label_after,
            "hold": hold, "wipe": round(c.seconds * FPS)}, start, sub=sub))
        plan.events.append((start + hold, "swoosh", SFX_GAIN["swoosh"]))

    # Overlays, staggered so they land one after another.
    k = 0
    for code_kind, code, geom, label, pt in highlights:
        x, y = unit_pt(*pt)
        body = geo.main_body(geom) if code_kind == "country" else geom
        plan.elements.append(Element("highlight", {"id": code, "name": label, "lx": x, "ly": y, "dim": step.dim},
                                     appear + 3 * k, geom=geom, sub=sub, bounds=_bounds_of([("geom", body)])))
        k += 1
    if highlights:
        plan.events.append((appear, "thump", SFX_GAIN["thump"]))
    for i, p in enumerate(places):
        start = appear + 4 + 6 * i
        plan.elements.append(Element("place", p, start, sub=sub, bounds=(p["x"], p["y"], p["x"], p["y"])))
        if p["marker"] not in ("sea", "label"):
            plan.events.append((start, "pop", SFX_GAIN["pop"]))
    for r, pts in routes:
        draw = round(r.seconds * FPS)
        plan.elements.append(Element("route", {"pts": [round(v * Q) for xy in pts for v in xy], "mode": r.mode,
                                               "tint": r.color, "label": r.label, "draw": draw}, appear, sub=sub,
                                     bounds=_bounds_of([("line", pts)])))
        plan.events.append((appear, "swoosh", SFX_GAIN["swoosh"]))
    for a, p0, p1 in arrows:
        plan.elements.append(Element("arrow", {"from": p0, "to": p1, "tint": a.color, "label": a.label, "bend": a.bend,
                                               "draw": round(0.9 * FPS)}, appear, sub=sub,
                                     bounds=_bounds_of([("line", _arrow_hull(p0, p1, a.bend))])))
        plan.events.append((appear, "swoosh", SFX_GAIN["swoosh"] - 2))
    if step.choropleth:
        plan.elements.append(Element("choropleth", {"spec": step.choropleth}, appear, sub=sub))
        plan.events.append((appear, "swoosh", SFX_GAIN["swoosh"] - 1))
        if step.choropleth.world_bank:
            plan.credits.add(WORLD_BANK_CREDIT)
    if true_size:
        code, body, c, to = true_size
        label = step.true_size.label if step.true_size.label is not None else geo.country(code).name
        plan.elements.append(Element("truesize", {"from": c, "to": to, "label": label, "move": round(3.0 * FPS)},
                                     appear + 6, geom=body, sub=sub))
        plan.events.append((appear + 6, "swoosh", SFX_GAIN["swoosh"]))
    if step.layer:
        plan.layers.append({"f": appear, "layer": step.layer})


def _arrow_hull(p0, p1, bend: float) -> list[tuple[float, float]]:
    """Ends plus the bulge of a bent arrow (control point of its curve), for framing."""
    (x0, y0), (x1, y1) = p0, p1
    dx, dy = x1 - x0, y1 - y0
    cx, cy = (x0 + x1) / 2 - dy * bend, (y0 + y1) / 2 + dx * bend
    return [(x0, y0), ((x0 + cx) / 2, (y0 + cy) / 2), ((cx + x1) / 2, (cy + y1) / 2), (x1, y1)]


def _context_labels(plan: Plan, frames: int) -> list[dict]:
    """Quiet names of the countries and big cities around each camera stop, so viewers know where they are.

    Countries: label point inside the view and wide enough on screen for the name; not when the story already labels
    them (highlights). Cities: Natural Earth scale rank by zoom, at most 8 per view, never next to a story marker.
    Placed with the lowest priority: story labels always win the space."""
    out = []
    countries = [(p, g) for p, g in geo.ne_geoms("ne_50m_admin_0_countries")]
    cities = [(p, g) for p, g in geo.ne_geoms("ne_10m_populated_places")]
    cams = plan.cams
    for i, c in enumerate(cams):
        start = c["start"] + round(c["frames"] * 0.7)
        end = cams[i + 1]["start"] + 6 if i + 1 < len(cams) else frames + 1
        if end - start < round(1.2 * FPS):
            continue  # gone before anyone could read it
        span = c["w"] * 360
        k = WIDTH / c["w"]  # px per unit
        x0, y0, x1, y1 = view_box(c, 0.84)
        story = [e for e in plan.elements if e.start < end and e.end > start]
        named = {e.data.get("id") for e in story if e.kind == "highlight"}
        marks = [(e.data["x"], e.data["y"]) for e in story if e.kind == "place"]
        shown = []
        for p, g in countries:
            code = p.get("ADM0_A3")
            if code in named or span > 140 or str(p.get("ISO_N3", "-99")) in ("-99", "-099"):
                continue  # story labels win; only places with an ISO code (not e.g. Somaliland, N. Cyprus)
            lx, ly = float(geo.mx(p.get("LABEL_X", g.centroid.x))), float(geo.my(p.get("LABEL_Y", g.centroid.y)))
            if not (x0 < lx < x1 and y0 < ly < y1):
                continue
            name = p.get("NAME_EN") or p.get("NAME") or ""
            name = name if len(name) <= 16 else (p.get("NAME") or name)
            bx = geo.to_unit(geo.main_body(g)).bounds
            if (bx[2] - bx[0]) * k < len(name) * 15 * UI_SCALE + 40:
                continue  # too small on screen for its name
            shown.append(((bx[2] - bx[0]) * (bx[3] - bx[1]), name, lx, ly))
        for _, name, lx, ly in sorted(shown, reverse=True)[:10 if span > 40 else 8]:  # the biggest on screen
            out.append({"kind": "context", "in": start, "out": end, "text": name, "x": round(lx, 7), "y": round(ly, 7),
                        "level": "country"})
        rank = 1 if span > 25 else 3 if span > 10 else 5 if span > 4 else 6 if span > 1.5 else 8
        if span > 60:
            continue
        picked = []
        for p, g in sorted(cities, key=lambda pg: (pg[0].get("SCALERANK", 10), -(pg[0].get("POP_MAX") or 0))):
            if p.get("SCALERANK", 10) > rank or len(picked) >= 8:
                break
            ux, uy = float(geo.mx(g.x)), float(geo.my(g.y))
            if not (x0 < ux < x1 and y0 < uy < y1):
                continue
            if any(math.hypot((ux - mx_) * k, (uy - my_) * k) < 60 * UI_SCALE for mx_, my_ in marks + picked):
                continue  # a story marker (or another city) is already there
            picked.append((ux, uy))
            out.append({"kind": "context", "in": start, "out": end, "text": p.get("NAME_EN") or p.get("NAME") or "", "x": round(ux, 7),
                        "y": round(uy, 7), "level": "city"})
    return out


def _place_or_none(name: str):
    try:
        return geo.place(name)
    except ValueError:
        return None


# ---------------------------------------------------------------- output

def _lod_for(w: float) -> str:
    span = w * 360.0
    return next(name for name, widest in LODS if span <= widest)


def _active_cams(plan: Plan, start: int, end: int, min_overlap: int = 12) -> list[dict]:
    """Camera keyframes that are on screen for a while during [start, end) (brief overlaps at the edges don't count)."""
    out, best = [], None
    for i, c in enumerate(plan.cams):
        nxt = plan.cams[i + 1]["start"] if i + 1 < len(plan.cams) else 10 ** 9
        overlap = min(end, nxt) - max(start, c["start"])
        if overlap >= min(min_overlap, end - start):
            out.append(c)
        if overlap > 0 and (best is None or overlap > best[0]):
            best = (overlap, c)
    return out or ([best[1]] if best else plan.cams[:1])


def land_mask(box, size, lakes: bool = True) -> Image.Image:
    """Natural Earth land rasterised over a unit-Mercator box, minus its lakes unless lakes=False: relief shading
    stays on land. Sentinel-2 keeps the lakes (lakes=False): Natural Earth draws reservoirs at full pool, and a
    shrunken lake is often the point of the view (Lake Powell at 1.6 degrees showed Blue Marble's 2004 lake inside
    the full-pool outline)."""
    w, h = size
    img = Image.new("L", (w, h), 0)
    draw = ImageDraw.Draw(img)
    lon0, lat0, lon1, lat1 = unit_box_to_lonlat(box)
    sx, sy = w / (box[2] - box[0]), h / (box[3] - box[1])

    def pix(ring):
        a = np.asarray(ring.coords)[:, :2]
        return list(zip(((geo.mx(a[:, 0]) - box[0]) * sx).tolist(), ((geo.my(a[:, 1]) - box[1]) * sy).tolist()))

    for layer, value in (("ne_10m_land", 255), ("ne_10m_lakes", 0))[:2 if lakes else 1]:
        for _, g in geo.ne_geoms(layer):
            b = g.bounds
            if b[2] < lon0 or b[0] > lon1 or b[3] < lat0 or b[1] > lat1:
                continue
            clipped = shapely.clip_by_rect(g, lon0 - 0.5, lat0 - 0.5, lon1 + 0.5, lat1 + 0.5)
            for poly in getattr(clipped, "geoms", [clipped]):
                if poly.geom_type != "Polygon" or poly.is_empty:
                    continue
                draw.polygon(pix(poly.exterior), fill=value)
                for hole in poly.interiors:
                    draw.polygon(pix(hole), fill=255 - value)
    return img.filter(ImageFilter.GaussianBlur(1.2))


def _night_cams(plan: Plan) -> list[dict]:
    """Keyframes on screen while the night layer is (becoming) visible."""
    out = []
    changes = sorted(plan.layers, key=lambda l: l["f"])
    for k, l in enumerate(changes):
        if l["layer"] != "night":
            continue
        end = changes[k + 1]["f"] if k + 1 < len(changes) else 10 ** 9
        out += [c for c in _active_cams(plan, l["f"] - 24, end, 1) if c not in out]
    return out


def _region(cams: list[dict]):
    return union_box([view_box(c, 2.2) for c in cams])


def _layers_for(lod: str, region, w_finest: float, vector: bool) -> dict:
    out = {}
    specs = [("borders", f"ne_{lod}_admin_0_boundary_lines_land", False)]
    if vector:
        specs = [("land", f"ne_{lod}_land", True), ("lakes", f"ne_{lod}_lakes", True),
                 ("rivers", f"ne_{lod}_rivers_lake_centerlines", False), ("coast", f"ne_{lod}_coastline", False)] + specs
    lon0, lat0, lon1, lat1 = unit_box_to_lonlat(region)
    for name, layer, polys in specs:
        parts = []
        for p, g in geo.ne_geoms(layer):
            if name == "rivers" and lod == "10m" and (p.get("scalerank") or 0) > 7:
                continue  # only the larger rivers at this scale
            bx = g.bounds
            if bx[2] < lon0 or bx[0] > lon1 or bx[3] < lat0 or bx[1] > lat1:
                continue
            parts += [q for q in getattr(g, "geoms", [g]) if q.geom_type == ("Polygon" if polys else "LineString")]
        merged = (shapely.MultiPolygon(parts) if polys else shapely.MultiLineString(parts)) if parts else None
        g = prepare_geom(merged, region, w_finest, polys) if merged is not None else None
        out[name] = encode(g) if g is not None else []
    return out


def _choropleth(spec, cams: list[dict]) -> dict:
    w = min(c["w"] for c in cams)
    lod = "110m" if w * 360 > 160 else "50m" if w * 360 > 30 else "10m"
    region = _region(cams)
    values: dict[str, float] = {}
    if spec.world_bank:
        wb = world_bank(spec.world_bank, spec.year)
        for code in geo.country_geoms("10m"):
            c = geo.country(code)
            v = wb.get(c.wb3, wb.get(c.iso3))
            if v is not None:
                values[code] = v
    for name, v in spec.values.items():
        code = geo.country_code(name)
        if not code:
            raise ValueError(f"choropleth value for unknown country {name!r}")
        values[code] = v
    if not values:
        raise ValueError(f"choropleth {spec.title!r} has no data")
    vals = np.array(list(values.values()), dtype=float)
    if spec.scale == "log":
        vals = vals[vals > 0]
    lo, hi = float(vals.min()), float(vals.max())

    def t_of(v: float) -> float:
        if spec.scale == "log":
            return 0.0 if v <= 0 else (math.log(v) - math.log(lo)) / max(1e-9, math.log(hi) - math.log(lo))
        return (v - lo) / max(1e-12, hi - lo)

    items = []
    for code, g in geo.country_geoms(lod).items():
        pg = prepare_geom(g, region, w, True)
        if pg is None:
            continue
        v = values.get(code)
        items.append({"t": None if v is None else round(min(max(t_of(v), 0.0), 1.0), 4), "rings": encode(pg)})
    return {"title": spec.title, "unit": spec.unit, "source": spec.source, "min": lo, "max": hi, "scale": spec.scale, "items": items}


def build_block(block_id: str, subs: list[dict], style: str, captions: bool, frames: int, out_dir: Path,
                episode_dir: Path | None = None) -> dict:
    """subs: [{"shot": Shot, "startFrame": block-relative int, "frames": int, "steps": [block-relative step frame]}].

    Returns {"file", "events": [(block frame, kind, gain_db)], "credits": set, "warnings": list}.
    """
    plan = Plan(style, captions, frames, episode_dir=episode_dir)
    for si, sub in enumerate(subs):
        spec = sub["shot"].map
        if si > 0 and not spec.keep:
            plan.clear(sub["startFrame"], grace=round(MIN_VISIBLE * FPS))
        sub_end = sub["startFrame"] + sub["frames"]
        for j, (step, f) in enumerate(zip(spec.steps, sub["steps"])):
            nxt = sub["steps"][j + 1] if j + 1 < len(sub["steps"]) else None
            _step(plan, step, f, si, sub_end, globe=(si == 0 and j == 0 and spec.globe), next_f=nxt, first=(si == 0 and j == 0))
    if not plan.cams:
        plan.move_to(dict(WORLD), 0, instant=True)

    vector = style != "satellite"
    # Levels of detail: every keyframe asks for the scale that suits its zoom, around its view.
    lods = []
    by_lod: dict[str, list[dict]] = {}
    for c in plan.cams:
        by_lod.setdefault(_lod_for(c["w"]), []).append(c)
    for lod, max_span in LODS:
        cams = by_lod.get(lod, [])
        if lod == "110m":
            region, w_finest = (0.0, 0.0, 1.0, 1.0), min([c["w"] for c in cams] + [1.0])
        elif cams:
            region, w_finest = _region(cams), min(c["w"] for c in cams)
        else:
            continue
        lods.append({"lod": lod, "maxSpan": max_span, "box": region, **_layers_for(lod, region, w_finest, vector)})

    out_elements = []
    for e in plan.elements:
        e.end = min(e.end, frames + 1)
        if e.end <= e.start:
            continue
        item = {"kind": e.kind, "in": e.start, "out": e.end, **{k: v for k, v in e.data.items() if k != "spec"}}
        cams = _active_cams(plan, e.start, e.end)
        if e.kind == "highlight":
            body = geo.main_body(e.geom) if e.geom.geom_type == "MultiPolygon" else e.geom
            item["bb"] = [round(v, 7) for v in geo.to_unit(body).bounds]
            w = min(c["w"] for c in cams)
            lod = _lod_for(w)
            g = prepare_geom(geo.country_geom(e.data["id"], lod) if geo.country_code(e.data["id"]) else e.geom,
                             _region(cams), w, True)
            item["rings"] = encode(g) if g is not None else []
        elif e.kind == "choropleth":
            item.update(_choropleth(e.data["spec"], cams))
        elif e.kind == "truesize":
            simple = e.geom.simplify(0.05)
            item["rings"] = [np.round(np.asarray(r.coords)[:, :2], 3).ravel().tolist()
                             for p in getattr(simple, "geoms", [simple]) for r in [p.exterior]]
        elif e.kind == "compare":
            if not _compare_images(item, block_id, len(out_elements), out_dir, plan):
                continue
        out_elements.append(item)

    out_elements += _context_labels(plan, frames)

    # Imagery: a world image under everything, plus a sharper one around each distinct camera view.
    raster_layer = "day" if style == "satellite" else "relief"
    rasters: list[dict] = []
    world_cache = _WORLD_IMAGES.setdefault(str(out_dir), {})

    def add(layer: str, bx, px: int, feather: bool, name: str) -> dict | None:
        try:
            r = gibs.backdrop(layer, bx, px, out_dir / name, feather, land_mask if layer == "relief" else None)
        except Exception as exc:  # imagery is decoration: a failed fetch must not stop the render
            plan.warnings.append(f"GIBS {layer} image failed ({exc}); map continues without it")
            return None
        if r:
            rasters.append(r)
        return r

    layers_used = [raster_layer] + (["night"] if any(l["layer"] == "night" for l in plan.layers) else [])
    for layer in layers_used:
        world_name = f"world_{layer}.webp"
        if layer == "relief":
            pass  # relief only around close views: at world scale ASTER is blocky near the poles and adds little
        elif world_cache.get(world_name):
            rasters.append(world_cache[world_name])
        else:
            world_cache[world_name] = add(layer, (0.0, 0.0, 1.0, 1.0), 4096, False, world_name)
        done: list[dict] = []
        for c in (plan.cams if layer != "night" else _night_cams(plan)):
            if c["w"] > 0.45:  # the world image is sharp enough for continent-sized views
                continue
            bx = view_box(c, 1.6)
            need = 1.6 * WIDTH * 1.1 / (bx[2] - bx[0])  # wanted pixels per unit width
            if any(d["x0"] <= bx[0] and d["y0"] <= bx[1] and d["x1"] >= bx[2] and d["y1"] >= bx[3]
                   and d["px"] / (d["x1"] - d["x0"]) >= min(need, gibs.LAYERS[layer][3]) * 0.75 for d in done):
                continue
            r = add(layer, bx, round(need * (bx[2] - bx[0])), True, f"{block_id}_{len(rasters) + 1}_{layer}.webp")
            if r:
                done.append(r)
    if style == "satellite":
        # A single-day date on a wide view: that day's MODIS image over Blue Marble (whose coasts date from 2004),
        # e.g. a shrinking sea's present shoreline. Windows and close views stay with Sentinel-2 below.
        done_modis: list[tuple] = []
        for c in plan.cams:
            day = c.get("date")
            if not day or "/" in day or c["w"] * 360 <= S2_MAX_SPAN:
                continue
            bx = view_box(c, 1.6)
            if any(d == day and b[0] <= bx[0] and b[1] <= bx[1] and b[2] >= bx[2] and b[3] >= bx[3] for b, d in done_modis):
                continue
            try:
                r = gibs.backdrop("modis", bx, round(1.6 * WIDTH * 1.1), out_dir / f"{block_id}_{len(rasters) + 1}_modis.webp",
                                  True, None, when=day)
            except Exception as exc:  # imagery is decoration: Blue Marble stays
                plan.warnings.append(f"MODIS image for {day} failed ({exc}); Blue Marble only for this view")
                continue
            if r:
                rasters.append(r)
                done_modis.append((bx, day))
                plan.credits.add(gibs.MODIS_CREDIT)
        done_s2: list[tuple] = []
        for c in plan.cams:
            span = c["w"] * 360
            if span > S2_MAX_SPAN:
                continue
            bx = view_box(c, 1.5)
            key = (round(bx[0], 5), round(bx[1], 5), c.get("date"))
            if key in done_s2:
                continue
            done_s2.append(key)
            try:
                r = sentinel.mosaic(bx, round(1.5 * WIDTH), out_dir / f"{block_id}_{len(rasters) + 1}_s2.webp", c.get("date"),
                                    gibs._feather,
                                    (lambda b, s: land_mask(b, s, lakes=False)) if span > S2_SEA_SPAN else None)
            except Exception as exc:  # imagery is decoration: fall back to Blue Marble
                plan.warnings.append(f"Sentinel-2 image failed ({exc}); Blue Marble only for this view")
                continue
            if r:
                _note_mixed_days(r, f"{block_id} view ({span:.2f} degrees, {c.get('date') or 'recent'})", plan)
                rasters.append(r)
    plan.credits.add(gibs.CREDIT)  # the Sentinel-2 line is added once by run.py, with the years of every block

    globe = None
    if plan.globe:
        globe = dict(plan.globe)
        globe["texture"] = None
        if style == "satellite":
            try:
                globe["texture"] = gibs.globe_texture("day", out_dir / "globe_day.jpg")
            except Exception as exc:
                plan.warnings.append(f"globe texture failed ({exc}); vector globe instead")
        globe["land"] = encode_lonlat_land()

    safe_bottom = MAP_SAFE["bottom"] if captions else MAP_SAFE["top"]
    data = {
        "style": style, "frames": frames, "fps": FPS, "drift": MAP_DRIFT, "rho": RHO, "q": Q,
        "safeBottom": safe_bottom,
        # screen box map labels must stay inside (clear of captions, and in a Short of the hook line and YouTube's buttons)
        "labelBox": [LABEL_INSET["left"], LABEL_INSET["top"], WIDTH - LABEL_INSET["right"],
                     HEIGHT - LABEL_INSET.get("bottom", safe_bottom - 40)],
        "cams": plan.cams, "globe": globe, "layers": plan.layers, "rasters": rasters, "lods": lods,
        "elements": out_elements,
    }
    out = out_dir / f"{block_id}.json"
    out.write_text(json.dumps(data, separators=(",", ":")), encoding="utf-8")
    print(f"  {block_id}: {len(plan.cams)} camera moves, {len(out_elements)} overlays, {len(rasters)} images, "
          f"{out.stat().st_size / 1e6:.2f} MB json, lods {[l['lod'] for l in lods]}")
    return {"file": out.name, "events": plan.events, "credits": plan.credits, "warnings": plan.warnings}


def _note_mixed_days(r: dict, what: str, plan: Plan) -> None:
    """Flag a Sentinel-2 image stitched from several days: tiles of different days can meet in a straight seam
    (tides, wet ground, snow). The storyboard review then knows where to look."""
    dates = r.get("dates", [])
    if len(dates) > 1:
        plan.warnings.append(f"{what}: Sentinel-2 scenes of {len(dates)} days ({', '.join(dates)}); check for a seam, "
                             f"or give the view a one-day window 'YYYY-MM-DD/YYYY-MM-DD'")


def _month_label(dates: list[str]) -> str:
    """'MARCH 2020' for the month most of the scenes come from."""
    if not dates:
        return ""
    months = [d[:7] for d in dates]
    y, m = max(set(months), key=months.count).split("-")
    return f"{calendar.month_name[int(m)].upper()} {y}"


def _compare_images(item: dict, block_id: str, n: int, out_dir: Path, plan: Plan) -> bool:
    """Fetch the before/after images of a compare element (same box; Sentinel-2 mosaics share one tone curve)."""
    bx = view_box(item.pop("cam"), 1.5)
    source = item.pop("source", "sentinel-2")
    for side, label in (("before", "labelBefore"), ("after", "labelAfter")):
        out = out_dir / f"{block_id}_cmp{n}_{side}.webp"
        try:
            if source == "modis":
                r = gibs.backdrop("modis", bx, round(1.5 * WIDTH), out, True, None, when=item[side])
                if r:
                    r["dates"] = [item[side]]
                    plan.credits.add(gibs.MODIS_CREDIT)
            else:
                r = sentinel.mosaic(bx, round(1.5 * WIDTH), out, item[side], gibs._feather, None)
                if r:
                    _note_mixed_days(r, f"{block_id} compare {side} ({item[side]})", plan)
        except Exception as exc:
            r = None
            plan.warnings.append(f"compare {side} image failed ({exc})")
        if r is None:
            plan.warnings.append(f"compare: no usable {source} image for {item[side]}; wipe dropped")
            return False
        item[label] = item[label] or _month_label(r.pop("dates", []))
        item[side] = r
    return True


def encode_lonlat_land() -> list[list[float]]:
    """110m land outlines in lon/lat (the spinning globe re-projects them every frame)."""
    rings = []
    for _, g in geo.ne_geoms("ne_110m_land"):
        for p in getattr(g, "geoms", [g]):
            rings.append(np.round(np.asarray(p.exterior.coords)[:, :2], 2).ravel().tolist())
    return rings
