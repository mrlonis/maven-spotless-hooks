# maven-spotless-hooks

## Table of Contents

- [maven-spotless-hooks](#maven-spotless-hooks)
  - [Table of Contents](#table-of-contents)
  - [Usage](#usage)
    - [Automatically Update Submodule With Maven](#automatically-update-submodule-with-maven)
      - [Executed Command](#executed-command)
    - [Install Git Hooks](#install-git-hooks)

## Usage

This repo should be added to another repo as a submodule

```sh
git submodule add --name .hooks -b main https://github.com/mrlonis/maven-spotless-hooks.git
git commit -m "Adding maven-spotless-hooks"
```

This will add the `maven-spotless-hooks` repository as a submodule in the `.hooks` folder within your project.

### Automatically Update Submodule With Maven

Submodules are not cloned by default so we need to add a plugin to our MAven root `pom.xml` to clone the submodule. The following is the recommended configuration:

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
