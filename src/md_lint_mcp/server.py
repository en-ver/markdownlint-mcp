from fastmcp import FastMCP, Context

server = FastMCP(
    name="AutoLint",
    instructions="A server that automatically lints files and reports issues.",
)


@server.tool
async def report_linting_issues(
    context: Context, file_path: str, linter_name: str, output: str
):
    """
    Receives and formats linting output.

    :param context: The FastMCP context.
    :param file_path: The path to the file that was linted.
    :param linter_name: The name of the linter that was used.
    :param output: The raw output of the linter.
    """
    if output.strip():
        message = f"Linting issues found in {file_path} by {linter_name}:\n{output}"
        await context.info(message)
        return "Unresolved violations reported, please review and fix."
    else:
        message = f"No issues found in {file_path} by {linter_name}."
        await context.info(message)
        return "No issues found."
