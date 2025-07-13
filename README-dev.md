# Developer Guide: MarkdownLint MCP Server

This document provides developers with a deep dive into the architecture,
implementation, and setup of the MarkdownLint MCP Server.

## Project Goal

The goal of this project is to build a Python package that provides a "Markdown
Linter" as a set of tools for an AI agent. The server is designed to be
launched on-demand by an MCP client (like Gemini CLI) when the agent needs to
check or fix a Markdown file, rather than running continuously.

This project is built using `uv` to automate setup and adhere to modern Python
packaging standards.

## Core Technologies

* **Python 3.11+**: The required Python version.
* **uv**: For project initialization, dependency management, and running
    scripts in a virtual environment.
* **FastMCP**: The framework used to create the MCP server and define the
    tools.
* **markdownlint-cli2**: The underlying Node.js-based tool that performs the
    actual Markdown linting and fixing.
* **npm**: Used to install `markdownlint-cli2`.

## Project Structure

The project was initialized using `uv init --lib` and follows the standard `src`
layout for a Python library.

```text
.
├── pyproject.toml          # Project metadata, dependencies, and scripts
├── scripts/
│   └── setup.sh            # User-friendly setup script
├── src/
│   └── markdownlint_mcp/
│       ├── __init__.py
│       └── main.py         # Core application logic
└── .venv/                    # Virtual environment managed by uv
```

## Development Setup

This setup is intended for developers who are actively working on the server's
source code.

> [!NOTE]
> For end-users, the recommended installation method is `pipx` as
> described in `README.md`.

The `setup.sh` script handles all the necessary steps for a local development
environment.

1. **Clone the repository.**
2. **Install `uv`**: This project uses `uv` for environment and package
    management.
3. **Run the setup script**:

    ```bash
    chmod +x scripts/setup.sh
    ./scripts/setup.sh
    ```

This script will:

1. Use `uv venv` to create a Python virtual environment.
2. Use `uv pip install -e .` to install the project in "editable" mode, along
    with its Python dependencies (`fastmcp`).
3. Use `npm` to install `markdownlint-cli2` locally.

## Implementation Deep Dive

### `pyproject.toml`

This file is the heart of the project's configuration.

* **`[project]`**: Defines the package name (`markdownlint-mcp`), version,
    description, and Python dependencies (`fastmcp`).
* **`[project.scripts]`**: This creates a command-line entry point.

  > [!IMPORTANT]
  > This is a crucial section that makes the on-demand server possible.

    ```toml
    [project.scripts]
    markdownlint-mcp-server = "markdownlint_mcp.main:run"
    ```

    When the package is installed, this creates a script named
    `markdownlint-mcp-server` that, when executed, calls the `run()` function
    in `src/markdownlint_mcp/main.py`.

### `src/markdownlint_mcp/main.py`

This file contains the core logic for the MCP server.

* **MCP Instance**: A `FastMCP` instance is created to define the server, its
    description, and its tools.
* **Tool**:
  * `lint`: The primary and only tool. It uses
        `asyncio.create_subprocess_shell` to run `markdownlint-cli2` commands.
        It first runs with the `--fix` flag to automatically correct issues,
        then runs again without it to report any remaining, non-fixable errors.
* **Resource**:
  * `get_inline_directives`: A resource exposed via
        `config://markdownlint/inline-directives`. It fetches the `README.md`
        from the official `markdownlint` GitHub repository and extracts the
        "Configuration" section. This provides the agent with up-to-date
        information on how to use inline comments (e.g.,
        `<!-- markdownlint-disable MD013 -->`) to control rules directly
        within a file.
* **Server Entry Point (`run` function)**:

    ```python
    def run():
        """This is the function the MCP client will call to start our server."""
        # This runs the server using the default transport (stdio)
        mcp.run()
    ```

    This function is called by the `markdownlint-mcp-server` script. It starts
    the server using `fast-mcp`'s default standard I/O (stdio) transport, which
    is ideal for communication with a parent process like the Gemini CLI.

### On-Demand Server Launch

The server is launched by the MCP client. The configuration for Gemini CLI for a
globally installed server via `pipx` is simple:

```json
{
  "mcp_servers": {
    "markdownlint": {
      "command": "markdownlint-mcp-server"
    }
  }
}
```

For local development, you can configure the client to run the server directly
from the source code using `uv`:

```json
{
  "mcp_servers": {
    "markdownlint": {
      "command": "uv",
      "args": [
        "run",
        "markdownlint-mcp-server"
      ],
      "working_directory": "/path/to/your/markdownlint-mcp/project"
    }
  }
}
```

Here's the sequence of events for the local development setup:

1. The agent calls a tool from the `markdownlint` server.
2. The Gemini CLI sees the `mcp_servers` configuration for `markdownlint`.
3. It executes `uv run markdownlint-mcp-server` in the specified project
    directory.
4. `uv` activates the project's virtual environment and runs the
    `markdownlint-mcp-server` script.
5. The script calls the `run()` function in `main.py`, starting the server.
6. The server communicates with the CLI over stdio to execute the tool and
    return the result.
7. Once the interaction is complete, the server process exits.

## Local Testing

> [!TIP]
> To test the server without a client, you can run `main.py` as a script. This
> starts the server on `localhost:8000` for easier debugging.

```bash
python -m src.markdownlint_mcp.main
```
