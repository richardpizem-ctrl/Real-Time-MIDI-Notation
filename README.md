# 🎼 Real-Time MIDI Notation  
### **Real‑time multi‑track MIDI visualization & notation engine (Python, Pygame)**  
A high‑performance renderer for real‑time MIDI events with 16‑track support, advanced beams, velocity dynamics, and a fully modular UI.

---

# 🔍 What is Real-Time MIDI Notation?  
**Real-Time MIDI Notation** is a **real‑time multi‑track MIDI renderer** written in Python.  
It converts incoming MIDI events into **live notation**, including:

- real‑time note placement  
- multi‑track color coding  
- velocity‑based dynamics  
- beams, stems, barlines  
- grid, timeline, and playhead  
- full Yamaha 16‑track standard  
- real‑time activity meters  
- zoom + scroll  

This project aims to evolve into a **full real‑time engraving engine**, similar to MuseScore or LilyPond, but optimized for **live MIDI input**.

---

# 🎯 Who Is This For?

- MIDI visualizers  
- DAW companion tools  
- real‑time notation engines  
- music education software  
- live performance analysis  
- Yamaha arranger keyboard users  
- MIDI debugging and development  

---

# 🧩 Why This Project Matters  
Real‑time notation is a **non‑trivial engineering challenge**.  
Most notation engines (MuseScore, LilyPond, Dorico) are **offline engravers** — they expect complete musical context.

This project solves:

- **real‑time note grouping**  
- **real‑time beam detection**  
- **real‑time velocity dynamics**  
- **real‑time multi‑track rendering**  
- **real‑time layout engine (no pre‑analysis)**  

This makes it ideal for:

- research  
- education  
- live performance tools  
- MIDI hardware development  

---

# 🎓 Academic Relevance  
This engine is suitable for:

- **music informatics research**  
- **real‑time systems courses**  
- **MIDI protocol analysis**  
- **digital signal processing labs**  
- **human–computer interaction studies**  
- **music pedagogy and visualization**  

A full **CITATION.cff** file will be added for academic referencing.

---

# 🌟 Long‑Term Vision (Future Concept)

### 🎼 1. Create Sheet Music for Musicians Who Play by Ear  
A major long‑term goal:  
**allow musicians who do not read notation to generate professional sheet music from their own playing.**

This includes:
- real‑time capture of performance  
- automatic rhythmic + pitch analysis  
- exportable notation (PNG/SVG/PDF in future)  
- clean layout suitable for professional musicians  

### 🎹 2. Bridge Between Amateur and Professional Worlds  
The engine aims to become a tool where:
- amateurs can record ideas  
- the engine converts them into readable notation  
- professionals can refine, orchestrate, and arrange  

### 🧪 3. Music Research Platform  
- timing deviation analysis  
- expressive performance studies  
- educational visualization  
- MIDI‑based research tools  

### 📄 4. Full Export & Sharing Ecosystem  
- snapshots  
- sheet exports  
- timeline exports  
- multi‑track score exports  

### 🎼 5. Future Engraving Engine  
- spacing algorithms  
- collision avoidance  
- slurs, ties, articulations  
- professional publishing quality  

---

# 🔎 SEO Keywords  
`midi`, `real-time midi`, `real-time midi notation`, `midi notation`, `midi visualizer`,  
`midi renderer`, `music notation`, `pygame`, `python midi`, `multi-track midi`,  
`midi to sheet music`, `yamaha`, `arranger keyboard`, `live midi`, `midi processing`,  
`real-time visualization`, `midi sheet music`, `midi score`

---

# ✅ Completed Modules & Features

## 🎨 GraphicNotationRenderer (core graphic engine)
- real‑time layout engine  
- time → X mapping  
- pitch → Y mapping  
- staff cache (performance boost)  
- barlines, grid, timeline ruler  
- real‑time playhead  
- velocity dynamics (color + size)  
- chord grouping  
- 8th/16th beam detection  
- dynamic stems  
- full Yamaha 16‑track support  
- track visibility + color integration  
- real‑time activity meters  
- zoom + scroll  
- fully stabilized  

---

## 📝 NotationRenderer (text/debug renderer)
- textual MIDI visualization  
- drum notation support  
- drum stave offset  
- timestamps on every line  
- `clear()` – reset buffer  
- `filter()` – filter by pitch/channel/drums  
- pygame‑safe fallback  
- ideal for debugging  

---

## 🧠 Processor
- note mapping  
- rhythmic analysis  
- BPM detection  
- velocity + timing extraction  
- basic Rhythm Analyzer  

---

## 🎚 TrackManager
- 16 tracks (Yamaha standard)  
- per‑track colors  
- volume, visibility, activity  
- active track highlighting  
- real‑time activity updates  

---

# 🏗 Architecture Overview
MIDI Input  
↓  
Processor (timing, rhythm, velocity)  
↓  
GraphicNotationRenderer  
↓  
UI Layer (Piano, Roll, Staff, Visualizer)  
↓  
TrackManager (16‑track control)  
↓  
Debug Layer (NotationRenderer)

Modular. Extensible. Professional.

---

# 📦 Code Structure

### Core Engine
- `src/processor.py`  
- `src/rhythm_analyzer.py`  
- `src/midi_input/midi_note_mapper.py`  
- `src/event_bus.py`  

### Track System
- `core/track_system.py`  
- `core/track_manager.py`  

### Rendering
- `renderer_new/graphic_renderer.py`  
- `renderer_legacy/notation_renderer.py`  

### UI Layer
- `ui/ui_manager.py`  
- `ui/ui_components/*`  

---

# 🚀 Current Status

| Area | Progress | Visual |
|------|----------|--------|
| GraphicNotationRenderer | **100%** | 🟩🟩🟩🟩🟩 |
| NotationRenderer | **100%** | 🟩🟩🟩🟩🟩 |
| Processor | **100%** | 🟩🟩🟩🟩🟩 |
| Rhythm Analyzer | **100%** | 🟩🟩🟩🟩🟩 |
| TrackManager | **100%** | 🟩🟩🟩🟩🟩 |
| Pipeline (MIDI → Renderer → UI) | **100%** | 🟩🟩🟩🟩🟩 |

---

# 🗺 Roadmap

## 🔜 Next steps
- UI Track Switcher improvements  
- minor UI polish  
- documentation: “How the renderer works”  

---

## 🎯 Version 1.2 – UI Improvements
- real‑time activity meter  
- improved layout  
- track color integration  

---

## 🎯 Version 1.3 – Export
- PNG export  
- SVG export  
- screenshot engine  
- **MIDI → PNG (simple sheet export)**  
- **foundation for MIDI → sheet‑music conversion**  

---

## 🎯 Version 2.0 – Advanced Layout Engine
- multi‑voice notation  
- polyphony  
- advanced beams  
- dynamics  
- articulations  

---

## 🎯 Version 3.0 – Professional Engraving
- MuseScore / LilyPond‑level engraving  
- full notation engine  

---

# 🧩 Summary

Real-Time MIDI Notation is now:

- stable  
- modular  
- professionally structured  
- fully functional end‑to‑end  
- ready for rapid expansion  

This is the foundation of a **full real‑time notation engine**.
