# 🎼 Real‑Time MIDI Notation (Reálny‑čas MIDI notácia)

Moderný systém na vizualizáciu MIDI dát v reálnom čase, určený najmä pre hráčov na aranžérskych klávesoch (arranger keyboards). Projekt pomáha hudobníkom pochopiť, čo ich nástroj hrá — aj keď nečítajú tradičný notový zápis.

---

## 🎯 Vízia projektu (Project Vision)

Cieľom je vytvoriť inteligentný, rýchly a prehľadný systém, ktorý dokáže:

- Reálne‑časovo vykresľovať viacero stôp (multi‑track rendering)
- Zobrazovať harmóniu farbami (color‑coded harmony)
- Interpretovať rytmus podľa timestampov a BPM (automatic rhythm interpretation)
- Vizualizovať doprovodné stopy ako bas, bicie, pady, akordy (accompaniment tracks)
- Exportovať dáta do MusicXML / PDF
- Pomôcť začiatočníkom pochopiť, čo ich keyboard hrá

Dlhodobým cieľom je kompletný notation engine pre moderné aranžérske klávesy.

---

## 🚀 Funkcie (Features)

- Reálny čas MIDI → Processor → Renderer pipeline
- Farebné akordy a harmónia (color harmony mapping)
- Podpora viacerých stôp (multi‑track architecture)
- Hotový layout engine (layout engine)
- Playhead line s DAW farbou (DAW‑style playhead)
- Taktové čiary v rendereri (measure lines)
- Základný funkčný Rhythm Analyzer (rhythm analyzer)
- UI komponenty: PianoRollUI, StaffUI, NoteVisualizerUI, ui_manager

---

## 🛠️ Inštalácia (Installation)

### 1. Klonovanie repozitára (Clone the repository)
```bash
git clone https://github.com/richardpizem-ctrl/Real-Time-MIDI-Notation.git
cd Real-Time-MIDI-Notation
