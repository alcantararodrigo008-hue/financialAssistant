# GitHub workflow

Follow [AGENTS.md](../AGENTS.md) for the permanent Developer/Senior Engineer responsibilities. A branch is a separate line of work; a pull request (PR) proposes bringing that work into `main` for review.

## Start one issue

Read the complete GitHub issue and its acceptance criteria, then check `git status`. Preserve existing work: do not discard, overwrite, or include unrelated changes. If existing edits prevent a safe branch switch, stop and resolve that separately with the user.

With a safe working directory, update `main` and create one branch per issue:

```powershell
git fetch --no-prune origin
git switch main
git merge --ff-only origin/main
git switch -c issue-3-define-github-workflow
```

Replace the example branch name with `issue-<number>-<short-description>`. A fast-forward moves the branch forward without rewriting commits. If it fails, inspect the history before continuing; do not reset, rebase, or force-push to bypass it.

## Implement and validate

Keep each PR small and focused on its issue. Add relevant documentation and tests for changed behavior. Record issue notes in `docs/issues/` and PR notes in `docs/pull-requests/`.

For Python changes, run the relevant tests and lint checks:

```powershell
python -m pytest -q
python -m ruff check app.py main.py src tests
```

For documentation, review accuracy, check local links, and run `git diff --check`. Explain checks that do not apply. Never commit local databases, installers, caches, or secrets.

## Commit and open a PR

Use clear conventional commit messages: `feat: add expense registration`, `fix: reject zero amounts`, or `docs: define GitHub workflow`. Keep commits focused. Stage specific intended files, then inspect `git diff --cached` before committing; avoid staging unrelated local edits.

Once authorized to publish the work:

```powershell
git commit -m "docs: define GitHub workflow"
git push --set-upstream origin issue-3-define-github-workflow
gh pr create --base main
```

The [PR template](../.github/pull_request_template.md) provides the summary, validation, and checklist. Include `Closes #3` (using the actual issue number) in the actual GitHub PR description when the work fully resolves the issue. A local PR note alone does not activate closing keywords.

GitHub discovers PR templates from the repository's default branch, currently `issue-1-configure-python-environment`, not `main`. Automatic discovery of this template is currently unavailable under the existing configuration. Merging the template into `main` alone will not automatically populate new PR descriptions. See [GitHub's template documentation](https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/creating-a-pull-request-template-for-your-repository).

Until the template is available on the default branch, use this manual fallback:

1. Open `.github/pull_request_template.md` on your issue branch (or `main` after this PR merges).
2. Copy its contents into the actual GitHub PR description, either while creating the PR or by editing its description afterward.
3. Replace placeholders with the real issue number, changes, validation results, and limitations.
4. Complete the checklist before requesting independent review.

**Current repository limitation:** GitHub's default branch is `issue-1-configure-python-environment`, while this workflow targets `main`. Closing keywords are interpreted only for PRs targeting the default branch. Until the owner changes that setting, do not assume a merge into `main` automatically links or closes an issue. Use the Development sidebar to link the issue and PR. Manual closure requires appropriate explicit authorization and does not itself create a structured closing relationship. Do not change repository settings as part of routine issue work.

## Review before merging

Developer Codex opens the PR and stops for independent Senior Engineer Codex review. Required changes are discussed in the Codex conversation. The developer addresses them on the same branch, validates, commits, and pushes; the Senior Engineer re-reviews the latest head until satisfied.

Once approved, the Senior Engineer checks for duplicates and posts exactly one final ordinary GitHub comment explaining the scope reviewed, satisfied requirements, validation results, and suitability for `main`, ending with `Final decision: APPROVED FOR MERGE`. No intermediate GitHub review comments are posted. An ordinary comment is not an official GitHub approval.

The Senior Engineer never merges. The user or an explicitly authorized developer verifies the latest reviewed commit, target, conflicts, and checks before merging. A merge commit preserves the issue commits. Branch deletion and history rewriting require separate explicit authorization.
