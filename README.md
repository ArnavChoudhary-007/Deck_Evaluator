# Deck Evaluator

A rubric-based grading system for Smart India Hackathon idea presentations.

## Current Status (Initial Setup Complete)

**Session 1** | **Date:** September 1, 2026 | **Author:** Arnav

Welcome to the team! The initial project foundation has been laid out. Here is what has been accomplished in the first session and what is currently in the repository:

1. **Contracts (`contracts/`)**: The core Pydantic models have been defined. This includes `SlideDigest` (the parsed deck representation), `EvidenceRef`, `AxisResult`, and the final `Report`. **Remember: The contracts folder is shared and frozen.**
2. **Scoring Logic (`engines/scoring/assemble.py`)**: The `build_report` function has been implemented. It correctly handles the 0.60 coverage gate and the weighted score renormalisation.
3. **Tests (`tests/`)**: We have a working pytest test suite covering the contracts and the scoring assembly logic. It currently passes 13/13 tests.
4. **Agent Rules (`.agents/rules/`)**: We've added persistent AI agent instructions to enforce our strict repository boundaries and code quality standards.

## How to Start Working

As per our project rules, each of you owns a specific stream:
- **Stream A — Spine**: `api/`, `orchestrator/`, `infra/`, `web/`
- **Stream B — Deterministic**: `engines/parser/`, `engines/structural/`, `engines/triage/`
- **Stream C — Model Layer**: `engines/scoring/`, `engines/vision/`, `engines/originality/`, `calibration/`

### Workflow Rules
1. **Never push directly to main.** Always create a feature branch for your stream (e.g., `git checkout -b stream-b/parser`).
2. **Do not edit outside your stream.** If you need a change in someone else's stream, ask them to do it.
3. **Open a Pull Request.** When your feature is done, push your branch and open a PR on GitHub.
4. **Use the "check" command.** Ask the AI agent to run the `check` command on your branch before asking a teammate for a final review. This ensures your code meets our strict quality standards before merging.
