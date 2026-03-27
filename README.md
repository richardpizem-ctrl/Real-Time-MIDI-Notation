# Real‑Time MIDI Notation

Reálny‑časový systém na vizualizáciu MIDI dát určený pre moderných hudobníkov, najmä hráčov na aranžérskych klávesoch. Projekt umožňuje sledovať, čo nástroj hrá, aj bez znalosti tradičného notového zápisu. Cieľom je vytvoriť moderný, rýchly a presný notation engine, ktorý dokáže v reálnom čase zobrazovať hudobné informácie z MIDI vstupu.

## Ciele projektu
- Reálne‑časové spracovanie MIDI dát cez pipeline Processor → Renderer
- Vizualizácia viacerých stôp (multi‑track) s možnosťou rozšírenia
- Farebné zobrazenie harmónie a akordových štruktúr
- Automatická rytmická analýza podľa BPM a timestampov
- Zobrazenie doprovodných stôp (bas, bicie, pady, akordy)
- Moderný layout engine pre čistý, čitateľný zápis
- Dlhodobý cieľ: plnohodnotný notation engine pre arranger keyboards a živé hranie

## Funkcie
- Pipeline MIDI → Processor → Renderer s nízkou latenciou
- Color harmony mapping pre akordy a harmóniu
- Multi‑track architektúra pripravená na rozšírenie
- Hotový layout engine pre presné rozmiestnenie prvkov
- DAW‑style playhead line pre vizuálne sledovanie prehrávania
- Measure lines v rendereri pre orientáciu v takte
- Funkčný Rhythm Analyzer pracujúci s timestampmi a BPM
- UI komponenty: PianoRollUI, StaffUI, NoteVisualizerUI, ui_manager

## Inštalácia
1. Klonovanie:
git clone https://github.com/richardpizem-ctrl/Real-Time-MIDI-Notation.git
cd Real-Time-MIDI-Notation

2. Závislosti (vyžaduje sa Python 3.10+):
pip install -r requirements.txt

3. Spustenie:
python run.py

4. Voliteľné testy:
python test_chords.py
python test_no_midi.py

## Štruktúra projektu
- core/ – základná logika systému
- midi_input/ – spracovanie MIDI vstupu
- notation_engine/ – interpretácia MIDI pre notáciu
- renderer/ – reálny‑časový renderer
- ui/ – hlavné UI komponenty
- ui_components/ – vizuálne prvky
- real_time_processing/ – spracovacia pipeline
- tests/ – testovacie skripty

## Roadmap
- Dokončenie multi‑track renderingu
- Vylepšenie farebného engine pre harmóniu
- Export do MusicXML / PDF
- Pokročilá rytmická analýza
- Interaktívne UI prvky
- Inteligentné rozpoznávanie akordov
- Optimalizácia výkonu pre živé hranie

## Autor
Richard Pizem

## Licencia
MIT License
