# =========================================================
# pyproject.toml — Real-Time MIDI Notation v2.0.0
# Stabilná build konfigurácia pre Python 3.10+
# =========================================================

[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "real-time-midi-notation"
version = "2.0.0"
description = "Real-time multi-track MIDI notation engine with Yamaha 16-track support, advanced rendering pipeline, TimelineUI v2, and real-time processing core."
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
    "live-notation",
    "timeline-ui",
    "real-time-processing"
]

dependencies = [
    "pygame>=2.1.0",
    "mido>=1.3.0",
    "python-rtmidi>=1.5.0"
]

[project.urls]
Homepage = "https://github.com/richardpizem-ctrl/Real-Time-MIDI-Notation"
Repository = "https://github.com/richardpizem-ctrl/Real-Time-MIDI-Notation"
Issues = "https://github.com/richardpizem-ctrl/Real-Time-MIDI-Notation/issues"
Documentation = "https://github.com/richardpizem-ctrl/Real-Time-MIDI-Notation/tree/main/docs"
