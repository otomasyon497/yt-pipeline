"""script.json validation."""
import json
from pathlib import Path
from typing import Literal, Optional

from pydantic import BaseModel, Field, model_validator

Visual = Literal["stock", "ai_image", "chart", "map", "title_card", "quote"]


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
    # Country names as used by Natural Earth / world-atlas (e.g. "Finland", "United States of America").
    highlight: list[str]
    points: list[MapPoint] = Field(default_factory=list)


class Scene(BaseModel):
    id: str
    visual: Visual
    narration: str
    query: Optional[str] = None  # stock
    prompt: Optional[str] = None  # ai_image
    on_screen_text: Optional[str] = None
    subtitle: Optional[str] = None
    chart: Optional[Chart] = None
    map: Optional[MapSpec] = None
    quote: Optional[str] = None
    author: Optional[str] = None
    captions: bool = True

    @model_validator(mode="after")
    def _check_required(self):
        need = {
            "stock": self.query,
            "ai_image": self.prompt,
            "chart": self.chart,
            "map": self.map,
            "title_card": self.on_screen_text,
            "quote": self.quote,
        }[self.visual]
        if not need:
            raise ValueError(f"scene {self.id}: visual '{self.visual}' is missing its required field")
        return self


class Thumbnail(BaseModel):
    text: str  # 2-4 words, rendered large on the thumbnail
    prompt: str  # background image prompt (objects/places/symbols, no real people)


class YouTubeMeta(BaseModel):
    title: str = Field(max_length=100)
    description: str  # intro text; credits.txt is appended automatically
    tags: list[str] = Field(default_factory=list)
    category_id: str = "27"  # 27 = Education
    contains_synthetic_media: bool = True  # disclose AI-generated realistic imagery / synthetic voice


class Script(BaseModel):
    title: str
    voice: str = "am_michael"
    music: str = "auto"  # "auto" | file name inside /music | "none"
    scenes: list[Scene]
    sources: list[str] = Field(default_factory=list)  # free-form fact-check notes, not rendered
    thumbnail: Optional[Thumbnail] = None
    youtube: Optional[YouTubeMeta] = None

    @model_validator(mode="after")
    def _unique_ids(self):
        ids = [s.id for s in self.scenes]
        if len(ids) != len(set(ids)):
            raise ValueError("scene ids must be unique")
        return self


def load_script(path: Path) -> Script:
    return Script.model_validate(json.loads(Path(path).read_text(encoding="utf-8")))
