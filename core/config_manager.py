import json
import os
from .logger import Logger


class ConfigManager:
    """
    Stabilný konfigurák:
    - bezpečné načítanie JSON
    - bezpečné ukladanie (atomic write)
    - fallback pri chybných súboroch
    - validácia typov
    - reset na default
    """

    def __init__(self, config_file="config.json", defaults=None):
        self.config_file = config_file
        self.defaults = defaults or {}
        self.config = {}

        self._ensure_file_exists()
        self.load()

    # ---------------------------------------------------------
    # INTERNAL: CREATE FILE IF MISSING
    # ---------------------------------------------------------
    def _ensure_file_exists(self):
        """Ak config neexistuje, vytvorí prázdny JSON súbor."""
        if not os.path.exists(self.config_file):
            try:
                with open(self.config_file, "w", encoding="utf-8") as f:
                    json.dump(self.defaults, f, indent=4)
                Logger.info(f"Created new config file: {self.config_file}")
            except Exception as e:
                Logger.error(f"Failed to create config file: {e}")

    # ---------------------------------------------------------
    # LOAD
    # ---------------------------------------------------------
    def load(self):
        """Load configuration from file if it exists."""
        if not os.path.exists(self.config_file):
            Logger.warning(f"Config file not found: {self.config_file}")
            self.config = dict(self.defaults)
            return

        try:
            with open(self.config_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            if not isinstance(data, dict):
                raise ValueError("Config root must be a dictionary.")

            # Merge defaults with loaded config
            merged = dict(self.defaults)
            merged.update(data)
            self.config = merged

        except json.JSONDecodeError as e:
            Logger.error(f"ConfigManager JSON decode error: {e}")
            self.config = dict(self.defaults)

        except Exception as e:
            Logger.error(f"ConfigManager error loading config: {e}")
            self.config = dict(self.defaults)

    # ---------------------------------------------------------
    # SAVE (ATOMIC)
    # ---------------------------------------------------------
    def save(self):
        """Save configuration to file using atomic write."""
        tmp_file = self.config_file + ".tmp"

        try:
            with open(tmp_file, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=4)

            os.replace(tmp_file, self.config_file)

        except Exception as e:
            Logger.error(f"ConfigManager error saving config: {e}")
            # Cleanup temp file if needed
            try:
                if os.path.exists(tmp_file):
                    os.remove(tmp_file)
            except Exception:
                pass

    # ---------------------------------------------------------
    # GET
    # ---------------------------------------------------------
    def get(self, key, default=None):
        try:
            return self.config.get(key, default)
        except Exception:
            return default

    # ---------------------------------------------------------
    # SET
    # ---------------------------------------------------------
    def set(self, key, value):
        """Set a config value and save safely."""
        try:
            # Basic validation: keys must be strings
            if not isinstance(key, str):
                raise ValueError("Config keys must be strings.")

            self.config[key] = value
            self.save()

        except Exception as e:
            Logger.error(f"ConfigManager set() error: {e}")

    # ---------------------------------------------------------
    # RESET TO DEFAULTS
    # ---------------------------------------------------------
    def reset(self):
        """Reset configuration to default values."""
        try:
            self.config = dict(self.defaults)
            self.save()
            Logger.info("Configuration reset to defaults.")
        except Exception as e:
            Logger.error(f"ConfigManager reset() error: {e}")
