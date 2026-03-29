# Config manager

import json
import os
from .logger import Logger


class ConfigManager:
    """
    Stabilizovaný konfigurák:
    - bezpečné načítanie JSON
    - bezpečné ukladanie
    - fallback pri chybných súboroch
    - žiadne print() – všetko ide cez Logger
    """

    def __init__(self, config_file="config.json"):
        self.config_file = config_file
        self.config = {}
        self.load()

    # ---------------------------------------------------------
    # LOAD
    # ---------------------------------------------------------
    def load(self):
        """Load configuration from file if it exists."""
        if not os.path.exists(self.config_file):
            Logger.warning(f"Config file not found: {self.config_file}")
            self.config = {}
            return

        try:
            with open(self.config_file, "r", encoding="utf-8") as f:
                self.config = json.load(f)

        except json.JSONDecodeError as e:
            Logger.error(f"ConfigManager JSON decode error: {e}")
            self.config = {}

        except Exception as e:
            Logger.error(f"ConfigManager error loading config: {e}")
            self.config = {}

    # ---------------------------------------------------------
    # SAVE
    # ---------------------------------------------------------
    def save(self):
        """Save configuration to file."""
        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=4)

        except Exception as e:
            Logger.error(f"ConfigManager error saving config: {e}")

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
        try:
            self.config[key] = value
            self.save()
        except Exception as e:
            Logger.error(f"ConfigManager set() error: {e}")
