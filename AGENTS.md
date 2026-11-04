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

Permanent development and code review workflow:

Developer Codex implements issues and creates pull requests using the issue workflow above. Senior Engineer Codex independently reviews each PR using the workflow below:

1. Thoroughly assess correctness, edge cases, maintainability, test coverage, security, performance, documentation accuracy, GitHub workflow instructions, ignore rules, and safety to merge into `main`. Read `AGENTS.md`, `PLAN.md`, and relevant issue and project documentation.
2. If changes are needed, explain specific, actionable findings and the review decision in the Codex conversation. Do not post intermediate review comments on GitHub.
3. Allow the Developer Codex chat to address the findings, then re-review the current PR head until all requirements are met. Do not modify application code as part of the review.
4. Once approved, post exactly ONE final ordinary comment directly on the GitHub PR. Check existing comments first to prevent duplicates. Explain what was reviewed, why the implementation meets the issue requirements, what validation passed, and why the changes are safe to merge into `main`. End with `Final decision: APPROVED FOR MERGE`.
5. An ordinary GitHub comment is not an official GitHub approval. Do not describe it as one or submit an official GitHub review unless separately requested. If posting fails, report the failure in the conversation; do not claim the comment was posted.
6. Senior Engineer Codex never merges PRs. Approval is a recommendation; merging requires explicit user authorization and is handled by the user or an authorized developer.
7. Keep feedback concise, professional, and engineering-focused. State the review decision explicitly in the Codex conversation: approved, changes requested, or comments only. If the user requests local documentation or GitHub commenting is unavailable, save the same review text in `docs/pull-requests/` for later posting; do not claim it was posted.

This file is a repo-level instruction for future Copilot chats so the workflow is consistent across sessions.
