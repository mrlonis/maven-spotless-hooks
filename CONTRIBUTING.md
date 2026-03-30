# Contributing

Thanks for contributing to `maven-spotless-hooks`.

This repository provides Git hooks for downstream Maven projects that want `Spotless` to run automatically around `git commit`. The core product here is the behavior of the hooks themselves, especially around staged files, partially staged files, fully unstaged tracked changes, and safe recovery when something goes wrong.

## Ways to Contribute

Small fixes and documentation improvements are welcome directly.

For larger behavioral changes, please open an issue or start a discussion first, especially if the change affects:

- how partially staged files are handled
- how fully unstaged tracked changes are preserved
- recovery behavior after failures or interrupts
- downstream installation workflows
- cross-platform behavior on Windows, macOS, or Linux

This project is small, but the hook behavior is subtle. A “simple” change can easily alter what gets committed.

## Reporting Bugs

If you hit a bug, please include as much concrete detail as you can.

The most useful bug reports usually include:

- the platform where the issue happened: Linux, macOS, or Windows
- how Git was being run: terminal, Git Bash, GitHub Desktop, IDE integration, etc.
- the exact files involved and whether they were staged, partially staged, or unstaged
- the hook output or error message
- whether the problem happened in `pre-commit`, `post-commit`, or both
- whether the issue is reproducible in a small sample repo

If the bug involves formatting/restoration behavior, please be especially clear about:

- what was staged before `git commit`
- what was unstaged before `git commit`
- what you expected to be committed
- what actually ended up in `HEAD` and in the worktree

## Suggesting Changes

Suggestions are welcome, especially if they improve:

- safety and recovery behavior
- partial-staging behavior
- downstream setup or documentation
- test coverage
- cross-platform reliability

For larger suggestions, it helps to describe:

- the user workflow you are trying to improve
- the current behavior
- the desired behavior
- any tradeoffs or compatibility risks you see

## Repository Overview

Important files:

- `pre-commit`
  The main hook. This is where most of the complexity lives.
- `post-commit`
  A simpler follow-up hook that re-runs `spotless:apply`.
- `install-hooks.sh`
  Manual Unix installation helper.
- `install-hooks.ps1`
  Manual Windows installation helper.
- `tests/hook_harness.py`
  Cross-platform integration-style test harness.
- `tests/fake_mvn.py`
  Deterministic fake formatter used by the test harness instead of real Maven/Spotless.
- `.github/workflows/hook-tests.yml`
  CI matrix covering Linux, macOS, and Windows.
- `README.md` and `docs/`
  User-facing documentation.

## Project Principles

Please keep these principles in mind when making changes.

### 1. Preserve the User’s Work

If the hook fails, the user should still be able to recover their changes.

That means:

- do not silently discard worktree changes
- do not silently damage stash history
- preserve recovery artifacts when restoration fails
- prefer explicit recovery instructions over “best effort” magic

### 2. Respect Partial Staging

Partially staged files are a core edge case in this repository.

Current intended behavior:

- partially staged files are promoted to fully staged before formatting
- this includes partially staged newly added files
- fully unstaged tracked changes are temporarily hidden and restored later

Please do not change this behavior casually.

### 3. Keep It Cross-Platform

The hooks and tests need to work on:

- Linux
- macOS
- Windows

Git behavior is not identical across those environments, especially around:

- shell execution
- hook spawning
- line endings
- path formats
- Git Bash vs native Windows paths

If a change feels Unix-only, it probably needs another look.

### 4. Prefer Simplicity Over Cleverness

These scripts run in user repos during commits. Reliability matters more than elegance.

Prefer:

- POSIX `sh`
- explicit state transitions
- NUL-safe Git plumbing
- small, understandable helpers
- tests that prove observable behavior

Avoid:

- Bash-only features
- fragile filename handling
- hidden global Git state changes
- “works on my machine” shortcuts

## Development Guidelines

### Shell Compatibility

`pre-commit` and `post-commit` are POSIX shell scripts.

Please avoid:

- Bash arrays
- `[[ ... ]]`
- process substitution
- other Bash-specific syntax

### Line Endings

Hook scripts must stay `LF`-terminated.

This repository uses `.gitattributes` to enforce that. If hook execution breaks unexpectedly, line endings are one of the first things to check.

### Maven Invocation

The hooks currently run:

```sh
mvn spotless:apply -DratchetFrom=HEAD -q -T 1C
```

or:

```sh
./mvnw spotless:apply -DratchetFrom=HEAD -q -T 1C
```

Please be cautious when changing this command. Even small flag changes can affect downstream performance and compatibility.

## Testing

If you change hook behavior, run the local checks before opening a PR.

Minimum checks:

```sh
sh -n pre-commit
python3 -m unittest -v tests.hook_harness
```

The CI workflow runs the harness on Linux, macOS, and Windows.

### About the Test Harness

The test harness is intentionally integration-style.

It does not mock the hook internals. Instead, it:

- creates a temporary Git repo
- installs the real hooks into `.git/hooks/`
- injects fake `mvn` / `mvnw`
- optionally injects a fake `git` wrapper for failure-path testing
- runs real `git commit`
- asserts on commit contents, worktree contents, status, stash preservation, and recovery behavior

When adding behavior to the hooks, prefer extending the harness rather than adding narrow unit tests that do not exercise real Git behavior.

## Documentation

If behavior changes, please update the relevant docs too.

Most likely files:

- `README.md`
- `docs/ADVANCED-CONFIGURATION.md`
- `docs/TROUBLESHOOTING.md`

If the change is subtle, it is usually worth adding or updating comments in the hook or test harness as well. Future maintainers will thank you.

## Pull Requests

A good PR for this repo usually includes:

- a clear description of the problem
- a concise explanation of the behavioral change
- tests covering the new behavior or regression
- docs updates if user-visible behavior changed

Please call out any platform-specific considerations in the PR description, especially if you had to do something special for Windows.

## Pull Request Checklist

Before opening or marking a PR ready for review, please check:

- the change is scoped to a clear problem or improvement
- hook behavior changes are covered by tests
- `sh -n pre-commit` passes locally if `pre-commit` was touched
- `python3 -m unittest -v tests.hook_harness` passes locally if hook or harness behavior changed
- relevant docs were updated if user-visible behavior changed
- any Windows-specific considerations are called out in the PR description
- recovery behavior was considered if the change touches hidden/unstaged file handling

## What Not to Do

Please avoid changes that:

- wipe or rewrite the user’s stash history
- silently change what gets committed without tests
- remove recovery behavior without a replacement
- rely on non-portable shell features
- skip Windows considerations when touching hook execution or path handling

## Questions

If you are unsure whether a change fits the project’s intended behavior, open an issue or draft PR and explain the scenario you are trying to improve. That is usually the fastest way to align on the right direction.

Thanks again for helping improve the project.
