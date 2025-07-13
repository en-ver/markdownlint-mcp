# src/markdownlint_mcp/main.py

import asyncio
from pathlib import Path
import httpx

from fastmcp import FastMCP

mcp = FastMCP(
    name="MarkdownLint MCP",
    instructions="This is a Markdown linting MCP server. You MUST use the 'lint' tool every time you create or modify a Markdown file ('.md', '.markdown').",
)


# === PRIMARY TOOL: LINT ===
@mcp.tool
async def lint(file_path: str) -> str:
    """
    Checks Markdown files for rule violations.

    You MUST use this tool every time you edit a Markdown-formatted file to check for
    violations.

    Args:
        file_path: The absolute or relative path to the Markdown file to lint.

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

MANDATORY DIRECTIVE: You MUST address each of the violations listed above.

NOTE:
In some cases, you may determine that a rule should be ignored for a specific line. If so, you MUST first propose the change to the user and get their confirmation. If the user agrees, you should then use the 'get_inline_directives' resource to learn how to disable the rule and apply the change.
"""


# === RESOURCE: INLINE DIRECTIVES ===
@mcp.resource("config://markdownlint/inline-directives")
async def get_inline_directives() -> str:
    """
    Returns information on how to use inline comments to control
    linting rules directly within a Markdown file.

    You MUST use this tool every time you are going to add inline
    directives to a Markdown file.

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
    # This runs the server using the default transport (stdio)
    mcp.run()


# This allows you to run the server directly with `python -m src.markdownlint_mcp.main` for testing
if __name__ == "__main__":
    print("Starting MarkdownLint MCP Server for local testing...")
    mcp.run()
