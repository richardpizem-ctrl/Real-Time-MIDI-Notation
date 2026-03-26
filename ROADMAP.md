## 📌 Roadmap – Real-Time MIDI Notation  
### (stav projektu po implementácii TrackSystemu, UI, scrollingu)

---

# 🟩 FÁZA 1 — Real‑Time MIDI Engine  
**STAV: HOTOVÉ (100 %)**

### 🎛 1.1 MIDI Input Pipeline  
- realtime MIDI capture **(hotové)**  
- stabilná latencia **(hotové)**  
- EventRouter → TrackSystem → UI pipeline **(hotové)**  

### 🎚 1.2 Stream Handler  
- spracovanie NOTE ON/OFF **(hotové)**  
- preposielanie do UI **(hotové)**  

### 🎼 1.3 Track System (16 stôp)  
- farby stôp **(hotové)**  
- aktívna stopa **(hotové)**  
- routing udalostí podľa tracku **(hotové)**  

---

# 🟩 FÁZA 2 — UI Engine  
**STAV: HOTOVÉ (100 %)**

### 🎹 2.1 PianoRollUI  
- highlight kláves podľa tracku **(hotové)**  
- automatický scrolling **(hotové)**  
- synchronizácia s StaffUI **(hotové)**  

### 🎼 2.2 StaffUI  
- vykreslenie osnovy **(hotové)**  
- vykreslenie nôt podľa MIDI **(hotové)**  
- automatický scrolling **(hotové)**  
- synchronizácia s PianoRollUI **(hotové)**  

### 🎨 2.3 NoteVisualizerUI  
- realtime vizualizácia **(hotové)**  

### 🎛 2.4 Track Selector UI  
- 16 tlačidiel pre stopy **(hotové)**  
- farby stôp **(hotové)**  
- prepojenie s TrackSystem **(hotové)**  

### 🧩 2.5 UIManager  
- centrálne riadenie scrollingu **(hotové)**  
- integrácia všetkých UI vrstiev **(hotové)**  
- BPM vizualizácia **(hotové)**  

---

# 🟧 FÁZA 3 — Renderer  
**STAV: PREBIEHA (30 %) – základný renderer už existuje**

### 🎨 3.1 Notový Renderer  
- vykresľovanie skutočných notových hlavičiek **(čiastočne hotové)**  
- rytmické hodnoty (štvrťová, osminová…) **(čiastočne)**  
- ligatúry / slurs **(nie)**  
- taktové čiary **(nie)**  

### 🔍 3.2 Highlight aktuálnej pozície  
- kurzor prehrávania **(čiastočne)**  

---

# 🟦 FÁZA 4 — Export  
**STAV: 0 %**

- export PNG **(nie)**  
- export PDF **(nie)**  
- export MusicXML **(nie)**  
- export MIDI **(nie)**  

---

# 🟪 FÁZA 5 — Inteligentné funkcie  
**STAV: 20 %**

- základná rytmická analýza **(hotové – základ)**  
- predikcia akordov **(nie)**  
- harmonická analýza **(nie)**  
- Yamaha arranger mode **(nie)**  

---

# 🟫 FÁZA 6 — Preview & Vizualizácia  
**STAV: 0 %**

- auto-screenshot **(nie)**  
- preview.png generátor **(nie)**  

---

# 🟦 FÁZA 7 — KONTROLNÁ & TESTOVACIA ROADMAPA (NOVÁ)  
### 🔍 Cieľ: stabilizácia, testovanie, optimalizácia, príprava na finálny release

## ✔ 7.1 Kódová stabilizácia  
- prejsť všetky moduly (Processor, Renderer, Layout Engine, Rhythm Analyzer)  
- odstrániť duplicity a starý kód  
- zjednotiť dátové štruktúry  
- optimalizovať pipeline MIDI → Processor → Renderer  

## ✔ 7.2 Testovanie  
- testy rytmického analyzátora  
- testy real‑time pipeline  
- testy multi‑track spracovania  
- testy extrémnych BPM  
- testy dlhých skladieb  
- testy rýchlych sekvencií  

## ✔ 7.3 Polishing & UX  
- vylepšenie UI  
- optimalizácia FPS  
- čitateľnosť notácie  
- farebné ladenie akordov  

## ✔ 7.4 Dokumentácia  
- README final  
- architektúra pipeline  
- príklady použitia  
- doplnenie technickej špecifikácie  

## ✔ 7.5 Príprava na Release  
- Issues pre komunitu  
- Discussions  
- licencovanie  
- verzia 1.0.0  
- demo video  

---

# 🟩 FÁZA 8 — Finálny Release  
**STAV: BUDE PO TESTOCH**

- release 1.0.0  
- changelog  
- preview obrázky  
- stabilná verzia projektu  

