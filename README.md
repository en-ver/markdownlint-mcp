# MD Lint MCP Server

This project provides an intelligent "Markdown Linter" as a set of tools for an
AI agent. It's an on-demand server that can be launched by a client (like
Gemini CLI) to check and fix Markdown files.

## Features: Your Intelligent Markdown Assistant

Stop wasting time on tedious Markdown formatting! This server acts as your
personal assistant, ensuring your documentation is always clean, consistent, and
professional. It integrates seamlessly with your AI agent to automate the
entire linting process.

### Why You'll Love It

* **Effortless Auto-Fixing**: When triggered, the `lint` tool automatically
    corrects most formatting errors in your Markdown files. It handles
    everything from extra spaces to inconsistent list styles, so you don't have
    to.
* **Focus on What Matters**: For complex issues that require a human touch
    (like a heading that needs rephrasing), the server pinpoints the exact
    problem. This lets you focus on creating great content, not on fighting
    with formatting rules.
* **On-Demand and Lightweight**: The server only runs when needed, so it won
    bog down your system. It’s there when you need it and gone when you don’t.
* **Customizable for Your Projects**: Do you have a specific style guide? The
    server can read a local `.markdownlint-cli.jsonc` configuration file,
    allowing you to tailor its rules to fit your project's unique needs.

## Available Tools

This server provides the following tools for your AI agent:

### `lint(file_path: str)`

This is the primary tool for linting your Markdown files. It automatically
corrects common formatting issues and reports any violations that may require
manual changes.

For violations that require manual changes, the agent can fix them or use
inline directives to ignore them. To learn how to use inline directives, the
agent can use the `get_inline_directives` resource. This ensures that you
always have the final say on how your files are formatted.

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

3. **Node.js and npm**: The underlying `markdownlint-cli` tool requires a
    Node.js environment. Install it via your system's package manager (e.g.,
    `apt`, `brew`, `yum`).
4. **markdownlint-cli**: Once Node.js is installed, install the linter
    globally:

    ```bash
    npm install -g markdownlint-cli
    ```

> [!NOTE]
> Depending on how you installed Node.js, you may need to use `sudo` to run
> `npm install -g`. To avoid this, we recommend using a Node Version
> Manager ([nvm](https://github.com/nvm-sh/nvm)) to install Node.js and
> npm. If you installed Node.js via a system package manager like `apt` or
> `brew`, you are not required to use `nvm`, but you may need to prefix
> the `npm` command with `sudo`.

### Install the MCP Server

With the prerequisites in place, install the server with a single `pipx`
command:

```bash
pipx install --pip-args="--no-cache-dir --force-reinstall" git+https://github.com/en-ver/md-lint-mcp.git
```

This command automatically creates a virtual environment for the server,
installs it, and makes the `md-lint-mcp-server` command available globally in
your system's PATH.

#### Verify the Installation

After the installation is complete, you can verify that the server is
accessible by running:

```bash
md-lint-mcp-server --version
```

You should see the version number printed to the console (e.g.,
`md-lint-mcp-server 0.1.0`). This confirms that the server is correctly
installed and ready to be used by your MCP client.

## Usage with Gemini CLI

To use this server, you must tell the Gemini CLI how to run it for your specific project. This is done by creating a configuration file inside your project directory.

### Step 1: Create the Configuration File

1. avigate to the root directory of the project you want to monitor.
2. reate a new directory named `.gemini`.
3. nside the `.gemini` directory, create a new file named `mcp_settings.json`.

Your project structure should look like this:

```
your-project/
├── .gemini/
│   └── mcp_settings.json
└── ... (your other project files)
```

### Step 2: Add the Configuration

Copy and paste the following JSON into your `mcp_settings.json` file.

> [!IMPORTANT]
> You **must** replace `"/path/to/your/monitored/project"` with the **absolute path** to your project's root directory.

```json
{
  "servers": [
    {
      "name": "AutoLint",
      "run": "md-lint-mcp-server",
      "transport": "stdio",
      "cwd": "/path/to/your/monitored/project"
    }
  ]
}
```

**How to get the absolute path:**

* inux or macOS, navigate to your project folder in the terminal and run the `pwd` command.
* On Windows, you can get it from the address bar in File Explorer.

### Step 3: Start the Server

The server will now start automatically in the background the first time the Gemini CLI needs to access one of its tools. Because it's a file watcher, it will remain running as long as the Gemini CLI is active in that project.

When you create or modify a Python or Markdown file, the `AutoLint` server will automatically format it and report any remaining issues directly into the agent's context, allowing it to fix them for you.

## Customization

You can tailor the linter's behavior to fit your project's specific style guide
by creating a `.markdownlint-cli.jsonc` file in the root of your project
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

Since this project installs `markdownlint-cli` directly on your machine, you
are free to use all of its capabilities. We highly recommend consulting the
official documentation to explore advanced features like creating custom rules,
using different style guides, and more.

> [!TIP]
> We recommend exploring the schema to see all the ways you can customize the
> linter to match your needs.
> [View the official .markdownlint.jsonc schema](https://github.com/DavidAnson/markdownlint/blob/main/schema/.markdownlint.jsonc)

## Uninstall

To remove the server and its dependencies, follow these steps to uninstall the
packages installed by `pipx` and `npm`.

> [!CAUTION]
> This will not remove `pipx` or `Node.js` from your system, only the
> packages related to this project.

1. **Uninstall the MCP Server**:

    ```bash
    pipx uninstall md-lint-mcp
    ```

2. **Uninstall the Linter**:

    ```bash
    npm uninstall -g markdownlint-cli
    ```

## For Developers

If you wish to contribute to the server, please see the
[Developer Guide](README-dev.md) for detailed instructions on local setup,
architecture, and testing.
