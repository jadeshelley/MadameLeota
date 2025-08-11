#!/usr/bin/env python3
"""
Setup script for Madame Leota AI Fortune Teller
"""

import os
import sys
import subprocess
import platform

def install_requirements():
    """Install Python dependencies"""
    print("Installing Python dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✓ Dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to install dependencies: {e}")
        return False
    return True

def create_directories():
    """Create necessary directories"""
    print("Creating project directories...")
    directories = ["ai", "audio", "video", "assets", "logs"]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✓ Created {directory}/ directory")
    
    # Create __init__.py files
    for directory in ["ai", "audio", "video"]:
        init_file = os.path.join(directory, "__init__.py")
        if not os.path.exists(init_file):
            with open(init_file, "w") as f:
                f.write("# Package initialization\n")
            print(f"✓ Created {init_file}")

def setup_pi_config():
    """Configure Raspberry Pi specific settings"""
    if platform.system() == "Linux":
        print("Detected Linux - configuring for Raspberry Pi...")
        try:
            # Configure HDMI output
            subprocess.run(["sudo", "raspi-config", "nonint", "do_hdmi_force_hotplug", "1"], 
                         capture_output=True)
            subprocess.run(["sudo", "raspi-config", "nonint", "do_gpu_mem", "128"], 
                         capture_output=True)
            print("✓ Raspberry Pi configuration applied")
        except Exception as e:
            print(f"⚠ Raspberry Pi configuration failed: {e}")
    else:
        print("Not on Linux - skipping Pi-specific configuration")

def main():
    print("Setting up Madame Leota AI Fortune Teller...")
    print("=" * 50)
    
    if not install_requirements():
        print("Setup failed. Please check the error messages above.")
        return False
    
    create_directories()
    setup_pi_config()
    
    print("\n" + "=" * 50)
    print("✓ Setup completed successfully!")
    print("\nNext steps:")
    print("1. Place your fortune teller video file in the assets/ directory")
    print("2. Run: python main.py")
    
    return True

if __name__ == "__main__":
    main()
