# Recovery roadmap

## Current PR

- Repair the supported entry point, MIDI parser/queue/model, UI and timed MIDI I/O.
- Unify compatibility launchers and add repeatable tests and read-only CI checks.
- Add startup diagnostics and explicit, backed-up recovery of invalid settings.
- Keep the PR draft until CI and real hardware/manual acceptance are reviewed.

## Before a public recovery release

- [ ] Connect a physical MIDI keyboard and verify all intended channels.
- [ ] Verify sustain/retrigger and reconnect behavior with the actual driver.
- [ ] Verify actual external MIDI sound output, mute, pause and note cleanup.
- [ ] Complete manual device selection, file import/export and close/restart checks.
- [ ] Review Windows/Linux and Python 3.10/3.12 CI results separately from local tests.

## Later proposals, not delivered features

- Consolidate or archive unused engraving/editing experiments after evaluating each one.
- Develop a BETA music-inspector bridge with reference-note/rhythm comparison.
- Add audio pitch/level analysis separately; do not infer sound from MIDI alone.
- Consider broader recovery only with trusted baselines, scoped permissions, backups,
  validation and a rollback test. Autonomous rewriting of broken source is not part of this PR.

No delivery dates or hardware compatibility guarantees are promised.
