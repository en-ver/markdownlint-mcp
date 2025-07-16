import threading
from watchdog.observers.polling import PollingObserver as Observer
from watchdog.events import FileSystemEventHandler
from queue import Queue

WATCHED_EXTENSIONS = ('.py', '.md')

class DualCallbackEventHandler(FileSystemEventHandler):
    """
    An event handler that manages two separate debounced callbacks: one for
    immediate linting and one for delayed formatting.
    """
    def __init__(self, lint_queue: Queue, format_queue: Queue,
                 lint_delay: float, format_delay: float):
        super().__init__()
        self.lint_queue = lint_queue
        self.format_queue = format_queue
        self.lint_delay = lint_delay
        self.format_delay = format_delay
        self.lint_timer: threading.Timer | None = None
        self.format_timer: threading.Timer | None = None

    def dispatch(self, event):
        """
        Dispatches events, filtering for relevant file changes and starting
        both lint and format timers.
        """
        if (not event.is_directory and
            event.event_type == 'modified' and
            event.src_path.endswith(WATCHED_EXTENSIONS)):
            
            if '/.' in event.src_path or '/node_modules/' in event.src_path:
                 return

            # Cancel previous timers
            if self.lint_timer:
                self.lint_timer.cancel()
            if self.format_timer:
                self.format_timer.cancel()
            
            # Start new timers for both callbacks
            self.lint_timer = threading.Timer(self.lint_delay, self.lint_queue.put, args=[event.src_path])
            self.format_timer = threading.Timer(self.format_delay, self.format_queue.put, args=[event.src_path])
            
            self.lint_timer.start()
            self.format_timer.start()

def start_watcher(directory: str, lint_queue: Queue, format_queue: Queue,
                  lint_delay: float, format_delay: float):
    """
    Initializes and starts a reliable, polling file system watcher with
    dual callbacks.
    """
    event_handler = DualCallbackEventHandler(lint_queue, format_queue, lint_delay, format_delay)
    observer = Observer()
    observer.schedule(event_handler, directory, recursive=True)
    observer.daemon = True
    observer.start()
    return observer