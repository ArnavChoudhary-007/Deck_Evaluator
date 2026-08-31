"""Report assembly: the coverage gate and renormalisation from architecture 5.4.

One public function, build_report, turns axis results, their rubric weights,
and rewrite suggestions into a Report.

Unassessed axes are excluded from both the numerator and the denominator of
the weighted score -- never scored as zero, never averaged in. Below the
0.60 coverage threshold the numeric score is withheld rather than derived
from partial evidence; the Report still carries every axis (assessed and
not) and the rewrite suggestions pass through unchanged either way.

architecture 5.4's own renormalisation pseudocode is unweighted
(`sum(a.score) / sum(a.max)`) because v0 weights are equal (5.4, citing
Section 12: "equal weighting until official numbers are confirmed"). This
function instead applies axis_weights inside both sums, extending the
baseline weighted formula (`Score = sum(w_i * s_i)`) into the renormalised
branch, per this task's spec -- with equal weights the two are identical.

No I/O, no model calls. Imports are limited to contracts/ and the stdlib.
"""

from typing import List, Mapping, Optional

from contracts.evidence import AxisName, AxisResult, ScoredAxis
from contracts.report import Report, RewriteSuggestion

# The coverage gate (architecture 4.4, 5.4): below this fraction of assessed
# axes, the numeric score is withheld rather than derived from partial
# evidence. Taken directly from the architecture rather than a config layer
# because this file may import only contracts/ and the stdlib.
COVERAGE_THRESHOLD = 0.60

# The upper bound every ScoredAxis.score is already constrained to
# (contracts/evidence.py: Field(ge=0.0, le=10.0)) -- the fixed 0-10 scale
# the rubric scores every axis on, not a rubric weight (axis_weights carries
# those).
AXIS_SCORE_CEILING = 10.0


def build_report(
    axis_results: List[AxisResult],
    axis_weights: Mapping[AxisName, float],
    suggestions: List[RewriteSuggestion],
) -> Report:
    """Apply the architecture 5.4 coverage gate and weighted renormalisation."""
    assessed: List[ScoredAxis] = [axis for axis in axis_results if isinstance(axis, ScoredAxis)]
    coverage = len(assessed) / len(axis_results) if axis_results else 0.0

    score: Optional[float] = None
    if assessed and coverage >= COVERAGE_THRESHOLD:
        weighted_score = sum(axis_weights[axis.axis] * axis.score for axis in assessed)
        weighted_ceiling = sum(axis_weights[axis.axis] * AXIS_SCORE_CEILING for axis in assessed)
        score = weighted_score / weighted_ceiling * 100

    return Report(axes=axis_results, suggestions=suggestions, score=score)
