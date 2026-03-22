## 📌 Roadmap – Real-Time MIDI Notation  
### (s označením HOTOVÉ / ČIASTOČNE / NIE)

---

## 🟩 FÁZA 1 — Stabilizácia základného engine  
**STAV: HOTOVÉ (100 %)**

### 🔧 1.1 Real‑time MIDI pipeline  
- optimalizácia latencie **(hotové)**  
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
- bubnové značky **(čiastočne)**  

### 🎨 2.3 Farby a štýly  
- farby stôp **(hotové)**  
- farby akordov **(hotové)**  
- farby rytmických prvkov **(hotové)**  

### 🧠 2.4 Smart Layout  
- Smart Justify 1.0 **(hotové)**  
- Smart Justify 2.0 (rytmické váhy) **(hotové)**  
- Center last line **(hotové)**  
- Debug vizualizácia spacingu **(hotové)**  

---

## 🟩 FÁZA 3 — Renderer (grafická vrstva)  
**STAV: 80 %**

### 🖼️ 3.1 Vykresľovanie symbolov  
- noty, stonky, bodky **(hotové)**  
- ligatúry **(nie)**  
- bubnové značky **(čiastočne)**  
- akordové symboly **(hotové)**  

### 🖥️ 3.2 Real‑time aktualizácia  
- plynulé prekresľovanie **(hotové)**  
- zvýraznenie aktuálnej pozície **(čiastočne)**  
- animácia prehrávania **(nie)**  

### 🧪 3.3 Debug panel  
- MIDI udalosti **(hotové)**  
- analyzovaný rytmus **(hotové)**  
- aktuálny akord **(hotové)**  

---

## 🟩 FÁZA 4 — Rhythm Analyzer  
**STAV: 100 %**

### 🥁 4.1 Kvantizácia  
- detekcia oneskorených úderov **(hotové)**  
- normalizácia rytmu **(hotové)**  

### 🎵 4.2 Pattern Recognition  
- rozpoznanie bicích patternov **(hotové)**  
- rozpoznanie basových fráz **(hotové)**  

### 🎚️ 4.3 Velocity → vizuálna dynamika  
- hrúbka nôt podľa úderu **(hotové)**  
- intenzita farby **(hotové)**  

### 🧠 4.4 Pokročilá analýza  
- swing / shuffle detection **(hotové)**  
- microtiming analyzer **(hotové)**  
- downbeat detection **(hotové)**  
- groove classifier **(hotové)**  

---

## 🟩 FÁZA 5 — UI Components  
**STAV: 60 %**

### 🪟 5.1 Hlavné okno  
- canvas **(hotové)**  
- zoom **(čiastočne)**  
- posúvanie timeline **(čiastočne)**  

### 🎛️ 5.2 Ovládacie prvky  
- výber MIDI zariadenia **(čiastočne)**  
- prepínanie stôp **(čiastočne)**  
- tempo / metronóm **(nie)**  

### 📊 5.3 Debug & Info panely  
- aktuálny takt **(hotové)**  
- BPM **(hotové)**  
- detekovaný akord **(hotové)**  

---

## 🟩 FÁZA 6 — Export & Integrácie  
**STAV: 0 %**

### 📄 6.1 Export  
- MusicXML **(nie)**  
- PDF **(nie)**  
- PNG snapshot **(nie)**  

### 🎼 6.2 Import  
- MIDI súbory **(nie)**  
- Yamaha Style Files **(nie)**  

---

## 🟩 FÁZA 7 — Extra funkcie  
**STAV: 40 %**

### 🎹 7.1 Yamaha Arranger Mode  
- rozpoznanie štýlov **(nie)**  
- zobrazenie PAD stôp **(nie)**  
- zobrazenie multi‑padov **(nie)**  

### 🎧 7.2 Playback Engine  
- prehrávanie MIDI **(nie)**  
- synchronizácia s notáciou **(nie)**  

### 🧠 7.3 Inteligentná analýza  
- predikcia akordov **(čiastočne)**  
- rozpoznanie tóniny **(hotové)**  
- harmonická analýza **(nie)**  

---

## 🟩 FÁZA 8 — Preview & Vizualizácia  
**STAV: 0 %**

### 🖼️ 8.1 Auto‑screenshot  
- generovanie `preview.png` **(nie)**  

### 🗂️ 8.2 Version Previews  
- `preview_001.png` **(nie)**  
- `preview_002.png` **(nie)**  

### 📈 8.3 Dashboard progresu  
- % hotového layoutu **(nie)**  
- % hotového renderera **(nie)**  
- % hotovej MIDI logiky **(nie)**  

---

## 🟩 FÁZA 9 — Stabilná verzia 2.0  
**STAV: čaká**

- kompletný engine  
- finalizácia roadmapy  
- release 2.0  

---

### 🔥 CELKOVÝ PROGRES: **70 %**
