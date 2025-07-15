import threading
import os
from .server import server
from .watcher import start_watching

def main():
    """Entry point for the AutoLint server."""
    monitored_directory = os.getcwd()

    # Pass the server instance directly to the watcher
    watcher_thread = threading.Thread(
        target=start_watching, args=(monitored_directory, server), daemon=True
    )
    watcher_thread.start()

    # Get transport settings from environment variables set by the runner
    transport = os.environ.get("MCP_TRANSPORT", "stdio")
    
    run_kwargs = {"transport": transport}
    if transport == "http":
        run_kwargs["host"] = os.environ.get("MCP_HOST", "127.0.0.1")
        run_kwargs["port"] = int(os.environ.get("MCP_PORT", 8080))

    try:
        server.run(**run_kwargs)
    except KeyboardInterrupt:
        print("Server shutting down.")

if __name__ == "__main__":
    main()
