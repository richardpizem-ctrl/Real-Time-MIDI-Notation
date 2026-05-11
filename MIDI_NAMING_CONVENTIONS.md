# 🎼 MIDI Naming Conventions  
Real‑Time MIDI Notation Engine — Official Naming Standard (v4.0.0)

This document defines unified naming rules for files, modules, classes, and components within the  
**Real‑Time MIDI Notation Engine (SIRIUS Engine)**.  
The goal is to maintain a consistent, professional, scalable, and future‑proof architecture.

Version **4.0.0** introduces a fully standardized naming system aligned with the v4 architecture and  
prepared for the v5 engraving/AI expansion.

---

# 1. Core Principles

- names must be descriptive and unambiguous  
- names must reflect the module’s function  
- names must be consistent across the entire project  
- names must be future‑expandable (v4.0.0 → v5.0.0)  
- names must be architectural, not script‑like  
- names must match the real‑time pipeline structure  
- names must avoid abbreviations unless industry‑standard  

---

# 2. MIDI Input & Processing (v4.0.0)

| Module | Purpose |
|--------|---------|
| `device_manager.py` | Safe detection + opening of MIDI ports (v4 safe) |
| `midi_input/stream_handler.py` | Reads real‑time MIDI messages |
| `midi_input/event_router.py` | Normalizes and routes MIDI events |
| `core/event_bus.py` | Thread‑safe event distribution |
| `real_time_processing/` | Entire real‑time engine |
| `activity_tracking.py` | Tracks MIDI activity (optional) |

**Naming rules:**
- all MIDI input modules use **snake_case**  
- all real‑time handlers end with `_handler.py`  
- routing modules end with `_router.py`  

---

# 3. Notation Engine (v4.0.0)

| Module | Purpose |
|--------|---------|
| `notation_engine.py` | Converts MIDI → notation objects |
| `notation_processor.py` | Real‑time note processing |
| `note_mapper.py` | Converts MIDI numbers → note names |
| `duration_resolver.py` | Calculates rhythmic durations |
| `rhythm_analyzer.py` | BPM, timing, rhythmic grouping |

**Naming rules:**
- all notation modules end with `_engine`, `_processor`, `_resolver`, or `_analyzer`  
- rhythmic/timing modules must include `rhythm` or `timing` in the name  

---

# 4. Graphic Rendering (v4.0.0)

| Module | Purpose |
|--------|---------|
| `renderer_new/graphic_renderer.py` | Main v4 renderer |
| `renderer_new/pixel_layout_engine.py` | Computes pixel positions |
| `renderer_new/layer_manager.py` | Manages render layers |
| `renderer_new/cache_manager.py` | Caching for v4 renderer |
| `renderer_legacy/` | Archive of the old renderer |

**Naming rules:**
- all renderer modules start with `graphic_` or `pixel_`  
- layout modules end with `_layout_engine.py`  
- caching modules end with `_cache.py` or `_cache_manager.py`  

---

# 5. User Interface Layer (v4.0.0)

| Module | Purpose |
|--------|---------|
| `ui/timeline_ui.py` | Timeline + markers |
| `ui/canvas_ui.py` | Main drawing surface |
| `ui/ui_manager.py` | Central UI orchestrator |
| `ui_components/track_switcher_ui.py` | Track switching UI |
| `ui_components/controls/` | Buttons, sliders, widgets |

**Naming rules:**
- all UI modules end with `_ui.py`  
- UI managers end with `_manager.py`  
- UI components live in `ui_components/`  

---

# 6. Processing Pipeline (v4.0.0)

| Module | Purpose |
|--------|---------|
| `pipeline/pipeline.py` | Main processing pipeline |
| `pipeline/pipeline_stage_x.py` | Individual pipeline stages |
| `pipeline/event_transformer.py` | MIDI event transformations |
| `pipeline/validators/` | Input validation modules |

**Naming rules:**
- pipeline stages must follow: `pipeline_stage_<name>.py`  
- transformers must end with `_transformer.py`  
- validators must end with `_validator.py`  

---

# 7. Versioned Modules

## Version 4.0.0 (current)
- `event_bus.py` (thread‑safe v4)  
- `device_manager.py` (safe port handling)  
- `ui_manager.py` (central UI orchestrator)  
- `rhythm_analyzer.py` (stable BPM + stability)  
- `graphic_renderer.py` (v4 renderer)  
- `pixel_layout_engine.py` (v4 layout engine)  
- `preview.py` (safe renderer preview)  

## Version 5.0.0 (planned)
- `engraving_engine.py`  
- `slur_engine.py`  
- `tie_resolver.py`  
- `collision_avoidance.py`  
- `spacing_engine.py`  
- `ai_performance_analyzer.py`  
- `predictive_layout_engine.py`  

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
  - `UIManager`  
  - `PlaybackEngine`  

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
  - `resolve_duration()`  

---

# 10. Constant Naming Rules

- **UPPER_CASE**  
- examples:  
  - `DEFAULT_VELOCITY_COLOR`  
  - `MAX_TRACKS = 16`  
  - `DEFAULT_BPM = 120`  
  - `DEFAULT_WINDOW_WIDTH = 1600`  

---

# 11. Conclusion

This document defines the official naming standard for the Real‑Time MIDI Notation Engine v4.0.0.  
It ensures architectural consistency, supports long‑term scalability, and prepares the project  
for the upcoming **v5.0.0 engraving + analysis expansion**.
