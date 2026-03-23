## 📌 Roadmap – Real-Time MIDI Notation
### (s označením HOTOVÉ / ČIASTOČNE / NIE)

---

## 🟩 FÁZA 1 — Stabilizácia základného engine  
**STAV: HOTOVÉ (100 %)**

### 🔧 1.1 Real‑time MIDI pipeline - optimalizácia latencie  
- stabilné spracovanie MIDI udalostí **(hotové)**  
- ochrana proti zahlteniu dát **(hotové)**  

### 🎹 1.2 Device Manager  
- spoľahlivá detekcia MIDI zariadení **(hotové)**  
- automatické prepínanie pri odpojení/pripojení **(hotové)**  
- fallback režim bez MIDI **(hotové)**  

### 🎼 1.3 Notation Engine – základ  
- jednotné objekty pre noty, bubny, basu a pady **(hotové)**  
- normalizácia MIDI udalostí **(hotové)**  
- mapovanie pitch → symbol **(hotové)**  

---

## 🟩 FÁZA 2 — Layout Engine  
**STAV: 95 %**

### 📏 2.1 Osnova a rozloženie  
- vykreslenie osnovy pre melódiu, basu a bicie **(hotové)**  
- dynamické rozostupy podľa počtu symbolov **(hotové)**  
- automatické zalamovanie riadkov **(hotové)**  
→ doplnené: **No justify on short lines**, **Minimum bars for justify**

### 🧩 2.2 Symbol Placement  
- presné pozície nôt **(hotové)**  
- taktové čiary **(hotové)**  
- akordové symboly **(hotové)**  
- bubnové značky **(hotové)** ← 🔥 OPRAVENÉ

### 🎨 2.3 Farby a štýly  
- farby stôp **(hotové)**  
- farby akordov **(hotové)**  
- farby rytmických prvkov **(hotové)**  

### 🧠 2.4 Smart Layout  
- Smart Justify 1.0 **(hotové)**  
- Smart Justify 2.0 (rytmické váhy) **(hotové)**  
- Center last line **(hotové)**  

---

## 🟩 FÁZA 3 — Renderer  
**STAV: 90 %**

### 🎨 3.1 Základné vykresľovanie  
- noty, bubny, bas, pady **(hotové)**  
- farby podľa stopy **(hotové)**  
- vrstvenie bicích **(hotové)**  

### 🔍 3.2 Zvýraznenie aktuálnej pozície  
- realtime highlight **(čiastočne)**  

### 🔗 3.3 Ligatúry (slurs)  
- vykresľovanie oblúkov **(nie)**  

### 🔎 3.4 Zoom  
- plynulé zväčšovanie/zmenšovanie **(HOTOVÉ)**  

### ↔ 3.5 Posúvanie timeline  
- automatický scroll **(hotové)**  
- ručné posúvanie myšou **(HOTOVÉ)**  
- posúvanie kolieskom **(HOTOVÉ)**  
- posúvanie klávesmi **(HOTOVÉ)**  

---

## 🟧 FÁZA 4 — UI Components  
**STAV: 60 %**

### 🖱 4.1 Ovládanie  
- zoom slider **(nie)**  
- timeline scrollbar **(nie)**  
- prepínanie stôp **(čiastočne)**  

### 🎛 4.2 MIDI zariadenia  
- výber MIDI vstupu **(čiastočne)**  

---

## 🟦 FÁZA 5 — Export  
**STAV: 0 %**

- PNG snapshot **(nie)**  
- PDF export **(nie)**  
- MusicXML export **(nie)**  
- MIDI import **(nie)**  

---

## 🟪 FÁZA 6 — Inteligentné funkcie  
**STAV: 40 %**

- predikcia akordov **(čiastočne)**  
- harmonická analýza **(čiastočne)**  
- Yamaha arranger mode **(nie)**  

---

## 🟫 FÁZA 7 — Preview & Vizualizácia  
**STAV: 0 %**

- auto-screenshot **(nie)**  
- preview.png **(nie)**  
