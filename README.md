# 🎵 Real‑Time MIDI Notation
A modern real‑time MIDI visualization system for Yamaha keyboards and any MIDI‑compatible device.  
Provides an interactive notation renderer, colored chords, multi‑track processing, and a professional layout engine.

This project is designed as a **fast, accurate, and extensible tool** for real‑time MIDI notation in Python.

---

## 🚀 Features

- **Real‑Time MIDI Input Engine**  
  Processes incoming MIDI events with precise timestamping.

- **MIDI Channel Splitter**  
  Automatically separates MIDI data by channels (tracks) – ideal for Yamaha arranger styles.

- **Notation Rendering Engine**  
  Renders notes, barlines, playhead, rhythmic elements, and visual layers.

- **Colored Chords & Harmony**  
  Each chord has its own DAW‑style color.  
  Supports real‑time harmony detection.

- **Multi‑Track Visualization**  
  Each track has its own color, layer, and behavior.  
  Supports up to 16 MIDI channels (Yamaha standard).

- **UI Components**  
  - PianoRollUI  
  - StaffUI  
  - NoteVisualizerUI  
  - UIManager (centralized UI control)

- **Stable Release v1.0.0**  
  The first functional version of the project is available as a release.

---

## 🖼️ Screenshots / Demo (to be added)

> Add a GIF or screenshot once the first visual output is ready.  
> Google loves images – this significantly improves SEO and project visibility.

---

## 🧩 Project Architecture

### **1. MIDI Pipeline**
- MIDI Input  
- Processor  
- Channel Splitter  
- Event Router  
- Renderer  

### **2. Rendering Pipeline**
- Layout Engine (completed)  
- GraphicNotationRenderer  
- Playhead Line (completed)  
- Barlines (completed)  
- Colored Chords  
- Multi‑Track Layers  

### **3. UI Layer**
- PianoRollUI  
- StaffUI  
- NoteVisualizerUI  
- UIManager (centralized control)

### **4. Core Modules**
- MidiNoteMapper (completed)  
- Rhythm Analyzer (basic version completed)  
- StreamHandler  
- EventRouter  

---

## 📦 Installation

```bash
git clone https://github.com/richardpizem-ctrl/Real-Time-MIDI-Notation
cd Real-Time-MIDI-Notation
python run.py
```

---

## 📚 Why This Project Exists

Real‑time MIDI notation is **almost nonexistent** in the open‑source world.  
This project was created to address the need for:

- fast real‑time MIDI visualization  
- Yamaha arranger style support  
- colored harmony and chord detection  
- multi‑track processing  
- a professional DAW‑like layout  

The goal is to build a **modern, extensible, and practical tool** for musicians and developers.

---

## 🔧 Planned Features (ROADMAP)

- PDF / PNG export  
- Advanced chord detection  
- Multi‑layer harmony  
- Advanced UI panels  
- External MIDI device integration  
- Real‑time rhythmic pattern visualization  

---

## 📝 License

MIT License – free for commercial and non‑commercial use.
