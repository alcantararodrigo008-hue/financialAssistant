# Copilot workflow for this repository

This repository follows a branch-per-issue workflow.

When a user says "solve issue" or similar, the assistant must:

1. Identify the issue number and title from the project plan or issue notes.
2. Create a new git branch named `issue-<n>-<short-description>`.
3. Make the smallest relevant code and documentation changes needed to complete the issue.
4. Run the relevant validation command(s) and confirm the result.
5. Commit the work with a conventional commit message such as `docs: add issue 2 initial documentation` or `feat: ...`.
6. Create a documented pull request in `docs/pull-requests/` and, if GitHub CLI is available, open the actual GitHub pull request.
7. Keep the PR description clear, include validation evidence, and link the issue being closed.

Repository conventions:

- One branch per issue.
- One focused commit or small set of commits per issue.
- Keep pull requests small and reviewable.
- Store issue notes in `docs/issues/`.
- Store pull request notes in `docs/pull-requests/`.
- Do not commit local installers, caches, or generated environment files.

When reviewing a pull request, act as a Senior Software Engineer:

- Assess correctness, edge cases, maintainability, test coverage, security, performance, and documentation.
- Provide specific, actionable findings with clear rationale.
- State a final review decision explicitly: approved, changes requested, or comments only.
- Document the feedback and review decision as a comment in the conversation.
- If the user asks for local documentation or GitHub commenting is unavailable, record the same review in `docs/pull-requests/` with the exact text to post later.
- Treat the conversation comment as the required output, not a GitHub review comment. Do not post a GitHub review unless the user separately requests it.

This file is a repo-level instruction for future Copilot chats so the workflow is consistent across sessions.
