# 🎵 Real‑Time MIDI Notation
Moderný systém na vizualizáciu MIDI v reálnom čase pre klávesy Yamaha a akékoľvek MIDI zariadenia.  
Poskytuje interaktívny renderer, farebné akordy, multi‑track spracovanie a profesionálny layout engine.

Tento projekt je navrhnutý ako **rýchly, presný a rozšíriteľný nástroj** na real‑time MIDI notáciu v Pythone.

---

## 🚀 Funkcie

- **Real‑Time MIDI Input Engine**  
  Spracovanie MIDI udalostí v reálnom čase s presným timestampingom.

- **MIDI Channel Splitter**  
  Automatické rozdelenie MIDI podľa kanálov (tracks) – ideálne pre Yamaha arranger štýly.

- **Notation Rendering Engine**  
  Zobrazenie nôt, taktových čiar, playheadu, rytmických prvkov a vizuálnych vrstiev.

- **Farebné akordy a harmónia**  
  Každý akord má vlastnú farbu (DAW‑style).  
  Podpora real‑time detekcie harmónie.

- **Multi‑track vizualizácia**  
  Každá stopa má vlastnú farbu, vrstvu a správanie.  
  Podpora až 16 MIDI kanálov (Yamaha štandard).

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
> Google miluje obrázky – výrazne to zlepší SEO a viditeľnosť projektu.

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
```

---

## 📚 Prečo tento projekt existuje?

Real‑time MIDI notácia je v open‑source svete **takmer neexistujúca**.  
Tento projekt vznikol ako odpoveď na potrebu:

- rýchlej vizualizácie MIDI v reálnom čase  
- podpory pre Yamaha arranger štýly  
- farebnej harmónie a akordov  
- multi‑track spracovania  
- profesionálneho layoutu podobného DAW softvéru  

Cieľom je vytvoriť **moderný, rozšíriteľný a praktický nástroj**, ktorý môže používať každý hudobník alebo vývojár.

---

## 🔧 Plánované funkcie (ROADMAP)

- Export PDF / PNG  
- Pokročilá detekcia akordov  
- Viacvrstvová harmónia  
- Pokročilé UI panely  
- Integrácia s externými MIDI zariadeniami  
- Real‑time vizualizácia rytmických patternov  

---

## 📝 Licencia

MIT License – voľné použitie pre komerčné aj nekomerčné projekty.

