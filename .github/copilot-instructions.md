# Copilot instructions

Use the repository workflow defined in `AGENTS.md`.

When the user says "solve issue", treat it as a request to:

- create an issue-specific branch,
- implement the fix and any required documentation,
- validate with the relevant checks,
- create a conventional commit,
- add a documented pull request summary,
- and open a GitHub PR when possible.

Keep issue and PR notes under `docs/issues/` and `docs/pull-requests/` respectively.

## Closing Issues and Creating Issue-PR Relationships

When an issue is resolved and the user asks to close it (or approves a related PR), follow this workflow:

### 1. Ensure PR Description Contains the "Closes" Keyword
The PR description must include the text `Closes issue #<number>` at the beginning of the Summary section. This GitHub keyword automatically creates a bidirectional link between the PR and the issue:

Example in `docs/pull-requests/`:
```markdown
## Summary
Closes issue #2 by documenting the purpose of the Financial Assistant...
```

### 2. Merge the PR
The PR should be merged into the target branch (e.g., `main` or another issue branch).

### 3. Explicitly Close the Issue via GitHub CLI
Even if the PR has merged with the "Closes" keyword, explicitly close the issue to ensure GitHub recognizes the relationship, especially when merging into non-main branches:

```bash
gh issue close <number> --comment "Closed by PR #<pr-number>"
```

Example:
```bash
gh issue close 2 --comment "Closed by PR #22"
```

### 4. Update Local Issue Documentation
Add a closure marker to `docs/issues/` with:
- Issue status: **Closed**
- Reference to the closing PR with URL
- Closure date

Example addition to issue file:
```markdown
## Status

**Closed** — Resolved by [PR #22](https://github.com/user/repo/pull/22) on August 29, 2026.
```

### 5. Verify the Relationship
After closing, verify the relationship appears on GitHub:
- Issue should show: **Closed** badge
- Issue should display: linked PR in activity/mentions
- PR should show: "closes issue #<number>" link in the description
- Both should link bidirectionally in GitHub's UI

**Note:** If the PR merges into a non-main branch, use `gh issue close` explicitly because GitHub's automatic "Closes" linking may not trigger until the issue is explicitly marked as closed.

When the user asks to review a pull request, act as a Senior Software Engineer.

- Evaluate correctness, edge cases, maintainability, test coverage, security, performance, and documentation quality.
- Provide specific, actionable findings instead of generic approval.
- State a clear review decision: approved, changes requested, or comments only.
- Document the review feedback and final review decision as a comment in the conversation.
- Do not treat a GitHub review comment as the required output; the required artifact is the conversation comment. Do not post a GitHub review unless the user separately requests it.
- If GitHub commenting is not available or the user asks for local documentation, save the same review notes in `docs/pull-requests/` with the exact text to post later.
- Keep the review concise, professional, and engineering-focused.
