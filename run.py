"""Compatibility launcher: both documented commands use the same application."""
from main import main
if __name__ == '__main__':
    raise SystemExit(main())
