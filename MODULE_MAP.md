# MODULE MAP — Real-Time MIDI Notation (v2.0.0 Architecture)

This document provides a complete overview of all modules in the Real-Time MIDI Notation project.  
It defines each module’s purpose, responsibilities, and relationships within the system.

---

## 1. CORE — Central Logic Layer
**Purpose:** Core data structures, processing logic, and real‑time synchronization.

**Responsibilities:**
- EventBus (routing of internal events)
- TrackManager (track creation, deletion, metadata)
- NotationProcessor (real‑time note processing)
- PlaybackEngine (timing, transport, synchronization)
- Data models (notes, tracks, markers, layout metadata)

---

## 2. UI — User Interface Layer
**Purpose:** Visual interaction, editing tools, and timeline visualization.

**Responsibilities:**
- TimelineUI (markers, loops, playhead, zoom/scroll)
- PianoUI (keyboard visualization)
- CanvasUI (rendering surface)
- NoteVisualizerUI (note highlights, animations)
- Interaction logic (mouse, keyboard, gestures)
- Editing groundwork (selection, snapping, hover effects)

---

## 3. renderer_new — High‑Performance Rendering Engine
**Purpose:** Pixel‑accurate rendering pipeline for real‑time notation.

**Responsibilities:**
- PixelLayoutEngine v2
- Cached grid rendering (dirty‑flag system)
- Graphic primitives preparation
- High‑performance drawing routines
- Separation of layout vs. rendering
- Preparation for v3 engraving engine

---

## 4. timeline — Editing & Navigation Layer
**Purpose:** Time‑based editing, markers, and playback navigation.

**Responsibilities:**
- Marker system (drag, rename, snapping, color)
- Loop regions (create, resize, drag)
- Playhead logic (seek, follow, sync)
- Zoom/scroll behavior
- TimelineController integration

---

## 5. runtime — Real‑Time Processing Layer
**Purpose:** High‑frequency event routing and stream handling.

**Responsibilities:**
- Burst‑safe event processing
- Real‑time MIDI stream handling
- Timestamp synchronization
- Low‑latency routing between modules

---

## 6. filesystem — Project I/O Layer
**Purpose:** Safe loading, saving, and serialization of project data.

**Responsibilities:**
- File validation
- Project save/load
- Serialization of tracks, markers, metadata
- Error handling and recovery

---

## 7. commands — Command Pattern Layer
**Purpose:** Unified command execution system.

**Responsibilities:**
- Command definitions
- Undo/redo groundwork
- Action routing
- Editing operations encapsulation

---

## 8. tests — Automated Testing Layer
**Purpose:** Stability, regression protection, and validation.

**Responsibilities:**
- Unit tests for CORE
- UI behavior tests
- Renderer performance tests
- Timeline logic tests

---

## 9. plugins — Extension Layer
**Purpose:** Optional modular extensions.

**Responsibilities:**
- Plugin API groundwork
- Optional feature modules
- External integrations

---

## 10. Future Modules (v3+ Roadmap)
**Engraving Engine (v3.0.0+)**
- Multi‑voice notation
- Polyphony
- Beams, articulations
- Collision avoidance
- Professional spacing engine

**Self‑Repair Layer (v4.0.0+)**
- Automatic diagnostics
- Module health checks
- Self‑repair routines

---

## Module Relationships (High‑Level)
- **CORE → UI:** Provides data for visualization  
- **CORE → renderer_new:** Provides layout metadata  
- **UI → renderer_new:** Requests drawing operations  
- **runtime → CORE:** Sends real‑time events  
- **timeline → UI:** Controls navigation and editing  
- **filesystem → CORE/UI:** Loads and saves project state  

---

## Summary
This MODULE_MAP.md defines the full architecture of the Real-Time MIDI Notation project as of version 2.0.0.  
It ensures clarity, maintainability, and scalability for future development.
