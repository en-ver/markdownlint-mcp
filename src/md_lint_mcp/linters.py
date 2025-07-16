import subprocess
import os

# Linters are for checking for style violations. Fixing is handled by formatters.
LINTER_COMMANDS = {
    ".py": ["ruff", "check"],
    ".md": ["markdownlint"],
}

def run_linter_on_file(file_path: str) -> str | None:
    """
    Runs the appropriate linter on a single file.
    Returns the violation output as a string, or None if there are no issues.
    """
    _, extension = os.path.splitext(file_path)
    
    command = LINTER_COMMANDS.get(extension)
    if not command:
        return None

    # Run the check
    result = subprocess.run(command + [file_path], capture_output=True, text=True)

    # Ruff writes to stdout, markdownlint writes to stderr
    output = result.stdout if extension == ".py" else result.stderr

    if result.returncode != 0 and output:
        return output.strip()
    
    return None