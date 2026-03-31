# 🧼☕🪝 maven-spotless-hooks

Running formatters in `pre-commit` is harder than it looks.

Most solutions use `git stash`. That’s where things go sideways.

- partially staged files get wrecked
- unstaged changes leak into commits
- stash apply turns into a merge problem

This repo uses a patch-based approach instead of `git stash`:

- hide only fully unstaged tracked changes
- run Spotless on exactly what you're committing
- restore your working tree without guesswork

The result is simple:

**auto-format on commit that doesn’t break Git.**

No stash. No merge weirdness. No surprises.

Prettier-style formatting for Maven.

Git-native. IDE-agnostic. Cross-platform.

## 📑 Table of Contents

<!-- TOC -->
* [🧼☕🪝 maven-spotless-hooks](#-maven-spotless-hooks)
  * [📑 Table of Contents](#-table-of-contents)
  * [⚖️ Why not just use Spotless pre-push?](#-why-not-just-use-spotless-pre-push)
  * [🎯 What this solves (in 10 seconds)](#-what-this-solves-in-10-seconds)
  * [🧩 What These Hooks Do](#-what-these-hooks-do)
  * [🪝 Included Hooks](#-included-hooks)
  * [🚀 Quickstart](#-quickstart)
    * [🔧 Installing the Git Hooks (required)](#-installing-the-git-hooks-required)
      * [🤖 Automatic Maven Hook Installation](#-automatic-maven-hook-installation)
        * [🧠 Note on IDEs](#-note-on-ides)
      * [⚠️ Manual Hook Installation (Not Recommended)](#-manual-hook-installation-not-recommended)
  * [🗺️ Flow Chart](#-flow-chart)
    * [🔀 Handling Staged and Unstaged Changes](#-handling-staged-and-unstaged-changes)
    * [🧭 Hook Behavior During Merge/Rebase](#-hook-behavior-during-mergerebase)
    * [🧰 Git Compatibility](#-git-compatibility)
  * [🧼 Setting up Spotless](#-setting-up-spotless)
  * [🛠️ Advanced Configuration](#-advanced-configuration)
  * [🤝 Contributing](#-contributing)
  * [🧯 Troubleshooting](#-troubleshooting)
<!-- TOC -->

## ⚖️ Why not just use Spotless pre-push?

Spotless now supports pre-push hooks, which run `spotless:check` before pushing (fail, don’t fix).

That enforces formatting, but doesn’t fix it for you.

This repo focuses on something different:

- automatically applying formatting at commit time
- preserving partial staging
- avoiding `git stash` entirely

Use both for a zero-friction workflow:

- `pre-commit`: auto-fix
- `pre-push`: final enforcement

## 🎯 What this solves (in 10 seconds)

1. Stage part of a file
2. Leave the rest unstaged
3. Commit

- Expected: only staged code is formatted
- Actual (most tools): chaos

This repo does exactly what you expected.

## 🧩 What These Hooks Do

This repo provides Git `pre-commit` and `post-commit` hooks that automatically run `Spotless` on files you've changed.
The `pre-commit` hook is careful about staged vs unstaged work so that formatting is applied to what you are committing
without trampling unrelated tracked changes in your working tree.

## 🪝 Included Hooks

- `pre-commit`: Promotes partially staged files, hides fully unstaged tracked changes, runs `Spotless`, and restores
  hidden changes
- `post-commit`: Re-runs `Spotless` after commit to handle any remaining changed files in the working tree

## 🚀 Quickstart

Add this repo as a [git submodule](https://git-scm.com/book/en/v2/Git-Tools-Submodules) to keep it up to date. 
[Advanced configuration](#️-advanced-configuration) is required to automate updates, but is not needed to get started.

If you have the `spotless-maven-plugin` already configured, you can add this repo as a submodule and manually
install the hooks by running the following command in the root of your project:

```sh
git submodule add -b main https://github.com/mrlonis/maven-spotless-hooks.git .hooks/

# Install the hooks
# If on Mac or Linux
./.hooks/install-hooks.sh
# If on Windows
.\.hooks\install-hooks.ps1

# Commit submodule addition - Also tests the hooks are installed
git commit -m "Adding maven-spotless-hooks"
```

This will add the `maven-spotless-hooks` repo as a `submodule` in the `.hooks` folder within your project, and
install the `pre-commit` and `post-commit` hooks into the `.git/hooks/` directory. This runs `spotless` automatically 
when you commit.

If you do not have `spotless` set up within your project, please refer to [SPOTLESS-CONFIG.md](./docs/SPOTLESS-CONFIG.md).

### 🔧 Installing the Git Hooks (required)

If you followed the [Quickstart](#-quickstart) instructions, you should have the submodule added within your project, and
the hooks installed, albeit manually. The next step is to ensure that the hooks are installed automatically, so you
don't have to worry about it in the future and so that other developers don't need to perform any additional
configuration to work on your project. This can be done by adding the `git-build-hook-maven-plugin` to your `pom.xml`
file, as described below.

#### 🤖 Automatic Maven Hook Installation

To setup automatic hook installation via `Maven`, add the following `plugin` to your application's `pom.xml` `<plugins>`
section:

<!-- markdownlint-disable-next-line MD033 -->
<details><summary>View <code>pom.xml</code> plugin</summary>

```xml
<plugin>
  <groupId>com.rudikershaw.gitbuildhook</groupId>
  <artifactId>git-build-hook-maven-plugin</artifactId>
  <version>${git-build-hook-maven-plugin.version}</version> <!-- Set this to the latest version -->
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

</details>

##### 🧠 Note on IDEs

Most IDEs (like `IntelliJ` or `Eclipse`) run `Maven` commands using an embedded runner or internal build process, which
may not trigger all `Maven` plugin goals, including this hook installation. To ensure the `git-build-hook-maven-plugin`
installs the hooks correctly, you should run `Maven` commands (like `mvn clean install`) from the `terminal`, **at least
once per fresh clone or submodule update**.

This aligns your local workflow with your CI/CD environment, **which always uses CLI Maven**, and helps catch any setup
or formatting issues early.

#### ⚠️ Manual Hook Installation (Not Recommended)

You can manually install the hooks, as described in the [quickstart](#-quickstart) section, by running
`./.hooks/install-hooks.sh` if on **Mac** or **Linux**, or `.\.hooks\install-hooks.ps1` if on **Windows**.

> **Note**: The above commands assume you are in the root of your project that has added this repo as a submodule,
> and that the submodule was added to the `.hooks` folder. If you are not, you will need to adjust the path to the
> `install-hooks.sh` or `install-hooks.ps1` script accordingly.

## 🗺️ Flow Chart

```pqsql
git commit
   ↓
pre-commit hook
   ↓
promote partially staged files
   ↓
hide fully unstaged tracked changes
   ↓
spotless:apply
   ↓
re-stage formatter edits (only if spotless succeeds)
   ↓
restore hidden tracked changes
   ↓
post-commit hook
   ↓
spotless:apply
   ↓
commit allowed or blocked (only blocked by `spotless` or pre-commit errors)
```

### 🔀 Handling Staged and Unstaged Changes

The `pre-commit` hook intentionally does **not** use `git stash` anymore.

Instead, it uses a patch-based workflow:

- partially staged files are promoted to fully staged before formatting
- fully unstaged tracked changes are saved as a temporary patch
- those fully unstaged tracked files are restored to index state before `spotless:apply` runs
- after formatting finishes, the hidden patch is re-applied to the working tree

This keeps the commit focused on the intended staged changes while leaving the user's existing stash history alone.

If `spotless:apply` itself fails, the hook restores any hidden tracked changes and aborts the commit without re-staging
formatter edits into the index.

If the hook cannot restore the hidden patch, it preserves the temporary workspace and prints the path to the recovery
patch so the user can apply it manually with `git apply`.

### 🧭 Hook Behavior During Merge/Rebase

These hooks are merge-aware and won’t interfere with merge commits or rebases. In the event of a merge or rebase, the
hooks will exit early and not run `spotless`.

### 🧰 Git Compatibility

The `pre-commit` hook prefers `git restore --worktree` when it is available, but it falls back to `git checkout --` for
older Git versions that do not support `git restore`.

Using a modern Git version is still recommended, especially on Windows.

## 🧼 Setting up Spotless

For more information on how to set up `spotless`, please refer to [SPOTLESS-CONFIG.md](./docs/SPOTLESS-CONFIG.md).

## 🛠️ Advanced Configuration

For more advanced configuration information, such as how to automatically update the submodule with Maven, exclude
submodule updates during CI, or a sample `README.md` change to make to your project, please refer
to [ADVANCED-CONFIGURATION.md](./docs/ADVANCED-CONFIGURATION.md).

## 🤝 Contributing

For contributing guidelines, please refer to [CONTRIBUTING.md](./CONTRIBUTING.md).

## 🧯 Troubleshooting

For troubleshooting, please refer to [TROUBLESHOOTING.md](./docs/TROUBLESHOOTING.md).
