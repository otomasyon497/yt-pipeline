"""script.json (v2) validation: chapters -> paragraphs (continuous narration) -> shots (visuals anchored to words)."""
import json
import re
from datetime import date
from pathlib import Path
from typing import Literal, Optional, Union

from pydantic import BaseModel, ConfigDict, Field, model_validator

ShotType = Literal["stock", "ai_image", "photo", "chart", "map", "title_card", "quote"]
Mood = Literal["calm", "curious", "tension"]


def words_of(text: str) -> list[str]:
    """Tokenisation shared by anchors, captions and alignment: whitespace-separated words."""
    return text.split()


def norm(word: str) -> str:
    return re.sub(r"[^\w]", "", word.lower())


class Chart(BaseModel):
    type: Literal["bar", "line"] = "bar"
    title: Optional[str] = None
    unit: str = ""
    data: list[tuple[str, float]] = Field(min_length=1, max_length=10)
    source: Optional[str] = None  # shown at the bottom, e.g. "World Bank; our calculation"
    ref: Optional[tuple[float, str]] = None  # reference line: (value, label), e.g. (500, "absolute scarcity")
    highlight: Optional[int] = None  # bar / point index drawn in the accent colour (bars: default the first)


class MapPoint(BaseModel):  # v2 shorthand, still accepted
    label: str
    lon: float
    lat: float


# A place is a gazetteer name ("Cairo", "Strait of Hormuz", "Suez, Egypt") or [lon, lat].
PlaceRef = Union[str, tuple[float, float]]
SeaPassage = Literal["babalmandab", "bosporus", "gibraltar", "suez", "panama", "ormuz", "northwest", "malacca",
                     "sunda", "chili", "south_africa"]
Tint = Literal["accent", "alt", "red", "blue", "neutral"]


class Place(BaseModel):
    name: str  # gazetteer lookup key and default label
    lon: Optional[float] = None
    lat: Optional[float] = None
    label: Optional[str] = None  # None -> name, "" -> marker only
    kind: Optional[Literal["city", "capital", "port", "site", "event", "sea", "label"]] = None  # default from the gazetteer; label = text only

    @model_validator(mode="after")
    def _coords(self):
        if (self.lon is None) != (self.lat is None):
            raise ValueError(f"place {self.name!r}: give both lon and lat or neither")
        return self


class Route(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    from_: Optional[PlaceRef] = Field(None, alias="from")
    to: Optional[PlaceRef] = None
    path: Optional[str] = None  # a curated line from pipeline/lines.json instead of from/to (e.g. "Suez Canal")
    via: list[PlaceRef] = Field(default_factory=list)
    mode: Literal["sea", "air", "line"] = "sea"  # sea: shipping lanes; air: great circle; line: straight segments
    avoid: list[SeaPassage] = Field(default_factory=list)  # sea passages the route must not use
    label: Optional[str] = None
    color: Tint = "accent"
    seconds: float = Field(3.0, gt=0.3, le=15)  # time to draw the line

    @model_validator(mode="after")
    def _ends(self):
        if self.path is None and (self.from_ is None or self.to is None):
            raise ValueError("route needs 'from' and 'to' (or a curated 'path')")
        return self


class Arrow(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    from_: PlaceRef = Field(alias="from")
    to: PlaceRef
    color: Tint = "red"
    label: Optional[str] = None
    bend: float = Field(0.2, ge=-0.6, le=0.6)  # curvature, sign picks the side


class Choropleth(BaseModel):
    title: str
    unit: str = ""
    values: dict[str, float] = Field(default_factory=dict)  # country -> value (fact-checked, inline)
    world_bank: Optional[str] = None  # World Bank indicator code, e.g. "NY.GDP.PCAP.CD" (CC BY 4.0)
    year: Optional[int] = None
    source: Optional[str] = None  # shown under the legend
    scale: Literal["linear", "log"] = "linear"

    @model_validator(mode="after")
    def _data(self):
        if not self.values and not self.world_bank:
            raise ValueError("choropleth needs inline 'values' or a 'world_bank' indicator")
        if self.world_bank and not self.year:
            raise ValueError("choropleth with 'world_bank' needs a 'year'")
        return self


class TrueSize(BaseModel):
    country: str
    to: PlaceRef  # where the outline is dragged (its centre ends here)
    label: Optional[str] = None


class View(BaseModel):
    lon: float
    lat: float
    span: float = Field(gt=0.03, le=360)  # degrees of longitude across the frame (Sentinel-2 holds up to ~0.05)


class Compare(BaseModel):
    """Sentinel-2 before/after of the step's view: a wipe line reveals the 'after' image over the 'before' one."""
    before: str  # "YYYY-MM-DD/YYYY-MM-DD": least cloudy scenes in that window (or one "YYYY-MM-DD" day)
    after: str
    label_before: Optional[str] = None  # default: month and year of the scenes used, e.g. "MARCH 2020"
    label_after: Optional[str] = None
    hold: float = Field(1.8, ge=0, le=8)  # seconds on the 'before' image before the wipe starts
    seconds: float = Field(3.6, gt=0.5, le=10)  # wipe duration

    @model_validator(mode="after")
    def _dates(self):
        for d in (self.before, self.after):
            parts = d.split("/")
            if len(parts) > 2:
                raise ValueError(f"compare date {d!r}: use YYYY-MM-DD or YYYY-MM-DD/YYYY-MM-DD")
            for part in parts:
                date.fromisoformat(part)
        return self


class MapStep(BaseModel):
    at: Optional[Union[int, str]] = None  # word index / phrase in the paragraph; None = when the shot starts
    focus: list[PlaceRef] = Field(default_factory=list)  # countries / places / regions to frame
    view: Optional[View] = None
    world: bool = False  # frame the whole world
    highlight: list[str] = Field(default_factory=list)  # countries, states/provinces, or "file:x.geojson" (episode geo/)
    dim: bool = False  # darken everything that is not highlighted
    places: list[Place] = Field(default_factory=list)
    routes: list[Route] = Field(default_factory=list)
    arrows: list[Arrow] = Field(default_factory=list)
    choropleth: Optional[Choropleth] = None
    true_size: Optional[TrueSize] = None
    layer: Optional[Literal["day", "night"]] = None  # night = VIIRS city lights
    date: Optional[str] = None  # "YYYY-MM-DD": Sentinel-2 imagery of that day for this view (real events)
    compare: Optional[Compare] = None  # Sentinel-2 before/after wipe over this view
    clear: bool = False  # remove everything shown earlier in this shot first

    @model_validator(mode="after")
    def _camera(self):
        if sum([bool(self.focus), self.view is not None, self.world]) > 1:
            raise ValueError("a map step takes only one of focus / view / world")
        if self.compare and not self.view:
            raise ValueError("map step 'compare' needs a 'view' (the before/after imagery is fetched for it)")
        if self.date:
            if not (self.focus or self.view):
                raise ValueError("map step 'date' needs a focus or view (the imagery is fetched for that view)")
            date.fromisoformat(self.date)
        return self


class MapSpec(BaseModel):
    globe: bool = False  # open on a spinning globe that dives into the first view
    keep: bool = False  # keep the previous map shot's overlays instead of clearing them
    steps: list[MapStep] = Field(default_factory=list)
    # v2 shorthand (one step): countries to highlight + labelled points
    highlight: list[str] = Field(default_factory=list)
    points: list[MapPoint] = Field(default_factory=list)

    @model_validator(mode="after")
    def _shorthand(self):
        if not self.steps:
            if not (self.highlight or self.points):
                raise ValueError("map needs 'steps' (or the v2 'highlight'/'points' shorthand)")
            self.steps = [MapStep(highlight=self.highlight,
                                  places=[Place(name=p.label, lon=p.lon, lat=p.lat) for p in self.points])]
        elif self.highlight or self.points:
            raise ValueError("map: use either 'steps' or the 'highlight'/'points' shorthand, not both")
        return self


class Shot(BaseModel):
    type: ShotType
    at: Union[int, str] = 0  # word index in the paragraph, or the word/phrase the cut lands on
    query: Optional[str] = None  # stock
    source: Literal["auto", "pexels", "pixabay"] = "auto"  # stock: auto = Pexels, then Pixabay if nothing fits
    prompt: Optional[str] = None  # ai_image
    photo: Optional[str] = None  # photo: Wikimedia Commons "File:..." (public domain / CC0 / CC BY only)
    on_screen_text: Optional[str] = None
    subtitle: Optional[str] = None
    chart: Optional[Chart] = None
    map: Optional[MapSpec] = None
    quote: Optional[str] = None
    author: Optional[str] = None
    where: Optional[PlaceRef] = None  # stock / photo / ai_image: "where are we" mini map in the corner
    where_label: Optional[str] = None  # default: the place name

    @model_validator(mode="after")
    def _required(self):
        need = {
            "stock": self.query,
            "ai_image": self.prompt,
            "photo": self.photo,
            "chart": self.chart,
            "map": self.map,
            "title_card": self.on_screen_text,
            "quote": self.quote,
        }[self.type]
        if not need:
            raise ValueError(f"shot type '{self.type}' is missing its required field")
        if self.where is not None and self.type not in ("stock", "photo", "ai_image"):
            raise ValueError("'where' (locator inset) is for stock, photo and ai_image shots")
        return self


class Ask(BaseModel):
    """Engagement question: the narration asks it (at this word) and a question card shows it on screen."""
    at: Union[int, str] = 0
    text: str = Field(max_length=70)


class Paragraph(BaseModel):
    text: str
    shots: list[Shot] = Field(default_factory=list)
    ask: Optional[Ask] = None

    def _find(self, at: Union[int, str], start: int) -> int:
        """Word index of an anchor; phrases are searched from word `start` on."""
        toks = [norm(w) for w in words_of(self.text)]
        if isinstance(at, int):
            if not 0 <= at < len(toks):
                raise ValueError(f"anchor {at} is outside the paragraph ({len(toks)} words): {self.text[:60]!r}")
            return at
        phrase = [norm(w) for w in words_of(at)]
        idx = next((i for i in range(start, len(toks) - len(phrase) + 1) if toks[i:i + len(phrase)] == phrase), None)
        if idx is None:
            raise ValueError(f"anchor {at!r} not found (in order) in: {self.text[:60]!r}")
        return idx

    def anchor_indices(self) -> list[int]:
        """Word index each shot starts on. Phrase anchors are searched in order after the previous shot."""
        out: list[int] = []
        for shot in self.shots:
            idx = self._find(shot.at, out[-1] + 1 if out else 0)
            if out and idx <= out[-1]:
                raise ValueError(f"shots must have increasing anchors: {self.text[:60]!r}")
            out.append(idx)
        return out

    def step_indices(self) -> list[list[int]]:
        """For every shot: the word index of each map step (empty for non-map shots).

        Steps live inside their shot: from the shot's anchor up to (not including) the next shot's anchor.
        """
        anchors = self.anchor_indices()
        n_words = len(words_of(self.text))
        out = []
        for k, (shot, start) in enumerate(zip(self.shots, anchors)):
            end = anchors[k + 1] if k + 1 < len(anchors) else n_words
            idxs: list[int] = []
            for j, step in enumerate(shot.map.steps if shot.type == "map" and shot.map else []):
                if step.at is None:
                    if j:
                        raise ValueError(f"only the first map step may omit 'at': {self.text[:60]!r}")
                    idx = start
                else:
                    idx = self._find(step.at, idxs[-1] + 1 if idxs else start)
                if not start <= idx < end:
                    raise ValueError(f"map step anchor {step.at!r} is outside its shot (words {start}-{end - 1}): {self.text[:60]!r}")
                if idxs and idx <= idxs[-1]:
                    raise ValueError(f"map steps must have increasing anchors: {self.text[:60]!r}")
                idxs.append(idx)
            out.append(idxs)
        return out

    def ask_index(self) -> int | None:
        return None if self.ask is None else self._find(self.ask.at, 0)

    @model_validator(mode="after")
    def _anchors(self):
        self.step_indices()
        self.ask_index()
        return self


class Chapter(BaseModel):
    title: str
    mood: Mood = "calm"
    card: Optional[bool] = None  # chapter title card; default: every chapter except the first
    paragraphs: list[Paragraph] = Field(min_length=1)


class Thumbnail(BaseModel):
    text: str  # 2-4 words, rendered large on the thumbnail
    prompt: str  # background image prompt (objects/places/symbols, no real people)


class YouTubeMeta(BaseModel):
    title: str = Field(max_length=100)
    description: str  # intro text; chapters and credits are appended automatically
    tags: list[str] = Field(default_factory=list)
    pinned_comment: Optional[str] = None  # posted and pinned by hand after upload


class Script(BaseModel):
    title: str
    voice: str = "am_michael"
    music: str = "auto"  # "auto" (a /music track if any, else procedural) | "procedural" | file in /music | "none"
    captions: bool = True
    map_style: Optional[Literal["satellite", "atlas", "midnight"]] = None  # None -> config.MAP_STYLE
    look: Literal["none", "warm", "cool"] = "none"  # one colour grade + vignette on every stock / photo / AI shot
    chapters: list[Chapter] = Field(min_length=1)
    sources: list[str] = Field(default_factory=list)  # fact-check notes, not rendered
    thumbnail: Optional[Thumbnail] = None
    youtube: Optional[YouTubeMeta] = None

    def has_card(self, i: int) -> bool:
        card = self.chapters[i].card
        return i > 0 if card is None else card

    @model_validator(mode="after")
    def _opening_shot(self):
        first = self.chapters[0].paragraphs[0]
        if not self.has_card(0) and not (first.shots and first.anchor_indices()[0] == 0):
            raise ValueError("the video must open with a visual: give the first paragraph a shot at word 0 or a chapter card")
        return self


def load_script(path: Path) -> Script:
    return Script.model_validate(json.loads(Path(path).read_text(encoding="utf-8")))
