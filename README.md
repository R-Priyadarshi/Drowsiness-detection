# Drowsiness-detection

This repository contains a real-time Drowsiness Detection application. It uses a webcam to monitor your eyes and sounds an alarm if it detects that you are falling asleep.

## Download and Run (No Installation Required)

You can run this application without installing Python or any dependencies!

1. Go to the [Releases](https://github.com/R-Priyadarshi/Drowsiness-detection/releases) page of this repository.
2. Download the latest `DrowsinessDetector.exe`.
3. Double-click the executable to run it. (It may take a few seconds to load the AI models on the first run).
4. Press `q` while the webcam window is active to quit the application.

## For Developers (Build Locally)

If you wish to modify the code or build the executable yourself:

1. Clone the repository:
   ```bash
   git clone https://github.com/R-Priyadarshi/Drowsiness-detection.git
   cd Drowsiness-detection/"Drowsiness detection"
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   pip install pyinstaller
   ```

3. Run the script directly:
   ```bash
   python "drowsiness detection.py"
   ```

4. Build the executable:
   ```bash
   python build_exe.py
   ```
   The generated executable will be found in the `dist` folder.
