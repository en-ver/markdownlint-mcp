# Auto-Lint MCP Server

This project provides an intelligent, background-running server that
automatically formats and lints your code, providing real-time feedback to AI
agents and other development tools.

## Features: Your Automated Code Quality Assistant

Stop wasting time on tedious formatting and style checks! This server acts as
your personal assistant, ensuring your code is always clean, consistent, and
professional. It runs in the background, watching for file changes and fixing
issues on the fly.

### Why You'll Love It

* **Delayed, Non-Disruptive Formatting**: The server waits for you to finish
    your work. Code formatting is applied after a configurable quiet period
    (defaulting to 60 seconds), so it never interrupts your typing.
* **Instant Linting Feedback**: As soon as you save a file, the server runs
    its linters and immediately updates its internal state with any non-fixable
    violations. This allows a connected AI agent to see and fix problems in
    near real-time.
* **Stateful and Queryable**: The server exposes a
    `resource://linting_violations` resource that always contains the complete
    list of current errors in the project. This allows tools to be built on top
    of a reliable source of truth for code quality.
* **Extensible and Configurable**: Easily enable or disable specific linters
    and formatters via command-line flags. The system is designed to be
    extended with new tools for different languages.
* **Efficient and Lightweight**: The server uses a reliable, low-impact
    polling mechanism to watch for file changes and operates in the background
    without bogging down your system.

## How It Works

The server runs in a special `auto` mode. When you start it, it does the
following:

1. **Watches for file modifications** to `.py` and `.md` files.
2. When a file is modified, it starts **two separate timers**:
    * A **short-delay timer** for linting (default: 0.5s).
    * A **long-delay timer** for formatting (default: 60s).
3. When the **linting timer** finishes, it runs the appropriate linter (e.g.,
    `ruff check`) and updates the `linting_violations` resource with any errors
    that couldn't be auto-fixed.
4. When the **formatting timer** finishes, it runs the appropriate formatter
    (e.g., `ruff format`) on the file, cleaning up the code style.

## Installation

This server is designed for local development and is not intended for a `pipx`
installation. Please follow the developer setup guide.

## Usage with Gemini CLI

To use this server, you must tell the Gemini CLI how to run it for your
specific project. This is done by creating a configuration file inside your
project directory.

### Step 1: Create the Configuration File

1. Navigate to the root directory of the project you want to monitor.
2. Create a new directory named `.gemini`.
3. Inside the `.gemini` directory, create a new file named
    `mcp_settings.json`.

### Step 2: Add the Configuration

Copy and paste the following JSON into your `mcp_settings.json` file.

> [!IMPORTANT]
> You **must** replace `"/path/to/your/monitored/project"` with the
> **absolute path** to your project's root directory.

```json
{
  "servers": [
    {
      "name": "AutoLint",
      "run": "uv run python -m src.agent_multitool.main --mode auto --linters ruff,markdownlint --formatters ruff,markdownlint", <!-- markdownlint-disable-line MD013 -->
      "transport": "http",
      "host": "127.0.0.1",
      "port": 8585,
      "cwd": "/path/to/your/monitored/project"
    }
  ]
}
```

### Step 3: Start the Server

The server will now start automatically in the background the first time the
Gemini CLI is active in that project. When you modify a file, the `AutoLint`
server will automatically format it and report any remaining issues.

## Command-Line Arguments

You can customize the server's behavior using the following flags in the `run`
command of your `mcp_settings.json`:

* `--mode {auto,manual}`: The operational mode. `auto` is recommended.
* `--linters {ruff,markdownlint}`: A comma-separated list of linters to
    enable.
* `--formatters {ruff,markdownlint}`: A comma-separated list of formatters to
    enable.
* `--lint-delay <seconds>`: The quiet period before running linters (default:
    0.5).
* `--format-delay <seconds>`: The quiet period before running formatters
    (default: 60.0).

## For Developers

If you wish to contribute to the server, please see the
[Developer Guide](README-dev.md) for detailed instructions on local setup,
architecture, and testing.
