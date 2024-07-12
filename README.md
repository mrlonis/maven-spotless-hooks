# maven-spotless-hooks

## Table of Contents

- [maven-spotless-hooks](#maven-spotless-hooks)
  - [Table of Contents](#table-of-contents)
  - [Usage](#usage)
    - [Automatically Update Submodule With Maven](#automatically-update-submodule-with-maven)
    - [Install Git Hooks](#install-git-hooks)

## Usage

This repo should be added to another repo as a submodule

```sh
git submodule add --name .hooks -b main https://github.com/mrlonis/maven-spotless-hooks.git
git commit -m "Adding maven-spotless-hooks"
```

This will add the `maven-spotless-hooks` repository as a submodule in the `.hooks` folder within your project.

### Automatically Update Submodule With Maven

Submodules are not cloned by default so you should add a step to your `setup` script in the project to initialize it if it wasn't cloned already. This `setup` script should work for most projects:

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

### Install Git Hooks

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
