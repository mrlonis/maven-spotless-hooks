# maven-spotless-hooks

## Table of Contents

- [maven-spotless-hooks](#maven-spotless-hooks)
  - [Table of Contents](#table-of-contents)
  - [Usage](#usage)
    - [(Optional) Automatically Update Submodule With Maven](#optional-automatically-update-submodule-with-maven)
      - [Executed Command](#executed-command)
      - [Excluding submodule updates during CI](#excluding-submodule-updates-during-ci)
        - [GitHub Actions](#github-actions)
    - [Install Git Hooks](#install-git-hooks)
    - [(Optional) Update Project README.md](#optional-update-project-readmemd)
  - [Setting up Spotless](#setting-up-spotless)
    - [Pre-requisites](#pre-requisites)
      - [Maven Wrapper Setup](#maven-wrapper-setup)
        - [Adding .gitattributes](#adding-gitattributes)
    - [Basic Plugin Setup](#basic-plugin-setup)
    - [Plugin Documentation](#plugin-documentation)
  - [Troubleshooting](#troubleshooting)
    - [How to fix "git-sh-setup: file not found" in windows](#how-to-fix-git-sh-setup-file-not-found-in-windows)
    - [Windows: Dynamic JAVA\_HOME Env Variable Changing](#windows-dynamic-java_home-env-variable-changing)
      - [PowerShell Profile](#powershell-profile)
        - [Notepad](#notepad)
        - [VS Code](#vs-code)
        - [Profile Content](#profile-content)

## Usage

This repo should be added to another repo as a submodule

```sh
git submodule add -b main https://github.com/mrlonis/maven-spotless-hooks.git .hooks/
git commit -m "Adding maven-spotless-hooks"
```

This will add the `maven-spotless-hooks` repository as a submodule in the `.hooks` folder within your project.

### (Optional) Automatically Update Submodule With Maven

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
---
env:
  SOME_ENV_VAR: this_can_be_anything_since_we_are_checking_for_its_absence_not_its_value
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

### (Optional) Update Project README.md

Consider adding something like the following to your project's `README.md` file, replacing the Java versions with the versions you are using:

````markdown
## Setup

If this is your first time opening or working on this project, you will need to run the following commands to set up the project:

```sh
./mvnw clean verify
```

This will install the necessary git hooks and update the submodule to the latest version. After performing this command at least one time, you won't need to do anything else. When you go to commit, the `spotless` formatter and pre-commit hooks will run automatically, formatting your code to the project's code style for easier PR review.

### Windows Setup Caveat

Windows users whose project is located within a filepath that contains a space will experience issues with Maven wrapper and should instead globally install `Maven` via `choco install maven -y` and run `mvn clean verify` instead. This typically happens due to the `C:\Users\<USERNAME>\` path containing a space (in this case `<USERNAME>` being something like `John Doe`).

A filepath such as this `C:\Git Hub\projects\fake` will cause issues with the `Maven Wrapper`. Instead, move the project to a different location, such as `C:\projects\fake` or `C:\GitHub\projects\fake` and run the command again. This is a known issue with the `Maven Wrapper` and is not specific to this project.
````

## Setting up Spotless

### Pre-requisites

- Your project must be on `Java 11`
- Your project must have the `Maven Wrapper` configured

#### Maven Wrapper Setup

To add Maven wrapper to your project, run the following command:

```sh
mvn wrapper:wrapper -Dmaven=3.8.8
```

You can do this in almost any IDE, since they often bundle Maven into the IDE itself. It is fine to continue using the bundled Maven when in the IDE, but we need the Maven Wrapper to perform `pre-commit` commands.

##### Adding .gitattributes

If your project doesn't have a .gitattributes file, create one in the root of your project and add the following lines:

```gitattributes
/mvnw text eol=lf
*.cmd text eol=crlf
# Add other files here before the * text=auto
# *.png binary
# * text=auto should be the last line in the file
* text=auto
```

This is **NOT** optional. Failure to do this, and messing up the line endings for `*.cmd` or the `mvnw` script files will cause issues with users on Windows and Mac. Mac cannot run `mvnw` if the line endings are `crlf`, and Windows cannot run `*.cmd*` if the line endings are not `crlf`.

### Basic Plugin Setup

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 https://maven.apache.org/xsd/maven-4.0.0.xsd">
  <properties>
    <cleanthat.vesion>2.20</cleanthat.vesion>
    <exec-maven-plugin.version>3.5.0</exec-maven-plugin.version>
    <git-build-hook-maven-plugin.version>3.5.0</git-build-hook-maven-plugin.version>
    <java.version>11</java.version> <!-- Replace with correct version, but minimum required is 11 -->
    <palantir-java-format.version>2.63.0</palantir-java-format.version>
    <spotless.version>2.44.4</spotless.version>
  </properties>
  <dependencyManagement>
    <dependencies>
      <dependency>
        <groupId>com.palantir.javaformat</groupId>
        <artifactId>palantir-java-format</artifactId>
        <version>${palantir-java-format.version}</version>
      </dependency>
      <dependency>
        <groupId>io.github.solven-eu.cleanthat</groupId>
        <artifactId>spotless</artifactId>
        <version>${cleanthat.version}</version>
      </dependency>
    </dependencies>
  </dependencyManagement>
  <dependencies>
    ...
  </dependencies>
  <build>
    <plugins>
      <plugin>
        <groupId>com.diffplug.spotless</groupId>
        <artifactId>spotless-maven-plugin</artifactId>
        <version>${spotless.version}</version>
        <configuration>
          <formats>
            <format>
              <includes>
                <include>.mvn/wrapper/maven-wrapper.properties</include>
                <include>.gitattributes</include>
                <include>.gitignore</include>
                <include>.gitmodules</include>
                <include>lombok.config</include>
                <include>mvnw</include>
              </includes>
              <trimTrailingWhitespace/>
              <endWithNewline/>
            </format>
            <format>
              <includes>
                <!-- This is separate to enforce proper line endings. See the Maven Wrapper Setup section for more information -->
                <!-- Delete these comments when adding to your project -->
                <include>mvnw.cmd</include>
              </includes>
              <trimTrailingWhitespace/>
              <endWithNewline/>
            </format>
            <format>
              <includes>
                <include>.github/**/*.yml</include>
                <include>.mvn/**/*.xml</include>
                <include>.vscode/**/*.json</include>
                <include>src/**/*.json</include>
                <include>src/**/*.html</include>
                <include>src/**/*.xml</include>
                <include>src/**/*.yaml</include>
                <include>src/**/*.yml</include>
                <include>.prettierrc</include>
                <include>compose.yml</include>
                <include>compose.yaml</include>
              </includes>
              <prettier>
                <npmInstallCache>true</npmInstallCache>
                <devDependencyProperties>
                  <property>
                    <name>prettier</name>
                    <value>^3</value>
                  </property>
                  <property>
                    <name>@prettier/plugin-xml</name>
                    <value>^3</value>
                  </property>
                </devDependencyProperties>
                <config>
                  <printWidth>120</printWidth>
                  <xmlSelfClosingSpace>false</xmlSelfClosingSpace>
                  <xmlSortAttributesByKey>true</xmlSortAttributesByKey>
                  <!-- The STRICT sensitivity here is REALLY important. DO NOT CHANGE UNLESS YOU KNOW WHAT YOU ARE DOING AND THE IMPLICATIONS CHANGING IT MEANS -->
                  <xmlWhitespaceSensitivity>strict</xmlWhitespaceSensitivity>
                  <plugins>@prettier/plugin-xml</plugins>
                </config>
              </prettier>
              <trimTrailingWhitespace/>
              <endWithNewline/>
            </format>
          </formats>
          <java>
            <includes>
              <include>src/main/java/**/*.java</include>
              <include>src/test/java/**/*.java</include>
            </includes>
            <cleanthat>
              <version>${cleanthat.vesion}</version>
              <mutators>
                <mutator>SafeAndConsensual</mutator>
                <mutator>SafeButNotConsensual</mutator>
              </mutators>
            </cleanthat>
            <palantirJavaFormat>
              <version>${palantir-java-format.version}</version>
              <style>PALANTIR</style>
              <formatJavadoc>true</formatJavadoc>
            </palantirJavaFormat>
            <formatAnnotations/>
            <removeUnusedImports/>
            <importOrder/>
            <trimTrailingWhitespace/>
            <endWithNewline/>
          </java>
          <pom>
            <includes>
              <include>pom.xml</include>
            </includes>
            <sortPom>
              <expandEmptyElements>false</expandEmptyElements>
              <lineSeparator>\n</lineSeparator>
              <keepBlankLines>false</keepBlankLines>
              <sortDependencies>scope,groupId,artifactId</sortDependencies>
              <sortDependencyExclusions>groupId,artifactId</sortDependencyExclusions>
              <sortDependencyManagement>scope,groupId,artifactId</sortDependencyManagement>
              <sortPlugins>groupId,artifactId</sortPlugins>
              <sortProperties>true</sortProperties>
            </sortPom>
            <trimTrailingWhitespace/>
            <endWithNewline/>
          </pom>
          <markdown>
            <includes>
              <include>**/*.md</include>
            </includes>
            <excludes>
              <exclude>.hooks/**/*.md</exclude>
              <exclude>target/**/*.md</exclude>
            </excludes>
            <flexmark/>
            <trimTrailingWhitespace/>
            <endWithNewline/>
          </markdown>
          <sql>
            <includes>
              <include>src/**/*.sql</include>
            </includes>
            <prettier>
              <npmInstallCache>true</npmInstallCache>
              <devDependencyProperties>
                <property>
                  <name>prettier</name>
                  <value>^3</value>
                </property>
                <property>
                  <name>prettier-plugin-sql</name>
                  <value>~0.18</value>
                </property>
              </devDependencyProperties>
              <config>
                <printWidth>120</printWidth>
                <plugins>prettier-plugin-sql</plugins>
              </config>
            </prettier>
          </sql>
        </configuration>
        <executions>
          <execution>
            <goals>
              <goal>check</goal>
            </goals>
          </execution>
        </executions>
      </plugin>
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
      <plugin>
        <groupId>org.apache.maven.plugins</groupId>
        <artifactId>maven-compiler-plugin</artifactId>
        <configuration>
          <compilerArgs>
            <arg>-Xlint:all</arg>
            <!-- -proc:full is only needed for Java 21+ -->
            <arg>-proc:full</arg>
          </compilerArgs>
          <showDeprecation>true</showDeprecation>
          <showWarnings>true</showWarnings>
        </configuration>
      </plugin>
      <!-- Only needed for mvn versions:display-plugin-updates -->
      <plugin>
        <groupId>org.apache.maven.plugins</groupId>
        <artifactId>maven-enforcer-plugin</artifactId>
        <executions>
          <execution>
            <id>enforce-maven</id>
            <goals>
              <goal>enforce</goal>
            </goals>
            <configuration>
              <rules>
                <requireMavenVersion>
                  <version>3.8</version>
                </requireMavenVersion>
              </rules>
            </configuration>
          </execution>
        </executions>
      </plugin>
      <plugin>
        <groupId>org.apache.maven.plugins</groupId>
        <artifactId>maven-surefire-plugin</artifactId>
        <configuration>
          <!-- -XX:+EnableDynamicAgentLoading is only needed for Java 21+ -->
          <argLine>-XX:+EnableDynamicAgentLoading</argLine>
        </configuration>
      </plugin>
    </plugins>
  </build>
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
</project>
```

### Plugin Documentation

To find out more information about the `spotless-maven-plugin`, please refer to the [Spotless Maven Plugin Documentation](https://github.com/diffplug/spotless/blob/main/plugin-maven/README.md). This will give you more information about the configuration options available to you. The configuration options laid out above are a full-fat recommended configuration. All of the sections might not apply to you, like the `sql` section. It is also strongly advised, if you are adding `spotless` to an existing project, to remove the `java` portion from the `spotless` configuration for a phase 1 migration. This way, you can start enforcing the `pre-commit` process and get formatting on some non-critical, non-java files. Once you are happy with the configuration, you can then add the `java` portion to the `spotless` configuration. This will allow you to get the formatting on the Java files without having to setup the overall configuration and process in one go.

## Troubleshooting

### How to fix "git-sh-setup: file not found" in windows

[https://stackoverflow.com/questions/49256190/how-to-fix-git-sh-setup-file-not-found-in-windows](https://stackoverflow.com/questions/49256190/how-to-fix-git-sh-setup-file-not-found-in-windows)

1. In the Windows Search bar, type `Environment Variables` and select `Edit the system environment variables`
2. In the `System Properties` window, click on the `Environment Variables` button
3. In the `Environment Variables` window, under `System variables`, click on `Path` and then click on `Edit`
4. In the `Edit Environment Variable` window, click on `New` and add the following paths:
   - `C:\Program Files\Git\usr\bin`
   - `C:\Program Files\Git\mingw64\libexec\git-core`
5. These will be added to the end of the list. Click on each one, and then click on `Move Up` until they are at the top of the list

### Windows: Dynamic JAVA_HOME Env Variable Changing

#### PowerShell Profile

Run the following command in PowerShell to determine your `$profile` path:

```powershell
echo $profile
```

Then, open the file in your favorite text editor:

##### Notepad

```powershell
notepad.exe $profile
```

##### VS Code

```powershell
code $profile
```

##### Profile Content

Below is the content of the PowerShell profile. This profile will give you dynamic functions, aptly named `java8`, `java11`, `java17`, and `java21` to set the JAVA_HOME environment variable to the correct version of Java. You can then run these functions in PowerShell to switch between Java versions at will in the CLI. However, this **ONLY** works in an `Administrator PowerShell` session.

```powershell
$global:JAVA_8_PATH = 'C:\Program Files\Eclipse Adoptium\jdk-8.0.442.6-hotspot' # Replace with your correct version
$global:JAVA_11_PATH = 'C:\Program Files\Eclipse Adoptium\jdk-11.0.26.4-hotspot' # Replace with your correct version
$global:JAVA_17_PATH = 'C:\Program Files\Eclipse Adoptium\jdk-17.0.14.7-hotspot' # Replace with your correct version
$global:JAVA_21_PATH = 'C:\Program Files\Eclipse Adoptium\jdk-21.0.6.7-hotspot' # Replace with your correct version

function java8 {
  $env:JAVA_HOME = $global:JAVA_8_PATH
  $env:Path = "$env:JAVA_HOME\bin;" + ($env:Path -split ';' | Where-Object { $_ -notmatch '\\jdk.*?\\bin' }) -join ';'
  Write-Host "JAVA_HOME set to: $env:JAVA_HOME"
  [Environment]::SetEnvironmentVariable('JAVA_HOME', $env:JAVA_HOME, 'Machine')
  Write-Host "Executing java --version to verify java version"
  # Note how Java 8 uses -version instead of --version
  # --version was introduced in Java 9+
  Write-Host $(java -version)
}
function java11 {
  $env:JAVA_HOME = $global:JAVA_11_PATH
  $env:Path = "$env:JAVA_HOME\bin;" + ($env:Path -split ';' | Where-Object { $_ -notmatch '\\jdk.*?\\bin' }) -join ';'
  Write-Host "JAVA_HOME set to: $env:JAVA_HOME"
  [Environment]::SetEnvironmentVariable('JAVA_HOME', $env:JAVA_HOME, 'Machine')
  Write-Host "Executing java --version to verify java version"
  Write-Host $(java --version)
}
function java17 {
  $env:JAVA_HOME = $global:JAVA_17_PATH
  $env:Path = "$env:JAVA_HOME\bin;" + ($env:Path -split ';' | Where-Object { $_ -notmatch '\\jdk.*?\\bin' }) -join ';'
  Write-Host "JAVA_HOME set to: $env:JAVA_HOME"
  [Environment]::SetEnvironmentVariable('JAVA_HOME', $env:JAVA_HOME, 'Machine')
  Write-Host "Executing java --version to verify java version"
  Write-Host $(java --version)
}
function java21 {
  $env:JAVA_HOME = $global:JAVA_21_PATH
  $env:Path = "$env:JAVA_HOME\bin;" + ($env:Path -split ';' | Where-Object { $_ -notmatch '\\jdk.*?\\bin' }) -join ';'
  Write-Host "JAVA_HOME set to: $env:JAVA_HOME"
  [Environment]::SetEnvironmentVariable('JAVA_HOME', $env:JAVA_HOME, 'Machine')
  Write-Host "Executing java --version to verify java version"
  Write-Host $(java --version)
}

Import-Module PSReadLine
Set-PSReadLineOption -PredictionSource History

# Import the Chocolatey Profile that contains the necessary code to enable
# tab-completions to function for `choco`.
# Be aware that if you are missing these lines from your profile, tab completion
# for `choco` will not function.
# See https://ch0.co/tab-completion for details.
$ChocolateyProfile = "$env:ChocolateyInstall\helpers\chocolateyProfile.psm1"
if (Test-Path($ChocolateyProfile)) {
  Import-Module "$ChocolateyProfile"
}

```
