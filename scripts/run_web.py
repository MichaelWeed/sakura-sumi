#!/usr/bin/env python3
"""Run the web portal for OCR compression."""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.web.app import create_app

def main():
    """Main entry point for web portal."""
    app = create_app()
    port = 5001  # Use 5001 to avoid conflict with macOS AirPlay
    print("Starting 🌸 Sakura Sumi - OCR Compression Portal...")
    print(f"Open http://localhost:{port} in your browser")
    app.run(debug=True, host='0.0.0.0', port=port)

if __name__ == '__main__':
    main()

