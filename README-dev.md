# Developer Guide: Auto-Lint MCP Server

This document provides developers with a deep dive into the architecture,
implementation, and setup of the Auto-Lint MCP Server.

## Project Goal

The goal of this project is to build a background service that automatically
formats and lints code when files are modified. It provides a stateful,
queryable resource (`resource://linting_violations`) that always reflects the
current set of non-fixable errors in the project, allowing AI agents and other
tools to programmatically access and act upon the project's code quality
status.

## Core Technologies

* **Python 3.11+**: The required Python version.
* **uv**: For project initialization, dependency management, and running
    scripts.
* **FastMCP**: The framework used to create the MCP server and expose
    resources/tools.
* **watchdog**: A library for monitoring file system events, specifically
    using the reliable `PollingObserver`.
* **typer**: For creating a clean and robust command-line interface.
* **ruff**: For linting and formatting Python files.
* **markdownlint-cli**: For linting and formatting Markdown files.

## Architecture Overview

The final implementation is a resilient, multi-threaded application built
around a **dual producer-consumer** pattern using two separate queues. This
design provides a highly responsive experience by separating immediate linting
feedback from less frequent, delayed formatting.

1. **Producer (The Watcher):** A single, reliable file system watcher
    (`PollingObserver`) continuously monitors the project directory. When a
    relevant file is modified, it starts **two separate timers**:
    * A short-delay timer for near-instant linting.
    * A long-delay timer for non-disruptive formatting.
    When each timer completes, the file path is added to the appropriate queue
    (`lint_queue` or `format_queue`).

2. **Consumer 1 (The Linter Worker):** A dedicated background thread for
    linting. It immediately pulls file paths from the `lint_queue`, executes
    the appropriate linter (e.g., `ruff check`), and updates the central
    violation state.

3. **Consumer 2 (The Formatter Worker):** A second background thread for
    formatting. It pulls file paths from the `format_queue` after a significant
    delay, then runs the code formatter (e.g., `ruff format` or
    `markdownlint --fix`) on the file.

4. **Stateful Server (The `LintingServer` Class):** The core logic is
    encapsulated in the `LintingServer` class in `server.py`. This class
    manages all state (the violation cache, locks), the worker threads, and the
    `FastMCP` instance. This object-oriented approach avoids global state and
    makes the system more robust and testable.

## Code Structure

* **`main.py`**: The application entry point. It uses `typer` to parse CLI
    arguments and then instantiates and starts the `LintingServer`.
* **`server.py`**: Contains the main `LintingServer` class, which
    orchestrates all components. It defines the MCP resource and tool, and
    contains the logic for the linter and formatter worker threads.
* **`watcher.py`**: Implements the `DualCallbackEventHandler` using
    `watchdog`'s `PollingObserver`. Its only job is to detect relevant file
    modifications and push file paths to the correct queues after their
    respective delays.
* **`linters.py`**: A stateless module that contains the logic for running
    "check-only" commands (e.g., `ruff check`). It returns any violations
    found.
* **`formatters.py`**: A stateless module that contains the logic for running
    "fixing" or "formatting" commands (e.g., `ruff format`,
    `markdownlint --fix`).

## Local Development Setup

1. **Clone the repository.**
2. **Install dependencies:**

    ```bash
    uv pip install -e .
    ```

3. **Install Node.js dependencies:**

    ```bash
    npm install
    ```

4. **Run the server:**

    ```bash
    uv run python -m src.md_lint_mcp.main --mode auto --linters ruff,markdownlint --formatters ruff,markdownlint <!-- markdownlint-disable-line MD013 -->
    ```

The server will start in the foreground, and you can test its behavior by
modifying `.py` or `.md` files within the project directory.
