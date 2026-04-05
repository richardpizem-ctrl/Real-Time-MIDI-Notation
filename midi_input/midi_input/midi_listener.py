"""
midi_listener.py – realtime MIDI vstup pre Real-Time-MIDI-Notation.

- počúva na MIDI porte v samostatnom vlákne
- dekóduje NOTE ON / NOTE OFF / CC
- publikuje udalosti do EventBusu:
    - MIDI_NOTE_ON
    - MIDI_NOTE_OFF
    - MIDI_CONTROL_CHANGE
"""

import threading
import time
from typing import Optional

import mido

from core.logger import Logger
from core.event_bus import EventBus
from core.event_types import (
    MIDI_NOTE_ON,
    MIDI_NOTE_OFF,
    MIDI_CONTROL_CHANGE,
)


class MIDIListener:
    """
    Stabilný MIDI listener:

    - bezpečné spúšťanie / zastavenie
    - automatický výber prvého dostupného MIDI vstupu (ak nie je zadaný)
    - thread-safe loop
    - žiadne pády pri chybných správach
    """

    def __init__(
        self,
        event_bus: EventBus,
        port_name: Optional[str] = None,
        poll_interval: float = 0.001,
    ):
        """
        :param event_bus: inštancia EventBusu
        :param port_name: názov MIDI vstupného portu (ak None → auto-detect)
        :param poll_interval: čas medzi iteráciami loopu (sekundy)
        """
        self.event_bus = event_bus
        self.port_name = port_name
        self.poll_interval = poll_interval

        self._thread: Optional[threading.Thread] = None
        self._running: bool = False
        self._input_port: Optional[mido.ports.BaseInput] = None

    # ---------------------------------------------------------
    # PORT SELECTION
    # ---------------------------------------------------------
    def _select_port(self) -> Optional[str]:
        """Vyberie MIDI port – buď konkrétny, alebo prvý dostupný."""
        try:
            available = mido.get_input_names()
        except Exception as e:
            Logger.error(f"MIDIListener: failed to list MIDI inputs → {e}")
            return None

        if not available:
            Logger.warning("MIDIListener: no MIDI input ports available.")
            return None

        if self.port_name and self.port_name in available:
            return self.port_name

        if self.port_name and self.port_name not in available:
            Logger.warning(
                f"MIDIListener: requested port '{self.port_name}' not found. "
                f"Available: {available}"
            )

        # fallback – prvý dostupný port
        selected = available[0]
        Logger.info(f"MIDIListener: using MIDI input port '{selected}'")
        return selected

    def _open_port(self) -> bool:
        """Otvorí MIDI vstupný port."""
        port_name = self._select_port()
        if not port_name:
            return False

        try:
            self._input_port = mido.open_input(port_name)
            Logger.info(f"MIDIListener: opened MIDI input '{port_name}'")
            return True
        except Exception as e:
            Logger.error(f"MIDIListener: failed to open MIDI input '{port_name}' → {e}")
            self._input_port = None
            return False

    def _close_port(self):
        """Bezpečne zatvorí MIDI port."""
        if self._input_port is not None:
            try:
                self._input_port.close()
            except Exception:
                pass
            self._input_port = None
            Logger.info("MIDIListener: MIDI input closed.")

    # ---------------------------------------------------------
    # PUBLIC CONTROL
    # ---------------------------------------------------------
    def start(self):
        """Spustí MIDI listener v samostatnom vlákne."""
        if self._running:
            return

        if not self._open_port():
            Logger.warning("MIDIListener: cannot start – no MIDI port.")
            return

        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()
        Logger.info("MIDIListener: started.")

    def stop(self):
        """Zastaví MIDI listener a zatvorí port."""
        if not self._running:
            return

        self._running = False
        if self._thread and self._thread.is_alive():
            try:
                self._thread.join(timeout=1.0)
            except Exception:
                pass

        self._close_port()
        Logger.info("MIDIListener: stopped.")

    def is_running(self) -> bool:
        return self._running

    # ---------------------------------------------------------
    # MAIN LOOP
    # ---------------------------------------------------------
    def _loop(self):
        """Hlavný loop – číta MIDI správy a publikuje ich do EventBusu."""
        while self._running:
            if self._input_port is None:
                # pokus o re-open, ak by port spadol
                if not self._open_port():
                    time.sleep(0.5)
                    continue

            try:
                for msg in self._input_port.iter_pending():
                    self._handle_message(msg)
            except Exception as e:
                Logger.error(f"MIDIListener: error while reading MIDI → {e}")
                # ak port zlyhal, zavri a skús neskôr znova
                self._close_port()

            time.sleep(self.poll_interval)

    # ---------------------------------------------------------
    # MESSAGE HANDLING
    # ---------------------------------------------------------
    def _handle_message(self, msg):
        """Spracuje jednu Mido správu a premapuje ju na EventBus event."""
        try:
            msg_type = msg.type
        except Exception:
            return

        # NOTE ON / NOTE OFF
        if msg_type == "note_on" or msg_type == "note_off":
            self._handle_note_message(msg)
            return

        # CONTROL CHANGE
        if msg_type == "control_change":
            self._handle_cc_message(msg)
            return

        # ostatné typy ignorujeme (pitchwheel, aftertouch, ...)
        # Logger.debug(f"MIDIListener: ignored message type '{msg_type}'")

    def _handle_note_message(self, msg):
        """Spracuje NOTE ON / NOTE OFF a publikuje do EventBusu."""
        try:
            note = int(msg.note)
            velocity = int(getattr(msg, "velocity", 0))
            channel = int(getattr(msg, "channel", 0)) + 1  # 1–16
        except Exception:
            return

        event_payload = {
            "note": note,
            "velocity": velocity,
            "channel": channel,
            "time": time.time(),
        }

        if msg.type == "note_on" and velocity > 0:
            event_type = MIDI_NOTE_ON
        else:
            # note_on s velocity 0 = note_off
            event_type = MIDI_NOTE_OFF

        try:
            self.event_bus.publish(event_type, event_payload)
        except Exception as e:
            Logger.error(f"MIDIListener: failed to publish note event → {e}")

    def _handle_cc_message(self, msg):
        """Spracuje CONTROL CHANGE a publikuje do EventBusu."""
        try:
            control = int(msg.control)
            value = int(msg.value)
            channel = int(getattr(msg, "channel", 0)) + 1
        except Exception:
            return

        event_payload = {
            "control": control,
            "value": value,
            "channel": channel,
            "time": time.time(),
        }

        try:
            self.event_bus.publish(MIDI_CONTROL_CHANGE, event_payload)
        except Exception as e:
            Logger.error(f"MIDIListener: failed to publish CC event → {e}")
# MIDI listener module
