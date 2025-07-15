import subprocess
import os
from fastmcp import Client
import asyncio
from .server import server as server_instance

LINTER_COMMANDS = {
    ".py": [
        "ruff format {file_path}",
        "ruff check --output-format=text --exit-zero {file_path}",
    ],
    ".md": ["markdownlint --fix {file_path}"],
}


async def call_autolint_tool(
    server: server_instance, file_path: str, linter_name: str, output: str
):
    """Programmatically calls the report_linting_issues tool using an in-memory client."""
    # The client connects directly to the server object, avoiding network issues.
    async with Client(server) as client:
        await client.call_tool(
            "report_linting_issues",  # No server prefix needed for in-memory client
            {
                "file_path": file_path,
                "linter_name": linter_name,
                "output": output,
            },
        )


def run_linters_for_file(file_path: str, server: server_instance):
    """
    Runs the appropriate linters for a given file.

    :param file_path: The path to the file to lint.
    :param server: The FastMCP server instance.
    """
    extension = os.path.splitext(file_path)[1]
    commands = LINTER_COMMANDS.get(extension)
    linter_name = ""
    if extension == ".py":
        linter_name = "Python linter (Ruff)"
    elif extension == ".md":
        linter_name = "Markdown linter (markdownlint)"

    if not commands:
        return

    output = ""
    for command_template in commands:
        command = command_template.format(file_path=file_path)
        try:
            result = subprocess.run(
                command.split(), capture_output=True, text=True, check=False
            )
            output = result.stdout + result.stderr
        except FileNotFoundError:
            output = f"Error: Linter command not found for '{command_template}'"
            break

    if linter_name:
        # Run the async function in a new event loop
        asyncio.run(call_autolint_tool(server, file_path, linter_name, output))
