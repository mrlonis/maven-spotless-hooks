# 🛠️ Spotless Configuration

## 📑 Table of Contents

<!-- TOC -->
* [🛠️ Spotless Configuration](#-spotless-configuration)
  * [📑 Table of Contents](#-table-of-contents)
  * [❓ What is Spotless?](#-what-is-spotless)
  * [❓ Why Spotless?](#-why-spotless)
  * [📚 Plugin Documentation](#-plugin-documentation)
  * [📋 Pre-requisites](#-pre-requisites)
  * [🧰 Maven Wrapper Setup](#-maven-wrapper-setup)
  * [🧾 Adding .gitattributes](#-adding-gitattributes)
  * [⚙️ Basic Plugin Setup](#-basic-plugin-setup)
    * [🦴 Plugin Skeleton](#-plugin-skeleton)
      * [☕️ Java Configuration](#-java-configuration)
      * [🧾 Pom.xml Configuration](#-pomxml-configuration)
      * [✍️ Markdown Configuration](#-markdown-configuration)
      * [🛢️ SQL (Surprise its prettier!) Configuration](#-sql-surprise-its-prettier-configuration)
      * [🗃️ "Formats" Configuration (Non-Code Files and Prettier)](#-formats-configuration-non-code-files-and-prettier)
        * [📄 Non-Code Files (Still Important!)](#-non-code-files-still-important)
        * [🎨 Prettier (JSON, HTML, YAML, XML) Configuration](#-prettier-json-html-yaml-xml-configuration)
<!-- TOC -->

## ❓ What is Spotless?

Spotless is a general-purpose formatting plugin used
by [6,000 projects on GitHub (Jan 2023)](https://github.com/search?l=Maven+POM&q=spotless&type=Code). It is completely à
la carte, but also includes powerful "batteries-included" if you opt-in.

## ❓ Why Spotless?

There really isn’t a strong alternative.

Spotless is one of the very few formatting tools that works seamlessly with both Maven and Gradle, and can be integrated
into Java projects without requiring new tooling ecosystems or language server configuration. It handles multi-format
linting, supports widely accepted formatting styles (like Palantir Java Format), and is extremely customizable—yet
doesn't get in your way.

If you’re coming from a frontend or Python world, tools like `prettier`, `black`, or `eslint` offer tight `pre-commit`
integration out of the box. In the `Java` ecosystem, that level of integration is oddly lacking. `Spotless` fills that
gap with the added benefit of being language-agnostic across file types.

## 📚 Plugin Documentation

To find out more information about the `spotless-maven-plugin`, please refer to
the [Spotless Maven Plugin Documentation](https://github.com/diffplug/spotless/blob/main/plugin-maven/README.md). This
will give you more information about the configuration options available to you. The configuration options laid out
above are a full-fat recommended configuration. All the sections might not apply to you, like the `sql` section. It is
also strongly advised, if you are adding `spotless` to an existing project, to remove the `java` portion from the
`spotless` configuration for a phase 1 migration. This way, you can start enforcing the `pre-commit` process and get
formatting on some non-critical, non-java files. Once you are happy with the configuration, you can then add the `java`
portion to the `spotless` configuration. This will allow you to get the formatting on the Java files without having to
set up the overall configuration and process in one go.

## 📋 Pre-requisites

- Your project must be on `Java 11`
- Your project must have the `Maven Wrapper` configured

## 🧰 Maven Wrapper Setup

To add Maven wrapper to your project, run the following command: `mvn wrapper:wrapper -Dmaven=3.8.8`

You can do this in almost any IDE, since they often bundle Maven into the IDE itself. It is fine to continue using the
bundled Maven when in the IDE, but we need the Maven Wrapper to perform `pre-commit` commands.

> You can keep using your IDE’s Maven integration for builds and testing, but pre-commit hooks must run through the
> Maven Wrapper (`./mvnw`) to ensure consistency across environments. Additionally, for users who do **not** have Maven
> installed, the wrapper will download the correct version of Maven for them. Otherwise, this `pre-commit` process would
> **force** all developers to install yet another tool on their local machine. This is not ideal, and we want to avoid 
> that if possible.

Despite the above warning, your IDEs built-in git process will also run these hooks. At the end of the day, these hooks
simply go into your `.git/hooks/` directory and are run by git. So, if you are using IntelliJ, Eclipse, or VS Code, the
hooks will run as expected. The wrapper is purely for CLI needs.

## 🧾 Adding .gitattributes

If your project doesn't have a `.gitattributes` file, create one in the root of your project. Failure to do this, and
messing up the line endings for `*.cmd` or the `mvnw` script files will cause issues for other developers on your team,
even if you yourself don't experience any issues.

<!-- markdownlint-disable-next-line MD033 -->
<details><summary>View the <code>.gitattributes</code> file</summary>

```gitattributes
# * text=auto should be the first line in the file
* text=auto
/mvnw text eol=lf
*.cmd text eol=crlf
# Add other files types here as needed
# *.png binary
```

</details>

## ⚙️ Basic Plugin Setup

This section details how to configure `spotless` in your `pom.xml` file. We start off with the overall skeleton of the
`plugin` within the `pom.xml` file, and then brerak out the different configurations for the different file types into
their own section. It is recommended to add all the formatting configurations you want **except** Java formatting in the
first phase. This way, you can get the `pre-commit` hooks set up and working, and then add the Java formatting in a
second phase. This will allow you to get the formatting on the non-critical files first, and then add the Java
formatting later.

### 🦴 Plugin Skeleton

Below is the overall skeleton of the `pom.xml` file. This is broken out here to show the overall high-level structure of
the `spotless` configuration. The actual configurations for specific programming languages and file types are below in
separate sections that are intended to be copied and pasted into the `spotless` plugin's `configuration` section,
replacing the `...` in the `configuration` section.

<!-- markdownlint-disable-next-line MD033 -->
<details><summary>View <code>pom.xml</code> skeleton</summary>

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/maven-v4_0_0.xsd">
  <modelVersion>4.0.0</modelVersion>
  <!-- App specific fields -->
  ...
  <properties>
    <cleanthat.version>2.25</cleanthat.version>
    <!-- Replace with correct version, but minimum required is 17 for Spotless 3.x.x -->
    <java.version>17</java.version>
    <palantir-java-format.version>2.90.0</palantir-java-format.version>
    <spotless.version>3.4.0</spotless.version>
  </properties>
  ...
  <dependencyManagement>
    <dependencies>
      <!-- We add them here because this lets us get dependabot updates for palantir-java-format and cleanthat -->
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
  <!-- Dependencies and other fields -->
  ...
  <build>
    <plugins>
      <!-- START PLUGIN CONFIG -->
      <plugin>
        <groupId>com.diffplug.spotless</groupId>
        <artifactId>spotless-maven-plugin</artifactId>
        <version>${spotless.version}</version>
        <configuration>
          ... <!-- This is where you will paste the configuration for the different file types below. You can quite literally copy and paste the sections below into this block, replacing the ... with what you copied -->
        </configuration>
        <executions>
          <execution>
            <goals>
              <goal>check</goal>
            </goals>
          </execution>
        </executions>
      </plugin>
      <!-- END PLUGIN CONFIG -->
      ...
      <!-- Other Plugins -->
    </plugins>
  </build>
  ...
</project>
```

</details>

An important callout here is that the `spotless` plugin has its `executions` block configured as follows:

```xml
<executions>
  <execution>
    <goals>
      <goal>check</goal>
    </goals>
  </execution>
</executions>
```

This has the side effect of making the CI/CD run the `spotless` check, **NOT** the `apply` goal. This checks that code
was formatted with `spotless` in the CI/CD, but does not apply formatting, and instead, will fail the maven build if the
code is not formatted correctly. This is a good practice to get into, as it will help you catch formatting issues before
they hit your main branch, and identify developers not configuring their local development environment correctly.

#### ☕️ Java Configuration

<!-- markdownlint-disable-next-line MD033 -->
<details><summary>View configuration</summary>

```xml
<java>
  <includes>
    <include>src/main/java/**/*.java</include>
    <include>src/test/java/**/*.java</include>
  </includes>
  <cleanthat>
    <version>${cleanthat.version}</version>
    <mutators>
      <mutator>SafeAndConsensual</mutator>
      <mutator>SafeButNotConsensual</mutator> <!-- Optional -->
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
```

</details>

#### 🧾 Pom.xml Configuration

<!-- markdownlint-disable-next-line MD033 -->
<details><summary>View configuration</summary>

```xml
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
```

</details>

#### ✍️ Markdown Configuration

<!-- markdownlint-disable-next-line MD033 -->
<details><summary>View configuration</summary>

```xml
<markdown>
  <includes>
    <include>**/*.md</include>
  </includes>
  <excludes>
    <!-- You NEED to exclude the submodule files -->
    <exclude>.hooks/**/*.md</exclude>
    <exclude>target/**/*.md</exclude>
  </excludes>
  <flexmark/>
  <trimTrailingWhitespace/>
  <endWithNewline/>
</markdown>
```

</details>

#### 🛢️ SQL (Surprise its prettier!) Configuration

<!-- markdownlint-disable-next-line MD033 -->
<details><summary>View configuration</summary>

```xml
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
```

</details>

#### 🗃️ "Formats" Configuration (Non-Code Files and Prettier)

Non-code files and `prettier` configuration is done in the `formats` block in the `configuration` section of the
`spotless` plugin. This is where you can configure the files that you want to format with `prettier`, and any other
non-code files that you want to format.

```xml
<formats>
  ... <!-- This is where you will paste the configuration for the different file types below. You can quite literally copy and paste the sections below into this block, replacing the ... with what you copied -->
</formats>
```

For now, you can copy this into the `spotless` plugin's `configuration` section, replacing the `...` in the `formats`
block, and then later replacing the `...` in the `formats` block with the sub-sections found below.

##### 📄 Non-Code Files (Still Important!)

This is important because it not only enforces some minor trimming of whitespace and newlines, but also ensures that the
`mvnw` and `mvnw.cmd` files are properly formatted for the OS you are on. `spotless` will format all files according to
the line endings defined in the `.gitattributes` file. This means, we need to keep `mvnw` and `mvnw.cmd` files in
separate blocks, since the first found line ending is used for all files in the `includes` block.

<!-- markdownlint-disable-next-line MD033 -->
<details><summary>View configuration</summary>

```xml
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
```

</details>

##### 🎨 Prettier (JSON, HTML, YAML, XML) Configuration

<!-- markdownlint-disable-next-line MD033 -->
<details><summary>View configuration</summary>

```xml
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
```

</details>

← Back to [README.md](../README.md)
