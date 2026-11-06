# Issue 20: Demonstrable MVP

## Acceptance mapping

- README gives explicit main-branch cloning, Python-version check, environment
  installation and module-based launch/validation commands in Windows PowerShell.
  No activation-policy changes, data deletion or reset commands are needed.
- A clean-data walkthrough uses manual synthetic forms and exact expected totals,
  goal progress, category/low-savings/deficit guidance, invalid money, cancel/confirm
  deletion, restart persistence and an empty-month round trip.
- Optional demo loader omitted to avoid silently mixing demo and existing data.
  Repeat in a new private clone, not by clearing an existing user's database.
- Existing regression coverage already exercises normal/invalid inputs, calendar
  and financial edge cases, persistence, data integrity and the full interface flow.
  Adapt the privacy regression for newer Windows asyncio socketpair setup, with
  explicit checks that application loopback/external attempts remain denied.
  No financial application behavior changes for this packaging issue.
- Pin the already validated Ruff 0.16.4 so a fresh setup uses the same linter
  without unrelated UTC-alias refactoring; application dependency ranges unchanged.
- README exposes educational/financial/privacy limits and missing goal editing/
  completion controls. A demonstrable prototype does not mean every broader
  PLAN capability is implemented or that deployment is production ready.

## Validation and scope

Run both existing pytest entry points, Ruff, dependencies, links, ignore/index and
complete diff checks. Create a separate fresh Python environment from requirements
and test the walkthrough in a clean temporary main clone/browser. Record resolved
versions, actual results and anything unverified in the PR notes/description.
Use only synthetic fixtures; preserve user data and every existing branch.

Follow-ups remain deferred: use_container_width migration, optional first-launch
email documentation, independent LAN isolation and minimum-version verification.
Stop after opening the main-targeted PR for independent Chat 3 review.
