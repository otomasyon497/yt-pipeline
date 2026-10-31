"""script.json (v2) validation: chapters -> paragraphs (continuous narration) -> shots (visuals anchored to words)."""
import json
import re
from pathlib import Path
from typing import Literal, Optional, Union

from pydantic import BaseModel, Field, model_validator

ShotType = Literal["stock", "ai_image", "chart", "map", "title_card", "quote"]
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
    data: list[tuple[str, float]]


class MapPoint(BaseModel):
    label: str
    lon: float
    lat: float


class MapSpec(BaseModel):
    # Country names as used by Natural Earth / world-atlas (e.g. "Egypt", "United States of America").
    highlight: list[str]
    points: list[MapPoint] = Field(default_factory=list)


class Shot(BaseModel):
    type: ShotType
    at: Union[int, str] = 0  # word index in the paragraph, or the word/phrase the cut lands on
    query: Optional[str] = None  # stock
    prompt: Optional[str] = None  # ai_image
    on_screen_text: Optional[str] = None
    subtitle: Optional[str] = None
    chart: Optional[Chart] = None
    map: Optional[MapSpec] = None
    quote: Optional[str] = None
    author: Optional[str] = None

    @model_validator(mode="after")
    def _required(self):
        need = {
            "stock": self.query,
            "ai_image": self.prompt,
            "chart": self.chart,
            "map": self.map,
            "title_card": self.on_screen_text,
            "quote": self.quote,
        }[self.type]
        if not need:
            raise ValueError(f"shot type '{self.type}' is missing its required field")
        return self


class Paragraph(BaseModel):
    text: str
    shots: list[Shot] = Field(default_factory=list)

    def anchor_indices(self) -> list[int]:
        """Word index each shot starts on. Phrase anchors are searched in order after the previous shot."""
        toks = [norm(w) for w in words_of(self.text)]
        out: list[int] = []
        for shot in self.shots:
            if isinstance(shot.at, int):
                idx = shot.at
                if not 0 <= idx < len(toks):
                    raise ValueError(f"anchor {idx} is outside the paragraph ({len(toks)} words): {self.text[:60]!r}")
            else:
                phrase = [norm(w) for w in words_of(shot.at)]
                start = out[-1] + 1 if out else 0
                idx = next((i for i in range(start, len(toks) - len(phrase) + 1) if toks[i:i + len(phrase)] == phrase), None)
                if idx is None:
                    raise ValueError(f"anchor {shot.at!r} not found (in order) in: {self.text[:60]!r}")
            if out and idx <= out[-1]:
                raise ValueError(f"shots must have increasing anchors: {self.text[:60]!r}")
            out.append(idx)
        return out

    @model_validator(mode="after")
    def _anchors(self):
        self.anchor_indices()
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


class Script(BaseModel):
    title: str
    voice: str = "am_michael"
    music: str = "auto"  # "auto" | file name inside /music | "none"
    captions: bool = True
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
