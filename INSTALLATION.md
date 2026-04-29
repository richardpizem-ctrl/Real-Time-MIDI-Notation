# 🛠️ Real-Time MIDI Notation — MEGA INSTALLATION GUIDE (Ultimate Edition, v1.3.0)

This guide explains how to install, configure, and run **Real-Time MIDI Notation (SIRIUS Engine)** on any supported system.  
It is designed for beginners, developers, testers, and musicians.

---

# 📦 1. Requirements

## ✔ Operating Systems
- Windows 10 / 11  
- macOS (Intel & Apple Silicon)  
- Linux (Ubuntu, Arch, Fedora)

## ✔ Python Version
- Python **3.10+** recommended  
(Older versions may work but are not officially supported.)

## ✔ Dependencies (installed automatically)
- pygame  
- mido  
- python-rtmidi  
- numpy  

---

# 📥 2. Installation

## 🔹 Step 1 — Clone the repository
```
git clone https://github.com/richardpizem-ctrl/Real-Time-MIDI-Notation
cd Real-Time-MIDI-Notation
```

## 🔹 Step 2 — Create a virtual environment
```
python -m venv venv
```

### Activate it:
Windows:
```
venv\Scripts\activate
```

macOS/Linux:
```
source venv/bin/activate
```

## 🔹 Step 3 — Install dependencies
```
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

---

# ▶️ 4. Running the Application

Start the program with:

```
python run.py
```

This will:

- initialize all modules  
- open the pygame window  
- start the real-time renderer  
- begin listening for MIDI input  

---

# 🧪 5. Testing Your Setup

Play notes on your MIDI device.  
You should see:

- real-time note rendering  
- velocity shading  
- track colors  
- playhead movement  
- barlines and grid  

If nothing appears:

- check MIDI device connection  
- verify Python version  
- check console logs  
- ensure no DAW is blocking the MIDI port  

---

# 🛠️ 6. Troubleshooting

### ❌ No MIDI device detected
- close DAWs  
- restart the app  
- reconnect the device  
- check OS permissions  

### ❌ Renderer is slow
- close GPU-heavy apps  
- update graphics drivers  
- reduce window size  
- disable background processes  

### ❌ Wrong track colors
- verify TrackManager configuration  
- check channel → track mapping  

---

# 🎉 Installation Complete

You are now ready to use **Real-Time MIDI Notation (SIRIUS Engine)**.  
For more help, see **FAQ.md** or **SUPPORT.md**.
