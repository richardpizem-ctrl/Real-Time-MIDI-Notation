# Real-Time MIDI Notation

Real-Time MIDI Notation je nástroj na vizualizáciu MIDI dát v reálnom čase, ktorý prevádza živé MIDI udalosti na prehľadnú grafickú notáciu.  
Projekt je navrhnutý ako modulárny, rozšíriteľný a pripravený na profesionálne použitie aj ďalší vývoj.

---

## Architecture Overview (Architektúra)

Projekt Real-Time MIDI Notation spracúva MIDI dáta v reálnom čase cez štyri hlavné vrstvy:

1. **MIDI Input (MIDI vstup)**  
   Prijíma MIDI eventy zo zariadenia alebo virtuálneho portu.

2. **Processor (Procesor)**  
   Analyzuje rytmus, timestampy, velocity, BPM, dĺžky tónov a mapuje noty do jednotného formátu.

3. **GraphicNotationRenderer (Grafický renderer)**  
   Prevádza MIDI eventy na grafické objekty, vykresľuje noty, taktové čiary, grid, playhead a podporuje 16 stôp podľa Yamaha štandardu.

4. **UI Layer (UI vrstva)**  
   Zobrazuje noty, taktové čiary, playhead, track activity a ďalšie vizuálne prvky v reálnom čase.

---

## How It Works (Ako to funguje)

- MIDI eventy sa načítavajú v reálnom čase.
- Processor analyzuje rytmus, BPM, velocity a dĺžky tónov.
- Renderer generuje grafické prvky pre každú notu (vrátane velocity shading, stems, beams, chord grouping).
- UI vrstva vykresľuje noty, taktové čiary, grid, playhead a track activity.
- TrackManager spracúva až **16 stôp** podľa Yamaha štandardu a riadi viditeľnosť, hlasitosť a aktivitu stôp.

---

## Renderer Features (Funkcie renderera)

### 🎼 GraphicNotationRenderer
- Real-time vykresľovanie nôt
- Velocity shading (farba + veľkosť podľa úderu)
- Chord grouping + ligatúry
- Beam detection (8th/16th grouping)
- Premium stems (dynamická dĺžka podľa výšky tónu)
- Taktové čiary, grid, timeline ruler
- Playhead v reálnom čase
- Podpora 16 stôp (Yamaha štandard)
- Track activity meter
- Staff caching pre vysoký výkon
- Zoom, scroll, čas → X a pitch → Y layout engine

### 📝 NotationRenderer (textový renderer)
- Textová vizualizácia MIDI udalostí
- Podpora bubnových značiek
- Layer offset pre bubny
- Timestamp pri každom výpise
- Filter() pre selektívny výpis
- Clear() pre reset bufferu
- Bezpečný fallback ak pygame nie je dostupný

---

## Modules (Moduly)

- **midi_input/** – MIDI listener, event parsing  
- **processor/** – mapovanie nôt, rytmická analýza, timestampy  
- **renderer/** – grafický renderer + textový renderer  
- **ui/** – UI manažér, track switcher, realtime zobrazenie  
- **core/** – event bus, device manager, systémové komponenty  
- **tests/** – testy pre MIDI, rytmus a renderer  

---

## Roadmap (Plán vývoja)

- **1.1** – doplnená dokumentácia + stabilizácia  
- **1.2** – menšie UI vylepšenia (Track Switcher, activity meter)  
- **1.3** – export do PNG/SVG  
- **2.0** – advanced layout engine (pokročilý layout)  
- **2.1** – multi-voice notation + polyfónia  
- **2.2** – MIDI file import/export  
- **3.0** – profesionálny notation engine (úroveň MuseScore/LilyPond)

---

## Status

Projekt je aktívne vyvíjaný a postupne smeruje k profesionálnemu real-time notation enginu.

