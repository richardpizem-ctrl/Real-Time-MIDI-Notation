# 🎼 Real-Time MIDI Notation — Project Overview (Ultimate Edition, v1.3.0)

This document serves as the **official architecture guide, technical overview, and system documentation** for the  
**Real-Time MIDI Notation (SIRIUS Engine)** — a professional real‑time multi‑track MIDI visualization and notation engine.

The goal of the project is to create a tool that:

- receives MIDI in real time  
- analyzes notes, rhythm, timing, and velocity  
- renders musical notation instantly  
- provides DAW‑style 16‑track control  
- enables playback, visualization, and future export  
- supports Yamaha‑style arranger workflows  

---

# 🆕 A New Class of Real‑Time MIDI Engine

**SIRIUS / Real‑Time MIDI Notation** does not belong to any existing category of music software.  
It is not a MIDI visualizer, not an offline notation editor, not a DAW plugin, and not a traditional MIDI library.

It represents a **completely new class of software**:

## ⭐ Real‑Time Multi‑Track MIDI Notation Engine

This engine combines features that have never existed together before:

- fully **real‑time** MIDI processing  
- **Yamaha‑compatible 16‑track** architecture  
- instant graphical notation (beams, stems, barlines)  
- **velocity‑based** dynamics  
- modular graphic renderer (Python + Pygame)  
- architecture optimized for **research, education, live performance, and studio workflows**  
- no preprocessing, no look‑ahead, no offline steps  

SIRIUS defines a **new category** of real‑time MIDI tools, complementing traditional offline notation systems (MuseScore, LilyPond, Dorico) and enabling:

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
| **core/** | TrackManager, PlaybackEngine, Logger, timing logic |
| **renderer/** | GraphicNotationRenderer — real‑time notation rendering |
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
- future expansion (export, advanced notation, DAW integration)  

---

# 🎼 2. Main Modules and Their Purpose

## **TrackManager (`core/track_manager.py`)**
- 16‑track Yamaha‑style system  
- mute / solo / volume / pan  
- record arm  
- real‑time activity (peak meter)  
- DAW‑style routing logic  
- track color + visibility management  

---

## **GraphicNotationRenderer (`renderer/graphic_notation_renderer.py`)**
- real‑time note rendering  
- velocity shading  
- barlines, grid, timeline ruler  
- real‑time playhead  
- chord grouping  
- beam detection  
- dynamic stems  
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

# ▶️ 4. How to Run the Project

Run the application with:

```
python run.py
```

`run.py`:

- initializes all modules  
- creates the UI  
- starts the PlaybackEngine  
- starts the main render loop  
- connects MIDI input → processor → renderer → UI  

---

# 🚀 5. Future Extensions

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

---

# 🏁 6. Project Status (v1.3.0)

All major modules are **finished and stable**:

- CanvasUI — ✔ final  
- GraphicNotationRenderer — ✔ final  
- TrackManager — ✔ final  
- PlaybackEngine — ✔ final  
- run.py — ✔ final integration  
- TimelineUI — ✔ finalized in v1.3.0  

The project is ready for large‑scale testing and expansion.

---

# 🕹️ 7. User Guide

## ▶️ Launching the Application
Run:

```
python run.py
```

The main pygame window will open automatically.

---

## 🎹 MIDI Input
When a MIDI device is connected:

- StreamHandler detects it  
- EventRouter routes events  
- NotationProcessor analyzes them  
- Renderer draws them in real time  

Every note is processed instantly.

---

## 🎼 Playback (PlaybackEngine)
PlaybackEngine controls:

- time  
- playhead  
- active notes  
- BPM  
- meter  
- scroll speed  

Playback starts automatically when MIDI arrives.

---

## 🎚 Track System
TrackSystem + TrackManager provide:

- mute / solo  
- volume  
- pan  
- record arm  
- track colors  
- activity meter (coming soon)  

Each note has a `track_id` → renderer uses the track’s color.

---

## 🖥 UI (CanvasUI + UIManager)
UI components:

- main pygame window  
- CanvasUI (renderer surface)  
- UIManager (interaction layer)  

UIManager handles:

- mouse  
- keyboard  
- track interactions  
- MIDI visualization  

---

## 🎨 Renderer
GraphicNotationRenderer:

- draws notes along the timeline  
- uses velocity shading  
- displays barlines  
- scrolls notes with the playhead  
- groups chords and beams  

---

## 💾 Export (planned)
Future export options:

- PNG  
- SVG  
- PDF  
- MIDI  

---

# 🔚 End of Documentation
