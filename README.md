# maven-spotless-hooks

## Table of Contents

- [maven-spotless-hooks](#maven-spotless-hooks)
  - [Table of Contents](#table-of-contents)
  - [Usage](#usage)
    - [Automatically Update Submodule With Maven](#automatically-update-submodule-with-maven)
      - [Executed Command](#executed-command)
      - [Excluding submodule updates during CI](#excluding-submodule-updates-during-ci)
        - [GitHub Actions](#github-actions)
    - [Install Git Hooks](#install-git-hooks)
  - [Troubleshooting](#troubleshooting)
    - [How to fix "git-sh-setup: file not found" in windows](#how-to-fix-git-sh-setup-file-not-found-in-windows)

## Usage

This repo should be added to another repo as a submodule

```sh
git submodule add -b main https://github.com/mrlonis/maven-spotless-hooks.git .hooks/
git commit -m "Adding maven-spotless-hooks"
```

This will add the `maven-spotless-hooks` repository as a submodule in the `.hooks` folder within your project.

### Automatically Update Submodule With Maven

Submodules are not cloned by default so we need to add a plugin to our Maven root `pom.xml` to clone the submodule. The following is the recommended configuration:

```xml
<project>
  ...
  <properties>
    ...
    <exec-maven-plugin.version>3.3.0</exec-maven-plugin.version>
    ...
  </properties>
  ...
  <build>
    ...
    <plugins>
      ...
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
      ...
    </plugins>
    ...
  </build>
  ...
</project>
```

#### Executed Command

The resulting command that is executed is `git submodule update --init --remote --force` which will clone the submodule if it does not exist, update the submodule to the latest commit, throw away local changes in submodules when switching to a different commit; and always run a checkout operation in the submodule, even if the commit listed in the index of the containing repository matches the commit checked out in the submodule.

#### Excluding submodule updates during CI

If you are using a CI/CD pipeline, you may want to exclude the submodule update during the CI/CD pipeline. This can be done by adding the following configuration to the `pom.xml`:

```xml
<project>
  ...
  <properties>
    ...
    <exec-maven-plugin.version>3.3.0</exec-maven-plugin.version>
    ...
  </properties>
  ...
  <profiles>
    <profile>
      <id>local-development</id>
      <activation>
        <property>
          <name>!env.SOME_ENV_VAR</name>
        </property>
      </activation>
      <build>
        <plugins>
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
        </plugins>
      </build>
    </profile>
  </profiles>
  ...
</project>
```

This works by checking for the absence of an environment variable `SOME_ENV_VAR` and if it is not present, the submodule update will be executed. This can be used to exclude the submodule update during the CI/CD pipeline.

##### GitHub Actions

If you are using GitHub Actions, you can exclude the submodule update by adding the following `env` configuration to the `.github/workflows/*.yml` file:

```yaml
...
env:
  SOME_ENV_VAR: this_can_be_anything_since_we_are_checking_for_its_absence_not_its_value
...
```

### Install Git Hooks

We then need to install the git hooks. This can be done by adding the following configuration to the `pom.xml`:

```xml
<project>
  ...
  <properties>
    ...
    <git-build-hook-maven-plugin.version>3.5.0</git-build-hook-maven-plugin.version>
    ...
  </properties>
  ...
  <build>
    ...
    <plugins>
      ...
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
      ...
    </plugins>
    ...
  </build>
  ...
</project>
```

## Troubleshooting

### How to fix "git-sh-setup: file not found" in windows

[https://stackoverflow.com/questions/49256190/how-to-fix-git-sh-setup-file-not-found-in-windows](https://stackoverflow.com/questions/49256190/how-to-fix-git-sh-setup-file-not-found-in-windows)
