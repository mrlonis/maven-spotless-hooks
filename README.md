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
  - [Setting up Spotless](#setting-up-spotless)
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

## Setting up Spotless

**Note**: To follow this section, your project must be at least on `Java 11`.

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
