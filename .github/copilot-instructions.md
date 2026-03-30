# GitHub Copilot Instructions for `maven-spotless-hooks`

## What This Repository Is

This repository ships Git hooks for downstream Maven projects that want `Spotless`
to run automatically around `git commit`.

The intended consumption model is:

- a downstream repository adds this repository as a git submodule, usually at `.hooks/`
- the downstream repository installs the hooks into `.git/hooks/`
- hook installation is typically automated via the
  `com.rudikershaw.gitbuildhook:git-build-hook-maven-plugin`

The core value of this repository is **hook behavior**, not a Java library or a
standalone CLI. When you work in this repo, think in terms of:

- index state
- worktree state
- downstream git-hook installation
- cross-platform Git behavior
- safe recovery when formatting or restore steps fail

## Repository Layout

Key files and their roles:

- [`README.md`](../README.md)
  High-level usage and downstream setup docs.
- [`pre-commit`](../pre-commit)
  The main hook. This is the most important file in the repository.
- [`post-commit`](../post-commit)
  A simpler follow-up hook that re-runs `spotless:apply`.
- [`install-hooks.sh`](../install-hooks.sh)
  Manual Unix installation helper.
- [`install-hooks.ps1`](../install-hooks.ps1)
  Manual Windows installation helper.
- [`tests/hook_harness.py`](../tests/hook_harness.py)
  Cross-platform test harness that spins up disposable git repos and executes the
  real hooks against them.
- [`tests/fake_mvn.py`](../tests/fake_mvn.py)
  Fake deterministic formatter used by the harness instead of real Maven/Spotless.
- [`tests/__init__.py`](../tests/__init__.py)
  Test package marker.
- [`docs/SPOTLESS-CONFIG.md`](../docs/SPOTLESS-CONFIG.md)
  Downstream Spotless setup docs.
- [`docs/ADVANCED-CONFIGURATION.md`](../docs/ADVANCED-CONFIGURATION.md)
  Advanced downstream integration guidance.
- [`docs/TROUBLESHOOTING.md`](../docs/TROUBLESHOOTING.md)
  Troubleshooting guidance.
- [`.github/workflows/hook-tests.yml`](workflows/hook-tests.yml)
  CI matrix for Linux, macOS, and Windows.
- [`.gitattributes`](../.gitattributes)
  Forces shell-facing files to `LF`, which is important for hook execution.

## Source of Truth

For behavior questions, the order of trust should be:

1. [`pre-commit`](../pre-commit)
2. [`tests/hook_harness.py`](../tests/hook_harness.py)
3. [`README.md`](../README.md) and `docs/`

If implementation and docs diverge, prefer fixing the docs to match the tested
implementation unless the implementation is clearly wrong.

## Core Product Semantics

The goal is **not** “format everything in the repo.”

The goal is:

- format what is being committed
- keep unrelated fully unstaged tracked changes out of the commit
- treat partially staged files carefully so formatting sees the whole file
- avoid mutating the user’s stash history
- give the user a recovery artifact if the hook cannot restore hidden changes

### Current `pre-commit` Flow

The current `pre-commit` behavior is intentional and should not be changed
casually:

1. Exit early for merge commits.
2. Exit early if there is nothing staged.
3. Identify staged files, including staged adds, excluding only deletions.
4. Detect partially staged files by intersecting:
   the staged set and files that still differ in the worktree.
5. Promote only those partially staged files to fully staged with
   `git add --pathspec-from-file=... --pathspec-file-nul`.
6. After that promotion step, treat remaining tracked worktree changes as fully
   unstaged tracked changes.
7. Save those fully unstaged tracked changes as a patch using a NUL-safe,
   non-colored `git diff --binary` invocation.
8. Restore those paths back to index state with `git restore --worktree`.
9. Run `spotless:apply`.
10. Re-stage formatter edits with `git add -u`.
11. Re-apply the hidden patch with `git apply`.
12. Abort if nothing remains staged at the end.

### Why This Uses a Patch Instead of `git stash`

Do not casually revert to stash-based logic.

The current patch-based design exists because:

- `git stash` mutates shared repo state
- `git stash` can interfere with the user’s existing stash stack
- `stash pop` is merge-like and increases restore/conflict complexity
- a local patch is narrower, easier to reason about, and easier to recover from

Important invariant:

- this hook must **not** clear, rewrite, or otherwise damage the user’s stash
  history

## `pre-commit` Invariants You Should Preserve

If you change [`pre-commit`](../pre-commit),
preserve these properties unless the repository owner explicitly wants different
behavior:

- Use POSIX `sh`, not Bash-only features.
- Keep filename handling NUL-safe.
- Do not assume filenames are whitespace-safe.
- Do not use `git stash clear`.
- Do not silently consume or mutate the user’s stash entries.
- Partially staged files must be promoted before formatting.
- This promotion must include partially staged **new** files as well as already
  tracked files.
- Fully unstaged tracked changes must be kept out of the commit.
- If hidden changes cannot be restored, preserve the recovery patch and tell the
  user how to apply it.
- Recovery patch generation must be forced to plain text with no ANSI color.
- Signal handling must not delete the only recovery artifact after hidden changes
  have been removed from the worktree.

## `post-commit` Semantics

[`post-commit`](../post-commit) is intentionally
simple:

- it re-runs `spotless:apply`
- it uses the same Maven command shape as `pre-commit`

Important nuance:

- the current test suite locks in the fact that `pre-commit` keeps fully
  unstaged tracked changes out of `HEAD`
- however, `post-commit` may still format the restored working-tree copy after
  the commit

So today the behavior is:

- the unrelated file stays out of the commit
- the working tree may come back modified after commit because `post-commit`
  reformatted it

If you change that behavior, update tests and docs together.

## Downstream Installation Model

This repository is designed to live as a submodule in another repo, commonly at
`.hooks/`.

The downstream Maven plugin configuration typically looks like:

```xml
<plugin>
  <groupId>com.rudikershaw.gitbuildhook</groupId>
  <artifactId>git-build-hook-maven-plugin</artifactId>
  <configuration>
    <installHooks>
      <pre-commit>.hooks/pre-commit</pre-commit>
      <post-commit>.hooks/post-commit</post-commit>
    </installHooks>
  </configuration>
  <executions>
    <execution>
      <goals>
        <goal>install</goal>
      </goals>
    </execution>
  </executions>
</plugin>
```

When editing install or usage docs, remember:

- the submodule path is conventionally `.hooks`
- [`install-hooks.sh`](../install-hooks.sh)
  and [`install-hooks.ps1`](../install-hooks.ps1)
  currently assume that path and assume the caller is at the downstream repo root
- changes here affect real downstream developer workflows, not just this repo

## Maven / Spotless Command Contract

The hooks currently use:

```sh
mvn spotless:apply -DratchetFrom=HEAD -q -T 1C
```

or:

```sh
./mvnw spotless:apply -DratchetFrom=HEAD -q -T 1C
```

Important intent:

- `ratchetFrom=HEAD` keeps Spotless focused on files changed since the last commit
- `-q` keeps hook output quieter
- `-T 1C` is meant to help large multi-module Maven repos without causing major
  downside for single-module repos
- `command -v mvn` is used because some Windows environments, including GitHub
  Desktop-style workflows, may expose `mvn` differently than Unix shells

If you change this command, think about:

- downstream projects with Maven Wrapper only
- monorepo performance
- thread-safety assumptions
- whether tests need additional fake formatter modes

## Shell and Cross-Platform Rules

### Hook Scripts

The hook scripts are intentionally plain POSIX shell.

Prefer:

- `if [ ... ]`
- `command -v`
- simple functions
- NUL-safe `git` plumbing
- `xargs -0`

Avoid:

- Bash arrays
- `[[ ... ]]`
- `local` if strict POSIX compatibility matters
- process substitution
- assumptions that GNU-only flags exist everywhere

### Line Endings

Line endings matter for hooks.

[`.gitattributes`](../.gitattributes) forces:

- `*.sh` to `LF`
- `pre-commit` to `LF`
- `post-commit` to `LF`

Do not remove this.

If hook execution mysteriously breaks on Windows, check line endings first.

### Paths

Git on Windows is a hybrid environment. The following are all different contexts:

- Python on Windows
- PowerShell / `cmd`
- Git Bash / `sh`
- native filesystem paths like `C:\...`
- shell paths like `/c/...`

Do not assume a path that works in one of these contexts works in another.

## Test Harness Architecture

The test harness is intentionally integration-like even though it runs quickly.

[`tests/hook_harness.py`](../tests/hook_harness.py)
does **not** test the hook by mocking shell functions. It:

- creates a temporary git repo
- configures git user/email
- installs the real hook scripts into `.git/hooks/`
- prepends a temp `.test-bin/` directory to `PATH`
- injects fake `mvn` / `mvnw`
- optionally injects a fake `git` wrapper for specific failure modes
- runs real `git commit`
- asserts on:
  - commit exit code
  - committed contents
  - worktree contents
  - git status
  - stash preservation
  - preserved recovery patch behavior

This is the preferred testing style for this repository.

If you add new hook behavior, prefer extending the harness instead of inventing a
totally separate unit-test style.

## Fake Formatter Design

[`tests/fake_mvn.py`](../tests/fake_mvn.py)
replaces real Maven/Spotless during tests.

It supports mode-driven behavior:

- `noop`
  does nothing
- `staged`
  formats only the files that look changed relative to `HEAD`
- `conflict`
  formats all tracked files

The fake formatter:

- replaces `BAD` with `GOOD`
- replaces `BASE` with `FORMATTED`
- trims trailing whitespace
- writes back `LF`

This gives deterministic, low-cost hook tests without needing Java, Maven, or
the real Spotless plugin.

## Fake `git` Wrapper Design

The harness also provides a fake `git` wrapper in `.test-bin/`.

Its purpose is not to reimplement git. Its purpose is to:

- intercept one specific git command pattern
- fail it in a deterministic way
- delegate all other commands to the real git binary

This is how the harness tests error paths like:

- recovery patch generation failure
- `git restore --worktree` failure
- partial-stage promotion failure
- `git apply` restore failure

If you change hook internals and a failure-path test stops firing, check the
wrapper match logic in both:

- the `sh` wrapper
- the `git.cmd` wrapper

Both may need updates when command shapes change.

## Important Windows Test Harness Nuances

The harness contains several pieces of Windows-specific logic that are easy to
break accidentally.

### The Generated Hook Copy Must Start With `#!` at Byte 0

The harness installs a test-local copy of each hook instead of editing the source
file in place.

Do not generate that hook copy with leading indentation before the shebang.
Git for Windows is stricter than Linux/macOS and can fail with:

```text
error: cannot spawn .git/hooks/pre-commit: No such file or directory
```

if the shebang is not at the first byte.

### `PATH` Injection Must Use Shell Paths on Windows

The harness-generated hook copy prepends `.test-bin` to `PATH` so the hook itself
sees the fake `git` and fake `mvn`.

On Windows, shell `PATH` entries for Git Bash must use `/c/...` form, not raw
`C:/...`, because the drive-letter colon collides with shell path separators.

That is why the harness has `_shell_path(...)`.

### The `sh` Wrapper Uses a Shell-Normalized Real Git Path

The shell-side fake `git` wrapper delegates to `REAL_GIT_SH`, not `REAL_GIT`,
because Git Bash is more reliable with `/c/...` paths than with raw native
Windows paths.

The `git.cmd` wrapper still uses the native Windows path.

### Patch Files Must Be Written With `LF`

For partial-stage simulation, writing a patch file and applying it is more
reliable than piping patch text over stdin on Windows. Text-mode stdin can
rewrite newlines and break `git apply`.

### Recovery Patch Paths Need Translation in Python

When the hook prints a preserved recovery patch path on Windows, it may come out
as `/c/...` or `/tmp/...` from Git Bash.

The harness translates those to native Windows paths before it calls
`Path.exists()`.

If recovery-patch assertions fail on Windows only, check this translation logic
first.

## Partial Staging Rules

Partial staging is the hardest part of this repository and should be treated as a
high-risk area.

Current intended rules:

- partially staged tracked files are promoted to fully staged before formatting
- partially staged newly added files are also promoted before formatting
- fully unstaged tracked files are hidden behind a patch and restored later

Why:

- hiding the unstaged half of a partially staged file, formatting the staged
  half, and then replaying the old unstaged hunk is much more likely to conflict
  or reintroduce stale formatting
- promoting the whole file is simpler and more deterministic

The harness includes explicit coverage for:

- partially staged tracked files
- partially staged new files

If you touch this logic, add or update tests immediately.

## Recovery and Failure Semantics

Failure handling is part of the product.

The hook must fail safely.

Important rules:

- if recovery patch generation fails, abort
- if hiding fully unstaged tracked changes fails, preserve artifacts and abort
- if restoring hidden changes fails, preserve artifacts and print a manual
  `git apply` command
- if the hook is interrupted by `HUP`, `INT`, or `TERM` after the recovery patch
  exists, preserve the artifacts instead of deleting them
- the recovery patch must be usable even if the user forces colored diff output

This is why recovery patch generation uses:

```sh
git -c color.ui=false diff --no-color --binary ...
```

## Test Philosophy

When you add or change behavior:

- update the hook
- update the harness
- run the harness locally
- keep Linux, macOS, and Windows in mind

Prefer tests that prove the external observable behavior:

- what got committed
- what stayed out of the commit
- what remains in the worktree
- whether recovery artifacts exist and are usable

Do not overfit the tests to exact incidental command ordering unless there is a
good reason.

## What to Run Before Finishing a Change

At minimum:

```sh
sh -n pre-commit
python3 -m unittest -v tests.hook_harness
```

In CI, Windows uses:

```sh
python -m unittest -v tests.hook_harness
```

If you change only docs, tests may not be necessary. If you change hook behavior,
they are necessary.

## When Editing Docs

If behavior changes, check whether these need updates:

- [`README.md`](../README.md)
- [`docs/ADVANCED-CONFIGURATION.md`](../docs/ADVANCED-CONFIGURATION.md)
- [`docs/TROUBLESHOOTING.md`](../docs/TROUBLESHOOTING.md)
- this file

The implementation and test harness are more authoritative than prose docs, but
the docs should still describe the real behavior.

## Practical Advice for Copilot

When suggesting changes in this repository, optimize for:

- correctness over cleverness
- recovery over silent failure
- portability over shell tricks
- explicit state transitions over magic
- tests that model real git behavior

When in doubt:

- preserve the user’s worktree
- preserve recovery artifacts
- preserve stash safety
- preserve cross-platform behavior
- add a harness test
