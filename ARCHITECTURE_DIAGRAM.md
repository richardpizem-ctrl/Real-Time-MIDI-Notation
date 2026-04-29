# 🏗️ Real-Time MIDI Notation — MEGA ARCHITECTURE DIAGRAM (Ultimate Edition)

This document provides a complete, high-level overview of the entire system architecture, including  
real-time MIDI flow, module responsibilities, and communication pathways.

It is designed for developers, contributors, researchers, and anyone studying the internal structure of the engine.

---

# 🆕 A New Class of Real-Time MIDI Engine

**SIRIUS / Real-Time MIDI Notation** does not belong to any existing category of music software.

It is NOT:
- a MIDI visualizer  
- an offline notation editor  
- a DAW plugin  
- a traditional MIDI library  

It represents a **completely new class of software** that did not exist before:

## 🎼 Real-Time Multi-Track MIDI Notation Engine

This engine combines features that have never been seen together:

- fully **real-time** MIDI processing  
- **16‑track Yamaha‑compatible** multi-track architecture  
- instant graphical notation (beams, stems, barlines)  
- **velocity‑based** real-time dynamics  
- modular graphic renderer (Python + Pygame)  
- architecture optimized for **research, education, live performance, and studio work**  
- no preprocessing, no lookahead, no offline steps  

SIRIUS defines a **new category of real-time MIDI tools**, complementing traditional offline notation systems (MuseScore, LilyPond, Dorico) and enabling:

- live notation  
- real-time performance analysis  
- expressivity research  
- pre‑recording studio tools  
- visualization for music education  

---

# 🎹 1. High-Level System Overview

```
🎹 MIDI Device (Keyboard / Yamaha Arranger / Virtual MIDI)
                │
                ▼
🛰 real_time_processing/StreamHandler
                │
                ▼
🔀 midi_input/EventRouter
                │
                ▼
📡 event_bus/EventBus  ───────────────────────────────────────────────┐
                │                                                     │
                ├──────────────► 🎚 track_system/TrackSystem          │
                │                                                     │
                ├──────────────► 🧠 notation_processor/NotationProcessor
                │                                                     │
                ▼                                                     │
⏱ core/PlaybackEngine                                                 │
                │                                                     │
                ▼                                                     │
🎨 renderer/GraphicNotationRenderer                                   │
                │                                                     │
                ▼                                                     │
🖼 ui/CanvasUI                                                         │
                │                                                     │
                ▼                                                     │
🧩 ui/UIManager  ◄────────────────────────────────────────────────────┘
                │
                ▼
🪟 Pygame Window (Final Output)
```

---

# 🧩 2. Module Responsibilities

## 🎹 MIDI Input Layer

### `real_time_processing/StreamHandler`
- Detects MIDI devices  
- Reads MIDI events in real time  
- Sends raw events to EventRouter  

### `midi_input/EventRouter`
- Normalizes MIDI events  
- Routes them into EventBus  
- Handles channel/track mapping  

---

## 📡 Event Communication Layer

### `event_bus/EventBus`
- Publish/Subscribe system  
- Decouples all modules  
- Enables communication between:
  - UI  
  - Renderer  
  - NotationProcessor  
  - TrackManager  
  - PlaybackEngine  

---

## 🎚 Track System

### `track_system/TrackSystem`
- 16‑track Yamaha‑style architecture  
- Track attributes (name, color, visibility)  

### `core/TrackManager`
- Mute / Solo / Volume / Pan  
- Record arm  
- Real-time activity meter  

---

## 🧠 Notation Processing

### `notation_processor/NotationProcessor`
- Converts MIDI → internal Note objects  
- Rhythm analysis  
- Timing + velocity extraction  
- Prepares data for renderer  

---

## ⏱ Playback Engine

### `core/PlaybackEngine`
- Controls global time  
- Moves playhead  
- Applies BPM + meter  
- Selects active notes  
- Drives the render loop  

---

## 🎨 Rendering Engine

### `renderer/GraphicNotationRenderer`
- Real-time note rendering  
- Beams, stems, barlines  
- Velocity shading  
- Chord grouping  
- Grid + timeline  
- Zoom + scroll  
- Staff caching  

---

## 🖥 UI Layer

### `ui/CanvasUI`
- Main drawing surface  
- Playhead rendering  
- Scroll + zoom  

### `ui/UIManager`
- Handles user input  
- Manages UI components  
- Integrates TrackSwitcherUI  
- Communicates with EventBus  

---

# 🔄 3. Full Real-Time Pipeline (Detailed)

```
🎹 MIDI Device
      │
      ▼
🛰 StreamHandler
      │  (raw MIDI events)
      ▼
🔀 EventRouter
      │  (normalized events)
      ▼
📡 EventBus
      │
      ├────────► TrackSystem (track attributes)
      │
      ├────────► NotationProcessor (note objects)
      │
      ▼
⏱ PlaybackEngine
      │  (timing + active notes)
      ▼
🎨 GraphicNotationRenderer
      │  (visual objects)
      ▼
🖼 CanvasUI
      │
      ▼
🧩 UIManager
      │
      ▼
🪟 Pygame Window
```

---

# 🧱 4. Architectural Principles

- **Modular** — each component is isolated  
- **Extensible** — new UI, processors, or renderers can be added  
- **Real-time safe** — no blocking operations  
- **Event-driven** — EventBus ensures clean communication  
- **DAW-inspired** — TrackManager mirrors professional workflows  
- **Renderer-first** — optimized for real-time drawing  

---

# 🔮 5. Future Architecture Extensions

- Audio engine integration  
- MIDI file loader  
- Export pipeline (PNG, SVG, PDF)  
- Advanced engraving engine  
- Multi-voice notation  
- Track inspector panel  
- Toolbar (Play/Pause/Stop/Seek)  

---

# 🎉 End of Architecture Diagram
