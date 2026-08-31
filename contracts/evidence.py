"""EvidenceRef and AxisResult.

The six axis names are read from architecture 2.1, not invented here.

An axis is either scored with at least one EvidenceRef, or marked
cannot_assess with a reason (architecture 4.4, 5.4). AxisResult is a
discriminated union on `status` so that a scored axis with zero evidence
cannot be constructed at all: Pydantic rejects it as a validation error, not
as a naming convention a caller could ignore.

Pydantic v2 models and Literal enums only. No functions, no I/O, no computed
defaults.
"""

from typing import Annotated, Literal, Union

from pydantic import BaseModel, Field

AxisName = Literal[
    "Innovation & Creativity",
    "Technical Feasibility",
    "Relevance to the PS",
    "Scalability",
    "Societal / Economic Impact",
    "Presentation Clarity",
]


class EvidenceRef(BaseModel):
    slide_number: int = Field(ge=1)
    text_span: str


class ScoredAxis(BaseModel):
    axis: AxisName
    status: Literal["scored"] = "scored"
    score: float = Field(ge=0.0, le=10.0)
    evidence: list[EvidenceRef] = Field(min_length=1)


class CannotAssessAxis(BaseModel):
    axis: AxisName
    status: Literal["cannot_assess"] = "cannot_assess"
    reason: str


AxisResult = Annotated[Union[ScoredAxis, CannotAssessAxis], Field(discriminator="status")]
