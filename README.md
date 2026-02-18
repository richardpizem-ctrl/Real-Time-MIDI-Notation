# Real‑Time MIDI Score Visualizer & Accompaniment Track Notation System

## 1. Introduction
Modern arranger keyboards such as the Yamaha PSR‑SX and Genos series generate rich, multi‑layered accompaniment in real time. While these instruments provide high‑quality musical output, there is currently no software tool capable of capturing and converting all accompaniment tracks into readable musical notation as they are being played. Existing notation programs focus primarily on the performer’s melody and ignore the arranger engine’s internal tracks, which contain valuable musical information such as bass lines, drum patterns, harmonic layers, and orchestral textures.

This project aims to fill that gap by creating a Real‑Time MIDI Score Visualizer & Accompaniment Track Notation System. The software will listen to the keyboard’s MIDI output, separate each accompaniment track by channel, and display it as standard musical notation. Users will be able to select which tracks they want to view, analyze, or export — including bass, drums, chord layers, pads, and melodic phrases.

The goal is to provide musicians, arrangers, teachers, and performers with a tool that transforms arranger keyboard accompaniment into clear, editable, and printable sheet music.

---

## 2. MIDI Input Architecture
The software receives MIDI data via USB‑MIDI or standard MIDI IN.  
Supported messages:
- Note On / Note Off  
- Control Change  
- Program Change  
- Pitch Bend  
- SysEx (optional)

### 2.1 Yamaha Style Engine – MIDI Channel Mapping
| Function | Channel | Description |
|---------|---------|-------------|
| Right1 | 1 | Live melody |
| Right2 | 2 | Additional live voice |
| Left | 3 | Left‑hand voice |
| Bass | 11 | Accompaniment bass |
| Chord1 | 12 | Harmony 1 |
| Chord2 | 13 | Harmony 2 |
| Pad | 14 | Pad / Strings |
| Phrase1 | 15 | Phrase 1 |
| Phrase2 | 16 | Phrase 2 |
| Drums | 10 | Drum track (GM standard) |

---

## 3. Track Selection & Display
Users can choose which accompaniment tracks to display in notation.

Selectable tracks:
- Right1  
- Right2  
- Left  
- Bass  
- Drums  
- Chord1  
- Chord2  
- Pad  
- Phrase1  
- Phrase2  

Each track can be enabled, disabled, color‑coded, or displayed alone.

---

## 4. Real‑Time Notation Engine
Features:
- real‑time note rendering  
- scrolling score view  
- adjustable quantization  
- playback and analysis mode  

Quantization options:
- 1/4  
- 1/8  
- 1/16  
- 1/32  
- swing quantization  

---

## 5. Drum Notation System
The drum track (channel 10) is processed according to the GM Drum Map.

The software:
- identifies individual drum hits  
- maps them to correct drum notation symbols  
- displays them in a percussion staff  
- allows exporting a drum part  

---

## 6. Bass Notation
The bass track (channel 11):
- is displayed in bass clef  
- can be color‑highlighted  
- can be exported as a separate bass part  

---

## 7. Accompaniment Track Notation
Tracks Chord1, Chord2, Pad, Phrase1, and Phrase2 each contain their own MIDI notes.

The software must:
- display each track in its own staff  
- allow combining multiple tracks  
- color‑code each track  
- export each track as an individual part  

---

## 8. Export Options
Supported export formats:
- PDF sheet music  
- individual instrument parts  
- full band score  
- MIDI files  
- MusicXML  

---

## 9. User Interface Structure
The UI includes:
- main score display  
- track selection panel  
- transport controls  
- quantization settings  
- export panel  
- color legend  
- zoom controls  

---

## 10. Target Users
This software is intended for:
- musicians  
- arrangers  
- teachers  
- studio players  
- Yamaha keyboard users  

---

## 11. Key Benefits
- instant notation of accompaniment  
- full band arrangement creation  
- analysis of Yamaha style engine tracks  
- drum and bass transcription  
- real‑time visualization  

---

## Conclusion
This document presents a complete technical specification for a real‑time MIDI notation system capable of displaying and exporting all accompaniment tracks from arranger keyboards.
