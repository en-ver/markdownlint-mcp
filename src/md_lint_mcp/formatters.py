import subprocess
import os

# Formatters are for enforcing code style
FORMATTER_COMMANDS = {
    "ruff": [["ruff", "format"]],
    "markdownlint": [["markdownlint", "--fix"]],
}

# Map file extensions to their associated formatter name
EXTENSION_TO_FORMATTER = {
    ".py": "ruff",
    ".md": "markdownlint",
}

def run_formatter_on_file(file_path: str, enabled_formatters: list[str]):
    """
    Runs the appropriate formatter on a single file if it's enabled.
    """
    _, extension = os.path.splitext(file_path)
    
    formatter_name = EXTENSION_TO_FORMATTER.get(extension)
    if formatter_name and formatter_name in enabled_formatters:
        format_commands = FORMATTER_COMMANDS.get(formatter_name)
        if format_commands:
            for command in format_commands:
                subprocess.run(command + [file_path], capture_output=True, text=True)
                print(f"Formatted {file_path} with {formatter_name}.")