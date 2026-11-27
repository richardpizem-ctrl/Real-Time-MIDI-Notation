"""Compatibility demo launcher. Uses the same verified application as main.py."""
import sys
from main import main as application_main

def main(argv=None):
    args = sys.argv[1:] if argv is None else list(argv)
    return application_main(['--demo', *args])

if __name__ == '__main__':
    raise SystemExit(main())
