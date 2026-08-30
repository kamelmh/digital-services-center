"""
DSC Desktop App — Zero-cost production path.
Run this file to start the DSC application locally.
Auto-opens browser, runs on localhost.
"""
import sys
import os
import socket
import time
import webbrowser
import threading
from pathlib import Path

# Ensure current directory is in path
sys.path.insert(0, str(Path(__file__).parent))

PORT = 8000
for p in (8000, 8001, 8002):
    try:
        s = socket.socket()
        s.bind(("", p))
        s.close()
        PORT = p
        break
    except Exception:
        continue
URL = f"http://localhost:{PORT}"


def open_browser():
    """Open browser after a short delay."""
    time.sleep(2)
    webbrowser.open(URL)


def main():
    if PORT != 8000:
        print(f"Port 8000 occupied, using {PORT}")
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
