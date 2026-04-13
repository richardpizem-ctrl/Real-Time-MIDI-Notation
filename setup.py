from setuptools import setup, find_packages

# Načítanie README.md ako long_description
with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="real-time-midi-notation",
    version="0.9.0",
    packages=find_packages(),
    install_requires=[
        "pygame",
        "mido",
        "python-rtmidi",
    ],
    author="Richard",
    author_email="",
    description="High-performance real-time 16-track MIDI notation engine for Python.",
    long_description=long_description,
    long_description_content_type="text/markdown",

    url="https://github.com/richardpizem-ctrl/Real-Time-MIDI-Notation",

    classifiers=[
        # Jazyk
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",

        # Licencia (ak máš MIT v repo)
        "License :: OSI Approved :: MIT License",

        # Platforma
        "Operating System :: OS Independent",

        # Cieľové publikum
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",

        # Témy
        "Topic :: Multimedia :: Sound/Audio :: MIDI",
        "Topic :: Multimedia :: Sound/Audio :: Sound Synthesis",
        "Topic :: Scientific/Engineering :: Visualization",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Education",

        # Real-time
        "Topic :: System :: Real-Time",
    ],

    python_requires=">=3.10",
)
