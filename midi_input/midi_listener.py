# MIDI Listener – stabilná verzia

import threading
import time
import mido

from .message_parser import MessageParser
from ..core.logger import Logger


class MIDIListener:
    """
    Stabilný MIDI listener:
    - bezpečné otváranie portu
    - auto-detect MIDI zariadenia
    - thread-safe štart/stop
    - žiadne duplikované porty
    - žiadne pády pri chybách
    """

    def __init__(self, event_bus, device_name=None, poll_interval=0.001):
        self.event_bus = event_bus
        self.device_name = device_name
        self.poll_interval = poll_interval

        self.running = False
        self.thread = None
        self.port = None

    # ---------------------------------------------------------
    # START LISTENING
    # ---------------------------------------------------------
    def start(self):
        if self.running:
            Logger.warning("MIDIListener is already running.")
            return

        self.running = True
        self.thread = threading.Thread(target=self._listen_loop, daemon=True)

        try:
            self.thread.start()
            Logger.info("MIDIListener started.")
        except Exception as e:
            Logger.error(f"MIDIListener thread start error: {e}")
            self.running = False

    # ---------------------------------------------------------
    # STOP LISTENING
    # ---------------------------------------------------------
    def stop(self):
        if not self.running:
            return

        self.running = False
        Logger.info("MIDIListener stopping...")

        # počkaj na ukončenie vlákna
        if self.thread and self.thread.is_alive():
            try:
                self.thread.join(timeout=1.0)
            except Exception:
                pass

        # zatvor port
        self._close_port()
        Logger.info("MIDIListener stopped.")

    # ---------------------------------------------------------
    # PORT HANDLING
    # ---------------------------------------------------------
    def _open_port(self):
        """Bezpečne otvorí MIDI port, fallback na prvý dostupný."""
        try:
            available = mido.get_input_names()
        except Exception as e:
            Logger.error(f"MIDIListener: cannot list MIDI ports → {e}")
            return None

        if not available:
            Logger.warning("MIDIListener: no MIDI input ports available.")
            return None

        # ak device_name nie je zadaný → auto-detect
        if self.device_name is None:
            selected = available[0]
            Logger.info(f"MIDIListener: auto-selected '{selected}'")
        else:
            if self.device_name in available:
                selected = self.device_name
            else:
                Logger.warning(
                    f"MIDIListener: device '{self.device_name}' not found. "
                    f"Available: {available}. Using '{available[0]}'"
                )
                selected = available[0]

        try:
            port = mido.open_input(selected)
            Logger.info(f"MIDIListener: opened MIDI input '{selected}'")
            return port
        except Exception as e:
            Logger.error(f"MIDIListener: failed to open '{selected}' → {e}")
            return None

    def _close_port(self):
        if self.port:
            try:
                self.port.close()
            except Exception:
                pass
            self.port = None

    # ---------------------------------------------------------
    # MAIN LISTEN LOOP
    # ---------------------------------------------------------
    def _listen_loop(self):
        """Hlavný loop – číta MIDI správy a posiela ich do EventBusu."""
        self.port = self._open_port()
        if not self.port:
            self.running = False
            return

        with self.port:
            Logger.info(f"MIDIListener: listening on '{self.port.name}'")

            while self.running:
                try:
                    for msg in self.port.iter_pending():
                        parsed = MessageParser.parse(msg)
                        if parsed:
                            try:
                                self.event_bus.publish("midi_event", parsed)
                            except Exception as e:
                                Logger.error(f"EventBus publish error: {e}")

                except Exception as e:
                    Logger.error(f"MIDIListener loop error: {e}")
                    time.sleep(0.1)

                time.sleep(self.poll_interval)
