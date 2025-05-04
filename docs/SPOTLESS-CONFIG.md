# 🛠️ Spotless Configuration

## 📑 Table of Contents

- [🛠️ Spotless Configuration](#️-spotless-configuration)
  - [📑 Table of Contents](#-table-of-contents)
  - [❓ Why Spotless?](#-why-spotless)
  - [📋 Pre-requisites](#-pre-requisites)
  - [🧰 Maven Wrapper Setup](#-maven-wrapper-setup)
  - [🧾 Adding .gitattributes](#-adding-gitattributes)
  - [⚙️ Basic Plugin Setup](#️-basic-plugin-setup)
    - [🦴 Plugin Skeleton](#-plugin-skeleton)
      - [🗃️ "Formats" Configuration (Non-Code Files and Prettier)](#️-formats-configuration-non-code-files-and-prettier)
        - [📄 Non-Code Files (Still Important!)](#-non-code-files-still-important)
        - [🎨 Prettier (JSON, HTML, YAML, XML) Configuration](#-prettier-json-html-yaml-xml-configuration)
      - [☕️ Java Configuration](#️-java-configuration)
      - [🧾 Pom.xml Configuration](#-pomxml-configuration)
      - [✍️ Markdown Configuration](#️-markdown-configuration)
      - [🛢️ SQL (Surprise its prettier!) Configuration](#️-sql-surprise-its-prettier-configuration)
  - [📚 Plugin Documentation](#-plugin-documentation)

## ❓ Why Spotless?

There really isn’t a strong alternative.

Spotless is one of the very few formatting tools that works seamlessly with both Maven and Gradle, and can be integrated into Java projects without requiring new tooling ecosystems or language server configuration. It handles multi-format linting, supports widely accepted formatting styles (like Palantir Java Format), and is extremely customizable—yet doesn't get in your way.

If you’re coming from a frontend or Python world, tools like `prettier`, `black`, or `eslint` offer tight `pre-commit` integration out of the box. In the `Java` ecosystem, that level of integration is oddly lacking. `Spotless` fills that gap with the added benefit of being language-agnostic across file types.

## 📋 Pre-requisites

- Your project must be on `Java 11`
- Your project must have the `Maven Wrapper` configured

## 🧰 Maven Wrapper Setup

To add Maven wrapper to your project, run the following command: `mvn wrapper:wrapper -Dmaven=3.8.8`

You can do this in almost any IDE, since they often bundle Maven into the IDE itself. It is fine to continue using the bundled Maven when in the IDE, but we need the Maven Wrapper to perform `pre-commit` commands.

> You can keep using your IDE’s Maven integration for builds and testing, but pre-commit hooks must run through the Maven Wrapper (`./mvnw`) to ensure consistency across environments. Additionally, for users who do **not** have Maven installed, the wrapper will download the correct version of Maven for them. Otherwise, this `pre-commit` process would **force** all developers to install yet another tool on their local machine. This is not ideal, and we want to avoid that if possible.

Despite the above warning, your IDEs built-in git process will also run these hooks. At the end of the day, these hooks simply go into your `.git/hooks/` directory and are run by git. So, if you are using IntelliJ, Eclipse, or VS Code, the hooks will run as expected. The wrapper is purely for CLI needs.

## 🧾 Adding .gitattributes

If your project doesn't have a `.gitattributes` file, create one in the root of your project and add the following lines:

<!-- markdownlint-disable-next-line MD033 -->
<details><summary>View the <code>.gitattributes</code> file</summary>

```gitattributes
/mvnw text eol=lf
*.cmd text eol=crlf
# Add other files here before the * text=auto
# *.png binary
# * text=auto should be the last line in the file
* text=auto
```

</details>

> This is **NOT** optional. Failure to do this, and messing up the line endings for `*.cmd` or the `mvnw` script files will cause issues with users on Windows and Mac. Mac cannot run `mvnw` if the line endings are `crlf`, and Windows cannot run `*.cmd*` if the line endings are not `crlf`.

## ⚙️ Basic Plugin Setup

Below is a full-fat `spotless` configuration, configuring many file types, including `Java`, `XML`, `JSON`, `YAML`, `HTML`, `Markdown`, and `SQL`.

This is a recommended `final` configuration for most projects. However, you can, and should, remove the sections that you do not need.

It is recommended to add everything **BUT** the `java` section to start with. Get that working in your local development workflow and your CI/CD. Merge those changes to your main branch. Then, add the `java` section to the `spotless` configuration. This will allow you to get the formatting on the `Java` files without having to setup the overall configuration and process in one go, reducing the burden on code reviewers and limiting the blast radius of merge conflicts on your most important files; `Java` files.

### 🦴 Plugin Skeleton

Below is the overall skeleton of the `pom.xml` file. This is broken out here to show the overall high-level structure of the `spotless` configuration. The actual configurations for specific programming languages and file types are below in separate sections that are intended to be copied and pasted into the `spotless` plugin's `configuration` section, replacing the `...` in the `configuration` section.

<!-- markdownlint-disable-next-line MD033 -->
<details><summary>View <code>pom.xml</code> skeleton</summary>

```xml
<project>
  <properties>
    <cleanthat.version>2.20</cleanthat.version>
    <!-- Replace with correct version, but minimum required is 11 -->
    <java.version>11</java.version>
    <palantir-java-format.version>2.63.0</palantir-java-format.version>
    <spotless.version>2.44.4</spotless.version>
  </properties>
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
  <build>
    <plugins>
      <plugin>
        <groupId>com.diffplug.spotless</groupId>
        <artifactId>spotless-maven-plugin</artifactId>
        <version>${spotless.version}</version>
        <configuration>
          ...
        </configuration>
        <executions>
          <execution>
            <goals>
              <goal>check</goal>
            </goals>
          </execution>
        </executions>
      </plugin>
    </plugins>
  </build>
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

This has the side effect of making the CI/CD run the `spotless` check, **NOT** the `apply` goal. This checks that code was formatted with `spotless` in the CI/CD, but does not apply formatting, and instead, will fail the maven build if the code is not formatted correctly. This is a good practice to get into, as it will help you catch formatting issues before they hit your main branch, and identify developers not configuring their local development environment correctly.

#### 🗃️ "Formats" Configuration (Non-Code Files and Prettier)

Non-code files and `prettier` configuration is done in the `formats` block in the `configuration` section of the `spotless` plugin. This is where you can configure the files that you want to format with `prettier`, and any other non-code files that you want to format.

```xml
<formats>
  ...
</formats>
```

For now, you can copy this into the `spotless` plugin's `configuration` section, replacing the `...` in the `formats` block, and then later replacing the `...` in the `formats` block with the sub-sections found below.

##### 📄 Non-Code Files (Still Important!)

This is important because it not only enforces some minor trimming of whitespace and newlines, but also ensures that the `mvnw` and `mvnw.cmd` files are properly formatted for the OS you are on. `spotless` will format all files according to the line endings defined in the `.gitattributes` file. This means, we need to keep `mvnw` and `mvnw.cmd` files in separate blocks, since the first found line ending is used for all files in the `includes` block.

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

## 📚 Plugin Documentation

To find out more information about the `spotless-maven-plugin`, please refer to the [Spotless Maven Plugin Documentation](https://github.com/diffplug/spotless/blob/main/plugin-maven/README.md). This will give you more information about the configuration options available to you. The configuration options laid out above are a full-fat recommended configuration. All the sections might not apply to you, like the `sql` section. It is also strongly advised, if you are adding `spotless` to an existing project, to remove the `java` portion from the `spotless` configuration for a phase 1 migration. This way, you can start enforcing the `pre-commit` process and get formatting on some non-critical, non-java files. Once you are happy with the configuration, you can then add the `java` portion to the `spotless` configuration. This will allow you to get the formatting on the Java files without having to set up the overall configuration and process in one go.

← Back to [README.md](./README.md)
