# Issue 3: Define the GitHub workflow

Source: [GitHub Issue #3](https://github.com/alcantararodrigo008-hue/financialAssistant/issues/3).

## Requirements implemented

- One branch per issue, with naming and safe synchronization examples.
- Small PRs and focused conventional commits.
- A PR template with a review checklist.
- Independent review and feedback before authorized merging.
- Beginner-friendly instructions in [the workflow guide](../github-workflow.md).

## Limitations

GitHub's default branch currently differs from `main`; the guide explains the effect on automatic issue closure. No repository settings are changed. Implementation is ready for independent review; the issue is not marked closed.

GitHub discovers PR templates from the default branch, currently `issue-1-configure-python-environment`. Automatic discovery of this template is currently unavailable; merging it into `main` alone will not populate new PR descriptions. The guide provides a manual fallback: open `.github/pull_request_template.md`, copy it into the actual GitHub PR description, replace placeholders with real information, and complete the checklist before requesting review.
