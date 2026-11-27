"""Read MIDI on a worker; event subscribers must enqueue, never render here."""
import threading
import mido
from core.logger import Logger
from .message_parser import MessageParser

class MIDIListener:
    def __init__(self, event_bus, device_name=None, poll_interval=0.003):
        self.event_bus = event_bus
        self.device_name = device_name
        self.poll_interval = max(0.001, float(poll_interval))
        self.running = False
        self.thread = None
        self.port = None
        self.error = None
        self._stop = threading.Event()

    def start(self):
        if self.running:
            return True
        if self.thread and self.thread.is_alive():
            raise RuntimeError('Previous MIDI reader has not stopped')
        self.error = None
        try:
            names = mido.get_input_names()
            selected = self.device_name or (names[0] if names else None)
            if selected not in names:
                raise RuntimeError('Selected MIDI input is unavailable')
            self.port = mido.open_input(selected)
            self.device_name = selected
        except Exception as error:
            self.error = str(error)
            self.event_bus.publish('system.error', self.error)
            return False
        self._stop.clear()
        self.running = True
        self.thread = threading.Thread(target=self._listen_loop, name='MidiReader', daemon=True)
        self.thread.start()
        return True

    def _listen_loop(self):
        try:
            while not self._stop.is_set():
                for message in self.port.iter_pending():
                    event = MessageParser.parse(message)
                    if event:
                        self.event_bus.publish('midi_event', event)
                self._stop.wait(self.poll_interval)
        except Exception as error:
            self.error = str(error)
            self.event_bus.publish('system.error', self.error)
        finally:
            self.running = False
            if self.port is not None:
                try:
                    self.port.close()
                except Exception as error:
                    Logger.warning(str(error))

    def stop(self):
        self._stop.set()
        if self.thread and self.thread is not threading.current_thread():
            self.thread.join(timeout=2)
            if self.thread.is_alive():
                raise RuntimeError('MIDI reader failed to stop')
        self.running = False
        self.port = None

MidiListener = MIDIListener
