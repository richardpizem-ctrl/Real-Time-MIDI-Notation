# 🏗️ Real‑Time MIDI Notation — ARCHITECTURE DIAGRAM (v4.2.0)

This document provides a complete, high‑level overview of the system architecture for  
**SIRIUS / Real‑Time MIDI Notation v4.2.0**, including real‑time MIDI flow, module responsibilities,  
communication pathways, and the newly added **Editing Layer (v4.2.0)**.

It is designed for developers, contributors, researchers, and engineers studying the internal structure  
of the engine.

---

# 🆕 A New Class of Real‑Time MIDI Engine

**SIRIUS** does not belong to any existing category of music software.

It is NOT:
- a MIDI visualizer  
- an offline notation editor  
- a DAW plugin  
- a traditional MIDI library  

It represents a **new class of software**:

## 🎼 Real‑Time Multi‑Track MIDI Notation Engine

This engine combines features that have never been seen together:

- fully **real‑time** MIDI processing  
- **16‑track Yamaha‑compatible** multi‑track architecture  
- instant graphical notation (beams, stems, barlines)  
- velocity‑based real‑time dynamics  
- modular graphic renderer (Python + Pygame)  
- architecture optimized for **research, education, live performance, and studio work**  
- no preprocessing, no lookahead, no offline steps  

SIRIUS defines a **new category of real‑time MIDI tools**, complementing traditional offline notation systems.

---

# 🎹 1. High‑Level System Overview (v4.2.0)

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
📡 core/EventBus v4 ───────────────────────────────────────────────────────────────────────────────┐
                │                                                                                  │
                ├──────────────► 🎚 track_system/TrackSystem                                       │
                │                                                                                  │
                ├──────────────► 🧠 notation_processor/NotationProcessor                            │
                │                                                                                  │
                ├──────────────► ✏️ editing/Editing Layer (v4.2.0)                                  │
                │                                                                                  │
                ▼                                                                                  │
⏱ core/PlaybackEngine v4                                                                           │
                │                                                                                  │
                ▼                                                                                  │
🎨 renderer_new/GraphicNotationRenderer v4                                                          │
                │                                                                                  │
                ▼                                                                                  │
🖼 ui/CanvasUI                                                                                       │
                │                                                                                  │
                ▼                                                                                  │
🧩 ui/UIManager v4 ◄────────────────────────────────────────────────────────────────────────────────┘
                │
                ▼
🪟 Pygame Window (Final Output)
```

---

# 🧩 2. Module Responsibilities (v4.2.0)

## 🎹 MIDI Input Layer

### `real_time_processing/StreamHandler`
- Detects MIDI devices  
- Reads MIDI events in real time  
- Sends raw events to EventRouter  
- Burst‑safe processing  

### `midi_input/EventRouter`
- Normalizes MIDI events  
- Routes them into EventBus v4  
- Handles channel/track mapping  
- Prevents malformed event propagation  

---

## 📡 Event Communication Layer

### `core/EventBus v4`
- Thread‑safe publish/subscribe system  
- Zero‑exception routing  
- Decouples all modules  
- Enables communication between:
  - UI  
  - Renderer  
  - NotationProcessor  
  - TrackManager  
  - PlaybackEngine  
  - **Editing Layer (v4.2.0)**  

---

## 🎚 Track System

### `track_system/TrackSystem`
- 16‑track Yamaha‑style architecture  
- Track attributes (name, color, visibility)  

### `core/TrackManager v4`
- Mute / Solo / Volume / Pan  
- Record arm  
- Real‑time activity meter  
- Safe track switching  

---

## 🧠 Notation Processing

### `notation_processor/NotationProcessor`
- Converts MIDI → internal Note objects  
- Rhythm analysis  
- Timing + velocity extraction  
- Prepares data for renderer  
- Integrated RhythmAnalyzer v4  

---

## ✏️ Editing Layer (v4.2.0)

### `editing/selection.py`
- SelectionSet  
- SelectionItem  
- Multi‑selection  
- Selection events  

### `editing/regions.py`
- RegionManager  
- Region creation  
- Region splitting  
- Region events  

### `editing/snapping.py`
- SnapGrid  
- snap_time  
- snap_range  
- Pitch/time snapping  

### `editing/ghosts.py`
- GhostNote  
- GhostRegion  
- HoverState  
- GhostController  

### `editing/events.py`
- SelectionChangedEvent  
- RegionCreatedEvent  
- RegionSplitEvent  
- GhostNotePreviewEvent  
- GhostRegionPreviewEvent  

---

## ⏱ Playback Engine

### `core/PlaybackEngine v4`
- Controls global time  
- Moves playhead  
- Applies BPM + meter  
- Selects active notes  
- Drives the render loop  
- Predictive timing‑safe updates  

---

## 🎨 Rendering Engine

### `renderer_new/GraphicNotationRenderer v4`
- Real‑time note rendering  
- Beams, stems, barlines  
- Velocity shading  
- Chord grouping  
- Grid + timeline  
- Zoom + scroll  
- Staff caching  
- PixelLayoutEngine v4 integration  

---

## 🖥 UI Layer

### `ui/CanvasUI`
- Main drawing surface  
- Playhead rendering  
- Scroll + zoom  

### `ui/UIManager v4`
- Handles user input  
- Manages UI components  
- Integrates TrackSwitcherUI  
- Communicates with EventBus v4  
- Central UI orchestrator  

---

# 🔄 3. Full Real‑Time Pipeline (Detailed v4.2.0)

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
📡 EventBus v4
      │
      ├────────► TrackSystem (track attributes)
      │
      ├────────► NotationProcessor (note objects)
      │
      ├────────► Editing Layer (selection, regions, snapping, ghosts)
      │
      ▼
⏱ PlaybackEngine v4
      │  (timing + active notes)
      ▼
🎨 GraphicNotationRenderer v4
      │  (visual objects)
      ▼
🖼 CanvasUI
      │
      ▼
🧩 UIManager v4
      │
      ▼
🪟 Pygame Window
```

---

# 🧱 4. Architectural Principles (v4.2.0)

- **Modular** — each component is isolated  
- **Extensible** — new UI, processors, or renderers can be added  
- **Real‑time safe** — no blocking operations  
- **Event‑driven** — EventBus v4 ensures clean communication  
- **DAW‑inspired** — TrackManager mirrors professional workflows  
- **Renderer‑first** — optimized for real‑time drawing  
- **Predictable timing** — PlaybackEngine v4 ensures stable frame pacing  
- **Safe device handling** — DeviceManager v4 prevents port‑locking issues  
- **Editing‑ready** — v4.2.0 introduces a complete editing foundation  

---

# 🔮 5. Future Architecture Extensions (v5+)

- Full engraving engine  
- Multi‑voice notation  
- Polyphony  
- Articulations, slurs, ties  
- Collision avoidance  
- Spacing engine  
- MusicXML export  
- Predictive layout (AI‑assisted)  
- Advanced performance analytics  
- Editing API v1 (v4.3.0)  
- Undo/Redo v2  
- Quantization engine  

---

# 🎉 End of Architecture Diagram (v4.2.0)
