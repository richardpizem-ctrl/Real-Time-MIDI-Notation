🚀 v1.2.0 — TimelineUI Refactor & UI Stabilization (Released)
🎯 TimelineUI — Full Professional Refactor
Kompletný refactor TimelineUI pre verziu 1.2.0

Zjednotená štruktúra, sekcie a interná logika

Prečistené kresliace funkcie (ruler, loop, markers, playhead)

Stabilizované marker interactions (drag, rename, color, type)

Stabilizované loop region správanie

Vylepšené výpočty pre marker rect, loop rect, handle rect

Zjednotený event handler, odstránené duplicity

Príprava na PixelLayoutEngine 2.0

Žiadne breaking changes

🎚 Selection Pipeline
Plná kompatibilita s TimelineUI 1.2.0

Stabilné správanie pri DELETE, MOVE, TRANSPOSE, VELOCITY, STRETCH

Zjednotený spôsob získavania selected indices

Žiadne zmeny API

🖥 Renderer & Layout Engine
Stabilné prepojenie s TimelineController

Vylepšené správanie pri playhead seek

Žiadne zmeny v rendereri, len stabilizácia interakcií

Pripravené na budúce rozšírenia (1.3.0 / 2.0.0)

🧹 Codebase Cleanup
Prečistené komentáre a staré fragmenty

Zjednotený štýl naprieč TimelineUI

Odstránené duplicity v event logike

Zjednotená štruktúra kresliacich a výpočtových metód

📘 Documentation
Aktualizovaný CHANGELOG

Aktualizované release notes

Aktualizované interné architektonické poznámky

🚀 v1.1.0 — Timeline Selection & Phase‑4 Stabilization (Released)
(pôvodný obsah ponechaný nižšie pre historickú konzistenciu)

🎯 TimelineUI — Phase 4 Complete
Fully cleaned and unified codebase

Integrated Selection Actions (delete, move, transpose, velocity, stretch)

Added safe retrieval of selected note indices

Improved marker handling (drag, rename, color, type)

Improved loop region logic

Improved playhead seeking

Stabilized scroll/zoom bars

Removed duplicate logic and legacy fragments

🎚 Selection Pipeline
Added new module: selection_actions.py

Supports:

deleting selected notes

horizontal movement

transposition

velocity adjustments

stretching/compressing durations

Fully integrated into TimelineUI

Renderer compatibility ensured

🖥 Renderer & Layout Engine
Confirmed compatibility with selection pipeline

Stable integration with TimelineController

No breaking changes

Improved refresh behavior

🧹 Codebase Cleanup
Removed unused imports

Removed legacy timeline code

Unified event handling

Improved internal consistency across UI modules

📘 Documentation
Updated CHANGELOG

Updated release notes

Updated internal architecture notes

🚀 v1.0.0 — Core Engine Complete (Released)
(ponechané bezo zmeny)

🔮 Planned for v1.3.0+
Selection box (drag rectangle)

Multi-note drag & resize

Note editing UI

Piano roll editor (new module)

Advanced selection tools

Improved timeline visuals

🔮 Planned for v2.0+
Multi‑voice notation

Polyphony

Advanced beams

Articulations

Dynamics

Engraving engine improvements

🔮 Planned for v3.0+
MuseScore / LilyPond‑level engraving

Full notation engine

Advanced layout intelligence

🎉 End of Changelog
