import threading
from queue import Queue
from typing import Callable
import os
import glob
import fastmcp

from fastmcp import FastMCP, Context
from fastmcp.resources import Resource
from fastmcp.tools import Tool
from .linters import run_linter_on_file
from .formatters import run_formatter_on_file
from .watcher import start_watcher

class LintingServer:
    def __init__(self, watch_dir: str, enabled_formatters: list[str],
                 lint_delay: float, format_delay: float):
        self.mcp = FastMCP()
        self.watch_dir = watch_dir
        self.enabled_formatters = enabled_formatters
        self.lint_delay = lint_delay
        self.format_delay = format_delay

        self._violation_cache = {}
        self._lock = threading.Lock()
        
        self._lint_queue = Queue()
        self._format_queue = Queue()

        # Create Resource and Tool objects from the instance methods
        violations_resource = Resource.from_function(
            fn=self.get_linting_violations,
            uri="resource://linting_violations"
        )
        run_tool = Tool.from_function(fn=self.run_all_linters)

        # Register the created objects
        self.mcp.add_resource(violations_resource)
        self.mcp.add_tool(run_tool)

    def get_linting_violations(self, context: Context) -> str:
        """Returns the current set of non-fixable linting violations."""
        with self._lock:
            if not self._violation_cache:
                return ""
            return "\n\n".join(self._violation_cache.values())

    def run_all_linters(self, context: Context):
        """Manually triggers a linting and formatting run on all project files."""
        context.info("Manual linting and formatting run triggered...")
        
        all_files = glob.glob(f"{self.watch_dir}/**/*", recursive=True)
        py_files = [f for f in all_files if f.endswith('.py')]
        md_files = [f for f in all_files if f.endswith('.md')]

        for file in py_files:
            run_formatter_on_file(file, self.enabled_formatters)

        for file in py_files + md_files:
            self._process_linter_task(file)
        
        context.info("Manual run complete. Check the 'linting_violations' resource.")
        return "Manual run complete."

    def _generic_worker(self, queue: Queue, task_function: Callable):
        """A generic worker that pulls a file path from a queue and runs a task."""
        while True:
            file_path = queue.get()
            task_function(file_path)
            queue.task_done()

    def _process_linter_task(self, file_path: str):
        """The task for the linter worker."""
        violations = run_linter_on_file(file_path)
        with self._lock:
            if violations:
                if self._violation_cache.get(file_path) != violations:
                    self._violation_cache[file_path] = violations
                    print(f"Linting violations updated in {file_path}")
            elif file_path in self._violation_cache:
                del self._violation_cache[file_path]
                print(f"Linting violations cleared in {file_path}")

    def _process_formatter_task(self, file_path: str):
        """The task for the formatter worker."""
        run_formatter_on_file(file_path, self.enabled_formatters)

    def start(self, mode: str, port: int, show_banner: bool):
        """Starts the server and all background threads."""
        if mode == "auto":
            start_watcher(self.watch_dir, self._lint_queue, self._format_queue,
                          self.lint_delay, self.format_delay)

            linter_worker = threading.Thread(
                target=self._generic_worker,
                args=(self._lint_queue, self._process_linter_task),
                daemon=True
            )
            linter_worker.start()

            formatter_worker = threading.Thread(
                target=self._generic_worker,
                args=(self._format_queue, self._process_formatter_task),
                daemon=True
            )
            formatter_worker.start()
            print("Auto-linting and formatting server started...")
        
        print(f"Serving resource on http://{fastmcp.settings.host}:{port}")
        self.mcp.run(transport='http', port=port, show_banner=show_banner)
