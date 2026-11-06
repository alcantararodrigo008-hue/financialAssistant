# PR: Repeatable MVP demonstration

Closes #20.

Review and replace README setup with explicit main-branch, environment-bound
commands; add a clean-data demonstration and visible prototype limitations. See
[Issue 20 acceptance mapping](../issues/milestone-6-issue-20-prepare-demonstrable-mvp.md)
and [walkthrough](../demo-walkthrough.md). No financial-runtime or schema changes.
Pin validated Ruff 0.16.4 to match fresh validation without unrelated style edits.
Adapt the network-denial regression for standard-library Windows asyncio socketpair
setup in newer Streamlit, while asserting application/external connections stay denied.
No optional loader/reset: manual synthetic forms avoid mixing user and demo data.

## Validation

Run both full pytest entry points, Ruff, dependency, Markdown-link, ignore/index and
diff checks. Existing 392 regressions cover expected/invalid inputs, persistence,
data integrity and UI integration; the compatibility guard gains positive/negative
connection probes rather than duplicate documentation snapshot tests.
Create a fresh isolated environment from the project requirements and exercise the
manual walkthrough in a new synthetic browser/database. Final results and resolved
versions are recorded in the actual PR description.

- Existing environment (Streamlit 1.62.0): both full entry points passed 392 tests
  (51.09s / 57.54s). Fresh Python 3.12.2 environment (Streamlit 1.67.0,
  pytest 8.4.2, Ruff 0.16.4): both full entry points passed 392 (43.21s / 34.44s).
- A final focused privacy run passed six cases in each environment after the
  explicit socketpair allowance and application/external denial probes were added.
- Ruff and pip consistency pass in both environments. Links across 55 Markdown
  documents and repository/index/ignore/whitespace checks pass.
- A clean temporary clone of main (runtime files unchanged by this PR), launched
  with the fresh environment, started without data. Actual Edge form submissions
  created the demo goal and six transactions; exact normal/low-savings/deficit
  values, explanations, 25% progress and rejected NaN were verified.
- Live probes also verified filter metric isolation, cancel/confirmed deletion,
  five remaining rows, persistence through a distinct server process, native
  empty-month navigation and mobile rendering without overflow or app exceptions.
  AppTest covers empty-month return and broader invalid-input/persistence cases.
- Synthetic records only; original user database never opened. Browser tooling,
  scratch clones and environments remain outside the project; test helpers stopped.

Fresh setup exposed a test-harness issue, not financial network access: Windows
asyncio builds its internal socketpair using loopback. Permit only the stdlib
handshake in a context-local guard and verify that ordinary loopback and external
application attempts remain denied. Fresh Ruff 0.17.4 added eight pre-existing
UTC-alias style findings; pin validated 0.16.4 instead of broad unrelated refactoring.

## Limits and review

Windows/Python environment and headless Edge only; no physical-device, accessibility,
load/concurrency or every-version compatibility certification. First-launch email,
minimum Streamlit and independent LAN verification remain deferred, as does P3
chart sizing. No goal-edit UI, completion controls, encryption, authentication or
production deployment guarantees are introduced. Existing single-month guidance
and manual goal balances remain.

Preserve every branch and exclude unchanged pre-existing instruction edits.
Target main explicitly because GitHub's default branch differs. Populate the actual
PR body manually; do not assume automatic issue closure. Leave open for independent
Chat 3 review, without developer approval, final Senior comment or merge.
