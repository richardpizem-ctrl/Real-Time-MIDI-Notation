# 📌 Roadmap – Real-Time MIDI Notation

Toto je oficiálna roadmapa projektu Real-Time MIDI Notation. Obsahuje všetky plánované fázy vývoja, zoradené logicky a profesionálne podľa architektúry projektu.

---

## 🟩 FÁZA 1 — Stabilizácia základného engine

### 🔧 1.1 Real‑time MIDI pipeline
- optimalizácia latencie
- stabilné spracovanie MIDI udalostí
- ochrana proti zahlteniu dát

### 🎹 1.2 Device Manager
- spoľahlivá detekcia MIDI zariadení
- automatické prepínanie pri odpojení/pripojení
- fallback režim bez MIDI

### 🎼 1.3 Notation Engine – základ
- jednotné objekty pre noty, bubny, basu a pady
- normalizácia MIDI udalostí
- mapovanie pitch → symbol

---

## 🟩 FÁZA 2 — Layout Engine

### 📏 2.1 Osnova a rozloženie
- vykreslenie osnovy pre melódiu, basu a bicie
- dynamické rozostupy podľa počtu symbolov
- automatické zalamovanie riadkov

### 🧩 2.2 Symbol Placement
- presné pozície nôt
- taktové čiary
- akordové symboly
- bubnové značky

### 🎨 2.3 Farby a štýly
- farby stôp
- farby akordov
- farby rytmických prvkov

---

## 🟩 FÁZA 3 — Renderer (grafická vrstva)

### 🖼️ 3.1 Vykresľovanie symbolov
- noty, stonky, bodky
- ligatúry
- bubnové značky
- akordové symboly

### 🖥️ 3.2 Real‑time aktualizácia
- plynulé prekresľovanie
- zvýraznenie aktuálnej pozície
- animácia prehrávania

### 🧪 3.3 Debug panel
- MIDI udalosti
- analyzovaný rytmus
- aktuálny akord

---

## 🟩 FÁZA 4 — Rhythm Analyzer

### 🥁 4.1 Kvantizácia
- detekcia oneskorených úderov
- normalizácia rytmu

### 🎵 4.2 Pattern Recognition
- rozpoznanie bicích patternov
- rozpoznanie basových fráz

### 🎚️ 4.3 Velocity → vizuálna dynamika
- hrúbka nôt podľa úderu
- intenzita farby

---

## 🟩 FÁZA 5 — UI Components

### 🪟 5.1 Hlavné okno
- canvas
- zoom
- posúvanie timeline

### 🎛️ 5.2 Ovládacie prvky
- výber MIDI zariadenia
- prepínanie stôp
- tempo / metronóm

### 📊 5.3 Debug & Info panely
- aktuálny takt
- BPM
- detekovaný akord

---

## 🟩 FÁZA 6 — Export & Integrácie

### 📄 6.1 Export
- MusicXML
- PDF
- PNG snapshot

### 🎼 6.2 Import
- MIDI súbory
- Yamaha Style Files (voliteľné)

---

## 🟩 FÁZA 7 — Extra funkcie

### 🎹 7.1 Yamaha Arranger Mode
- rozpoznanie štýlov
- zobrazenie PAD stôp
- zobrazenie multi‑padov

### 🎧 7.2 Playback Engine
- prehrávanie MIDI
- synchronizácia s notáciou

### 🧠 7.3 Inteligentná analýza
- predikcia akordov
- rozpoznanie tóniny
- harmonická analýza

---

## 🟩 FÁZA 8 — Preview & Vizualizácia

### 🖼️ 8.1 Auto‑screenshot
- generovanie `preview.png` pri každom spustení

### 🗂️ 8.2 Version Previews
- `preview_001.png`
- `preview_002.png`
- podľa commitov

### 📈 8.3 Dashboard progresu
- % hotového layoutu
- % hotového renderera
- % hotovej MIDI logiky

---

## 🟩 FÁZA 9 — Stabilná verzia 2.0
Kompletný real‑time MIDI notation engine pripravený na používanie.

