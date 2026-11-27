# SIRIUS MIDI — current project status

The recovery PR establishes one tested MIDI-to-UI/file pipeline from a previously disconnected
source tree. See [README](README.md) for the supported feature set, [repair scope](REPAIR_STATUS.md)
for evidence, and [launcher map](LAUNCHERS.md) for the correct startup route.

The application is a local Python/Pygame MIDI recorder and basic notation/keyboard preview.
It supports 16 channels, simulated or physical MIDI inputs, timed MIDI file I/O and optional
external MIDI playback. Physical input and output still need acceptance with real hardware.

This work does not establish complete engraving, audio intonation/loudness inspection,
world-unique capabilities, universal instrument compatibility or BETA integration.
Those are separate future work, requiring their own implementation and tests.
