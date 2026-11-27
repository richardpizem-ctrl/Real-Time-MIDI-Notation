"""Compatibility window and launcher; no separate, disconnected application loop."""
from pathlib import Path
import os
import sys
os.environ.setdefault('PYGAME_HIDE_SUPPORT_PROMPT','1')
if __package__ in (None, ''):
    sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from ui.application import MidiApplication

class UIWindow(MidiApplication):
    pass

if __name__ == '__main__':
    from main import main
    raise SystemExit(main())
