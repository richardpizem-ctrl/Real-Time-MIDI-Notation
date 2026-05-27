# 📝 Real-Time MIDI Notation — CHANGELOG (v4.2.0)

This document tracks all major changes, improvements, stabilizations, and milestones  
for **SIRIUS / Real-Time MIDI Notation v4.2.0**.

---

# 🚀 v4.2.0 — Editing Layer Foundation (Released)

## ✏️ New Editing Layer (CORE)
- Added new module: `core/editing/`
- **Selection model v2**
  - SelectionSet
  - SelectionItem
  - Multi-selection
  - SelectionChangedEvent
- **Region editing groundwork**
  - RegionManager
  - Region creation
  - Region splitting
  - RegionCreatedEvent
  - RegionSplitEvent
- **Snapping logic v2**
  - SnapGrid
  - snap_time
  - snap_range
- **Ghost primitives**
  - GhostNote
  - GhostRegion
  - HoverState
  - GhostController
  - GhostNotePreviewEvent
  - GhostRegionPreviewEvent

---

## 🧪 Tests Added
- `test_editing_selection.py`
- `test_editing_regions.py`
- `test_editing_snapping.py`
- `test_editing_ghosts.py`

---

## 🔧 Integration
- AppController updated to **v4.2.0**
- Editing layer initialized (selection, regions, snapping, ghosts)
- EventBus updated to register editing events
- `core/__init__.py` updated with editing exports

---

## 🧠 Core Architecture — v4 Foundation (from v4.0.0)
- Unified **v4 architecture** across all modules  
- EventBus v4 (thread‑safe, exception‑safe, real‑time safe)  
- DeviceManager v4 (robust port handling, Windows/ASIO lock protection)  
- RhythmAnalyzer v4 (stability index, BPM clamping, timing safety)  
- Logger v4 added (safe fallback logging)  
- Real-time pipeline synchronized across:
  - TrackManager v4  
  - NotationProcessor v4  
  - PlaybackEngine v4  
  - UIManager v4  
  - Renderer stack v4  

---

## 🎨 Renderer & Layout Engine — v4 Rendering Pipeline
- GraphicNotationRenderer v4 stabilized  
- PixelLayoutEngine v4 fully upgraded  
- Improved staff caching (dirty‑region system)  
- Improved chord grouping logic  
- Improved barline + grid synchronization  
- Renderer prepared for **v5 engraving engine**  

---

## 🖥 UI Layer — v4
- UIManager v4 (central UI orchestrator)  
- CanvasUI updated for v4 timing + rendering safety  
- TimelineUI stabilized (markers, loops, zoom/scroll)  
- Unified event handling across UI components  
- Improved input handling (mouse, keyboard, gestures)  

---

## 🎚 Track System — v4 Stability
- TrackManager v4 stabilized  
- Real-time activity meter improvements  
- Safe track switching  
- Yamaha‑compatible 16‑track architecture preserved  

---

## 🧩 Notation Processor — v4 Pipeline
- Stable MIDI → NoteObject pipeline  
- Improved velocity extraction  
- Improved timing normalization  
- RhythmAnalyzer v4 integrated  
- Safe event routing through EventBus v4  

---

## ⏱ Playback Engine — v4 Timing Core
- Stable play/pause/seek logic  
- Improved delta‑time handling  
- Safe renderer updates  
- BPM + meter synchronization  

---

## 🧹 Codebase Cleanup — v4 Standardization
- Removed all legacy v1.x and v2.x fragments  
- Unified naming conventions  
- Improved internal comments  
- Ensured consistent structure across all modules  
- Documentation rewritten for v4  

---

# 📦 v3.0.0 — Advanced Engraving Groundwork (Historical)
- Multi‑voice groundwork  
- Polyphony preparation  
- Beam/articulation preparation  
- Graphic primitives layer  
- Renderer_new improvements  
- Real-time engraving preview groundwork  

---

# 📦 v2.0.0 — Architecture Upgrade (Historical)
- Unified naming  
- Renderer_new  
- PixelLayoutEngine v2  
- Cached grid rendering  
- Full documentation rewrite  

---

# 📦 v1.3.0 — TimelineUI Finalization (Historical)
- Finalized TimelineUI  
- Stabilized markers, loop region, playhead, scroll/zoom  
- Renderer integration improvements  

---

# 📦 v1.2.0 — TimelineUI Refactor (Historical)
- Full TimelineUI refactor  
- Stabilized drawing + event logic  
- Renderer integration improvements  

---

# 📦 v1.1.0 — Timeline Selection & Phase‑4 Stabilization (Historical)

---

# 📦 v1.0.0 — Core Engine Complete (Historical)

---

# 🔮 Planned for v5.0.0+
- Full engraving engine  
- Multi‑voice notation  
- Polyphony  
- Advanced beams  
- Articulations  
- Dynamics  
- Collision avoidance  
- Spacing engine  
- Predictive layout (AI-assisted)  
- MusicXML export  
- MuseScore/LilyPond‑level engraving  
- Editing API v1 (v4.3.0)  
- Undo/Redo v2  
- Quantization engine  

---

# 🎉 End of CHANGELOG (v4.2.0)
