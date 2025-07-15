import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from threading import Timer
from .linters import run_linters_for_file
from .server import server as server_instance  # To get the type hint

debounce_timers = {}
IGNORE_DIRS = [".venv", ".ruff_cache", ".git", "node_modules", "__pycache__"]


def trigger_linting(path: str, server: server_instance):
    """Debounced: Triggering linting for a given path."""
    print(f"Debounced: Triggering linting for {path}")
    run_linters_for_file(path, server)


class LintingEventHandler(FileSystemEventHandler):
    def __init__(self, server: server_instance):
        self.server = server
        super().__init__()

    def on_modified(self, event):
        if event.is_directory:
            return

        path = event.src_path
        if any(d in path for d in IGNORE_DIRS):
            return

        if path in debounce_timers:
            debounce_timers[path].cancel()

        debounce_timers[path] = Timer(1.0, lambda: trigger_linting(path, self.server))
        debounce_timers[path].start()

    def on_created(self, event):
        if not event.is_directory:
            self.on_modified(event)


def start_watching(path: str, server: server_instance):
    """
    Starts watching a directory for file changes.

    :param path: The path to the directory to watch.
    :param server: The FastMCP server instance.
    """
    event_handler = LintingEventHandler(server)
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    print(f"Watching for file changes in {path}")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
