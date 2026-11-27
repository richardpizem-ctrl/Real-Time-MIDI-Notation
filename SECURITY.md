# Security and recovery scope

This local MIDI preview opens user-selected devices and MIDI files. It is not a security-audited
sandbox. Review logs and recordings before sharing them in issues.

## Diagnostics

Startup checks inspect required Python libraries, critical source syntax and `config.json`.
They do not install packages, access network services, execute repair shell commands or alter
source files. Missing libraries are handled by an explicit preparation step.

## Settings recovery

`OPRAVIT-NASTAVENIA.cmd` / `python main.py --repair-settings` can restore missing/invalid settings.
Valid custom settings are not reset. Before replacement, the exact original bytes are saved
under `recovery-backups`. A temporary validated file is atomically replaced; a failed replacement
leaves the original in place. Symlinked settings/backups are refused. Concurrent configuration
changes abort replacement. Existing recordings and source files are outside recovery scope.

This is not autonomous code repair, an antivirus function, a general integrity guarantee or a
claim that every retained legacy module is secure. A real device/output test is still required.
Report reproducible concerns without publishing secrets or private recordings.
