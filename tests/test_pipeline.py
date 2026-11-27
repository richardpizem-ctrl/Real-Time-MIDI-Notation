"""Regression tests for actual recording, timed export and the supported GUI."""
from contextlib import contextmanager
import importlib
import os
from pathlib import Path
import threading
import time
from unittest.mock import patch
import mido
import pytest
from core.app_controller import AppController
from core.event_bus import EventBus
from core.track_system import TrackSystem
from core.notation_processor import NotationProcessor
from core.playback_engine import PlaybackEngine
from midi_input.message_parser import MessageParser
from midi_input.midi_listener import MIDIListener
from notation_engine.chord_detector import detect_chord
from notation_engine.key_detector import detect_key


def event(kind='note_on', at=0.0, **values):
    return MessageParser.parse(mido.Message(kind,**values),at)


@pytest.mark.parametrize('channel',[0,1,9,15])
def test_record_channels_and_velocity_zero(channel):
    model=TrackSystem(clock=lambda:0)
    model.process(event(at=1,note=60,velocity=80,channel=channel))
    model.process(event(at=2,note=60,velocity=0,channel=channel))
    assert model.notes[0]['timestamp']==1
    assert model.notes[0]['end']==2
    assert model.notes[0]['track_id']==channel+1
    assert len(model.recorded_events[channel+1])==2
    assert not model.active


def test_same_pitch_on_different_channels_is_independent():
    model=TrackSystem(clock=lambda:0)
    for channel in (0,1):model.process(event(at=0,note=60,channel=channel))
    model.process(event('note_off',at=1,note=60,channel=0))
    assert set(model.active)=={(1,60)}


def test_sustain_only_releases_unheld_notes_on_its_channel():
    model=TrackSystem(clock=lambda:0)
    model.process(event(at=0,note=60))
    model.process(event(at=0,note=64))
    model.process(event('control_change',at=.2,control=64,value=127))
    model.process(event('note_off',at=.5,note=60))
    assert model.notes[0]['end'] is None
    model.process(event('control_change',at=.8,control=64,value=0))
    assert model.notes[0]['end']==.8
    assert set(model.active)=={(0,64)}


def test_repeated_note_does_not_leave_a_stuck_voice():
    model=TrackSystem(clock=lambda:0)
    model.process(event(at=0,note=60))
    model.process(event(at=.5,note=60))
    model.process(event('note_off',at=1,note=60))
    assert [n['end'] for n in model.notes]==[.5,1]
    assert not model.active


@pytest.mark.parametrize('command',[120,123])
def test_all_notes_off_is_scoped_to_channel(command):
    model=TrackSystem(clock=lambda:0)
    for channel in (0,2):model.process(event(at=0,note=60,channel=channel))
    model.process(event('control_change',at=1,channel=0,control=command,value=0))
    assert set(model.active)=={(2,60)}


def test_clock_message_is_not_a_note_and_mido_time_is_not_live_timestamp():
    assert MessageParser.parse(mido.Message('clock')) is None
    assert MessageParser.parse(mido.Message('note_on',note=60,time=10000),7)['time']==7


@pytest.mark.parametrize('channel',[0,9,15])
def test_export_reload_preserves_pitch_channel_duration_and_controls(tmp_path,channel):
    model=TrackSystem(clock=lambda:0)
    model.process(event('program_change',at=0,channel=channel,program=7))
    model.process(event(at=.25,channel=channel,note=64,velocity=93))
    model.process(event('pitchwheel',at=.4,channel=channel,pitch=1000))
    model.process(event('note_off',at=.9,channel=channel,note=64,velocity=15))
    target=tmp_path/'test.mid'
    NotationProcessor(model).export_midi(target,bpm=100)
    mid=mido.MidiFile(target)
    assert mid.length==pytest.approx(.9,abs=.002)
    restored=TrackSystem(clock=lambda:0)
    NotationProcessor(restored).import_midi(target)
    note=restored.notes[0]
    assert note['channel']==channel and note['pitch']==64 and note['velocity']==93
    assert note['timestamp']==pytest.approx(.25,abs=.002)
    assert note['end']==pytest.approx(.9,abs=.002)
    assert any(e['type']=='pitchwheel' and e['pitch']==1000 for e in restored.recorded_events[channel+1])


def test_export_closes_held_note_without_mutating_live_model(tmp_path):
    model=TrackSystem(clock=lambda:0)
    model.process(event(at=.1,note=60))
    model.process(event('control_change',at=.2,control=64,value=127))
    NotationProcessor(model).export_midi(tmp_path/'held.mid')
    assert (0,60) in model.active
    restored=TrackSystem(clock=lambda:0)
    NotationProcessor(restored).import_midi(tmp_path/'held.mid')
    assert restored.notes[0]['end'] is not None and not restored.active


def test_import_tempo_changes(tmp_path):
    mid=mido.MidiFile(ticks_per_beat=480)
    mid.tracks.append(mido.MidiTrack([
        mido.Message('note_on',note=60,time=0),
        mido.MetaMessage('set_tempo',tempo=1000000,time=480),
        mido.Message('note_off',note=60,time=480)]))
    path=tmp_path/'tempo.mid';mid.save(path)
    model=TrackSystem(clock=lambda:0)
    NotationProcessor(model).import_midi(path)
    assert model.notes[0]['end']==pytest.approx(1.5)


def test_failed_import_preserves_work(tmp_path):
    model=TrackSystem(clock=lambda:0);model.process(event(at=0,note=60))
    bad=tmp_path/'bad.mid';bad.write_text('not MIDI')
    with pytest.raises((OSError,EOFError,ValueError)):
        NotationProcessor(model).import_midi(bad)
    assert len(model.notes)==1 and (0,60) in model.active


class FakePort:
    def __init__(self,messages=(),fail=False):
        self.messages=list(messages);self.closed=False;self.sent=[];self.fail=fail
    def iter_pending(self):
        if self.fail:raise OSError('disconnected')
        messages,self.messages=self.messages,[]
        return iter(messages)
    def send(self,message):self.sent.append(message)
    def close(self):self.closed=True


def test_fake_device_runs_the_real_listener_queue_and_model():
    app=AppController()
    port=FakePort([mido.Message('note_on',note=60),mido.Message('note_on',note=64),
                   mido.Message('note_on',note=67),mido.Message('note_off',note=60)])
    with patch('mido.get_input_names',return_value=['fake']),patch('mido.open_input',return_value=port):
        assert app.start('fake')
        deadline=time.monotonic()+1
        while app.queue.qsize()<4 and time.monotonic()<deadline:time.sleep(.005)
        assert app.drain()==4
        assert len(app.track_system.notes)==3
        assert set(app.track_system.active)=={(0,64),(0,67)}
        app.shutdown()
    assert port.closed and not app.track_system.active


def test_disconnected_device_reports_error_and_stops_reader():
    bus=EventBus();errors=[];bus.subscribe('system.error',errors.append)
    port=FakePort(fail=True)
    with patch('mido.get_input_names',return_value=['fake']),patch('mido.open_input',return_value=port):
        reader=MIDIListener(bus,'fake');assert reader.start()
        reader.thread.join(timeout=1)
        assert not reader.running and errors==['disconnected'] and port.closed
        reader.stop()


def test_missing_requested_device_does_not_silently_select_another():
    bus=EventBus()
    with patch('mido.get_input_names',return_value=['different']),patch('mido.open_input') as opened:
        reader=MIDIListener(bus,'missing');assert not reader.start();opened.assert_not_called()


def test_main_loop_owns_recording_changes():
    app=AppController(clock=lambda:0)
    thread=threading.Thread(target=lambda:app.inject(mido.Message('note_on',note=60),0))
    thread.start();thread.join()
    assert not app.track_system.notes
    app.drain()
    assert len(app.track_system.notes)==1


def test_playback_timing_channel_and_stop_note_cleanup():
    now=[0.0];port=FakePort()
    playback=PlaybackEngine(clock=lambda:now[0],output=port)
    playback.set_notes([{'timestamp':.5,'duration':1,'pitch':60,'velocity':90,'channel':2}])
    playback.play();now[0]=.4;playback.update();assert not port.sent
    now[0]=.5;playback.update()
    assert port.sent[0].type=='note_on' and port.sent[0].channel==2
    playback.pause()
    assert any(m.type=='note_off' and m.note==60 and m.channel==2 for m in port.sent)
    assert not playback.active
    playback.shutdown();assert port.closed


def test_mute_volume_and_release_are_applied_to_actual_midi_output():
    from core.track_manager import TrackManager
    manager=TrackManager()
    manager.set_mute(1,True)
    manager.set_volume(2,.5)
    now=[0.0];port=FakePort()
    player=PlaybackEngine(track_manager=manager,output=port,clock=lambda:now[0])
    player.set_notes([{'timestamp':0,'duration':1,'pitch':60,'velocity':100,'channel':0},
                      {'timestamp':0,'duration':1,'pitch':64,'velocity':100,'channel':1}])
    player.play();player.update()
    played=[m for m in port.sent if m.type=='note_on']
    assert len(played)==1 and played[0].channel==1 and played[0].velocity==50
    player.release_channel(1)
    assert not player.active
    assert any(m.type=='note_off' and m.channel==1 for m in port.sent)


def test_pause_resume_restores_held_note_without_replaying_the_past():
    now=[0.0];port=FakePort()
    playback=PlaybackEngine(clock=lambda:now[0],output=port)
    playback.set_notes([{'timestamp':0,'duration':1,'pitch':60,'channel':3}])
    playback.play();now[0]=.5;playback.update();playback.pause()
    before=len(port.sent)
    now[0]=10;playback.play()
    assert any(m.type=='note_on' and m.note==60 for m in port.sent[before:])
    now[0]=10.5;playback.update()
    assert not playback.playing and not playback.active


def test_stop_input_and_restart_same_reader():
    bus=EventBus();ports=[FakePort(),FakePort()]
    with patch('mido.get_input_names',return_value=['fake']),patch('mido.open_input',side_effect=ports):
        reader=MIDIListener(bus,'fake')
        assert reader.start();reader.stop()
        assert ports[0].closed
        assert reader.start();reader.stop()
        assert ports[1].closed


def test_export_finishes_held_notes_at_snapshot_time(tmp_path):
    now=[0.0];model=TrackSystem(clock=lambda:now[0])
    model.process(event(at=.2,note=60))
    now[0]=2
    filename=tmp_path/'held.mid';NotationProcessor(model).export_midi(filename)
    loaded=TrackSystem(clock=lambda:0);NotationProcessor(loaded).import_midi(filename)
    assert loaded.notes[0]['end']==pytest.approx(2)


def test_queue_overflow_is_visible_and_cannot_keep_a_note_held():
    from queue import Queue
    app=AppController(clock=lambda:0)
    app.inject(mido.Message('note_on',note=60),0);app.drain()
    app.queue=Queue(maxsize=1)
    app.inject(mido.Message('note_on',note=64),.1)
    app.inject(mido.Message('note_off',note=60),.2)
    app.drain()
    assert app.dropped==1 and not app.recording and not app.track_system.active
    assert not app.errors.empty()


def test_controller_closes_active_notes_after_reader_failure():
    from types import SimpleNamespace
    app=AppController(clock=lambda:1)
    app.inject(mido.Message('note_on',note=60),1)
    app.drain()
    app.listener=SimpleNamespace(running=False,error='disconnected')
    app.drain()
    assert not app.track_system.active and not app.recording


def test_quit_confirmation_cannot_be_reused_for_clear(monkeypatch):
    monkeypatch.setenv('SDL_VIDEODRIVER','dummy')
    monkeypatch.setenv('SDL_AUDIODRIVER','dummy')
    import pygame
    from ui.application import MidiApplication
    ui=MidiApplication(headless=True)
    try:
        ui.app.inject(mido.Message('note_on',note=60));ui.tick()
        assert ui.dirty
        ui.quit();assert ui.running
        ui.clear();assert len(ui.app.track_system.notes)==1
        ui.clear();assert not ui.app.track_system.notes
    finally:
        ui.playback.shutdown();ui.app.shutdown();pygame.quit()


def test_session_with_large_event_burst_preserves_note_pairs():
    app=AppController(clock=lambda:0)
    for i in range(4000):
        app.inject(mido.Message('note_on',channel=i%16,note=40+i%40),i*.01)
        app.inject(mido.Message('note_off',channel=i%16,note=40+i%40),i*.01+.005)
    while not app.queue.empty():app.drain()
    assert len(app.track_system.notes)==4000
    assert not app.track_system.active and app.dropped==0


@pytest.mark.parametrize('root',range(12))
def test_all_major_and_minor_triads(root):
    names=['C','C#','D','D#','E','F','F#','G','G#','A','A#','B']
    assert detect_chord([60+root,64+root,67+root])==names[root]
    assert detect_chord([60+root,63+root,67+root])==names[root]+'m'


@pytest.mark.parametrize('root',range(12))
def test_transposed_major_scale_key(root):
    pitches=[60+root+i for i in [0,2,4,5,7,9,11]]*5
    names=['C','C#','D','D#','E','F','F#','G','G#','A','A#','B']
    assert detect_key(pitches)==names[root]


def test_full_dummy_ui_demo_exports_and_reopens(tmp_path,monkeypatch):
    monkeypatch.setenv('SDL_VIDEODRIVER','dummy')
    monkeypatch.setenv('SDL_AUDIODRIVER','dummy')
    import pygame
    from ui.application import MidiApplication
    ui=MidiApplication(headless=True)
    try:
        ui.start_demo()
        ui.demo_start-=2
        ui.tick();ui.render()
        assert len(ui.app.track_system.notes)==6
        assert not ui.app.track_system.active
        path=tmp_path/'demo.mid'
        ui.app.export_midi(path)
        ui.load(path);ui.toggle_playback();ui.render()
        assert len(ui.app.track_system.notes)==6
        assert ui.playback.events
        pygame.image.save(ui.screen,str(tmp_path/'preview.png'))
    finally:
        ui.playback.shutdown();ui.app.shutdown();pygame.quit()
