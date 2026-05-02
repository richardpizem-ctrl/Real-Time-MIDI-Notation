# 🎼 MIDI Naming Conventions  
Real‑Time MIDI Notation Engine — Official Naming Standard (v2.0.0)

This document defines unified naming rules for files, modules, classes, and components within the  
**Real‑Time MIDI Notation Engine**.  
The goal is to maintain a consistent, professional, scalable, and future‑proof architecture.

Version **2.0.0** introduces a fully standardized naming system aligned with the v2 architecture and  
prepared for the v3 AI/TIMELINE expansion.

---

# 1. Core Principles

- names must be descriptive and unambiguous  
- names must reflect the module’s function  
- names must be consistent across the entire project  
- names must be future‑expandable (v2.0.0 → v3.0.0)  
- names must be architectural, not script‑like  
- names must match the real‑time pipeline structure  

---

# 2. MIDI Input & Processing

| Module | Purpose |
|--------|---------|
| `device_manager.py` | Safe detection + opening of MIDI ports |
| `midi_input/stream_handler.py` | Reads real‑time MIDI messages |
| `midi_input/event_router.py` | Normalizes and routes MIDI events |
| `core/event_bus.py` | Distributes events between modules |
| `real_time_processing/` | Entire real‑time engine |
| `activity_tracking.py` | Tracks MIDI activity (optional) |

---

# 3. Notation Engine

| Module | Purpose |
|--------|---------|
| `notation_engine.py` | Converts MIDI → notation objects |
| `notation_processor.py` | Real‑time note processing |
| `note_mapper.py` | Converts MIDI numbers → note names |
| `duration_resolver.py` | Calculates rhythmic durations |
| `rhythm_analyzer.py` | BPM, timing, rhythmic grouping |

---

# 4. Graphic Rendering

| Module | Purpose |
|--------|---------|
| `renderer_new/graphic_renderer.py` | Main v2 renderer |
| `renderer_new/pixel_layout_engine.py` | Computes pixel positions |
| `renderer_new/layer_manager.py` | Manages render layers |
| `renderer_legacy/` | Archive of the old renderer |
| `renderer_new/cache_manager.py` | Caching for v2/v3 renderer |

---

# 5. User Interface Layer

| Module | Purpose |
|--------|---------|
| `ui/timeline_ui.py` | Timeline + markers |
| `ui/canvas_ui.py` | Main drawing surface |
| `ui/ui_manager.py` | Central UI orchestrator |
| `ui_components/track_switcher_ui.py` | Track switching UI |
| `ui_components/controls/` | Buttons, sliders, widgets |

---

# 6. Processing Pipeline

| Module | Purpose |
|--------|---------|
| `pipeline/pipeline.py` | Main processing pipeline |
| `pipeline/pipeline_stage_x.py` | Individual pipeline stages |
| `pipeline/event_transformer.py` | MIDI event transformations |
| `pipeline/validators/` | Input validation modules |

---

# 7. Future Versions

## Version 2.0.0 (current)
- `undo_redo_manager.py`  
- `cached_grid_renderer.py`  
- `text_input.py`  
- `hover_effects.py`  
- `layer_manager.py`  
- `cache_manager.py`  

## Version 3.0.0 (planned)
- `mpe_visualizer.py`  
- `vibrato_animator.py`  
- `poly_pressure_waveform.py`  
- `rgb_velocity_pulse.py`  
- `ai_timeline_predictor.py`  
- `gesture_interpreter.py`  

---

# 8. Class Naming Rules

- **PascalCase**  
- class name must reflect a single responsibility  
- examples:  
  - `GraphicRenderer`  
  - `NotationEngine`  
  - `PixelLayoutEngine`  
  - `TrackManager`  
  - `EventRouter`  
  - `StreamHandler`  

---

# 9. Function Naming Rules

- **snake_case**  
- must be action‑based (verb + object)  
- examples:  
  - `process_event()`  
  - `render_note()`  
  - `calculate_position()`  
  - `update_timeline()`  
  - `open_input_port()`  
  - `publish_event()`  

---

# 10. Constant Naming Rules

- **UPPER_CASE**  
- examples:  
  - `DEFAULT_VELOCITY_COLOR`  
  - `MAX_TRACKS = 16`  
  - `DEFAULT_BPM = 120`  

---

# 11. Conclusion

This document defines the official naming standard for the Real‑Time MIDI Notation Engine v2.0.0.  
It ensures architectural consistency, supports long‑term scalability, and prepares the project  
for the upcoming **v3.0.0 AI/TIMELINE expansion**.

