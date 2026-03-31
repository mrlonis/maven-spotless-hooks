# 🧯 Troubleshooting

## 📑 Table of Contents

<!-- TOC -->
* [🧯 Troubleshooting](#-troubleshooting)
  * [📑 Table of Contents](#-table-of-contents)
  * [🪟 How to fix "git-sh-setup: file not found" in Windows](#-how-to-fix-git-sh-setup-file-not-found-in-windows)
    * [🧪 Git Environment Variable Repair](#-git-environment-variable-repair)
  * [🚫 Disabling Spotless](#-disabling-spotless)
    * [💡 Use Cases for Disabling Spotless](#-use-cases-for-disabling-spotless)
    * [🎍 Bamboo Example](#-bamboo-example)
    * [🤖 GitHub Actions Example](#-github-actions-example)
  * [🪟 Windows: Dynamic JAVA_HOME Env Variable Changing](#-windows-dynamic-java_home-env-variable-changing)
    * [🛠️ PowerShell Profile](#-powershell-profile)
      * [📜 Profile Content](#-profile-content)
  * [🐞 Debugging These Scripts](#-debugging-these-scripts)
<!-- TOC -->

## 🪟 How to fix "git-sh-setup: file not found" in Windows

If you get any errors related to `git-sh-setup` or `git-sh-setup: file not found`, or some other error when performing 
the `git submodule update --init --remote --force` command, it is likely due to a problem with your `git` installation 
or your `PATH` environment variable.

Make sure you are on a recent version of `git`. If you are using `choco`, you can run 
`choco upgrade git -y` to update `git` and if you don't use `choco` to manage `git`, you can download the latest 
version of `git` from the [Git for Windows](https://gitforwindows.org/) website.

### 🧪 Git Environment Variable Repair

[https://stackoverflow.com/questions/49256190/how-to-fix-git-sh-setup-file-not-found-in-windows](https://stackoverflow.com/questions/49256190/how-to-fix-git-sh-setup-file-not-found-in-windows)

1. In the Windows Search bar, type `Environment Variables` and select `Edit the system environment variables`
2. In the `System Properties` window, click on the `Environment Variables` button
3. In the `Environment Variables` window, under `System variables`, click on `Path` and then click on `Edit`
4. In the `Edit Environment Variable` window, click on `New` and add the following paths:
   - `C:\Program Files\Git\usr\bin`
   - `C:\Program Files\Git\mingw64\libexec\git-core`
5. These will be added to the end of the list. Click on each one, and then click on `Move Up` until they are at the top
   of the list

## 🚫 Disabling Spotless

If you ever need or want to disable `spotless`, we can do so by specifying a Maven profile. This can be done by adding 
the following profile configuration to the `pom.xml`:

<!-- markdownlint-disable-next-line MD033 -->
<details><summary>View <code>pom.xml</code> example profile</summary>

```xml
<profile>
  <id>github</id>
  <build>
    <plugins>
      <plugin>
        <groupId>com.diffplug.spotless</groupId>
        <artifactId>spotless-maven-plugin</artifactId>
        <version>${spotless.version}</version>
        <executions>
          <execution>
            <phase>none</phase>
          </execution>
        </executions>
      </plugin>
    </plugins>
  </build>
</profile>
```

</details>

This sets up a profile called `github` that prevents the `spotless` plugin from running. You can then run the following 
command to disable `spotless`: `mvn clean verify -P github`

### 💡 Use Cases for Disabling Spotless

This is often needed if the CI/CD pipeline is a 2-phase or 2-job process. This often has impacted projects that publish 
JARs instead of full Spring Boot applications that get deployed out to the cloud.

### 🎍 Bamboo Example

Your `Bamboo Specs` or `Bamboo UI` should be configured to run the following command: `mvn clean verify -P github`. The 
key here is the `-P github` flag. This will run the `github` profile and disable the `spotless` plugin.

### 🤖 GitHub Actions Example

<!-- markdownlint-disable-next-line MD033 -->
<details><summary>View example GitHub Actions Pipeline</summary>

```yaml
name: CI
on:
  push:
    branches:
      - main
  pull_request:
    branches:
      - main
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v2
      - name: Set up JDK 11
        uses: actions/setup-java@v2
        with:
          java-version: "11"
      - name: Build with Maven
        run: mvn clean verify -P github # Notice the -P github flag here
```

</details>

## 🪟 Windows: Dynamic JAVA_HOME Env Variable Changing

### 🛠️ PowerShell Profile

Run the following command in PowerShell to determine your `$profile` path: `echo $profile`. Then, open the file in your 
favorite text editor. `notepad.exe $profile` or `code $profile` if you have VS Code installed.

#### 📜 Profile Content

Below is the content of the `PowerShell profile`. This `profile` will give you dynamic functions, aptly named `java8`, 
`java11`, `java17`, and `java21` to set the `JAVA_HOME` environment variable to the correct version of `Java`. You can 
then run these functions in PowerShell to switch between `Java` versions at will.

> **Note**: Setting `JAVA_HOME` for the current session works without admin privileges.
> Persisting it machine-wide requires an Administrator PowerShell session.

<!-- markdownlint-disable-next-line MD033 -->
<details><summary>View example <code>PowerShell</code> profile</summary>

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
```

</details>

## 🐞 Debugging These Scripts

To debug these scripts, simply set the `MAVEN_SPOTLESS_HOOKS_DEBUG` environment variable to `1`. This enables verbose 
logging for the hook scripts.

← Back to [README.md](../README.md)
