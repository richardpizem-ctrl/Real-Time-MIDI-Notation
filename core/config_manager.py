"""Settings, without circular application imports."""
import json
from pathlib import Path
from .diagnostics import DEFAULT_SETTINGS, validate_settings
class ConfigManager:
    DEFAULTS = DEFAULT_SETTINGS
    def __init__(self, path=None):
        self.path = Path(path) if path else None
        self.data = dict(self.DEFAULTS)
        if self.path and self.path.exists():
            data = json.loads(self.path.read_text(encoding='utf-8'))
            if not isinstance(data, dict):
                raise ValueError('Settings must be an object')
            self.data.update(validate_settings(data))
    def get(self, key, default=None):
        return self.data.get(key, default)
    def set(self, key, value):
        self.data[key] = value
    def save(self):
        if self.path:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self.path.write_text(json.dumps(self.data, indent=2), encoding='utf-8')
