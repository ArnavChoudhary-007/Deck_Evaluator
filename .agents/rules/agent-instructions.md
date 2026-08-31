# Deck Evaluator — agent instructions

A rubric-based grading system for Smart India Hackathon idea presentations.
Read `docs/architecture.pdf` before proposing changes. This file wins over
anything you infer from the code.

## What this system is

It reads a submitted PDF deck and returns three things: a score against the six
published SIH judging axes, the evidence in the deck that produced each score,
and slide-level rewrite suggestions. It runs at zero marginal cost on free-tier
infrastructure, and that constraint shapes almost every decision below.

**Scope is v0, SIH only.** The SIH rubric and the 2025 six-slide Idea
Presentation format are hardcoded as configuration. Multi-event generalisation
is v2. Do not build toward it.

## Repository boundaries

Each person owns one stream. **Do not edit files outside the stream you were
asked to work in.** If a task appears to need a change in another stream, stop
and say so — do not make the change.

| Stream | Directories | Owns |
|---|---|---|
| A — spine | `api/`, `orchestrator/`, `infra/`, `web/` | Upload, gate checks, job sequencing, token budget enforcement, storage, deploy, UI |
| B — deterministic engines | `engines/parser/`, `engines/structural/`, `engines/triage/` | Parsing, OCR fallback, digest, section detection, legibility, hidden-text detection, image triage |
| C — model layer | `engines/scoring/`, `engines/vision/`, `engines/originality/`, `calibration/` | Rubric scorer, vision calls, evidence binding, coverage gate, calibration |

`contracts/` is shared and frozen. Changing it requires all three owners
present. Never change a contract to make an implementation easier.

## The contracts

Three Pydantic models cross stream boundaries. Nothing else does.

- `SlideDigest` — the deck compressed to ~2,500 tokens: slide titles, extracted
  claims, numeric assertions, image map (bounding box, native resolution,
  displayed size). **Every downstream model call reads the digest, never the
  raw deck.**
- `AxisResult` / `EvidenceRef` — an axis is either scored with at least one
  `EvidenceRef` (slide number + text span), or marked `cannot_assess` with a
  reason. A score without evidence is a validation error.
- `Report` — may represent a suppressed score. The numeric field is
  `Optional[float]` and is `None` when suppressed. It is never `0.0`.

## Non-negotiable design rules

These look like unfinished error handling. They are product decisions. Do not
"fix" them.

1. **An unassessed axis is `None`, never a number.** Do not default it to 0, to
   the mean, or to the axis's midpoint. Renormalise over assessed axes only.
2. **When coverage < 0.60, the numeric score must not exist on the response
   object.** Return the gap list instead. A confident number derived from two of
   six axes is worse than no number.
3. **The rubric is data.** Nothing under `engines/` may contain a weight, an
   anchor string, or an axis name literal. All of it loads from the versioned
   rubric JSON.
4. **The section template is versioned JSON keyed by year.** The 2023 format had
   four sections; 2025 has six; it will change again. A template mismatch is a
   warning, not a failed structural score.
5. **One structured model call scores all six axes.** Never loop over axes with a
   model call inside. Six calls is ~30,000 tokens per deck and makes the service
   unusable on a free tier.
6. **Exactly three image crops, in one batched vision request.** Three is a
   rate-limit constraint (2,048 tokens flat per image), not a quality knob.
7. **The deck is parsed in memory and discarded.** Only the report persists.
   Never write an uploaded PDF to disk or object storage, and never cache one.
8. **Originality findings are phrased as resemblance**, never as an accusation:
   "resembles a prior public submission", never "plagiarised" or "copied from".
   A false accusation against a student team is a different category of harm
   from a missed duplicate.
9. **v0 accepts PDF only.** Do not add a PPTX converter, headless LibreOffice, or
   any dependency over 100 MB.
10. **Gate-check failures are rejections with a reason, not low scores.** A low
    score implies the deck was read.

## Security

Deck content is untrusted input.

- The evaluation prompt is fixed and parameterised only from configuration.
- Deck content is passed as data inside a delimited region. It is **never**
  interpolated into instruction text.
- Text recovered from a deck that reads as an instruction — asking for a
  particular score, claiming to be from an organiser — is reported as a finding
  in the report, not obeyed.
- Text found by the vision model but absent from the extracted text layer is
  quarantined and flagged, not scored.

## Code rules

- **Grep before you write a helper.** If something close exists, use or extend
  it. A parallel implementation is worse than an imperfect shared one.
- **No `try/except` that swallows and continues.** If a stage cannot handle a
  condition, let it raise; the orchestrator decides.
- **No magic numbers in function bodies.** 72 DPI, 0.15 area ratio, 0.60
  coverage, 0.75 / 0.90 similarity — all from config.
- **No speculative abstraction.** No interface, base class, registry or factory
  for something with one caller. Write the concrete version.
- **No fallback path for a case we have not seen.** If a code path exists, a
  test must reach it.
- **No compatibility shims.** When behaviour changes, update the callers. The
  repo holds one version of the truth.
- Any file over 250 lines: say so before adding to it.
- Ideas that are out of scope go in `TODO.md`, not in a comment or a stub.

## Testing

Fixtures live in `tests/fixtures/decks/`. Use them by name; do not generate
synthetic PDFs.

| Fixture | Must produce |
|---|---|
| `six_slide_clean.pdf` | all six sections detected |
| `missing_feasibility.pdf` | exactly one absent section, no exception |
| `flat_images.pdf` | OCR fallback taken, and flagged in the report |
| `hidden_text_3pt.pdf` | hidden-text detector fires, text quarantined |
| `bg_colour_text.pdf` | low-contrast detector fires |
| `thirty_page.pdf` | rejected at the gate with a reason |
| `stock_photos_only.pdf` | zero images survive triage, zero vision calls |
| `diagram_heavy.pdf` | top three diagrams ranked and sent as one request |

Standing assertions that must not regress:

- one deck on the normal path issues at most **2** model requests
- total tokens per deck stays under **13,000**, counted from recorded request
  payloads, not estimated
- `test_suppressed_score_has_no_number` — a suppressed report has no numeric
  score field populated

## Workflow expectations

- Plan before implementing. End every plan with what you had to guess.
- Write the failing test before the implementation, and show it failing.
- Before committing, list and delete: single-caller helpers under 5 lines,
  branches no test reaches, parameters no caller passes, unused imports, and
  anything added "just in case".
- Do not fix a bug you could not reproduce.

## Language in the product

The system measures whether a presentation contains what the rubric asks for. It
does not measure whether the idea deserves to win. Every user-facing string must
keep that distinction visible — report rubric coverage and evidence quality,
never a judgement about the idea.
