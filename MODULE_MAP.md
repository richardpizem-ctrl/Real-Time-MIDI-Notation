# MODULE MAP — Real-Time MIDI Notation (v4.2.0 Architecture)

This document provides a complete overview of all modules in the Real-Time MIDI Notation project.  
It defines each module’s purpose, responsibilities, and relationships within the system.

---

# 1. CORE — Central Logic Layer (v4.2.0)
**Purpose:** Core data structures, processing logic, editing layer, and real‑time synchronization.

**Responsibilities:**
- **EventBus v4** — thread‑safe routing of internal events  
- **TrackManager v4** — track creation, deletion, metadata, visibility, color  
- **NotationProcessor v4** — real‑time note processing + rhythmic analysis  
- **PlaybackEngine v4** — timing, transport, synchronization, playhead  
- **Editing Layer v4.2.0**  
  - SelectionSet v2  
  - RegionManager  
  - SnapGrid v2  
  - GhostController  
  - Editing events  
- **Data models** — notes, tracks, markers, layout metadata  
- **Logger v4** — safe logging with fallback  

---

# 2. UI — User Interface Layer (v4.2.0)
**Purpose:** Visual interaction, editing tools, and timeline visualization.

**Responsibilities:**
- **UIManager v4** — central UI orchestrator  
- **TimelineUI** — markers, loops, playhead, zoom/scroll  
- **CanvasUI** — rendering surface for notation  
- **TrackSwitcher / TrackSelector** — track visibility + selection  
- **Interaction logic** — mouse, keyboard, gestures  
- **Editing groundwork** — selection previews, snapping previews, ghost previews  

---

# 3. renderer_new — High‑Performance Rendering Engine (v4.2.0)
**Purpose:** Pixel‑accurate rendering pipeline for real‑time notation.

**Responsibilities:**
- **PixelLayoutEngine v4**  
- Cached grid rendering (dirty‑flag system)  
- Graphic primitives preparation  
- High‑performance drawing routines  
- Separation of layout vs. rendering  
- Ready for v5 engraving engine (slurs, ties, articulations)  

---

# 4. editing — Editing Layer (v4.2.0)
**Purpose:** Real‑time editing foundation for selection, regions, snapping, and ghost previews.

**Responsibilities:**
- **SelectionSet v2** — multi‑selection logic  
- **RegionManager** — region creation, splitting, manipulation  
- **SnapGrid v2** — snapping utilities for time/pitch  
- **GhostController** — ghost notes, ghost regions, hover previews  
- **Editing events** — SelectionChangedEvent, RegionCreatedEvent, RegionSplitEvent, GhostNotePreviewEvent, GhostRegionPreviewEvent  

---

# 5. timeline — Editing & Navigation Layer
**Purpose:** Time‑based editing, markers, and playback navigation.

**Responsibilities:**
- Marker system (drag, rename, snapping, color)  
- Loop regions (create, resize, drag)  
- Playhead logic (seek, follow, sync)  
- Zoom/scroll behavior  
- TimelineController integration  
- Editing groundwork for v5  

---

# 6. runtime / real_time_processing — Real‑Time Processing Layer (v4.2.0)
**Purpose:** High‑frequency event routing and stream handling.

**Responsibilities:**
- Burst‑safe event processing  
- Real‑time MIDI stream handling  
- Timestamp synchronization  
- Low‑latency routing between modules  
- Stable under heavy MIDI load  

---

# 7. filesystem — Project I/O Layer
**Purpose:** Safe loading, saving, and serialization of project data.

**Responsibilities:**
- File validation  
- Project save/load  
- Serialization of tracks, markers, metadata  
- Error handling and recovery  
- Ready for v5 export engine (PDF, SVG, MusicXML)  

---

# 8. commands — Command Pattern Layer
**Purpose:** Unified command execution system.

**Responsibilities:**
- Command definitions  
- Undo/redo groundwork  
- Action routing  
- Editing operations encapsulation  
- Future integration with Editing API v4.3.0  

---

# 9. tests — Automated Testing Layer
**Purpose:** Stability, regression protection, and validation.

**Responsibilities:**
- Unit tests for CORE  
- Editing Layer tests (v4.2.0)  
- UI behavior tests  
- Renderer performance tests  
- Timeline logic tests  
- Stress tests for real‑time engine  

---

# 10. plugins — Extension Layer
**Purpose:** Optional modular extensions.

**Responsibilities:**
- Plugin API groundwork  
- Optional feature modules  
- External integrations  
- Future AI/analysis plugins (v5+)  

---

# 11. Future Modules (v5+ Roadmap)

## Engraving Engine (v5.0.0+)
- Multi‑voice notation  
- Polyphony  
- Beams, articulations  
- Collision avoidance  
- Professional spacing engine  

## AI/Analysis Layer (v5.0.0+)
- Predictive layout  
- Expressive timing analysis  
- Harmonic analysis  
- Performance analytics  

## Self‑Repair Layer (v5.0.0+)
- Automatic diagnostics  
- Module health checks  
- Self‑repair routines  

---

# Module Relationships (High‑Level)
- **CORE → UI:** Provides data for visualization  
- **CORE → renderer_new:** Provides layout metadata  
- **CORE → editing:** Provides editing state + events  
- **UI → renderer_new:** Requests drawing operations  
- **runtime → CORE:** Sends real‑time events  
- **timeline → UI:** Controls navigation and editing  
- **filesystem → CORE/UI:** Loads and saves project state  
- **midi_input → EventBus:** Routes MIDI events into the system  

---

# Summary
This MODULE_MAP.md defines the full architecture of the Real-Time MIDI Notation project as of version **4.2.0**.  
It ensures clarity, maintainability, and scalability for future development, including the upcoming v4.3.0 Editing API and v5 engraving engine.
