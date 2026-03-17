![Project Banner](https://github.com/richardpizem-ctrl/Real-Time-MIDI-Notation/blob/main/SIRIUS%20PROGRAM%20S%20EM.png)

# Real-Time MIDI Score Visualizer & Accompaniment Track Notation System

This project provides real-time visualization of MIDI accompaniment tracks.  
It is designed for users of arranger keyboards (Yamaha PSR-SX, Genos, Tyros, and others) who want to display bass lines, drum patterns, chord layers, pads, and other internal MIDI tracks as readable musical notation.

---

## 🚀 Features

### ✔️ Implemented
- Real-time MIDI data capture  
- Automatic separation of accompaniment tracks by MIDI channel  
- Device detection and MIDI routing  
- Real-time event processing (low-latency stream handler)

### 🔧 In Development
- Full notation rendering for bass, drums, pads, and chord tracks  
- Layout engine for staff, spacing, and symbol placement  
- UI components for real-time score display  
- Rhythm analysis and quantization

### 🧭 Planned
- Export to MusicXML / PDF  
- Track selection and filtering  
- Advanced timing analysis  
- Support for additional MIDI devices

---

## 🧩 Project Architecture

| Module | Purpose |
|--------|---------|
| **midi_input/** | Captures MIDI data from the selected device |
| **real_time_processing/stream_handler.py** | Processes MIDI events with minimal latency |
| **notation_engine/** | Converts MIDI events into musical notation |
| **layout_engine/** | Handles staff layout and note positioning |
| **ui_components/** | Visual components for real-time score display |
| **device_manager.py** | Detects and manages MIDI devices |
| **rhythm_analyzer.py** | Performs rhythm and timing analysis |
| **run.py** | Main application entry point |

---

## 🛠️ Installation

### 1. Clone the repository
