# MarkdownLint MCP Server

This project provides an intelligent "Markdown Linter" as a set of tools for an
AI agent. It's an on-demand server that can be launched by a client (like
Gemini CLI) to check and fix Markdown files.

## Features: Your Intelligent Markdown Assistant

Stop wasting time on tedious Markdown formatting! This server acts as your
personal assistant, ensuring your documentation is always clean, consistent, and
professional. It integrates seamlessly with your AI agent to automate the
entire linting process.

### Why You'll Love It

* **Effortless Auto-Fixing**: Automatically corrects most formatting errors
    the moment you create or modify a Markdown file. It handles everything from
    extra spaces to inconsistent list styles, so you don't have to.
* **Focus on What Matters**: For complex issues that require a human touch
    (like a heading that needs rephrasing), the server pinpoints the exact
    problem. This lets you focus on creating great content, not on fighting
    with formatting rules.
* **On-Demand and Lightweight**: The server only runs when needed, so it won’t
    bog down your system. It’s there when you need it and gone when you don’t.
* **Customizable for Your Projects**: Do you have a specific style guide? The
    server can read a local `.markdownlint-cli2.jsonc` configuration file,
    allowing you to tailor its rules to fit your project's unique needs.

## Available Tools

This server provides the following tools for your AI agent:

### `lint(file_path: str)`

This is the primary tool for linting your Markdown files. It automatically
corrects common formatting issues and reports any violations that may require
manual changes.

When violations are found, the tool returns a mandatory directive to the agent,
instructing it to fix them. If the agent determines that a rule should be
ignored for a specific line, it must first ask for your confirmation. Once you
agree, it will use the `get_inline_directives` resource to learn how to disable
the rule and apply the change. This ensures that you always have the final say
on how your files are formatted.

### `get_inline_directives()`

This resource fetches the official documentation for inline directives from
the `markdownlint` repository. It provides up-to-date information on how to
use inline comments to control linting rules directly within a Markdown
file.

## Installation

This server is designed for easy installation and use as a command-line tool
via `pipx`.

### Prerequisites

1. **Python 3.11+**
2. **pipx**: A tool for installing and running Python applications in isolated
    environments. If you don't have it, install it with:

    ```bash
    python3 -m pip install --user pipx
    python3 -m pipx ensurepath
    ```

3. **Node.js and npm**: The underlying `markdownlint-cli2` tool requires a
    Node.js environment. Install it via your system's package manager (e.g.,
    `apt`, `brew`, `yum`).
4. **markdownlint-cli2**: Once Node.js is installed, install the linter
    globally:

    ```bash
    npm install -g markdownlint-cli2
    ```

> [!NOTE]
> Depending on how you installed Node.js, you may need to use `sudo` to run
> `npm install -g`. To avoid this, we recommend using a Node Version
> Manager ([nvm](https://github.com/nvm-sh/nvm)) to install Node.js and
> npm. If you installed Node.js via a system package manager like `apt` or
> `brew`, you are not required to use `nvm`, but you may need to prefix the
> `npm` command with `sudo`.

### Install the MCP Server

With the prerequisites in place, install the server with a single `pipx`
command:

```bash
pipx install git+https://github.com/en-ver/markdownlint-mcp.git
```

This command automatically creates a virtual environment for the server,
installs it, and makes the `markdownlint-mcp-server` command available
globally in your system's PATH.

#### Verify the Installation

After the installation is complete, you can verify that the server is
accessible by running:

```bash
markdownlint-mcp-server --version
```

You should see the version number printed to the console (e.g.,
`markdownlint-mcp-server 0.1.0`). This confirms that the server is correctly
installed and ready to be used by your MCP client.

## Usage

Once the server is installed and verified, you need to configure your MCP
client to use it.

### Gemini CLI Configuration

Add the following configuration to your Gemini settings. This tells the CLI how
to launch the globally available `markdownlint-mcp-server`.

```json
{
  "mcp_servers": {
    "markdownlint": {
      "command": "markdownlint-mcp-server",
      "args": [
        "--no-banner"
      ]
    }
  }
}
```

This configuration is much simpler because `pipx` handles the complexity of
environments and paths. The `command` is now just the name of the script.

## Customization

You can tailor the linter's behavior to fit your project's specific style guide
by creating a `.markdownlint-cli2.jsonc` file in the root of your project
directory. When the `lint` tool is run, it will automatically detect and apply
the rules defined in this file.

This allows you to:

* Enable or disable specific rules.
* Configure parameters for rules (e.g., set the allowed line length).
* Extend pre-configured style guides.

### Example Configuration

Here is a simple example that disables the `line-length` rule:

```json
{
  "config": {
    "line-length": false
  }
}
```

### Finding Configuration Options

The full set of configurable rules and options can be found in the official
`markdownlint` JSON schema. This document is the definitive source for all
available settings.

Since this project installs `markdownlint-cli2` directly on your machine, you
are free to use all of its capabilities. We highly recommend consulting the
official documentation to explore advanced features like creating custom rules,
using different style guides, and more.

> [!TIP]
> We recommend exploring the schema to see all the ways you can customize the
> linter to match your needs.
>
> [View the official .markdownlint.jsonc schema](https://github.com/DavidAnson/markdownlint/blob/main/schema/.markdownlint.jsonc)

## Uninstall

To remove the server and its dependencies, follow these steps to uninstall the
packages installed by `pipx` and `npm`.

> [!CAUTION]
> This will not remove `pipx` or `Node.js` from your system, only the
> packages related to this project.

1. **Uninstall the MCP Server**:

    ```bash
    pipx uninstall markdownlint-mcp
    ```

2. **Uninstall the Linter**:

    ```bash
    npm uninstall -g markdownlint-cli2
    ```

## For Developers

If you wish to contribute to the server, please see the
[Developer Guide](README-dev.md) for detailed instructions on local setup,
architecture, and testing.
