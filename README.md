# 🧼☕🪝 maven-spotless-hooks

These hooks are Git-native and IDE-agnostic. You do not need to configure anything inside IntelliJ, Eclipse, or VS Code.

## 📑 Table of Contents

- [🧼☕🪝 maven-spotless-hooks](#-maven-spotless-hooks)
  - [📑 Table of Contents](#-table-of-contents)
  - [🧩 What These Hooks Do](#-what-these-hooks-do)
  - [🪝 Included Hooks](#-included-hooks)
  - [🗺️ Flow Chart](#️-flow-chart)
    - [🔀 Conflict Resolution](#-conflict-resolution)
    - [🧭 Hook Behavior During Merge/Rebase](#-hook-behavior-during-mergerebase)
  - [🚀 Quickstart](#-quickstart)
    - [🔧 Installing the Git Hooks](#-installing-the-git-hooks)
      - [🤖 Automatic Maven Hook Installation](#-automatic-maven-hook-installation)
        - [🧠 Note on IDEs](#-note-on-ides)
      - [⚠️ Manual Hook Installation (Not Recommended)](#️-manual-hook-installation-not-recommended)
  - [🧼 Setting up Spotless](#-setting-up-spotless)
  - [🛠️ Advanced Configuration](#️-advanced-configuration)
  - [🤝 Contributing](#-contributing)
  - [🧯 Troubleshooting](#-troubleshooting)

## 🧩 What These Hooks Do

This repo provides Git `pre-commit` and `post-commit` hooks that automatically run `Spotless` on files you've changed. This ensures consistent formatting and reduces noisy diffs before commits ever hit GitHub for PR Review.

## 🪝 Included Hooks

- `pre-commit`: Applies `Spotless` to staged files before commit
- `post-commit`: Re-runs `Spotless` after commit to handle missed diffs

## 🗺️ Flow Chart

```pqsql
git commit
   ↓
pre-commit hook
   ↓
spotless:apply
   ↓
conflict resolution
   ↓
post-commit hook
   ↓
spotless:apply
   ↓
commit allowed or blocked (only blocked by `spotless` or pre-commit errors)
```

### 🔀 Conflict Resolution

These hooks are designed to stash non-committed changes prior to commit, so that when `spotless` is run, it can apply the formatting to only the files being changed. After un-stashing, if there are conflicts, we will resolve them using a [theirs strategy](https://www.atlassian.com/git/tutorials/using-branches/merge-strategy) (i.e. We take the un-stashed files changes over the current file's changes), re-run `spotless`, and re-commit the changes. This is done to ensure that the commit is always in a clean state, and that `spotless` has been applied before committing.

### 🧭 Hook Behavior During Merge/Rebase

These hooks are merge-aware and won’t interfere with merge commits or rebases. In the event of a merge or rebase, the hooks will exit early and not run `spotless`.

## 🚀 Quickstart

This repository should be added to another repository as a [git submodule](https://git-scm.com/book/en/v2/Git-Tools-Submodules). By adding this repository as a submodule, you can easily keep it up to date with the latest changes and improvements. Some [advanced configuration](#️-advanced-configuration) is required to perform submodule updates automatically, but this is not required to get started.

If you have the `spotless-maven-plugin` already configured, you can add this repository as a submodule and manually install the hooks by running the following command in the root of your project:

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

This will add the `maven-spotless-hooks` repository as a `submodule` in the `.hooks` folder within `your project`, and install the `pre-commit` and `post-commit` hooks into the `.git/hooks/` directory. This will allow you to run the `spotless` formatter and `pre-commit` hooks automatically when you commit your code.

If you do not have `spotless` set up in your project, please refer to [SPOTLESS-CONFIG.md](./docs/SPOTLESS-CONFIG.md).

### 🔧 Installing the Git Hooks

If you followed the [Quickstart](#-quickstart) instructions, you should have the submodule added to your project, and the hooks installed, albeit manually. The next step is to ensure that the hooks are installed automatically, so you don't have to worry about it in the future and so that other developers don't need to perform any additional configuration to work on your project. This can be done by adding the `git-build-hook-maven-plugin` to your `pom.xml` file, as described below.

#### 🤖 Automatic Maven Hook Installation

To setup automatic hook installation via `Maven`, add the following `plugin` to your application's `pom.xml` `<plugins>` section:

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

Most IDEs (like `IntelliJ` or `Eclipse`) run `Maven` commands using an embedded runner or internal build process, which may not trigger all `Maven` plugin goals, including this hook installation. To ensure the `git-build-hook-maven-plugin` installs the hooks correctly, you should run `Maven` commands (like `mvn clean install`) from the `terminal`, **at least once per fresh clone or submodule update**.

This aligns your local workflow with your CI/CD environment, **which always uses CLI Maven**, and helps catch any setup or formatting issues early.

#### ⚠️ Manual Hook Installation (Not Recommended)

You can manually install the hooks, as described in the [quickstart](#-quickstart) section, by running `./.hooks/install-hooks.sh` if on **Mac** or **Linux**, or `.\.hooks\install-hooks.ps1` if on **Windows**.

> **Note**: The above commands assume you are in the root of your project that has added this repository as a submodule, and that the submodule was added to the `.hooks` folder. If you are not, you will need to adjust the path to the `install-hooks.sh` or `install-hooks.ps1` script accordingly.

## 🧼 Setting up Spotless

For more information on how to set up `spotless`, please refer to [SPOTLESS-CONFIG.md](./docs/SPOTLESS-CONFIG.md).

## 🛠️ Advanced Configuration

For more advanced configuration information, such as how to automatically update the submodule with Maven, exclude submodule updates during CI, or a sample `README.md` change to make to your project, please refer to [ADVANCED-CONFIGURATION.md](./docs/ADVANCED-CONFIGURATION.md).

## 🤝 Contributing

PRs welcome! Please open an issue first for discussion.

## 🧯 Troubleshooting

For troubleshooting, please refer to [TROUBLESHOOTING.md](./docs/TROUBLESHOOTING.md).
