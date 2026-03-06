#!/usr/bin/env python
"""
AIM v3 Setup Script
Initializes the AIM development environment
"""

import os
import sys
from pathlib import Path
import subprocess


def run_command(cmd, description):
    """Run a shell command with error handling."""
    print(f"\n{'='*60}")
    print(f"📦 {description}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(cmd, shell=True, check=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed")
        return False


def setup_environment():
    """Set up the development environment."""
    
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║           🎯 AIM v3 - Open AI Model Ecosystem 🎯            ║
    ║                    Development Setup                         ║
    ╚══════════════════════════════════════════════════════════════╝
    """)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required")
        sys.exit(1)
    
    print(f"✅ Python {sys.version}")
    
    # Install dependencies
    if not run_command(
        f"{sys.executable} -m pip install -r requirements.txt",
        "Installing dependencies"
    ):
        return False
    
    # Install CLI tool in development mode
    if not run_command(
        f"{sys.executable} -m pip install -e aim_cli/",
        "Installing AIM CLI"
    ):
        return False
    
    # Create necessary directories
    print(f"\n{'='*60}")
    print("📁 Creating directories")
    print(f"{'='*60}")
    
    dirs_to_create = [
        'models',
        'backend/uploads',
        'docs',
        'tests'
    ]
    
    for dir_name in dirs_to_create:
        dir_path = Path(dir_name)
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"✅ Created {dir_name}/")
    
    print(f"\n{'='*60}")
    print("🎉 Setup Complete!")
    print(f"{'='*60}")
    print("""
    Next steps:
    
    1. Start the Flask server:
       cd backend
       python app.py
    
    2. Visit the web interface:
       http://localhost:5000
    
    3. Train your first model via CLI:
       aim train examples/sample_text.txt --name "My First Model"
    
    4. Read documentation:
       - AIM_V3_GUIDE.md (Overview)
       - docs/AIM_FORMAT.md (File format)
       - docs/API_REFERENCE.md (API guide)
       - docs/PLUGIN_GUIDE.md (Create plugins)
    
    5. Try example notebooks:
       aim_notebooks/quickstart.ipynb
    """)


if __name__ == '__main__':
    setup_environment()
