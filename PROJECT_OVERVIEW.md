# 🎼 Real-Time MIDI Notation — Project Overview (v2.0.0)

This document serves as the **official architecture overview, technical summary, and system description**  
for the **Real-Time MIDI Notation (SIRIUS Engine)** — a professional real‑time multi‑track MIDI  
visualization and notation engine.

The goal of the project is to create a tool that:

- receives MIDI in real time  
- analyzes notes, rhythm, timing, and velocity  
- renders musical notation instantly  
- provides DAW‑style 16‑track control  
- enables playback, visualization, and future export  
- supports Yamaha‑style arranger workflows  
- maintains a modular, scalable architecture ready for v3.0.0  

---

# 🆕 A New Class of Real‑Time MIDI Engine

**SIRIUS / Real‑Time MIDI Notation** does not belong to any existing category of music software.

It is NOT:

- a MIDI visualizer  
- an offline notation editor  
- a DAW plugin  
- a traditional MIDI library  

It represents a **new class of software**:

## ⭐ Real‑Time Multi‑Track MIDI Notation Engine

This engine combines features that have never existed together before:

- fully **real‑time** MIDI processing  
- **Yamaha‑compatible 16‑track** architecture  
- instant graphical notation (beams, stems, barlines)  
- **velocity‑based** dynamics  
- modular graphic renderer (Python + Pygame)  
- architecture optimized for **research, education, live performance, and studio workflows**  
- no preprocessing, no look‑ahead, no offline steps  

SIRIUS defines a **new category** of real‑time MIDI tools, complementing traditional offline notation systems  
and enabling:

- live notation  
- real‑time performance analysis  
- expressive timing research  
- pre‑recording studio diagnostics  
- educational visualization  

---

# 🧩 1. Project Architecture

The project is organized into modular directories, each with a clear responsibility:

| Directory | Purpose |
|----------|---------|
| **core/** | TrackManager, PlaybackEngine, timing logic |
| **renderer_new/** | v2 renderer stack (GraphicRenderer, PixelLayoutEngine) |
| **ui/** | CanvasUI, UIManager — visual interface and interaction |
| **track_system/** | 16‑channel MIDI track system (Yamaha standard) |
| **notation_processor/** | MIDI → notes → rhythm → visualization pipeline |
| **event_bus/** | Publish/subscribe communication between modules |
| **midi_input/** | MIDI input, EventRouter, device detection |
| **real_time_processing/** | StreamHandler — real‑time MIDI pipeline |
| **docs/** | Documentation and technical references |

This modular structure ensures:

- clean separation of concerns  
- easy debugging  
- scalable architecture  
- future expansion (export, advanced notation, AI/TIMELINE v3)  

---

# 🎼 2. Main Modules and Their Purpose

## **TrackManager (`core/track_manager.py`)**
- 16‑track Yamaha‑style system  
- mute / solo / volume / pan  
- record arm  
- real‑time activity  
- track color + visibility management  

---

## **GraphicNotationRenderer (`renderer_new/graphic_renderer.py`)**
- real‑time note rendering  
- velocity shading  
- barlines, grid, timeline ruler  
- real‑time playhead  
- chord grouping  
- beam detection  
- zoom + scroll  
- optimized staff caching  

---

## **CanvasUI (`ui/canvas_ui.py`)**
- main drawing surface  
- playhead rendering  
- scroll + zoom handling  
- receives timing from PlaybackEngine  

---

## **PlaybackEngine (`core/playback_engine.py`)**
- controls playback timing  
- calculates current time position  
- selects active notes  
- synchronizes playhead with UI  
- applies BPM and meter  
- drives the entire render loop  

---

## **UIManager (`ui/ui_manager.py`)**
- central UI controller  
- manages UI components  
- handles mouse + keyboard input  
- integrates TrackSwitcherUI  
- communicates with EventBus  

---

## **TrackSystem (`track_system/track_system.py`)**
- 16 MIDI channels  
- track attributes (color, name, visibility)  
- channel → track mapping  

---

## **NotationProcessor (`notation_processor/notation_processor.py`)**
- analyzes MIDI events  
- generates note objects  
- performs rhythmic analysis  
- prepares data for the renderer  

---

## **EventBus (`event_bus/event_bus.py`)**
- publish/subscribe system  
- decouples modules  
- ensures clean communication between:  
  - MIDI input  
  - UI  
  - Processor  
  - Renderer  
  - TrackManager  

---

## **StreamHandler (`real_time_processing/stream_handler.py`)**
- reads MIDI input in real time  
- forwards events to EventRouter  
- handles device detection  

---

## **EventRouter (`midi_input/event_router.py`)**
- routes MIDI → EventBus → TrackSystem → UI  
- ensures correct channel/track mapping  

---

# 🔄 3. Real-Time Pipeline

```
MIDI Input  
   ↓  
StreamHandler  
   ↓  
EventRouter  
   ↓  
EventBus  
   ↓  
TrackSystem + NotationProcessor  
   ↓  
PlaybackEngine  
   ↓  
GraphicNotationRenderer  
   ↓  
CanvasUI + UIManager  
   ↓  
Pygame Window (final output)
```

Each step is isolated, modular, and replaceable — ideal for future expansion.

---

# ▶️ 4. Running the Project

Run the application with:

```
python main.py
```

This initializes:

- all v2 modules  
- UIManager + CanvasUI  
- PlaybackEngine  
- real‑time renderer  
- MIDI input pipeline  

---

# 🚀 5. Future Extensions (v2 → v3)

Planned features include:

- toolbar (Play / Pause / Stop / Seek)  
- MIDI file loader (.mid import)  
- peak meter visualization  
- metronome  
- export to PDF / PNG / SVG  
- recording mode  
- tempo automation  
- track inspector panel  
- advanced engraving (articulations, dynamics, slurs)  
- AI/TIMELINE predictive layout (v3)  

---

# 🏁 6. Project Status (v2.0.0)

All major modules are **stable and complete**:

- CanvasUI — ✔  
- GraphicNotationRenderer — ✔  
- TrackManager — ✔  
- PlaybackEngine — ✔  
- main.py — ✔  
- TimelineUI — ✔ (from v1.3 foundation)  

The project is ready for large‑scale testing and v3 expansion.

---

# 🔚 End of Project Overview (v2.0.0)
