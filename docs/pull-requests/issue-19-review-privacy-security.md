# PR: Local privacy defaults and security regression checks

Closes #19.

Bind the documented local Streamlit launch to loopback and disable usage statistics;
retain CORS/XSRF protection and disable static serving. Guard common SQLite/secret
paths against accidental Git additions. Add privacy documentation, UI notice and
regressions without changing financial calculations, schema or chart sizing.
See [Issue 19 findings](../issues/milestone-6-issue-19-review-privacy-security.md).

## Validation

Six focused tests cover runtime config resolution, ignore rules/public trackability,
indexed database/known-secret signatures, a socket-blocked persisted financial flow
and inline minimized chart data. Full suite, static/dependency/link/repository and
isolated browser results are recorded in the actual PR description.

- `pytest -q`: 392 passed (42.98s).
- `python -m pytest -q`: 392 passed (36.59s).
- Ruff, pip consistency, links across 52 Markdown files and diff checks passed.
- Indexed guard passed; a separate reachable-history scan checked 142 blobs for
  SQLite headers and selected credential signatures with no findings. Neither
  check is comprehensive secret detection; no suspected contents are printed.
- Headless Edge at 1366x900 and 390x844 used copied repository config without
  address/telemetry CLI overrides, with external HTTP/WebSocket traffic blocked
  and observed. No external attempts, script/image interpretation, app errors
  or horizontal overflow; save, invalid NaN rejection and reload persistence passed.
  Startup log reported loopback; OS listener enumeration was inconclusive.
  Synthetic data only, temporary server/browser stopped; no tooling dependencies
  added to the project.

## Limitations

No encryption, authentication, secure erasure, comprehensive credential detection,
full dependency vulnerability audit or production deployment protection is claimed.
OS cloud syncing, backups, browser extensions and hostile local users are outside
these safeguards. Use synthetic data only. See [privacy boundaries](../privacy-security.md).
P3 Streamlit chart sizing remains deferred. Preserve user edits and every branch.
Default GitHub branch differs from main; manually populate the PR description and
do not assume automatic issue closure. Leave open for Chat 3 independent review;
no merge, approval or final Senior comment by the developer.
