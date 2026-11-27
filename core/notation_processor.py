"""Timed MIDI file I/O. Recorded seconds are converted to per-track delta ticks."""
from pathlib import Path
import math
import mido
from .track_system import TrackSystem

class NotationProcessor:
    def __init__(self, track_system=None, event_bus=None, track_manager=None):
        self.track_system = track_system if track_system is not None else track_manager.track_system
        self.event_bus = event_bus

    def export_midi(self, filename='export.mid', bpm=120.0):
        if not math.isfinite(float(bpm)) or not 1 <= float(bpm) <= 1000:
            raise ValueError('Invalid tempo')
        tempo = mido.bpm2tempo(bpm)
        mid = mido.MidiFile(type=1, ticks_per_beat=480)
        conductor = mido.MidiTrack()
        conductor.append(mido.MetaMessage('set_tempo',tempo=tempo,time=0))
        mid.tracks.append(conductor)
        # Work on a copy: closing an export must not stop a live session.
        import copy
        source = copy.deepcopy(self.track_system.recorded_events)
        end = max(self.track_system.last_time, self.track_system.clock()-self.track_system.origin)
        for track_id, events in source.items():
            channel = track_id - 1
            for key in self.track_system.active:
                if key[0] == channel:
                    events.append({'type':'note_off','channel':channel,'note':key[1],'velocity':0,'time':end})
            if self.track_system.sustain[channel]:
                events.append({'type':'control_change','channel':channel,'control':64,'value':0,'time':end})
            if not events:
                continue
            track = mido.MidiTrack()
            track.append(mido.MetaMessage('track_name',name=self.track_system.get_track_name(track_id),time=0))
            previous = 0
            for event in sorted(events,key=lambda x:x['time']):
                tick = round(mido.second2tick(event['time'],mid.ticks_per_beat,tempo))
                payload = {k:v for k,v in event.items() if k != 'time'}
                track.append(mido.Message.from_dict(dict(payload,time=max(0,tick-previous))))
                previous = tick
            mid.tracks.append(track)
        destination = Path(filename)
        destination.parent.mkdir(parents=True,exist_ok=True)
        mid.save(destination)
        if self.event_bus:
            self.event_bus.publish('export.midi_done',str(destination))
        return destination

    def import_midi(self, filename):
        mid = mido.MidiFile(filename)
        if mid.type == 2:
            raise ValueError('Asynchronous type-2 MIDI files are not supported')
        # Build off to the side. A malformed file must not erase current work.
        result = TrackSystem(clock=self.track_system.clock)
        elapsed = 0.0
        tempo = 500000
        for message in mido.merge_tracks(mid.tracks):
            elapsed += mido.tick2second(message.time,mid.ticks_per_beat,tempo)
            if message.type == 'set_tempo':
                tempo = message.tempo
            elif not message.is_meta and message.type in {'note_on','note_off','control_change','pitchwheel','program_change','aftertouch','polytouch'}:
                event = message.dict()
                event['time'] = result.origin + elapsed
                result.process(event)
        result.finish(elapsed)
        self.track_system.origin = result.origin
        self.track_system.recorded_events = result.recorded_events
        self.track_system.notes = result.notes
        self.track_system.active = result.active
        self.track_system.held = result.held
        self.track_system.sustain = result.sustain
        self.track_system.last_time = elapsed
        return self.track_system

    def shutdown(self):
        pass
