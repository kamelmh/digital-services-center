"""
DSC Desktop App — Zero-cost production path.
Run this file to start the DSC application locally.
Auto-opens browser, runs on localhost.
"""
import sys
import os
import time
import webbrowser
import threading
from pathlib import Path

# Ensure current directory is in path
sys.path.insert(0, str(Path(__file__).parent))

PORT = 8000
URL = f"http://localhost:{PORT}"


def open_browser():
    """Open browser after a short delay."""
    time.sleep(2)
    webbrowser.open(URL)


def main():
    print("=" * 60)
    print("  DSC — Digital Services Center")
    print("  مركز الخدمات الرقمية")
    print("=" * 60)
    print()
    print("  Starting application...")
    print(f"  Open {URL} in your browser")
    print()
    print("  Press Ctrl+C to stop")
    print("=" * 60)

    # Auto-open browser in background
    browser_thread = threading.Thread(target=open_browser, daemon=True)
    browser_thread.start()

    # Import and run the Violit app
    from main import app
    app.run()


if __name__ == "__main__":
    main()
