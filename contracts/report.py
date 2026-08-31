"""Report.

Holds a single list covering all six SIH axes (architecture 2.1) rather than
parallel scored/unassessed lists: each entry is either a ScoredAxis (with
evidence) or a CannotAssessAxis (with a reason), and a model validator
enforces that the list is exactly the six rubric axes, no duplicates, no
drift. `coverage` is a computed property over that list rather than a stored
field, so there is exactly one source of truth for it (architecture 5.4:
`coverage = len(assessed) / len(axes)`).

`score` stays Optional[float] defaulting to None, never 0.0 (architecture
4.4, 5.4) — a suppressed score carries no numeric placeholder. Report does
not enforce the 0.60 coverage threshold against `score` itself; that gate
(architecture 4.4) is orchestrator logic, not a contract invariant.

`suggestions` carries per-slide rewrite suggestions (architecture 11.1) and
is independent of `score`/coverage: a suppressed report still tells the team
what to fix. Each RewriteSuggestion must reference at least one axis, the
same evidence-honesty rule ScoredAxis applies to scores.

Pydantic v2 models and Literal enums, plus the model validator and computed
property this fix requires. Deriving a value from stored data is not the
banned "logic in contracts" — analysis is; a function that would let two
figures disagree is what this file exists to make impossible.
"""

from typing import Optional, get_args

from pydantic import BaseModel, Field, computed_field, model_validator

from contracts.evidence import AxisName, AxisResult


class RewriteSuggestion(BaseModel):
    slide_number: int = Field(ge=1)
    weakness: str
    suggested_rewrite: str
    axes: list[AxisName] = Field(min_length=1)


class Report(BaseModel):
    axes: list[AxisResult]
    suggestions: list[RewriteSuggestion]
    score: Optional[float] = Field(default=None, ge=0.0, le=100.0)

    @model_validator(mode="after")
    def _axes_are_exactly_the_six_rubric_axes(self) -> "Report":
        names = [entry.axis for entry in self.axes]
        if len(names) != 6:
            raise ValueError(f"Report.axes must have exactly six entries, got {len(names)}.")
        if len(set(names)) != len(names):
            raise ValueError("Report.axes must not contain a duplicated axis name.")
        if set(names) != set(get_args(AxisName)):
            raise ValueError("Report.axes must match the six SIH rubric axis names exactly.")
        return self

    @computed_field  # type: ignore[misc]
    @property
    def coverage(self) -> float:
        assessed = sum(1 for entry in self.axes if entry.status == "scored")
        return assessed / len(self.axes)
