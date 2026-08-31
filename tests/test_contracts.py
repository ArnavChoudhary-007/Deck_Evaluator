"""Prove the contracts hold their shape. Does not modify contracts/."""

from typing import get_args

import pytest
from pydantic import ValidationError

from contracts.evidence import AxisName, CannotAssessAxis, EvidenceRef, ScoredAxis
from contracts.report import Report, RewriteSuggestion

SIX_AXES = list(get_args(AxisName))


def _scored(axis, score=7):
    return ScoredAxis(
        axis=axis,
        score=score,
        evidence=[EvidenceRef(slide_number=1, text_span="placeholder evidence")],
    )


def _cannot_assess(axis, reason="No evidence found for this axis."):
    return CannotAssessAxis(axis=axis, reason=reason)


def test_axis_scored_with_evidence():
    axis = ScoredAxis(
        axis="Technical Feasibility",
        score=7,
        evidence=[EvidenceRef(slide_number=3, text_span="Built on Firebase and Redis.")],
    )
    assert axis.score == 7
    assert axis.evidence[0].slide_number == 3


def test_axis_scored_without_evidence_is_rejected():
    with pytest.raises(ValidationError):
        ScoredAxis(axis="Technical Feasibility", score=7, evidence=[])


def test_report_coverage_is_derived_five_of_six():
    axes = [_scored(name) for name in SIX_AXES[:5]] + [_cannot_assess(SIX_AXES[5])]
    report = Report(axes=axes, suggestions=[], score=None)
    assert round(report.coverage, 3) == 0.833


def test_report_axes_wrong_count_is_rejected():
    axes = [_scored(name) for name in SIX_AXES[:5]]  # only five
    with pytest.raises(ValidationError):
        Report(axes=axes, suggestions=[], score=None)


def test_report_axes_duplicate_name_is_rejected():
    # SIX_AXES[0] appears twice; the sixth axis name is never covered.
    axes = [_scored(name) for name in SIX_AXES[:5]] + [_scored(SIX_AXES[0])]
    with pytest.raises(ValidationError):
        Report(axes=axes, suggestions=[], score=None)


def test_suppressed_report_still_carries_rewrite_suggestions():
    axes = [_cannot_assess(name) for name in SIX_AXES]
    suggestions = [
        RewriteSuggestion(
            slide_number=n,
            weakness="No named tech stack.",
            suggested_rewrite="Name the stack and one data source.",
            axes=["Technical Feasibility"],
        )
        for n in (2, 3, 4)
    ]
    report = Report(axes=axes, suggestions=suggestions, score=None)
    assert report.coverage == 0.0
    assert report.score is None
    assert len(report.suggestions) == 3


def test_rewrite_suggestion_without_axis_is_rejected():
    with pytest.raises(ValidationError):
        RewriteSuggestion(
            slide_number=2,
            weakness="Vague claim.",
            suggested_rewrite="State the number and its source.",
            axes=[],
        )
