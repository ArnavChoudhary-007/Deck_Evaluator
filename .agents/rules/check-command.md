# "check" Command Workflow

When the user asks you to "check", it means you must run the strict pre-merge code-quality audit. 

## Instructions for "check"

Act as a strict senior software engineer performing a pre-merge code-quality audit.

Your job is to review the current repository changes and determine whether this code is safe, maintainable, complete, and free of obvious bugs or dead code.

First, inspect:
1. The current Git diff or recent file changes
2. All files changed in this branch
3. Related existing code, types, API routes, tests, and utilities
4. Package/dependency changes
5. The feature requirements and acceptance criteria

Do not edit code immediately.

Audit the changes for:

### Correctness and bugs
- Missing requirements or incorrect behavior
- Incorrect assumptions, edge cases, null/undefined issues, race conditions, and state bugs
- Broken loading, empty, error, retry, and unauthorized states
- Broken API request/response contracts
- Input validation problems
- Incorrect error handling, swallowed errors, silent fallbacks, or fake success messages
- Logic that works only for the happy path
- Potential security, authentication, authorization, secret, or data-exposure issues

### Code quality
- Confusing naming, overly large functions/components, excessive nesting, duplicated logic
- Inconsistent patterns compared with the existing codebase
- Unnecessary abstractions, generic helpers, wrappers, or new dependencies
- Type safety issues, especially `any`, unsafe casting, ignored errors, or weak types
- Comments that explain obvious code or have become inaccurate
- Performance issues that matter for the expected usage

### Dead and duplicate code
- Unused imports, variables, functions, components, hooks, routes, exports, types, props, and dependencies
- Files that are no longer referenced
- Unreachable branches, redundant conditions, obsolete feature flags, old TODOs, and stale mock data
- Newly created utilities that duplicate existing utilities
- Code written for hypothetical future features rather than the current task
- Tests that do not test meaningful observable behavior

### Tests and verification
- Missing unit, integration, or end-to-end tests
- Missing tests for key failure paths and boundary cases
- Tests that only test implementation details
- Tests that would still pass if the feature were broken
- Whether the test suite was weakened to make the code pass

Then run the supplied lint, type-check, test, and build commands (e.g. `pytest tests/`).

Output format:

# Verdict
Choose exactly one:
- APPROVE: Ready to merge
- APPROVE WITH FOLLOW-UPS: Safe to merge, but minor improvements remain
- REQUEST CHANGES: Must be fixed before merge

# Verification results
For every command:
- Exact command
- Passed / Failed / Not available
- Important output or failure reason

# Findings
Group findings by severity:
- Blocker
- Important
- Suggestion

For each finding, include:
- File path and function/component/symbol
- What is wrong
- Why it matters
- A minimal recommended fix
- Whether it is a bug, dead code, duplication, maintainability issue, test gap, or security issue

# Dead-code report
Create a separate list containing:
- Item
- File path
- Evidence that it is unused, duplicated, unreachable, or stale
- Safe to remove now / needs team confirmation / intentionally keep
- Reason

# Requirement coverage
Create a table:

| Acceptance criterion | Status: Pass / Partial / Fail | Evidence |
|---|---|---|

# Final cleanup checklist
List the exact actions required before merge.

Important rules:
- Do not claim that code is correct unless verification commands actually pass.
- Do not weaken tests, lint rules, types, validation, or build settings to get a pass.
- Do not recommend a large refactor unless it is necessary to fix a concrete problem.
- Do not remove exported/public APIs, database fields, environment variables, or routes without first searching the repository for usages.
- Do not make code changes until explicitly told: "apply the fixes."
