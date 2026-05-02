# INDEX — Real-Time MIDI Notation (v2.0.0 Documentation)

Welcome to the central index of the Real-Time MIDI Notation project.  
This document provides a structured overview of the entire system, modules, architecture, and documentation set.

---

## 📌 Project Overview
Real-Time MIDI Notation is a high‑performance, real‑time music notation engine designed for:
- live MIDI input
- real‑time rendering
- timeline‑based editing
- advanced engraving (v3+)
- modular architecture with clean separation of UI, logic, and rendering

The project is built for long‑term scalability, clarity, and professional‑grade performance.

---

## 🧱 Core Architecture (v2.0.0)
The system is divided into stable, well‑defined modules:

### **CORE/**
- EventBus  
- TrackManager  
- NotationProcessor  
- PlaybackEngine  
- Timing & synchronization  
- Data models  

### **UI/**
- TimelineUI  
- PianoUI  
- CanvasUI  
- NoteVisualizerUI  
- Interaction logic  
- Zoom/scroll system  
- Marker & loop region tools  

### **renderer_new/**
- PixelLayoutEngine v2  
- Cached grid rendering  
- Graphic primitives preparation  
- High‑performance drawing pipeline  

### **runtime/**
- Real‑time event routing  
- Stream handling  
- Burst‑safe processing  

### **timeline/**
- Marker system  
- Loop regions  
- Playhead logic  
- Editing groundwork  

### **filesystem/**
- Project loading  
- Saving  
- Serialization  

### **commands/**
- Command pattern  
- Undo/redo groundwork  

---

## 🧩 Documentation Set (v2.0.0)
All documentation files follow the unified v2.0.0 standard.

- **README.md** — Project introduction  
- **INDEX.md** — Central documentation index  
- **ARCHITECTURE.md** — Full system architecture  
- **API.md** — Public API reference  
- **TESTING.md** — Testing strategy  
- **DATA_MODEL.md** — Internal data structures  
- **WORKFLOW.md** — Development workflow  
- **RELEASE_NOTES/** — Version history  
- **CONTRIBUTING.md** — Contribution guidelines (optional)  

---

## 🚀 Release History
### **v1.3.0 — TimelineUI Finalization**
- Completed TimelineUI  
- Stabilized markers, loops, playhead  
- Prepared for architecture upgrade  

### **v2.0.0 — Architecture Upgrade**
- Unified naming  
- Renderer_new  
- PixelLayoutEngine v2  
- Cached grid rendering  
- Full documentation rewrite  

### **v3.0.0 — Advanced Engraving Engine**
- Multi‑voice notation  
- Polyphony  
- Beams, articulations  
- Graphic primitives layer  
- Real‑time engraving preview  

---

## 🔮 Roadmap
### **v3.x**
- Full engraving engine  
- Advanced editing tools  
- Ripple editing  
- Magnetic markers  
- Intelligent spacing  

### **v4.x**
- Self‑repair layer  
- Health‑check system  
- Automated diagnostics  

---

## 🏁 Summary
This INDEX.md serves as the central navigation point for the entire Real-Time MIDI Notation project.  
It reflects the stable v2.0.0 documentation standard and provides a clear overview of modules, architecture, and releases.

