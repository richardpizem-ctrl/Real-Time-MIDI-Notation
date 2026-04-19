# 🏗️ Real-Time MIDI Notation — MEGA ARCHITECTURE DIAGRAM (Ultimate Edition)

This document provides a complete, high‑level overview of the entire system architecture, including  
real‑time MIDI flow, module responsibilities, and communication pathways.

It is designed for developers, contributors, researchers, and anyone studying the internal structure of the engine.

---

# 🆕 A New Class of Real‑Time MIDI Engine

**SIRIUS / Real‑Time MIDI Notation** nepatrí do žiadnej existujúcej kategórie softvéru.  
Nie je to MIDI vizualizér, nie je to offline notátor, nie je to DAW plugin a nie je to tradičná MIDI knižnica.

Predstavuje **úplne novú triedu softvéru**, ktorá doteraz v hudobnej technológii neexistovala:

### **Real‑Time Multi‑Track MIDI Notation Engine**

Tento typ softvéru kombinuje vlastnosti, ktoré sa nikdy predtým nevyskytli spolu:

- plne **real‑time** spracovanie MIDI udalostí  
- **16‑track Yamaha kompatibilný** multi‑track engine  
- okamžitá grafická notácia (beams, stems, barlines)  
- **velocity‑based** dynamika v reálnom čase  
- modulárny grafický renderer (Python + Pygame)  
- architektúra optimalizovaná pre **výskum, výučbu, živé hranie a štúdiá**  
- žiadne predspracovanie, žiadna analýza dopredu, žiadne offline kroky  

SIRIUS tým definuje **novú kategóriu real‑time MIDI nástrojov**, ktorá dopĺňa tradičné offline notátory (MuseScore, LilyPond, Dorico) a otvára priestor pre:

- živú notáciu  
- real‑time analýzu výkonu  
- výskum expresivity  
- štúdiové pred‑nahrávacie nástroje  
- vizualizáciu pre hudobnú pedagogiku  

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

## 🎹 **MIDI Input Layer**
### `real_time_processing/StreamHandler`
- Detects MIDI devices  
- Reads MIDI events in real time  
- Sends raw events to EventRouter  

### `midi_input/EventRouter`
- Routes MIDI → EventBus  
- Normalizes event format  
- Handles channel/track mapping  

---

## 📡 **Event Communication Layer**
### `event_bus/EventBus`
- Publish/subscribe system  
- Decouples all modules  
- Ensures clean communication between:
  - UI  
  - Renderer  
  - Processor  
  - TrackManager  
  - PlaybackEngine  

---

## 🎚 **Track System**
### `track_system/TrackSystem`
- 16-track Yamaha-style architecture  
- Track attributes (color, name, visibility)  

### `core/TrackManager`
- Mute / Solo / Volume / Pan  
- Record arm  
- Real-time activity meter  
- DAW-style logic  

---

## 🧠 **Notation Processing**
### `notation_processor/NotationProcessor`
- Converts MIDI → internal note objects  
- Rhythm analysis  
- Timing + velocity extraction  
- Prepares data for renderer  

---

## ⏱ **Playback Engine**
### `core/PlaybackEngine`
- Controls global time  
- Moves playhead  
- Selects active notes  
- Applies BPM + meter  
- Drives the entire render loop  

---

## 🎨 **Rendering Engine**
### `renderer/GraphicNotationRenderer`
- Real-time note rendering  
- Beams, stems, barlines  
- Velocity shading  
- Chord grouping  
- Grid + timeline  
- Zoom + scroll  
- Staff caching  

---

## 🖥 **UI Layer**
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
