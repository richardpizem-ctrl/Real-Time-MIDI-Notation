# 🎼 MIDI Naming Conventions
Real‑Time MIDI Notation Engine – Official Naming Standard (v1.0.0)

Tento dokument definuje jednotné pravidlá pomenovania súborov, modulov, tried a komponentov v rámci Real‑Time MIDI Notation Engine. Cieľom je zachovať konzistentnú, profesionálnu a rozšíriteľnú architektúru.

---

## 1. Základné princípy
- názvy musia byť popisné a jednoznačné
- názvy musia odrážať funkciu modulu
- názvy musia byť konzistentné v celom projekte
- názvy musia byť budúco‑rozšíriteľné (verzie 2.0.0, 3.0.0)
- názvy musia byť architektonické, nie skriptové

---

## 2. MIDI Input & Processing
| Modul | Účel |
|-------|------|
| `midi_input_manager.py` | Príjem MIDI správ v reálnom čase |
| `real_time_processing/` | Celý real‑time engine |
| `event_bus.py` | Distribúcia MIDI eventov medzi modulmi |
| `activity_tracking.py` | Logovanie a sledovanie aktivity |

---

## 3. Notation Engine
| Modul | Účel |
|-------|------|
| `notation_engine.py` | Prevod MIDI → notové objekty |
| `notation_renderer.py` | Renderovanie notových symbolov |
| `note_mapper.py` | Prevod MIDI čísla → názov noty |
| `duration_resolver.py` | Výpočet rytmických hodnôt |

---

## 4. Graphic Rendering
| Modul | Účel |
|-------|------|
| `graphic_renderer.py` | Hlavný grafický renderer |
| `pixel_layout_engine.py` | Výpočet pixelovej pozície prvkov |
| `renderer_new/` | Nová generácia renderera |
| `renderer_legacy/` | Archív starého renderera |

---

## 5. User Interface Layer
| Modul | Účel |
|-------|------|
| `timeline_ui.py` | Timeline + markers |
| `track_manager.py` | Správa 16 MIDI stôp |
| `track_control.py` | UI prvky pre prepínanie stôp |
| `ui_components/` | Všetky UI widgety |

---

## 6. Processing Pipeline
| Modul | Účel |
|-------|------|
| `pipeline.py` | Hlavná pipeline pre spracovanie |
| `pipeline_stage_x.py` | Jednotlivé kroky pipeline |
| `event_transformer.py` | Transformácie MIDI eventov |

---

## 7. Budúce verzie

### Verzia 2.0.0
- `undo_redo_manager.py`
- `cached_grid_renderer.py`
- `text_input.py`
- `hover_effects.py`

### Verzia 3.0.0
- `mpe_visualizer.py`
- `vibrato_animator.py`
- `poly_pressure_waveform.py`
- `rgb_velocity_pulse.py`

---

## 8. Pravidlá pre názvy tried
- PascalCase
- názov triedy musí odrážať jednu zodpovednosť
- príklady:
  - `GraphicRenderer`
  - `NotationEngine`
  - `PixelLayoutEngine`
  - `TrackManager`

---

## 9. Pravidlá pre názvy funkcií
- snake_case
- musia byť akčné (sloveso + objekt)
- príklady:
  - `process_event()`
  - `render_note()`
  - `calculate_position()`
  - `update_timeline()`

---

## 10. Pravidlá pre názvy konštánt
- UPPER_CASE
- príklady:
  - `DEFAULT_VELOCITY_COLOR`
  - `MAX_TRACKS = 16`

---

## 11. Záver
Tento dokument definuje oficiálny naming štandard pre Real‑Time MIDI Notation Engine. Je navrhnutý tak, aby podporoval rast projektu, udržiaval profesionálnu architektúru a vytváral nový štandard v MIDI svete.
