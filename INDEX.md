# INDEX — Real-Time MIDI Notation (v4.2.0 Documentation)

Welcome to the central index of the **Real-Time MIDI Notation (SIRIUS Engine)** project.  
This document provides a structured overview of the entire system, modules, architecture, and documentation set for **version 4.2.0**.

---

## 📌 Project Overview

Real-Time MIDI Notation is a high‑performance, real‑time music notation engine designed for:

- live MIDI input  
- real‑time rendering  
- timeline‑based editing  
- modular UI + renderer separation  
- Yamaha‑style 16‑track workflows  
- Editing Layer (v4.2.0)  
- future engraving engine (v5+)  

The project is built for long‑term scalability, clarity, and professional‑grade performance.

---

## 🧱 Core Architecture (v4.2.0)

The system is divided into stable, well‑defined modules:

### **CORE/**
- EventBus v4 (thread‑safe, no‑exception routing)  
- TrackManager v4  
- NotationProcessor v4  
- PlaybackEngine v4  
- Timing & synchronization  
- Data models  
- Logger v4  
- **Editing Layer v4.2.0**  
  - SelectionSet v2  
  - RegionManager  
  - SnapGrid v2  
  - GhostController  
  - Editing events  

### **UI/**
- UIManager v4  
- TimelineUI  
- CanvasUI  
- TrackSwitcherUI  
- Interaction logic  
- Zoom/scroll system  
- Marker & loop region tools  

### **renderer_new/**
- PixelLayoutEngine v4  
- Cached grid rendering  
- Graphic primitives preparation  
- High‑performance drawing pipeline  
- Ready for v5 engraving engine  

### **midi_input/**
- DeviceManager v4  
- EventRouter  
- MIDI port detection  
- Safe port handling (Windows/ASIO protection)  

### **real_time_processing/**
- StreamHandler  
- Real‑time event routing  
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
- Ready for v5 export engine  

### **commands/**
- Command pattern  
- Undo/redo groundwork  
- Editing API preparation (v4.3.0)  

---

## 🧩 Documentation Set (v4.2.0)

All documentation files follow the unified v4.2.0 standard.

- **README.md** — Project introduction  
- **INDEX.md** — Central documentation index  
- **ARCHITECTURE_DIAGRAM.md** — Full system architecture  
- **MODULE_MAP.md** — Module responsibilities  
- **PROJECT_OVERVIEW.md** — High‑level system description  
- **INSTALLATION.md** — Installation guide  
- **SUPPORT.md** — Support & help  
- **SECURITY.md** — Security policy  
- **MIDI_NAMING_CONVENTIONS.md** — Naming rules  
- **ROADMAP.md** — Development roadmap  
- **RELEASE_NOTES/** — Version history  
- **CONTRIBUTING.md** — Contribution guidelines  
- **FAQ.md** — Frequently asked questions  
- **CITATION.cff** — Academic citation metadata  

---

## 🚀 Release History

### **v4.2.0 — Editing Layer Foundation**
- New Editing Layer (selection, regions, snapping, ghosts)  
- Editing events  
- AppController updated  
- Tests added  
- Architecture prepared for Editing API v4.3.0  

### **v4.0.0 — Professional Architecture**
- EventBus v4  
- DeviceManager v4  
- UIManager v4  
- PixelLayoutEngine v4  
- Real‑time safety improvements  
- Documentation v4 standard  
- Full system stabilization  

### **v3.0.0 — Advanced Engraving Groundwork**
- Multi‑voice preparation  
- Polyphony groundwork  
- Beam/articulation preparation  
- Graphic primitives layer  

### **v2.0.0 — Architecture Upgrade**
- Unified naming  
- Renderer_new  
- PixelLayoutEngine v2  
- Cached grid rendering  
- Full documentation rewrite  

### **v1.3.0 — TimelineUI Finalization**
- Completed TimelineUI  
- Stabilized markers, loops, playhead  
- Prepared for architecture upgrade  

---

## 🔮 Roadmap

### **v4.3.0 — Editing API v1**
- High‑level editing operations  
- Undo/Redo v2  
- Batch editing  
- Quantization hooks  

### **v5.x — Engraving Engine**
- Full engraving engine  
- Slurs, ties, articulations  
- Collision avoidance  
- Spacing algorithms  
- MusicXML export  
- Predictive layout (AI-assisted)  

---

## 🏁 Summary

This **INDEX.md** serves as the central navigation point for the entire Real-Time MIDI Notation project.  
It reflects the stable **v4.2.0 documentation standard** and provides a clear overview of modules, architecture, and releases.
