[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "real-time-midi-notation"
version = "1.3.0"
description = "Real-time multi-track MIDI notation engine with Yamaha 16-track support, advanced rendering, and finalized TimelineUI architecture."
readme = "README.md"
requires-python = ">=3.10"
license = { text = "MIT" }

authors = [
    { name = "Richard Pizem", email = "" }
]

keywords = [
    "midi",
    "real-time",
    "real-time-midi",
    "midi-notation",
    "music-notation",
    "visualization",
    "python",
    "pygame",
    "yamaha",
    "multi-track",
    "music-technology",
    "digital-audio",
    "midi-visualizer",
    "notation-engine",
    "live-notation"
]

dependencies = [
    "pygame",
    "mido",
    "python-rtmidi"
]

[project.urls]
Homepage = "https://github.com/richardpizem-ctrl/Real-Time-MIDI-Notation"
Repository = "https://github.com/richardpizem-ctrl/Real-Time-MIDI-Notation"
Issues = "https://github.com/richardpizem-ctrl/Real-Time-MIDI-Notation/issues"
Documentation = "https://github.com/richardpizem-ctrl/Real-Time-MIDI-Notation/tree/main/docs"
