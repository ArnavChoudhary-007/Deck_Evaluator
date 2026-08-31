"""Prove build_report applies the architecture 5.4 coverage gate correctly."""

from typing import get_args

import pytest

from contracts.evidence import AxisName, CannotAssessAxis, EvidenceRef, ScoredAxis
from contracts.report import RewriteSuggestion
from engines.scoring.assemble import build_report

SIX_AXES = list(get_args(AxisName))
EQUAL_WEIGHTS = {axis: 1.0 for axis in SIX_AXES}


def _scored(axis, score):
    return ScoredAxis(
        axis=axis,
        score=score,
        evidence=[EvidenceRef(slide_number=1, text_span="placeholder evidence")],
    )


def _cannot_assess(axis, reason="No evidence found for this axis."):
    return CannotAssessAxis(axis=axis, reason=reason)


def test_six_assessed_all_perfect_scores():
    axes = [_scored(axis, 10) for axis in SIX_AXES]
    report = build_report(axes, EQUAL_WEIGHTS, [])
    assert report.score == pytest.approx(100.0)


def test_six_assessed_all_six_out_of_ten():
    axes = [_scored(axis, 6) for axis in SIX_AXES]
    report = build_report(axes, EQUAL_WEIGHTS, [])
    assert report.score == pytest.approx(60.0)


def test_four_assessed_at_eight_two_unassessed():
    axes = [_scored(axis, 8) for axis in SIX_AXES[:4]] + [
        _cannot_assess(axis) for axis in SIX_AXES[4:]
    ]
    report = build_report(axes, EQUAL_WEIGHTS, [])
    assert report.score == pytest.approx(80.0)
    assert report.score != pytest.approx(53.3, abs=0.1)


def test_three_assessed_suppresses_score_with_three_gaps():
    axes = [_scored(axis, 7) for axis in SIX_AXES[:3]] + [
        _cannot_assess(axis) for axis in SIX_AXES[3:]
    ]
    report = build_report(axes, EQUAL_WEIGHTS, [])
    assert report.score is None
    gaps = [axis for axis in report.axes if isinstance(axis, CannotAssessAxis)]
    assert len(gaps) == 3


def test_zero_assessed_suppresses_score_without_dividing_by_zero():
    axes = [_cannot_assess(axis) for axis in SIX_AXES]
    report = build_report(axes, EQUAL_WEIGHTS, [])
    assert report.score is None
    assert report.coverage == 0.0


def test_suppressed_score_still_keeps_both_suggestions():
    axes = [_scored(axis, 7) for axis in SIX_AXES[:3]] + [
        _cannot_assess(axis) for axis in SIX_AXES[3:]
    ]
    suggestions = [
        RewriteSuggestion(
            slide_number=2,
            weakness="No named tech stack.",
            suggested_rewrite="Name the stack and one data source.",
            axes=["Technical Feasibility"],
        ),
        RewriteSuggestion(
            slide_number=5,
            weakness="No usage numbers.",
            suggested_rewrite="Cite a users-served figure with its source.",
            axes=["Societal / Economic Impact"],
        ),
    ]
    report = build_report(axes, EQUAL_WEIGHTS, suggestions)
    assert report.score is None
    assert len(report.suggestions) == 2
