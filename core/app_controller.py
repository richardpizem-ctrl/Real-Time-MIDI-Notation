"""One supported MIDI -> queue -> model -> analysis pipeline."""
from queue import Queue, Empty, Full
import mido
from .event_bus import EventBus
from .track_system import TrackSystem
from .track_manager import TrackManager
from .notation_processor import NotationProcessor
from midi_input.message_parser import MessageParser
from midi_input.midi_listener import MIDIListener
from midi_input.event_router import EventRouter
from notation_engine.chord_detector import detect_chord
from notation_engine.key_detector import detect_key

class AppController:
    def __init__(self, clock=None):
        self.event_bus = EventBus()
        self.track_system = TrackSystem(self.event_bus, **({'clock':clock} if clock else {}))
        self.track_manager = TrackManager(self.track_system,self.event_bus)
        self.notation_processor = NotationProcessor(self.track_system,self.event_bus)
        self.queue = Queue(maxsize=16384)
        self.errors = Queue()
        self.dropped = 0
        self.recording = True
        self.listener = None
        self.router = EventRouter(self.event_bus)
        self.event_bus.subscribe('midi_event', self.enqueue)
        self.event_bus.subscribe('note_event', self._process)
        self.event_bus.subscribe('control_event', self._process)
        self.event_bus.subscribe('system.error', self.errors.put)
        self.current_chord = None
        self.current_key = None
        self.last_velocity = None
        self._last_analysis_count = 0

    def enqueue(self, event):
        try:
            self.queue.put_nowait(event)
        except Full:
            self.dropped += 1
            if self.dropped == 1:
                self.errors.put('MIDI queue overflow; recording stopped to prevent stuck notes')

    def inject(self, message, timestamp=None):
        event = MessageParser.parse(message,timestamp)
        if event:
            self.enqueue(event)

    def _process(self, event):
        if self.recording:
            self.track_system.process(event)
            if event['type'] == 'note_on':
                self.last_velocity = event['velocity']

    def drain(self, limit=4096):
        if self.dropped:
            self.recording = False
            self.track_system.finish()
        count = 0
        while count < limit:
            try:
                event = self.queue.get_nowait()
            except Empty:
                break
            self.router.route(event)
            count += 1
        if self.listener and not self.listener.running and self.listener.error:
            self.track_system.finish()
            self.recording = False
        pitches = [pitch for channel,pitch in self.track_system.active if channel != 9]
        self.current_chord = detect_chord(pitches)
        note_count = len(self.track_system.notes)
        if note_count != self._last_analysis_count:
            self.current_key = detect_key([n['pitch'] for n in self.track_system.notes[-128:] if n['channel'] != 9])
            self._last_analysis_count = note_count
        return count

    def start(self, device_name=None):
        self.stop_input()
        self.listener = MIDIListener(self.event_bus,device_name)
        return self.listener.start()

    def stop_input(self):
        if self.listener:
            self.listener.stop()
            self.listener = None
        self.drain()
        self.track_system.finish()

    def set_recording(self, enabled):
        self.drain()
        if not enabled:
            self.track_system.finish()
        self.recording = bool(enabled) and self.dropped == 0

    def reset(self):
        self.stop_input()
        while not self.queue.empty():
            self.queue.get_nowait()
        self.track_system.reset()
        self.dropped = 0
        self.recording = True
        self.current_chord = self.current_key = self.last_velocity = None
        self._last_analysis_count = 0

    def export_midi(self, filename='export.mid', bpm=120):
        self.drain()
        return self.notation_processor.export_midi(filename,bpm)

    def shutdown(self):
        self.stop_input()
        self.event_bus.shutdown()
