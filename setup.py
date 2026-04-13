python
from setuptools import setup, find_packages

setup(
    name="real-time-midi-notation",
    version="0.9.0",
    packages=find_packages(),
    install_requires=[
        "pygame",
        "mido",
        "python-rtmidi",  # alebo iné knižnice, ktoré reálne importuješ
    ],
    author="Richard",
    description="High-performance real-time 16-track MIDI notation engine",
    url="https://github.com",
)
Kód používajte opatrne.

