"""SlideDigest and its parts.

The digest is the ~2,500 token compression of a parsed deck that every
downstream model call reads instead of the raw deck (architecture 4.2):
slide titles, extracted claims, numeric assertions, and an image map with
bounding box, native resolution, and displayed size per image (architecture
5.1).

Pydantic v2 models and Literal enums only. No functions, no I/O, no computed
defaults.
"""

from pydantic import BaseModel


class BoundingBox(BaseModel):
    x: float
    y: float
    width: float
    height: float


class Resolution(BaseModel):
    width_px: int
    height_px: int


class DisplayedSize(BaseModel):
    width_pt: float
    height_pt: float


class SlideTitle(BaseModel):
    slide_number: int
    title: str


class Claim(BaseModel):
    slide_number: int
    text: str


class NumericAssertion(BaseModel):
    slide_number: int
    text: str


class ImageMapEntry(BaseModel):
    slide_number: int
    bounding_box: BoundingBox
    native_resolution: Resolution
    displayed_size: DisplayedSize


class SlideDigest(BaseModel):
    slide_titles: list[SlideTitle]
    claims: list[Claim]
    numeric_assertions: list[NumericAssertion]
    images: list[ImageMapEntry]
