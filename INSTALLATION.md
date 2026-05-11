# 🛠️ Real‑Time MIDI Notation — Installation Guide (v4.0.0)

This guide explains how to install, configure, and run  
**Real‑Time MIDI Notation (SIRIUS Engine)** on any supported system.

It is designed for beginners, developers, testers, and musicians.

---

# 📦 1. Requirements

## ✔ Operating Systems
- Windows 10 / 11  
- macOS (Intel & Apple Silicon)  
- Linux (Ubuntu, Arch, Fedora)

## ✔ Python Version
- Python **3.10+** required  
(v4.0.0 is fully tested on Python 3.10–3.12)

## ✔ Dependencies (installed automatically)
- pygame  
- mido  
- python‑rtmidi  

All dependencies are installed via `requirements.txt`.

---

# 📥 2. Installation

## 🔹 Step 1 — Clone the repository
```bash
git clone https://github.com/richardpizem-ctrl/Real-Time-MIDI-Notation
cd Real-Time-MIDI-Notation
```

## 🔹 Step 2 — Create a virtual environment
```bash
python -m venv venv
```

### Activate it:
Windows:
```bash
venv\Scripts\activate
```

macOS/Linux:
```bash
source venv/bin/activate
```

## 🔹 Step 3 — Install dependencies
```bash
pip install -r requirements.txt
```

---

# 🎹 3. MIDI Device Setup

The engine automatically detects:

- USB MIDI keyboards  
- Yamaha arranger keyboards  
- virtual MIDI ports (LoopMIDI, IAC Driver, etc.)

If your device is not detected:

- close all DAWs (they may lock the MIDI port)  
- reconnect the device  
- restart the application  
- check OS MIDI permissions  
- ensure no other app is using the MIDI port  

The **DeviceManager v4** includes protection against Windows/ASIO locked‑port issues.

---

# ▶️ 4. Running the Application

Start the program with:

```bash
python main.py
```

This will:

- initialize all **v4.0.0 modules**  
- open the Pygame window  
- start the real‑time renderer  
- begin listening for MIDI input  
- activate UIManager v4 + CanvasUI  
- start the PlaybackEngine v4 timing loop  

---

# 🧪 5. Testing Your Setup

Play notes on your MIDI device.  
You should see:

- real‑time note rendering  
- velocity shading  
- track colors  
- playhead movement  
- barlines and grid  
- stable v4 renderer performance  

If nothing appears:

- check MIDI device connection  
- verify Python version  
- check console logs  
- ensure no DAW is blocking the MIDI port  
- restart the application  

---

# 🛠️ 6. Troubleshooting

### ❌ No MIDI device detected
- close DAWs  
- restart the app  
- reconnect the device  
- check OS permissions  
- verify DeviceManager v4 logs  

### ❌ Renderer is slow
- close GPU‑heavy apps  
- update graphics drivers  
- reduce window size  
- disable background processes  
- ensure hardware acceleration is enabled  

### ❌ Wrong track colors
- verify TrackManager configuration  
- check channel → track mapping  
- ensure no custom mapping overrides are active  

---

# 🎉 Installation Complete

You are now ready to use **Real‑Time MIDI Notation (SIRIUS Engine) v4.0.0**.  
For more help, see:

- **FAQ.md**  
- **SUPPORT.md**  
- **PROJECT_OVERVIEW.md**  
- **MODULE_MAP.md**  

Enjoy real‑time notation!
