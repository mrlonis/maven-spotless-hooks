# maven-spotless-hooks

These hooks are Git-native and IDE-agnostic. You do not need to configure anything inside IntelliJ, Eclipse, or VS Code.

## Table of Contents

- [maven-spotless-hooks](#maven-spotless-hooks)
  - [Table of Contents](#table-of-contents)
  - [Quickstart](#quickstart)
    - [Install Git Hooks](#install-git-hooks)
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
    - [Automatically Update Submodule With Maven](#automatically-update-submodule-with-maven)
      - [Executed Command](#executed-command)
      - [Excluding submodule updates during CI](#excluding-submodule-updates-during-ci)
        - [GitHub Actions](#github-actions)
    - [(Optional) Update Project README.md](#optional-update-project-readmemd)
  - [Troubleshooting](#troubleshooting)

## Quickstart

This repository should be added to another repository as a [git submodule](https://git-scm.com/book/en/v2/Git-Tools-Submodules):

```sh
git submodule add -b main https://github.com/mrlonis/maven-spotless-hooks.git .hooks/
git commit -m "Adding maven-spotless-hooks"
```

This will add the `maven-spotless-hooks` repository as a `submodule` in the `.hooks` folder within `your project`.

### Install Git Hooks

Simply adding this `submodule` is not enough. We then need to install the scripts within this repository as proper `git hooks`.

#### Manual Hook Installation (Not Recommended)

You can manually install the hooks by running `./.hooks/install-hooks.sh` if on **Mac** or **Linux**, or `.\.hooks\install-hooks.ps1` if on **Windows**. This will install the `pre-commit` and `post-commit` hooks into the `.git/hooks/` directory.

> **Note**: The above commands assume you are in the root of your project that has added this repository as a submodule. If you are not, you will need to adjust the path to the `install-hooks.sh` or `install-hooks.ps1` script accordingly.

#### Automatic Maven Hook Installation

It should go without saying why a manual only means of hook installation is bad. Ideally, we have the hook installation enforced automatically for us by some sort of shared mechanism. Luckily, if you are reading this, then you are using Maven, which happens to have a plugin called [git-build-hook-maven-plugin](https://github.com/rudikershaw/git-build-hook) that can install our hooks automatically. This can be done by adding the following configuration to your application's `pom.xml`:

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

Then, anytime any developer runs any commands in Maven that target the `install` goal as part of its build lifecycle, the `git-build-hook-maven-plugin` will install the `pre-commit` and `post-commit` hooks into the `.git/hooks/` directory. This will allow you to run the `spotless` formatter and `pre-commit` hooks automatically when you commit your code.

You might be sitting there thinking, "Why would I run Maven in the terminal, I run my stuff through the IDE". Well, your CI/CD process will run Maven in the terminal, and you should be testing your code in the same way your CI/CD process will run it. This is a good practice to get into, and it will help you avoid issues when you push your code to the remote repository and end up with an easily catch-able error had you run the full test suit locally (often `mvn verify`).

## Contributing

PRs welcome! Please open an issue first for discussion.

## What These Hooks Do

This repo provides Git pre-commit and post-commit hooks that automatically run Spotless on files you've changed. This ensures consistent formatting and reduces noisy diffs before commits ever hit your branch.

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

For more information on how to set up `spotless`, please refer to [SPOTLESS-CONFIG.md](SPOTLESS-CONFIG.md).

## Advanced Configuration

### Automatically Update Submodule With Maven

`Submodules` are not cloned by default on a fresh clone from GitHub so we need to add a plugin to our Maven root `pom.xml` to clone the submodule. The following is the recommended configuration (**hold off on copying this! You likely want to NOT run this in your CI/CD pipeline. Continue reading to find out how to do this**):

<!-- markdownlint-disable-next-line MD033 -->
<details><summary>View the plugin configuration</summary>

```xml
<plugin>
  <groupId>org.codehaus.mojo</groupId>
  <artifactId>exec-maven-plugin</artifactId>
  <version>${exec-maven-plugin.version}</version>
  <inherited>false</inherited>
  <executions>
    <execution>
      <id>git submodule update</id>
      <goals>
        <goal>exec</goal>
      </goals>
      <phase>initialize</phase>
      <configuration>
        <executable>git</executable>
        <arguments>
          <argument>submodule</argument>
          <argument>update</argument>
          <argument>--init</argument>
          <argument>--remote</argument>
          <argument>--force</argument>
        </arguments>
      </configuration>
    </execution>
  </executions>
</plugin>
```

</details>

#### Executed Command

The resulting command that is executed is `git submodule update --init --remote --force` which will `clone the submodule` if it does not exist, `update the submodule` to the latest commit, throw away local changes in submodules when switching to a different commit, and always run a checkout operation in the submodule, even if the commit listed in the index of the containing repository matches the commit checked out in the submodule.

#### Excluding submodule updates during CI

If you are using a CI/CD pipeline, you may want to `exclude the submodule update during the CI/CD pipeline`. This can be done by adding the following configuration to the `pom.xml`:

<!-- markdownlint-disable-next-line MD033 -->
<details><summary>View <code>pom.xml</code> profile</summary>

```xml
<profile>
  <id>local-development</id>
  <activation>
    <property>
      <name>!env.SOME_ENV_VAR</name>
    </property>
  </activation>
  <build>
    <plugins>
      <!-- Copy the plugin configuration above -->
    </plugins>
  </build>
</profile>
```

</details>

This works by checking for the absence of an environment variable `SOME_ENV_VAR` and if it is not present, the submodule update will be executed. This can be used to exclude the submodule update during the CI/CD pipeline.

##### GitHub Actions

If you are using GitHub Actions, you can exclude the submodule update by adding the following `env` configuration to the `.github/workflows/*.yml` file:

```yaml
env:
  SOME_ENV_VAR: this_can_be_anything_since_we_are_checking_for_its_absence_not_its_value
```

### (Optional) Update Project README.md

Consider adding something like the following to your project's `README.md` file, replacing the Java versions with the versions you are using:

<!-- markdownlint-disable-next-line MD033 -->
<details><summary>View example README.md</summary>

```markdown
## Setup

If this is your first time opening or working on this project, you will need to run the following commands to set up the project: `./mvnw clean verify`

This will install the necessary git hooks and update the submodule to the latest version. After performing this command at least one time, you won't need to do anything else. When you go to commit, the `spotless` formatter and pre-commit hooks will run automatically, formatting your code to the project's code style for easier PR review.

### Windows Setup Caveat

Windows users whose project is located within a filepath that contains a space will experience issues with Maven wrapper and should instead globally install `Maven` via `choco install maven -y` and run `mvn clean verify` instead. This typically happens due to the `C:\Users\<USERNAME>\` path containing a space (in this case `<USERNAME>` being something like `John Doe`).

A filepath such as this `C:\Git Hub\projects\fake` will cause issues with the `Maven Wrapper`. Instead, move the project to a different location, such as `C:\projects\fake` or `C:\GitHub\projects\fake` and run the command again. This is a known issue with the `Maven Wrapper` and is not specific to this project.
```

</details>

## Troubleshooting

For troubleshooting, please refer to [TROUBLESHOOTING.md](./TROUBLESHOOTING.md).
