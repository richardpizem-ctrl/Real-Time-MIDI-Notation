# 🤝 Contributing to Real-Time MIDI Notation  
### Version 2.0.0 — Stable Edition

Thank you for your interest in contributing to **Real‑Time MIDI Notation (SIRIUS Engine)** —  
the world’s first open‑source real‑time multi‑track Yamaha‑style notation engine.

Your participation helps shape a tool that has never existed before.  
We welcome **testers, developers, musicians, researchers, UI/UX designers, and anyone**  
who wants to help improve the project.

---

# 🌍 Global Testing Appeal (v2.0.0)

Real‑time MIDI behavior varies dramatically across:

- operating systems  
- CPUs and GPUs  
- audio/MIDI drivers  
- hardware MIDI devices  
- latency conditions  
- Yamaha arranger keyboards  
- DAW routing setups  

To reach **professional‑grade stability**, we need **worldwide testing**.

### ✔️ If you study this project, please also test it  
Every test improves accuracy, stability, and cross‑platform compatibility.

### What to test
- MIDI input latency  
- multi‑track behavior  
- rendering performance  
- notation accuracy  
- UI responsiveness  
- Yamaha style compatibility  
- any unexpected behavior  

Please report your results in the **Issues** tab.

---

# 🐞 Reporting Issues

If you find a bug, inconsistency, or unexpected behavior:

1. Go to the **Issues** tab  
2. Create a new issue  
3. Include:
   - OS version  
   - Python version  
   - MIDI device used  
   - steps to reproduce  
   - screenshots or logs (if possible)

Clear reports help us fix problems faster and improve stability across platforms.

---

# 🔧 Submitting Pull Requests

We welcome all improvements — from small fixes to major features.

### Steps:
1. **Fork** the repository  
2. **Create a new branch** for your changes  
3. Make your edits  
4. Submit a **Pull Request** with:
   - a clear description  
   - why the change is needed  
   - screenshots or examples (if relevant)

### PR Guidelines:
- keep code clean and readable  
- follow the existing project structure  
- comment complex logic  
- avoid unnecessary dependencies  
- test your changes before submitting  
- ensure no regressions in:
  - MIDI input  
  - rendering  
  - TimelineUI  
  - TrackManager  
  - playback timing  

---

# 🧩 Architecture Overview (v2.0.0)

### 🔧 Core Engine
- **NotationProcessor** → `core/notation_processor.py`  
- **RhythmAnalyzer** → `rhythm_analyzer.py`  
- **EventBus** → `core/event_bus.py`  
- **DeviceManager** → `device_manager.py`  

### 🎚 Track System
- **TrackSystem** → `core/track_system.py`  
- **TrackManager** → `core/track_manager.py`  

### 🎨 Rendering
- **GraphicNotationRenderer** → `renderer_new/graphic_renderer.py`  
- **PixelLayoutEngine** → `renderer_new/pixel_layout_engine.py`  

### 🖥 UI Layer
- **UIManager** → `ui/ui_manager.py`  
- **CanvasUI** → `ui/canvas_ui.py`  
- **TimelineUI** → `ui/timeline_ui.py`  

---

# 🧭 Contributor Task Levels (Beginner → Advanced)

## 🟦 Beginner‑Friendly Tasks
Perfect for newcomers:
- improve documentation  
- add comments to complex renderer functions  
- fix typos or formatting issues  
- add simple unit tests  
- improve UI labels or text clarity  

## 🟩 Intermediate Tasks
For contributors with some experience:
- improve UI animations  
- optimize scroll/zoom performance  
- add layer toggles (grid, barlines, stems, beams)  
- improve track highlighting  
- refine playhead rendering  

## 🟥 Advanced Tasks
For experienced developers:
- beam caching  
- chord group caching  
- GIF/MP4 export  
- extreme MIDI stress testing  
- performance profiling (CPU/GPU)  
- memory footprint optimization  
- advanced engraving logic  

---

# 💡 Suggesting Features

If you have an idea that could improve the project:

- open an **Issue** labeled *Feature Request*  
- describe the idea clearly  
- explain why it would be useful  
- include examples or references if possible  

We especially welcome ideas related to:

- real‑time rendering  
- Yamaha style compatibility  
- UI improvements  
- performance optimizations  
- advanced harmony analysis  
- export formats (PDF/PNG/MusicXML)  

---

# 🤝 Community Values

We aim to build a community that is:

- respectful  
- collaborative  
- open to ideas  
- focused on quality  
- welcoming to beginners and experts alike  

Everyone is invited to participate.

---

# 📬 Contact

If you want to discuss ideas or need help, feel free to open an issue or contact the maintainer:

📧 **richardpizem@gmail.com**

Thank you for helping shape the future of this project!  
Your contribution — even a single test — makes a real difference.
