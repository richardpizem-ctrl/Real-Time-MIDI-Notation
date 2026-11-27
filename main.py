"""Supported entry point for the recovered SIRIUS MIDI application."""
import argparse
import os
from pathlib import Path

def main(argv=None):
    parser=argparse.ArgumentParser(description='SIRIUS MIDI - recovered source preview')
    parser.add_argument('--demo',action='store_true',help='Feed a simulated two-channel phrase')
    parser.add_argument('--headless',action='store_true',help='Use SDL dummy display for tests')
    parser.add_argument('--frames',type=int,help='Stop after N frames for a startup check')
    parser.add_argument('--input',help='Exact MIDI input name')
    parser.add_argument('--midi',help='Open a MIDI file')
    parser.add_argument('--diagnose',action='store_true',help='Report startup issues without opening a window')
    parser.add_argument('--repair-settings',action='store_true',help='Back up invalid config.json and restore default settings')
    args=parser.parse_args(argv)
    root = Path(__file__).resolve().parent
    from core.diagnostics import diagnose, load_settings, repair_settings
    import json
    if args.repair_settings:
        try:
            print(json.dumps(repair_settings(root),ensure_ascii=False,indent=2))
            return 0
        except (OSError,ValueError) as error:
            print('Obnova nastavení zlyhala: '+str(error))
            return 2
    report = diagnose(root)
    if args.diagnose or not report['ok']:
        print(json.dumps(report,ensure_ascii=False,indent=2))
        if not report['settings_ok']:
            print('Nastavenia možno obnoviť cez OPRAVIT-NASTAVENIA.cmd; pôvodný súbor bude zálohovaný.')
        if not report['ok'] or args.diagnose:
            return 0 if report['ok'] else 2
    if args.frames is not None and args.frames < 1:
        parser.error('--frames must be positive')
    if args.headless:
        os.environ['SDL_VIDEODRIVER']='dummy'
        os.environ['SDL_AUDIODRIVER']='dummy'
    os.environ['PYGAME_HIDE_SUPPORT_PROMPT']='1'
    from ui.application import MidiApplication
    app=MidiApplication(demo=args.demo,midi_file=args.midi,input_name=args.input,headless=args.headless,settings=load_settings(root))
    app.run(max_frames=args.frames)
    return 0

if __name__=='__main__':
    raise SystemExit(main())
