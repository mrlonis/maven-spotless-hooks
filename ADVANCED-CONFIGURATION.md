# Advanced Configuration

This guide covers optional but powerful Spotless hook extensions for teams operating in CI/CD environments, cross-platform setups, or larger codebases.

## Table of Contents

- [Advanced Configuration](#advanced-configuration)
  - [Table of Contents](#table-of-contents)
  - [Automatically Update Submodule With Maven](#automatically-update-submodule-with-maven)
    - [Executed Command](#executed-command)
    - [Excluding submodule updates during CI](#excluding-submodule-updates-during-ci)
      - [GitHub Actions](#github-actions)
  - [(Optional) Update YOUR Project README.md](#optional-update-your-project-readmemd)

## Automatically Update Submodule With Maven

`Submodules` are not cloned by default on a fresh clone from GitHub so we need to add a plugin to our Maven root `pom.xml` to clone the submodule. Additionally, once a submodule is cloned, it will not be updated to the latest commit unless we run a command to do so. This can be done by adding the `exec-maven-plugin` to our `pom.xml` file. This plugin allows us to run any command as part of the Maven build lifecycle. We will use this plugin to run the `git submodule update --init --remote --force` command as part of the `initialize` phase of the Maven build lifecycle.

The following is the recommended configuration (**hold off on copying this! You likely want to NOT run this in your CI/CD pipeline. Continue reading to find out how to do this**):

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

### Executed Command

The resulting command that is executed is `git submodule update --init --remote --force` which will `clone the submodule` if it does not exist, `update the submodule` to the latest commit, throw away local changes in submodules when switching to a different commit, and always run a checkout operation in the submodule, even if the commit listed in the index of the containing repository matches the commit checked out in the submodule.

### Excluding submodule updates during CI

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

#### GitHub Actions

If you are using GitHub Actions, you can exclude the submodule update by adding the following `env` configuration to the `.github/workflows/*.yml` file:

```yaml
env:
  SOME_ENV_VAR: this_can_be_anything_since_we_are_checking_for_its_absence_not_its_value
```

## (Optional) Update YOUR Project README.md

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

← Back to [README.md](./README.md)
