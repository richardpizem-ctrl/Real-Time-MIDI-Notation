# 🎼 MIDI Naming Conventions
Real‑Time MIDI Notation Engine – Official Naming Standard (v1.0.0)

This document defines unified naming rules for files, modules, classes, and components within the Real‑Time MIDI Notation Engine.  
The goal is to maintain a consistent, professional, and scalable architecture.

---

## 1. Core Principles
- names must be descriptive and unambiguous  
- names must reflect the module’s function  
- names must be consistent across the entire project  
- names must be future‑expandable (versions 2.0.0, 3.0.0)  
- names must be architectural, not script‑like  

---

## 2. MIDI Input & Processing
| Module | Purpose |
|--------|---------|
| `midi_input_manager.py` | Receives real‑time MIDI messages |
| `real_time_processing/` | Entire real‑time engine |
| `event_bus.py` | Distributes MIDI events between modules |
| `activity_tracking.py` | Logs and tracks activity |

---

## 3. Notation Engine
| Module | Purpose |
|--------|---------|
| `notation_engine.py` | Converts MIDI → notation objects |
| `notation_renderer.py` | Renders notation symbols |
| `note_mapper.py` | Converts MIDI numbers → note names |
| `duration_resolver.py` | Calculates rhythmic durations |

---

## 4. Graphic Rendering
| Module | Purpose |
|--------|---------|
| `graphic_renderer.py` | Main graphic renderer |
| `pixel_layout_engine.py` | Computes pixel positions of elements |
| `renderer_new/` | New‑generation renderer |
| `renderer_legacy/` | Archive of the old renderer |

---

## 5. User Interface Layer
| Module | Purpose |
|--------|---------|
| `timeline_ui.py` | Timeline + markers |
| `track_manager.py` | Management of 16 MIDI tracks |
| `track_control.py` | UI elements for track switching |
| `ui_components/` | All UI widgets |

---

## 6. Processing Pipeline
| Module | Purpose |
|--------|---------|
| `pipeline.py` | Main processing pipeline |
| `pipeline_stage_x.py` | Individual pipeline stages |
| `event_transformer.py` | MIDI event transformations |

---

## 7. Future Versions

### Version 2.0.0
- `undo_redo_manager.py`  
- `cached_grid_renderer.py`  
- `text_input.py`  
- `hover_effects.py`  

### Version 3.0.0
- `mpe_visualizer.py`  
- `vibrato_animator.py`  
- `poly_pressure_waveform.py`  
- `rgb_velocity_pulse.py`  

---

## 8. Class Naming Rules
- PascalCase  
- class name must reflect a single responsibility  
- examples:  
  - `GraphicRenderer`  
  - `NotationEngine`  
  - `PixelLayoutEngine`  
  - `TrackManager`  

---

## 9. Function Naming Rules
- snake_case  
- must be action‑based (verb + object)  
- examples:  
  - `process_event()`  
  - `render_note()`  
  - `calculate_position()`  
  - `update_timeline()`  

---

## 10. Constant Naming Rules
- UPPER_CASE  
- examples:  
  - `DEFAULT_VELOCITY_COLOR`  
  - `MAX_TRACKS = 16`  

---

## 11. Conclusion
This document defines the official naming standard for the Real‑Time MIDI Notation Engine.  
It is designed to support project growth, maintain a professional architecture, and establish a new standard in the MIDI ecosystem.
