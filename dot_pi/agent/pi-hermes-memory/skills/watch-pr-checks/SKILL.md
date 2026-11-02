---
name: "watch-pr-checks"
description: "Watch GitHub Actions CI checks for a pull request, inspect failed workflow logs with gh CLI, diagnose and fix failures, and verify until all checks pass. Triggered by 'watch pr', 'check pr actions', 'monitor pr ci', or 'fix pr checks'."
version: 1
created: "2026-11-02"
updated: "2026-11-02"
---
## When to Use
Use when asked to monitor GitHub PR checks, diagnose CI workflow failures, debug failing GitHub Actions, or fix CI errors on a pull request across any repository using GitHub Actions and GitHub CLI (gh).

## Procedure
1. Identify the target PR number or branch using 'gh pr list' or 'gh pr view'.
2. Monitor CI status using 'gh pr checks <pr-number> --watch'.
3. If any check fails, retrieve the run ID and inspect logs using 'gh run view <run-id> --log-failed', or inspect a specific job with 'gh run view <run-id> --job <job-id> --log'.
4. Reproduce the failure locally with the appropriate test, linter, or build command.
5. Implement the minimal targeted fix for the root cause.
6. Verify the fix locally using the exact command that failed in CI.
7. Commit following project conventions and push to the PR's tracking branch.
8. Resume 'gh pr checks <pr-number> --watch' until all checks report 'pass'.

## Pitfalls
- Do not poll 'gh pr checks' in a tight bash loop with sleep; use 'gh pr checks <pr> --watch' which refreshes every 10s natively.
- Do not guess failure causes without reading 'gh run view <run-id> --log-failed'; CI environments often expose race conditions, linter strictness, or version differences not seen in casual local runs.
- Do not push fixes to main or detached HEAD; always verify the current branch tracks the PR branch ('git status' / 'git branch -vv').
- Ensure local pre-commit hooks, linters, and typecheck pass before pushing fixes to prevent introducing secondary failures.

## Verification
1. 'gh pr checks <pr-number>' reports 'pass' for all checks on the latest commit.
2. The PR checks exit with code 0 and no failed jobs remain.