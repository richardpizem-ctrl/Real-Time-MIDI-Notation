# Real-Time MIDI Notation – Project Overview

This document serves as a **guide, architecture description, and technical documentation** for the entire  
**Real-Time MIDI Notation** project.

The goal of the project is to create a professional tool that:

- receives MIDI in real time  
- analyzes notes and rhythm  
- renders musical notation in real time  
- provides DAW‑style track control  
- enables playback, visualization, and export  

---

# 🧩 1. Project Architecture

The project is divided into modules by function:
core/
renderer/
ui/
track_system/
notation_processor/
event_bus/
midi_input/
real_time_processing/
docs/

Each directory has a clear responsibility:

| Directory | Purpose |
|----------|---------|
| **core/** | Project logic: TrackManager, PlaybackEngine, Logger |
| **renderer/** | GraphicNotationRenderer – real‑time note rendering |
| **ui/** | CanvasUI, UIManager – visual interface |
| **track_system/** | 16‑channel MIDI track system |
| **notation_processor/** | MIDI → notes → rhythm → visualization |
| **event_bus/** | Communication between modules |
| **midi_input/** | MIDI input, EventRouter |
| **real_time_processing/** | StreamHandler – realtime MIDI pipeline |
| **docs/** | Project documentation |

---

# 🎼 2. Main Modules and Their Purpose

## **TrackManager (core/track_manager.py)**
- controls track visibility  
- mute / solo / volume / pan  
- record arm  
- realtime activity (peak meter)  
- applies DAW logic to MIDI events  

## **GraphicNotationRenderer (renderer/graphic_renderer.py)**
- renders notes in real time  
- heatmap colors, glow effect, velocity visualization  
- barlines, grid, playhead  
- processes note groups (chords, beams)  

## **CanvasUI (ui/canvas_ui.py)**
- displays the playhead  
- UI layer for the renderer  
- receives timing from PlaybackEngine  

## **PlaybackEngine (core/playback_engine.py)**
- controls playback  
- calculates time  
- selects active notes  
- sends them to the renderer  
- synchronizes playhead with UI  
- applies BPM and meter  

## **UIManager (ui/ui_manager.py)**
- main UI controller  
- connects all UI components  
- handles user input  

## **TrackSystem (track_system/track_system.py)**
- 16 MIDI channels  
- track colors, names, attributes  

## **NotationProcessor (notation_processor/notation_processor.py)**
- analyzes MIDI  
- generates notes, rhythm, visualization  

## **EventBus (event_bus/event_bus.py)**
- publish/subscribe system  
- connects UI, MIDI input, processor, renderer  

## **StreamHandler (real_time_processing/stream_handler.py)**
- reads MIDI input in real time  
- sends events to EventRouter  

## **EventRouter (midi_input/event_router.py)**
- MIDI → EventBus → UI → TrackSystem  

---

# 🔄 3. Realtime Pipeline

MIDI input  
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
Pygame window  

Each step is separated to keep the project modular and extendable.

---

# ▶️ 4. How to Run the Project

Each step is separated to keep the project modular and extendable.  
python run.py

`run.py`:

- initializes all modules  
- creates the UI  
- starts the PlaybackEngine  
- starts the main render loop  

---

# 🚀 5. Future Extensions

- Toolbar (Play / Pause / Stop / Seek)  
- MIDI loader (import .mid files)  
- Peak meter visualization  
- Metronome  
- Export to PDF / PNG  
- Recording mode  
- Tempo automation  
- Track inspector panel  

---

# 🏁 6. Project Status

All major modules are **finished and stable**:

- CanvasUI – final  
- GraphicNotationRenderer – final  
- TrackManager – final  
- PlaybackEngine – final  
- run.py – final integration  

The project is ready for further expansion.

---

# 🕹️ 7. User Guide

## ▶️ Launching the Application
The project is launched with:
python run.py

After launching, the main application window (pygame) opens.

---

## 🎹 MIDI Input
- If you have a connected MIDI controller, StreamHandler detects it automatically.  
- Every played note is immediately:
  - sent to EventRouter  
  - displayed in the UI  
  - processed in NotationProcessor  
  - rendered in GraphicNotationRenderer  

---

## 🎼 Playback (PlaybackEngine)
PlaybackEngine controls:

- time  
- playback  
- playhead  
- active notes  
- tempo (BPM)  
- meter (beats per bar)

### Controls (temporary until toolbar is added):
- playback starts automatically when MIDI arrives  
- playhead moves according to BPM  
- renderer draws notes in real time  

---

## 🎚️ Track System
TrackSystem + TrackManager allow:

- mute / solo  
- volume  
- pan  
- record arm  
- track colors  
- activity (peak meter – coming soon)

Each note has a track_id → renderer draws it using the track’s color.

---

## 🖥️ UI (CanvasUI + UIManager)
The UI consists of:

- the main window (pygame)  
- CanvasUI (playhead + renderer)  
- UIManager (other UI elements)

UIManager handles:

- mouse clicks  
- keyboard input  
- track interactions  
- MIDI input visualization  

---

## 🎨 Renderer
GraphicNotationRenderer:

- renders notes along the timeline  
- uses heatmap colors  
- displays velocity  
- draws barlines  
- scrolls notes according to the playhead  

---

## 💾 Export (planned)
In the future it will be possible to:

- export MIDI  
- export images  
- export PDF  

---

# 🔚 End of Documentation
