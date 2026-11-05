# Privacy and security boundaries

Financial Assistant is a local, single-user educational prototype. **Use synthetic
data only**, including for tests, screenshots, demonstrations and review. No bank
account connection, login, API key, credential or external account is required.
The app's Python code stores records in SQLite and computes guidance locally;
there is no financial-service client or automatic data export.

## Launch locally

Run `streamlit run app.py` from the repository root. The tracked
[Streamlit configuration](../.streamlit/config.toml) sets:

- `server.address = "127.0.0.1"`: listen on IPv4 loopback, not the LAN.
- `browser.gatherUsageStats = false`: opt out of Streamlit usage statistics.
- CORS and XSRF protection enabled, static-file serving disabled. These settings
  are not authentication or authorization.

Open `http://127.0.0.1:8501`. The configuration is relative to the **working
directory**, not the app script's location. Launching elsewhere, changing config,
environment variables, CLI flags or global Streamlit settings can change behavior.
Restart after configuration changes. Do not expose this server to a LAN, public
interface, tunnel, cloud host or reverse proxy: no application authentication,
user separation or production deployment security has been implemented.

The browser necessarily receives the financial records it displays over the local
Streamlit connection. Local-only operation is not protection against another local
process, browser extension, person using the browser or account with file access.
CORS/XSRF protections and loopback binding do not make a shared computer trustworthy.
Installing dependencies and using GitHub require separate network access; the
financial flow needs neither service. Do not enable third-party analytics or add
external chart data URLs. Charts embed their necessary data in the local app and
omit raw transaction descriptions. Names and guidance render as plain text, not
user-authored HTML/Markdown; transaction values are passed as SQL parameters.

## Storage, syncing and deletion

Default storage is `data/financial_assistant.db` under the working directory. The
app does not encrypt it, set restrictive OS permissions, manage backups or provide
reliable secure erasure. Money, descriptions and goal names are readable in the
SQLite file and may also appear in process/browser memory, journals, backups,
screenshots and logs. Avoid putting personal data in names/descriptions or error
reports. See [SQLite persistence](sqlite-persistence.md).

**Cloud-folder syncing is independent of Git and the app.** A checkout or working
directory in OneDrive, Dropbox or another synced folder can upload the database,
sidecars and backups even when Git ignores them. Choose a private, non-synced
working folder if you need to prevent that. OS backups and other installed software
may also copy data. Local storage is not a promise that data never leaves the PC.

Confirmed deletion removes the selected record logically; it does not guarantee
removal from SQLite free pages, sidecars, copies, browser state or backups. Do not
manipulate live database/sidecar files to erase records. This issue adds no secure
storage, encryption, authentication or production-grade privacy guarantee.

## Git safeguards and secrets

The [ignore rules](../.gitignore) exclude:

- Everything under root `data/` except `.gitkeep`, including arbitrary exports and
  nested private files.
- Common `.db`, `.sqlite`, `.sqlite3` files and their extension-based sidecars
  elsewhere in the checkout (for example `private.db-wal`).
- `.env`, `.env.*` and the root `.streamlit/secrets.toml`. No application feature requires these files; ignoring them is an
  accidental-commit guard, not permission to store credentials in the project.

Extensionless databases and arbitrary exports outside `data/` need separate care.
Ignore rules do not untrack files, remove historical commits, encrypt files or
prevent `git add -f`. Keep passwords, private keys, tokens and real banking data out
of every committed file, including fixtures and documentation. A GitHub remote URL
or public issue URL is not a credential. Do not add real credentials as test canaries.

Before committing, inspect `git status --short`, `git diff --cached --stat` and the
actual staged diff; use `git check-ignore -v <path>` for a candidate private path.
The privacy regression checks inspect indexed files for database paths/headers
and selected token/private-key signatures, reporting **paths only**, not content.
This is a limited safety net, not proof that every possible secret is absent.
If a real credential is ever committed, stop sharing it and arrange revocation/
rotation with its owner; deleting a working file is insufficient. Do not rewrite
history or delete branches without explicit authorization.

## Verification and limits

[Privacy regressions](../tests/test_privacy_security.py) verify actual Streamlit
configuration resolution in a fresh process; private ignore paths and public
trackability; indexed database/known-secret checks; chart payload minimization; and
synthetic goal/income/expense creation, invalid-input rejection and reopening while
Python socket connections are blocked. Existing tests cover bound SQL, rollback,
confirmed/stale deletion, amount validation and literal user text.

Live browser verification uses an isolated synthetic database and the repository
configuration, with external HTTP/WebSocket traffic blocked/observed. It is an
observation of tested flows, not a guarantee about all dependency versions or
future features. This review is not a penetration test, vulnerability audit of all
dependencies, OS/cloud-sync audit, encryption assessment or regulatory certification.
Browser extensions, physical/shared devices, hostile local users, load/concurrency
and remote deployment are outside the tested privacy model. Runtime configuration
and the loopback startup address were verified; OS listener enumeration was
inconclusive, so independent OS/LAN exposure testing is not claimed. The existing P3
Streamlit chart-sizing deprecation remains a separate follow-up.
