<p align="center">
  <img src="Drowsiness detection/static/logo.jpg" alt="AURA Logo" width="280">
</p>

<h1 align="center">AURA — Cognitive Telemetry System</h1>

<p align="center">
  <b>Real-Time AI-Powered Drowsiness & Fatigue Detection for Drivers</b><br>
  <i>Preventing micro-sleeps before they happen.</i>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.9+-blue?logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/TensorFlow-Keras_CNN-FF6F00?logo=tensorflow&logoColor=white" alt="TensorFlow">
  <img src="https://img.shields.io/badge/OpenCV-Haar_Cascades-5C3EE8?logo=opencv&logoColor=white" alt="OpenCV">
  <img src="https://img.shields.io/badge/MediaPipe-Face_Mesh-00A98F?logo=google&logoColor=white" alt="MediaPipe">
  <img src="https://img.shields.io/badge/Flask-Web_Dashboard-000?logo=flask&logoColor=white" alt="Flask">
  <img src="https://img.shields.io/badge/License-MIT-green" alt="License">
</p>

---

## 🧠 What is AURA?

**AURA** (Autonomous User Recognition & Alerting) is a production-grade, real-time drowsiness detection system that monitors a driver's face through a webcam and triggers escalating alarms the moment it detects the onset of sleep. It runs 100% offline with zero cloud dependency — your camera feed never leaves your machine.

Unlike simple blink detectors, AURA is a **full cognitive telemetry platform** that simultaneously tracks:

| Capability | How It Works |
|---|---|
| 👁️ **Eye Closure Detection** | Keras CNN (cnnCat2.h5) classifies each eye as Open/Closed with per-eye probability |
| 🥱 **Yawn Detection** | Adaptive Mouth Aspect Ratio (MAR) calibrated to your baseline facial geometry |
| 😤 **Stress / Anger Detection** | Brow-furrow distance tracking against your personal baseline |
| 🔄 **Distraction Detection** | MediaPipe head-pose estimation detects when you look away from the road |
| ❤️ **Heart Rate Estimation** | Remote Photoplethysmography (rPPG) extracts BPM from subtle skin color changes |
| 🚨 **Smart Cabin IoT** | Webhook integration to trigger car windows, AC, lights via IoT devices |
| 🤖 **AI Vision Mode** | Debug overlay showing exactly what the neural network sees in real-time |
| 📊 **Live Dashboard** | Sci-fi themed real-time telemetry with charts, drag-and-drop cards, 3 themes |

### Key Design Principles

- **Failproof** — The video stream and AI engine never crash. Every exception is caught and recovered from automatically.
- **Privacy-First** — 100% local processing. No data leaves your machine. No internet required.
- **Dual-Engine Redundancy** — Haar Cascades (primary) + MediaPipe EAR (fallback) ensure detection works even with glasses.
- **Zero Configuration** — Just run the executable. No Python, no drivers, no setup.


---

## 🚀 Download & Run (No Installation Required)

AURA ships as a **single portable executable**. No Python, no pip, no dependencies — just download and double-click.

---

### 🪟 Windows

<table>
<tr><td>

**Step 1.** Go to the **[Releases](https://github.com/R-Priyadarshi/Drowsiness-detection/releases)** page.

**Step 2.** Download **`DrowsinessDetector.exe`** from the latest release.

**Step 3.** Double-click the file to launch it.

> ⚠️ **Windows SmartScreen Warning:** Since this is not a signed commercial app, Windows may show a SmartScreen popup. Click **"More info"** → **"Run anyway"**. This is normal for unsigned open-source software.

**Step 4.** Your default browser will automatically open to `http://127.0.0.1:5000` with the AURA dashboard.

**Step 5.** Click **"Initialize System"** on the landing page to start monitoring.

**Step 6.** To stop: Click the 🛑 button in the toolbar → View your Trip Report → Click **"Return to Home"**.

</td></tr>
</table>

---

### 🐧 Ubuntu / Linux

<table>
<tr><td>

**Step 1.** Go to the **[Releases](https://github.com/R-Priyadarshi/Drowsiness-detection/releases)** page.

**Step 2.** Download **`DrowsinessDetector`** (the Linux binary, no extension) from the latest release.

**Step 3.** Open a terminal and navigate to the download location:

```bash
cd ~/Downloads
```

**Step 4.** Make the file executable:

```bash
chmod +x DrowsinessDetector
```

**Step 5.** Run it:

```bash
./DrowsinessDetector
```

> 💡 **If the browser doesn't open automatically**, open it manually and go to: `http://127.0.0.1:5000`

> ⚠️ **Camera permissions:** If the camera doesn't work, ensure your user has access to the video device:
> ```bash
> sudo usermod -aG video $USER
> ```
> Then **log out and log back in** for the change to take effect.

> ⚠️ **Audio dependencies:** If you don't hear alarm sounds, install the audio libraries:
> ```bash
> sudo apt install -y libasound2-dev libsdl2-mixer-2.0-0 pulseaudio
> ```

**Step 6.** Click **"Initialize System"** on the landing page to start monitoring.

**Step 7.** To stop: Click the 🛑 button in the toolbar → View your Trip Report → Click **"Return to Home"**.

**Step 8.** To terminate the background process, press `Ctrl+C` in the terminal.

</td></tr>
</table>

---

## 🛠️ For Developers (Build From Source)

If you want to modify the code, add features, or build the executable yourself:

### Prerequisites

- Python 3.9 – 3.11 (3.12+ may have TensorFlow/MediaPipe compatibility issues)
- A working webcam
- pip (Python package manager)

### 1. Clone the Repository

```bash
git clone https://github.com/R-Priyadarshi/Drowsiness-detection.git
cd "Drowsiness-detection/Drowsiness detection"
```

### 2. Create a Virtual Environment (Recommended)

```bash
# Linux / macOS
python3 -m venv venv
source venv/bin/activate

# Windows (PowerShell)
python -m venv venv
.\venv\Scripts\Activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the Application

```bash
python "drowsiness detection.py"
```

The app will automatically find a free port (default: 5000) and open your browser.

### 5. Build the Standalone Executable

```bash
pip install pyinstaller
python build_exe.py
```

The generated executable will appear in the `dist/` folder. It bundles all models, cascades, templates, static files, and audio — everything needed to run standalone.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     AURA System                         │
├─────────────┬───────────────┬───────────────────────────┤
│  Camera     │  AI Engine    │  Web Dashboard (Flask)    │
│  (OpenCV)   │               │                           │
│             │  ┌──────────┐ │  ┌───────────────────┐    │
│  Webcam ──► │  │Haar Casc.│ │  │ MJPEG Video Stream│    │
│  Frame      │  │(Primary) │ │  │ /video_feed       │    │
│  Capture    │  └────┬─────┘ │  └───────────────────┘    │
│             │       │       │  ┌───────────────────┐    │
│             │  ┌────▼─────┐ │  │ JSON Status API   │    │
│             │  │Keras CNN │ │  │ /status (150ms)   │    │
│             │  │cnnCat2.h5│ │  └───────────────────┘    │
│             │  └──────────┘ │  ┌───────────────────┐    │
│             │  ┌──────────┐ │  │ Chart.js + Themes │    │
│             │  │MediaPipe │ │  │ Drag & Drop Cards │    │
│             │  │(Fallback)│ │  │ Zoom / Pan / Snap │    │
│             │  └──────────┘ │  └───────────────────┘    │
├─────────────┴───────────────┴───────────────────────────┤
│  Audio Engine (pygame)  │  IoT Webhook (requests)       │
│  alarm.mp3 / yawn.wav   │  Configurable endpoint        │
└─────────────────────────┴───────────────────────────────┘
```

---

## 📂 Project Structure

```
Drowsiness-detection/
├── README.md
└── Drowsiness detection/
    ├── drowsiness detection.py    # Main application (Flask + AI engine)
    ├── build_exe.py               # PyInstaller build script
    ├── requirements.txt           # Python dependencies
    ├── alarm.mp3                  # Drowsiness alarm sound
    ├── distracted.wav             # Distraction alert sound
    ├── yawn.wav                   # Yawn alert sound
    ├── models/
    │   └── cnnCat2.h5             # Trained Keras CNN model (eye open/closed)
    ├── haar cascade files/
    │   ├── haarcascade_frontalface_alt.xml
    │   ├── haarcascade_lefteye_2splits.xml
    │   └── haarcascade_righteye_2splits.xml
    ├── templates/
    │   └── index.html             # Full dashboard UI (single-page app)
    └── static/
        ├── logo.jpg               # AURA logo
        └── chart.js               # Chart.js library
```

---

## 🎮 Dashboard Controls

| Button | Function |
|---|---|
| 🤖 **AI Vision Mode** | Toggle debug overlay — see eye landmarks, bounding boxes, EAR values, and what the CNN sees |
| ➕ **Zoom In** | Zoom into the video feed (up to 5x) |
| ➖ **Zoom Out** | Zoom out (minimum 1x) |
| 🔄 **Reset Zoom** | Reset to default 1x zoom and center position |
| 💾 **Save Snapshot** | Download a JPEG snapshot of the current video frame |
| ⚙️ **Settings** | Configure IoT webhook URL and dashboard theme |
| 🛑 **End Drive** | Stop monitoring and view your Trip Report summary |

---

## 🔧 Tech Stack

| Component | Technology |
|---|---|
| **AI Model** | Keras Sequential CNN (24×24 grayscale input, softmax output) |
| **Face Detection** | OpenCV Haar Cascade Classifiers |
| **Face Mesh** | Google MediaPipe (468 landmarks, refined) |
| **Backend** | Flask (Python) |
| **Frontend** | Vanilla HTML/CSS/JS + Chart.js |
| **Audio** | pygame.mixer |
| **Heart Rate** | FFT-based rPPG (remote photoplethysmography) |
| **Packaging** | PyInstaller (single-file executable) |

---

## 📜 License

This project is open-source and available under the [MIT License](LICENSE).

---

<p align="center">
  <b>Built with ❤️ by R. Priyadarshi</b><br>
  <i>Saving lives, one blink at a time.</i>
</p>
