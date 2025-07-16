import typer
from typing_extensions import Annotated

from .server import LintingServer


def main(
    mode: Annotated[
        str,
        typer.Option(
            help="The operational mode: 'auto' or 'manual'.",
            case_sensitive=False,
        ),
    ] = "manual",
    watch_dir: Annotated[
        str, typer.Option(help="The directory to watch for file changes.")
    ] = ".",
    linters: Annotated[
        str,
        typer.Option(
            help="Comma-separated string of linters to use (e.g., 'ruff,markdownlint')."
        ),
    ] = "",
    formatters: Annotated[
        str,
        typer.Option(
            help="Comma-separated string of formatters to use (e.g., 'ruff')."
        ),
    ] = "",  # Default to no formatters
    lint_delay: Annotated[
        float,
        typer.Option(help="Quiet period in seconds before linting."),
    ] = 0.5,
    format_delay: Annotated[
        float,
        typer.Option(help="Quiet period in seconds before formatting."),
    ] = 5.0,  # Shortened default for easier testing
):
    """
    Main entry point for the agent-multitool server.
    """
    formatter_list = [f.strip() for f in formatters.split(",") if f.strip()]

    # Instantiate the main server class
    server = LintingServer(
        watch_dir=watch_dir,
        enabled_formatters=formatter_list,
        lint_delay=lint_delay,
        format_delay=format_delay,
    )

    # Start the server and its background components
    server.start(mode=mode, port=8585, show_banner=False)


if __name__ == "__main__":
    typer.run(main)
