# 🎼 Real‑Time MIDI Notation — Project Overview (v4.0.0)

This document serves as the **official architecture overview, technical summary, and system description**  
for the **Real‑Time MIDI Notation (SIRIUS Engine)** — a professional real‑time multi‑track MIDI  
visualization and notation engine.

The goal of the project is to create a tool that:

- receives MIDI in real time  
- analyzes notes, rhythm, timing, and velocity  
- renders musical notation instantly  
- provides DAW‑style 16‑track control  
- enables playback, visualization, and future export  
- supports Yamaha‑style arranger workflows  
- maintains a modular, scalable architecture (v4‑ready)  

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

SIRIUS defines a **new category** of real‑time MIDI tools, enabling:

- live notation  
- real‑time performance analysis  
- expressive timing research  
- pre‑recording studio diagnostics  
- educational visualization  

---

# 🧩 1. Project Architecture (v4.0.0)

The project is organized into modular directories, each with a clear responsibility:

| Directory | Purpose |
|----------|---------|
| **core/** | TrackManager, PlaybackEngine, EventBus v4, timing logic |
| **renderer_new/** | v4 renderer stack (GraphicRenderer, PixelLayoutEngine v4) |
| **ui/** | CanvasUI, TimelineUI, UIManager v4 |
| **track_system/** | 16‑channel Yamaha‑style track system |
| **notation_processor/** | MIDI → notes → rhythm → visualization pipeline |
| **midi_input/** | DeviceManager v4, EventRouter |
| **real_time_processing/** | StreamHandler — real‑time MIDI pipeline |
| **docs/** | Documentation and technical references |

This modular structure ensures:

- clean separation of concerns  
- easy debugging  
- scalable architecture  
- future expansion (engraving engine v5)  

---

# 🎼 2. Main Modules and Their Purpose (v4.0.0)

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
- v4 rendering pipeline  

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
- v4 real‑time safety  

---

## **UIManager (`ui/ui_manager.py`)**
- central UI controller  
- manages UI components  
- handles mouse + keyboard input  
- integrates TrackSwitcherUI  
- communicates with EventBus  
- injects renderer + CanvasUI into PlaybackEngine  

---

## **NotationProcessor (`notation_processor/notation_processor.py`)**
- analyzes MIDI events  
- generates note objects  
- performs rhythmic analysis  
- prepares data for the renderer  
- stable v4 pipeline  

---

## **EventBus (`core/event_bus.py`)**
- publish/subscribe system  
- thread‑safe v4 implementation  
- no‑exception guarantees  
- decouples modules cleanly  

---

## **DeviceManager (`midi_input/device_manager.py`)**
- safe MIDI device detection  
- Windows/ASIO locked‑port protection  
- v4 error routing  

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

# 🔄 3. Real‑Time Pipeline (v4.0.0)

```
MIDI Input  
   ↓  
StreamHandler  
   ↓  
EventRouter  
   ↓  
EventBus v4  
   ↓  
TrackSystem + NotationProcessor  
   ↓  
PlaybackEngine v4  
   ↓  
GraphicNotationRenderer v4  
   ↓  
CanvasUI + UIManager v4  
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

- all v4 modules  
- UIManager v4  
- PlaybackEngine v4  
- real‑time renderer  
- MIDI input pipeline  

---

# 🚀 5. Future Extensions (v4 → v5)

Planned features include:

- engraving engine (slurs, ties, articulations)  
- MusicXML export  
- advanced spacing algorithms  
- collision avoidance  
- performance analytics  
- predictive layout (v5)  

---

# 🏁 6. Project Status (v4.0.0)

All major modules are **stable and complete**:

- CanvasUI — ✔  
- GraphicNotationRenderer — ✔  
- TrackManager — ✔  
- PlaybackEngine — ✔  
- UIManager v4 — ✔  
- TimelineUI — ✔  
- DeviceManager v4 — ✔  
- EventBus v4 — ✔  

The project is ready for **professional use**, research, education, and future v5 expansion.

---

# 🔚 End of Project Overview (v4.0.0)
