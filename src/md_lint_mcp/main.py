# src/md_lint_mcp/main.py

import asyncio
from pathlib import Path
import httpx
import sys
from importlib import metadata

from fastmcp import FastMCP

mcp = FastMCP(
    name="MD Lint MCP",
    instructions="This is a Markdown linting MCP server. You can use the 'lint' tool to check for and fix formatting issues in Markdown files ('.md', '.markdown').",
)


# === PRIMARY TOOL: LINT ===
@mcp.tool
async def lint(file_path: str) -> str:
    """
    You can use this tool to validate if a Markdown file has formatting rule violations.

    It automatically fixes any violations that can be addressed automatically and
    returns a list of violations that require manual intervention.

    If the user wants, you can manually fix the remaining violations or use
    inline directives to ignore them.

    Args:
        file_path: The path to the Markdown file to lint. This MUST be an
            absolute path, as relative paths are not supported.
            - Linux/macOS example: '/home/user/project/file.md'
            - Windows example: 'C:\\Users\\user\\project\\file.md'

    Returns:
        A string indicating either that no violations were found or a
        formatted list of the remaining violations that require manual correction.
    """
    path = Path(file_path)
    if not path.exists():
        return f"Error: File not found at '{file_path}'"
    if not path.is_file():
        return f"Error: Path '{file_path}' is not a file."

    # First, run with --fix to autocorrect any violations.
    # We suppress the output of this command as it's not needed.
    fix_command = f'markdownlint-cli2 --fix "{path.resolve()}"'
    fix_process = await asyncio.create_subprocess_shell(
        fix_command,
        stdout=asyncio.subprocess.DEVNULL,
        stderr=asyncio.subprocess.DEVNULL,
    )
    await fix_process.communicate()

    # Second, run without --fix to get a clean list of remaining errors.
    lint_command = f'markdownlint-cli2 "{path.resolve()}"'
    lint_process = await asyncio.create_subprocess_shell(
        lint_command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    _, stderr = await lint_process.communicate()

    # Exit code 0 means no violations were found.
    # Exit code 1 means violations remain.
    # Any other exit code indicates a tool error.
    if lint_process.returncode is not None and lint_process.returncode > 1:
        error_message = stderr.decode("utf-8").strip()
        return f"Error during linting process for '{file_path}':\n{error_message}"

    remaining_errors = stderr.decode("utf-8").strip()

    if not remaining_errors:
        return f"No linting violations found in '{file_path}'."
    else:
        return f"""The file has the following violations:
{remaining_errors}

I recommend addressing all of the violations listed above at once, as it is inefficient to fix them one by one. After you have addressed all of them, please run `lint` again to confirm the file is clean.

NOTE: In some cases, you may determine that a rule should be ignored for a specific line. If so, you can first propose the change to the user and get their confirmation. If the user agrees, you can then use the 'get_inline_directives' resource to learn how to disable the rule and apply the change.
"""


# === RESOURCE: INLINE DIRECTIVES ===
@mcp.resource("config://markdownlint/inline-directives")
async def get_inline_directives() -> str:
    """
    You can use this resource to get information about how to use inline comments
    (directives) to control linting rules directly within a Markdown file.

    These directives allow you to disable or enable specific rules for certain
    lines or sections of the file, which is useful for handling exceptions to
    the linting rules.

    Returns:
        A string containing the documentation for inline directives, or an
        error message if the documentation could not be retrieved.
    """
    url = "https://raw.githubusercontent.com/DavidAnson/markdownlint/main/README.md"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            content = response.text

        # It finds the "## Configuration" heading and extracts content until the next H2 heading.
        start_phrase = "## Configuration"
        start_index = content.find(start_phrase)

        if start_index == -1:
            return "Error: Could not find the 'Configuration' section in the documentation."

        # Find the next H2 heading to determine the end of the section.
        end_index = content.find("\n## ", start_index + len(start_phrase))

        if end_index == -1:
            # If no subsequent H2 heading is found, assume it's the last section.
            return content[start_index:].strip()
        else:
            return content[start_index:end_index].strip()

    except httpx.HTTPStatusError as e:
        return f"Error fetching documentation: {e.response.status_code} {e.response.reason_phrase}"
    except Exception as e:
        return f"An unexpected error occurred: {e}"


# === SERVER ENTRY POINT ===
def run():
    """This is the function the MCP client will call to start our server."""
    if "--version" in sys.argv:
        try:
            version = metadata.version("md-lint-mcp")
        except metadata.PackageNotFoundError:
            version = "0.1.0"  # Fallback for local dev
        print(f"md-lint-mcp-server {version}")
        return

    if "--help" in sys.argv or "-h" in sys.argv:
        print(
            """Usage: md-lint-mcp-server [options]

An intelligent "Markdown Linter" as a set of tools for an AI agent.

Options:
  --version             Show version number and exit.
  -h, --help            Show this help message and exit.
  --banner              Start the server with the FastMCP banner (hidden by default).
"""
        )
        return

    # This runs the server using the default transport (stdio)
    mcp.run(show_banner=False)


# This allows you to run the server directly with `python -m src.md_lint_mcp.main` for testing
if __name__ == "__main__":
    print("Starting MD Lint MCP Server for local testing...")
    print("Navigate to http://localhost:8000/tools/lint in your browser to test.")
    mcp.run(transport="http", host="127.0.0.1", port=8000, show_banner=False)
