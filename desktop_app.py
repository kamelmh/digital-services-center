"""
DSC Desktop App — Zero-cost production path.
Run this file to start the DSC application locally.
"""
import sys
from pathlib import Path

# Ensure current directory is in path
sys.path.insert(0, str(Path(__file__).parent))

# Import the Violit app
from main import app

if __name__ == "__main__":
    print("=" * 60)
    print("  DSC — Digital Services Center")
    print("  مركز الخدمات الرقمية")
    print("=" * 60)
    print()
    print("  Starting application...")
    print("  Open http://localhost:8501 in your browser")
    print()
    print("  Press Ctrl+C to stop")
    print("=" * 60)
    
    # Run the app
    app.run()
