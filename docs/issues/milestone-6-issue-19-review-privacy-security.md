# Issue 19: Privacy and security review

## Findings and focused changes

Local main was synchronized before branching. The repository contains no tracked
financial database or required credentials; app SQL uses bound parameters, chart
payloads are inline and user names/guidance use literal text. Tests use synthetic
records and temporary databases. No external account client is present.

Installed Streamlit defaults had usage statistics enabled and no specific server
address. Add repository-local config for loopback binding, telemetry opt-out,
CORS/XSRF protection and disabled static serving. Add accidental-commit guards for
common SQLite paths/sidecars and local secret files. Explain unencrypted storage,
cloud-sync risks and synthetic-only usage in UI/README and the
[privacy guide](../privacy-security.md); update storage ignore documentation.

## Acceptance and validation

- Database/secrets: indexed database path/header and selected known-secret checks;
  ignore regressions keep config/.gitkeep trackable. Limited signatures do not
  certify absence of every possible credential. Never print suspected contents.
- No external accounts: socket-blocked AppTest creates synthetic goals and both
  transaction types, rejects invalid money and reopens unchanged persisted data.
- Privacy expectations: launch/config precedence, browser connection, lack of
  authentication/encryption, cloud syncing, backups/deletion and Git limits explicit.
- Run both pytest entry points, Ruff, dependency/link/diff checks and isolated live
  browser verification with external traffic blocked/observed.

P3 chart sizing remains deferred. No financial rules, storage schema, authentication,
encryption or remote deployment work is added. Preserve all branches and the existing
instruction edits exactly; stop for independent Chat 3 review.
