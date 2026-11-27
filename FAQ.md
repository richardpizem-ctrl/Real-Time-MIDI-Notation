# FAQ — recovery preview

**Which file starts the application?** Use `SPUSTIT-MIDI.cmd` after preparation. Python entry
points all lead to the same implementation; see [LAUNCHERS.md](LAUNCHERS.md).

**Can I test without a keyboard?** Yes, click DEMO. This tests simulated input, not hardware.

**Why is there no sound?** There is no built-in synthesizer. Select an external MIDI output;
otherwise playback is visual.

**Are velocity and loudness the same?** No. Velocity describes a MIDI performance parameter,
not measured audio level or sound pressure.

**Can it judge out-of-tune singing?** No audio input analysis has been implemented.

**Does self-repair fix code?** No. Diagnostics report startup issues; explicit recovery only
backs up invalid settings and restores defaults. Valid settings and recordings are retained.

**Is the whole historical source tree verified?** No. The supported path is tested; earlier
unconnected experiments are labelled as such. Real hardware and manual UI acceptance remain.
