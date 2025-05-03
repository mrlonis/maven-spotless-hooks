# maven-spotless-hooks

These hooks are Git-native and IDE-agnostic. You do not need to configure anything inside IntelliJ, Eclipse, or VS Code.

## Table of Contents

- [maven-spotless-hooks](#maven-spotless-hooks)
  - [Table of Contents](#table-of-contents)
  - [Quickstart](#quickstart)
    - [Installing the Git Hooks](#installing-the-git-hooks)
      - [Manual Hook Installation (Not Recommended)](#manual-hook-installation-not-recommended)
      - [Automatic Maven Hook Installation](#automatic-maven-hook-installation)
  - [Contributing](#contributing)
  - [What These Hooks Do](#what-these-hooks-do)
  - [Included Hooks](#included-hooks)
  - [Flow Chart](#flow-chart)
    - [Conflict Resolution](#conflict-resolution)
    - [Hook Behavior During Merge/Rebase](#hook-behavior-during-mergerebase)
  - [Setting up Spotless](#setting-up-spotless)
  - [Advanced Configuration](#advanced-configuration)
  - [Troubleshooting](#troubleshooting)

## Quickstart

This repository should be added to another repository as a [git submodule](https://git-scm.com/book/en/v2/Git-Tools-Submodules). Assuming you have `spotless` already set up in your project, you can add this repository as a submodule and manually install the hooks by running the following command in the root of your project:

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

If you do not have `spotless` set up in your project, you can follow the instructions in the [Setting up Spotless](#setting-up-spotless) section to set it up.

### Installing the Git Hooks

Simply adding this `submodule` is not enough. We then need to install the scripts within this repository as proper `git hooks`.

#### Manual Hook Installation (Not Recommended)

You can manually install the hooks, as described in the [quickstart](#quickstart) section, by running `./.hooks/install-hooks.sh` if on **Mac** or **Linux**, or `.\.hooks\install-hooks.ps1` if on **Windows**.

> **Note**: The above commands assume you are in the root of your project that has added this repository as a submodule, and that the submodule was added to the `.hooks` folder. If you are not, you will need to adjust the path to the `install-hooks.sh` or `install-hooks.ps1` script accordingly.

#### Automatic Maven Hook Installation

It should go without saying why a manual only means of hook installation is bad. Ideally, we have the hook installation enforced automatically for us by some sort of shared mechanism. Luckily, if you are reading this, then you are using `Maven`, which happens to have a plugin called [git-build-hook-maven-plugin](https://github.com/rudikershaw/git-build-hook) that can install our hooks automatically. This can be done by adding the following `plugin` to your application's `pom.xml` `<plugins>` section:

<!-- markdownlint-disable-next-line MD033 -->
<details><summary>View <code>pom.xml</code> plugin</summary>

```xml
<plugin>
  <groupId>com.rudikershaw.gitbuildhook</groupId>
  <artifactId>git-build-hook-maven-plugin</artifactId>
  <version>${git-build-hook-maven-plugin.version}</version>
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

Then, anytime any developer runs any commands in Maven that target the `install` goal as part of its build lifecycle, the `git-build-hook-maven-plugin` will install the `pre-commit` and `post-commit` hooks into the `.git/hooks/` directory. This will ensure that the hooks are always installed and up to date, and that any developer who clones the repository will have the hooks installed automatically.

You might be sitting there thinking, "Why would I run Maven in the terminal, I run my stuff through the IDE". Well, your CI/CD process will run Maven in the terminal, and you should be testing your code in the same way your CI/CD process will run it. This is a good practice to get into, and it will help you avoid issues when you push your code to the remote repository and end up with an easily catch-able error had you run the full test suit locally (often `mvn verify`).

## Contributing

PRs welcome! Please open an issue first for discussion.

## What These Hooks Do

This repo provides Git `pre-commit` and `post-commit` hooks that automatically run `Spotless` on files you've changed. This ensures consistent formatting and reduces noisy diffs before commits ever hit GitHub for PR Review.

## Included Hooks

- `pre-commit`: Applies `Spotless` to staged files before commit
- `post-commit`: Re-runs `Spotless` after commit to handle missed diffs

## Flow Chart

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

### Conflict Resolution

These hooks are designed to stash non-committed changes prior to commit, so that when `spotless` is run, it can apply the formatting to only the files being changed. After un-stashing, if there are conflicts, we will resolve them, re-run `spotless`, and re-commit the changes. This is done to ensure that the commit is always in a clean state, and that `spotless` has been applied before committing.

### Hook Behavior During Merge/Rebase

These hooks are merge-aware and won’t interfere with merge commits or rebases. Conflicting files are automatically resolved in favor of 'theirs' and re-staged after formatting.

## Setting up Spotless

For more information on how to set up `spotless`, please refer to [SPOTLESS-CONFIG.md](./docs/SPOTLESS-CONFIG.md).

## Advanced Configuration

For more advanced configuration information, such as how to automatically update the submodule with Maven, exclude submodule updates during CI, or a sample `README.md` change to make to your project, please refer to [ADVANCED-CONFIGURATION.md](./docs/ADVANCED-CONFIGURATION.md).

## Troubleshooting

For troubleshooting, please refer to [TROUBLESHOOTING.md](./docs/TROUBLESHOOTING.md).
