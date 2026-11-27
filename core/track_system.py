"""Recording model. MIDI channels are zero-based; track IDs are 1..16."""
import copy
import math
import time

COLORS = [(70, 190, 240), (240, 170, 60), (150, 210, 100), (225, 100, 170)]


class TrackSystem:
    def __init__(self, event_bus=None, clock=time.monotonic):
        self.event_bus = event_bus
        self.clock = clock
        self.names = {i: f'Track {i}' for i in range(1, 17)}
        self.active_track = 1
        self.reset()

    def reset(self):
        self.origin = self.clock()
        self.recorded_events = {i: [] for i in range(1, 17)}
        self.notes = []
        self.active = {}
        self.held = {}
        self.sustain = {i: False for i in range(16)}
        self.last_time = 0.0

    def process(self, event):
        event = copy.deepcopy(event)
        timestamp = float(event['time']) - self.origin
        if not math.isfinite(timestamp):
            raise ValueError('Invalid timestamp')
        timestamp = max(0.0, timestamp)
        channel = event.get('channel', 0)
        if not isinstance(channel, int) or not 0 <= channel < 16:
            raise ValueError('Invalid MIDI channel')
        kind = event['type']
        if kind not in {'note_on','note_off','control_change','pitchwheel','program_change','aftertouch','polytouch'}:
            raise ValueError('Unsupported MIDI event')
        if 'note' in event and (not isinstance(event['note'], int) or not 0 <= event['note'] <= 127):
            raise ValueError('Invalid MIDI note')
        if 'velocity' in event and not 0 <= event['velocity'] <= 127:
            raise ValueError('Invalid velocity')
        if kind == 'note_on' and event['velocity'] == 0:
            event['type'] = kind = 'note_off'
        event['time'] = timestamp
        self.recorded_events[channel + 1].append(event)
        self.last_time = max(self.last_time, timestamp)
        if kind in ('note_on','note_off'):
            key = channel, event['note']
            if kind == 'note_on':
                self._finish(key, timestamp)
                note = {'channel': channel, 'track_id': channel + 1, 'pitch': event['note'],
                        'velocity': event['velocity'], 'timestamp': timestamp, 'end': None}
                self.notes.append(note)
                self.active[key] = note
                self.held[key] = note
            else:
                self.held.pop(key, None)
                if not self.sustain[channel]:
                    self._finish(key, timestamp)
        elif kind == 'control_change':
            if event['control'] == 64:
                self.sustain[channel] = event['value'] >= 64
                if not self.sustain[channel]:
                    for key in list(self.active):
                        if key[0] == channel and key not in self.held:
                            self._finish(key, timestamp)
            elif event['control'] in (120,123):
                for key in list(self.active):
                    if key[0] == channel:
                        self._finish(key, timestamp)
        if self.event_bus:
            self.event_bus.publish('recording.note_recorded', event)
        return event

    def _finish(self, key, timestamp):
        note = self.active.pop(key, None)
        self.held.pop(key, None)
        if note:
            note['end'] = max(note['timestamp'], timestamp)

    def finish(self, timestamp=None):
        relative = max(self.last_time, self.clock()-self.origin if timestamp is None else timestamp)
        for channel, pitch in list(self.active):
            self.process({'type':'note_off','channel':channel,'note':pitch,'velocity':0,'time':self.origin+relative})
        for channel, down in list(self.sustain.items()):
            if down:
                self.process({'type':'control_change','channel':channel,'control':64,'value':0,'time':self.origin+relative})

    def get_track_name(self, track_id):
        return self.names[track_id]

    def get_track_color(self, track_id):
        return COLORS[(track_id - 1) % len(COLORS)]

    def set_active_track_by_channel(self, channel):
        self.active_track = channel + 1
        return self.active_track

    def shutdown(self):
        self.finish()
