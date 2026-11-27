"""Playback is advanced only by the UI thread; timestamps remain seconds."""
import copy
import time
import mido

class PlaybackEngine:
    def __init__(self, track_manager=None, renderer=None, canvas_ui=None,
                 event_bus=None, bpm=120.0, beats_per_bar=4, clock=time.monotonic, output=None, **unused):
        self.track_manager = track_manager
        self.renderer = renderer
        self.canvas_ui = canvas_ui
        self.event_bus = event_bus
        self.bpm = bpm
        self.beats_per_bar = beats_per_bar
        self.clock = clock
        self.output = output
        self.playing = False
        self.position_sec = 0.0
        self.events = []
        self.index = 0
        self.active = set()
        self.channels = set()
        self._last_time = clock()
        self.duration = 0.0
        self._resume_pending = False

    def load_recording(self, track_system):
        self.stop()
        self.events = sorted([copy.deepcopy(e) for es in track_system.recorded_events.values() for e in es],key=lambda x:x['time'])
        self.duration = max((e['time'] for e in self.events),default=0.0)

    def set_notes(self, notes):
        self.stop()
        self.events = []
        for n in notes:
            channel = n.get('channel',n.get('track_id',1)-1)
            start = float(n.get('timestamp',0))
            pitch = n.get('pitch',n.get('note'))
            self.events.extend([{'type':'note_on','note':pitch,'channel':channel,'velocity':n.get('velocity',100),'time':start},
                                {'type':'note_off','note':pitch,'channel':channel,'velocity':0,'time':start+float(n.get('duration',0.1))}])
        self.events.sort(key=lambda x:x['time'])
        self.duration = max((e['time'] for e in self.events),default=0)

    def _send(self, event):
        message = mido.Message.from_dict({k:v for k,v in event.items() if k != 'time'})
        if message.type == 'note_on' and message.velocity > 0 and self.track_manager:
            transformed = self.track_manager.apply_midi_transform(message.channel+1,message.note,message.velocity)
            if transformed is None:
                return
            message = message.copy(note=transformed[0],velocity=transformed[1])
        if self.output is not None:
            self.output.send(message)
        key = (getattr(message,'channel',0),getattr(message,'note',None))
        self.channels.add(key[0])
        if message.type == 'note_on' and message.velocity > 0:
            self.active.add(key)
        elif message.type in ('note_on','note_off'):
            self.active.discard(key)

    def play(self):
        if not self.events:
            return
        if self.index >= len(self.events):
            self.index = 0
            self.position_sec = 0.0
        if self._resume_pending:
            # Reconstruct only the state at the pause point; do not replay old notes.
            from .track_system import TrackSystem
            model = TrackSystem(clock=lambda:0)
            controls = {}
            for event in self.events[:self.index]:
                model.process(event)
                if event['type'] not in ('note_on','note_off'):
                    controls[(event['channel'],event['type'],event.get('control'),event.get('note'))] = event
            for event in controls.values():
                self._send(event)
            for key,note in model.active.items():
                self._send({'type':'note_on','channel':key[0],'note':key[1],'velocity':note['velocity']})
                if key not in model.held:
                    self._send({'type':'note_off','channel':key[0],'note':key[1],'velocity':0})
            self._resume_pending = False
        self.playing = True
        self._last_time = self.clock()

    def pause(self):
        was_playing = self.playing
        if self.playing:
            self.update()
        self.playing = False
        self._panic()
        self._resume_pending = was_playing and self.index < len(self.events)

    def _panic(self):
        for channel,note in list(self.active):
            self._send({'type':'note_off','channel':channel,'note':note,'velocity':0})
        if self.output is not None:
            for channel in self.channels:
                self.output.send(mido.Message('control_change',channel=channel,control=64,value=0))
        self.active.clear()
        self.channels.clear()

    def release_channel(self, channel):
        for key in list(self.active):
            if key[0] == channel:
                self._send({'type':'note_off','channel':channel,'note':key[1],'velocity':0})
        if self.output is not None:
            self.output.send(mido.Message('control_change',channel=channel,control=64,value=0))

    def stop(self):
        self.playing = False
        self._resume_pending = False
        self._panic()
        self.position_sec = 0.0
        self.index = 0

    def is_playing(self):
        return self.playing

    def update(self, dt=None):
        if not self.playing:
            return None
        now = self.clock()
        self.position_sec += max(0.0,now-self._last_time)
        self._last_time = now
        while self.index < len(self.events) and self.events[self.index]['time'] <= self.position_sec:
            self._send(self.events[self.index])
            self.index += 1
        if self.index == len(self.events):
            self.playing = False
            self._panic()
        return None

    def shutdown(self):
        self.stop()
        if self.output is not None:
            self.output.close()
            self.output = None
