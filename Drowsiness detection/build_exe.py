import os
import subprocess
import sys

def main():
    # Ensure PyInstaller is installed
    try:
        import PyInstaller
    except ImportError:
        print("PyInstaller not found. Please install it with 'pip install pyinstaller'")
        sys.exit(1)

    # Define paths
    script_path = "drowsiness detection.py"
    
    # Extra data to bundle (format: 'source:destination' for Windows, 'source:destination' for Linux/Mac)
    # PyInstaller uses --add-data "source;dest" on Windows and "source:dest" on POSIX
    separator = ';' if os.name == 'nt' else ':'
    
    data_files = [
        f"alarm.mp3{separator}.",
        f"models{separator}models",
        f"haar cascade files{separator}haar cascade files"
    ]
    
    # Build the PyInstaller command
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--windowed", # Don't open a console window
        "--name", "DrowsinessDetector"
    ]
    
    for data in data_files:
        cmd.extend(["--add-data", data])
        
    cmd.append(script_path)
    
    print(f"Running command: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)
    print("Build complete. Check the 'dist' folder for the executable.")

if __name__ == "__main__":
    main()
