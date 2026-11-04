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

### 1. Add a Closing Keyword to the Actual GitHub PR Description

Use `Closes #<number>` in the actual GitHub PR description when the PR resolves the issue. A local record in `docs/pull-requests/` alone does not activate GitHub closing keywords; copy the relevant text into the PR description.

Example PR description:
```markdown
## Summary
Closes #2 by documenting the purpose of the Financial Assistant.
```

GitHub interprets PR closing keywords only when the PR targets the repository's default branch. With automatic issue closure enabled, merging that PR into the default branch closes the linked issue automatically. Verify the default branch rather than assuming it is `main`. Keywords in PRs targeting other branches are ignored for automatic linking and closure.

### 2. Verify the Link and Merge Only When Authorized

Check the GitHub Development sidebar for the linked issue or PR. Users with write permissions can also use this sidebar on an issue or PR to create a structured link manually. A mention in a comment or a local Markdown file is not a substitute for this link.

Merge only after review and user authorization. For PRs targeting the default branch, verify automatic issue closure after merging.

### 3. Close an Issue Manually Only When Appropriate

Use `gh issue close` only when explicitly closing the issue is appropriate and authorized, for example when completed work has been verified but automatic closure did not occur. Do not close an issue merely to establish a PR relationship or because a PR merged into a non-default branch.

Manually closing an issue changes its status; it does not create a structured PR closing relationship. A comment referencing a PR provides context but does not create that relationship either. Use the Development sidebar to link the issue and PR when needed.

```bash
gh issue close <number> --comment "Resolved by PR #<pr-number>"
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

### 5. Verify Closure and the Relationship Separately

- Confirm the issue is closed only when the work is complete and closure is appropriate.
- Confirm the issue and PR are linked in GitHub's Development sidebar.
- For keyword-based linking, confirm `Closes #<number>` appears in the actual GitHub PR description and the PR targets the default branch.
- Do not treat a Closed badge or a PR mention as proof of a structured closing relationship.

Reference: [GitHub Docs: Linking a pull request to an issue](https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/linking-a-pull-request-to-an-issue).

When the user asks to review a pull request, act as a Senior Software Engineer.

- Evaluate correctness, edge cases, maintainability, test coverage, security, performance, and documentation quality.
- Provide specific, actionable findings instead of generic approval.
- State a clear review decision: approved, changes requested, or comments only.
- Document the review feedback and final review decision as a comment in the conversation.
- Do not treat a GitHub review comment as the required output; the required artifact is the conversation comment. Do not post a GitHub review unless the user separately requests it.
- If GitHub commenting is not available or the user asks for local documentation, save the same review notes in `docs/pull-requests/` with the exact text to post later.
- Keep the review concise, professional, and engineering-focused.
