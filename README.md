# 🎵 Real‑Time MIDI Notation
Moderný systém na vizualizáciu MIDI v reálnom čase.  
Interaktívny renderer, farebné akordy, multi‑track spracovanie a profesionálny layout engine.

---

## 🚀 Funkcie

- **Real‑time MIDI Input Engine**  
  Spracovanie MIDI udalostí v reálnom čase s presným timestampingom.

- **MIDI Channel Splitter**  
  Automatické rozdelenie MIDI podľa kanálov (tracks).

- **Notation Rendering Engine**  
  Zobrazenie nôt, taktových čiar, playheadu a rytmických prvkov.

- **Farebné akordy a harmónia**  
  Každý akord má vlastnú farbu (DAW‑style).

- **Multi‑track vizualizácia**  
  Každá stopa môže mať vlastnú farbu, vrstvu a správanie.

- **UI komponenty**  
  - PianoRollUI  
  - StaffUI  
  - NoteVisualizerUI  
  - UIManager (centralizované riadenie UI)

- **Stabilná verzia v1.0.0**  
  Prvá funkčná verzia projektu je dostupná ako release.

---

## 🖼️ Screenshoty / Demo (pridáš neskôr)

> Sem vložíš GIF alebo screenshot, keď budeš mať prvé vizuálne výstupy.  
> Toto je najdôležitejšia časť pre získanie hviezdičiek.

---

## 🧩 Architektúra projektu

### **1. MIDI Pipeline**
- MIDI Input  
- Processor  
- Channel Splitter  
- Event Router  
- Renderer

### **2. Rendering Pipeline**
- Layout Engine (hotový)  
- GraphicNotationRenderer  
- Playhead Line (hotový)  
- Taktové čiary (hotové)  
- Farebné akordy  
- Multi‑track vrstvy

### **3. UI Layer**
- PianoRollUI  
- StaffUI  
- NoteVisualizerUI  
- UIManager (centralizované riadenie)

### **4. Core Modules**
- MidiNoteMapper (hotový)  
- Rhythm Analyzer (základná verzia hotová)  
- StreamHandler  
- EventRouter  

---

## 📦 Inštalácia

```bash
git clone https://github.com/richardpizem-ctrl/Real-Time-MIDI-Notation
cd Real-Time-MIDI-Notation
python run.py
