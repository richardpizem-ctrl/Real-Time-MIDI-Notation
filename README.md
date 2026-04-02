Real-Time MIDI Notation je nástroj na vizualizáciu MIDI dát v reálnom čase, ktorý prevádza živé MIDI udalosti na prehľadnú grafickú notáciu. Projekt je navrhnutý ako modulárny, rozšíriteľný a pripravený na profesionálne použitie aj ďalší vývoj.

## Architecture Overview (Architektúra)

Projekt Real-Time MIDI Notation spracúva MIDI dáta v reálnom čase cez štyri hlavné vrstvy:
1. MIDI Input (MIDI vstup) – prijíma MIDI eventy zo zariadenia alebo virtuálneho portu.
2. Processor (Procesor) – analyzuje rytmus, timestampy, velocity a mapuje noty.
3. GraphicNotationRenderer (Grafický renderer) – prevádza MIDI eventy na grafické objekty.
4. UI Layer (UI vrstva) – zobrazuje noty, taktové čiary a playhead v reálnom čase.

## How It Works (Ako to funguje)

- MIDI eventy sa načítavajú v reálnom čase.
- Processor analyzuje rytmus, BPM a dĺžky tónov.
- Renderer generuje grafické prvky pre každú notu.
- UI vrstva vykresľuje noty, taktové čiary a playhead.
- TrackManager spracúva až 16 stôp podľa Yamaha štandardu.

## Roadmap (Plán vývoja)

- 1.1 – doplnená dokumentácia + stabilizácia
- 1.2 – menšie UI vylepšenia
- 1.3 – export do PNG/SVG
- 2.0 – advanced layout engine (pokročilý layout)

