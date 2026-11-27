"""One Pygame main loop for capture, notation preview, tracks and playback."""
from collections import deque
from pathlib import Path
import time
import mido
import pygame
from core.app_controller import AppController
from core.playback_engine import PlaybackEngine
from .PianoUI import PianoUI
from .timeline_ui import TimelineUI


class MidiApplication:
    def __init__(self, demo=False, midi_file=None, input_name=None, headless=False, settings=None):
        from core.diagnostics import DEFAULT_SETTINGS, validate_settings
        self.settings = validate_settings(settings or DEFAULT_SETTINGS)
        pygame.display.init()
        pygame.font.init()
        self.screen = pygame.display.set_mode((self.settings['width'],self.settings['height']))
        pygame.display.set_caption('SIRIUS MIDI - pracovná oprava 4.3.1')
        self.font = pygame.font.SysFont('Segoe UI', 18)
        self.small = pygame.font.SysFont('Segoe UI', 15)
        self.app = AppController()
        self.playback = PlaybackEngine(track_manager=self.app.track_manager)
        self.piano = PianoUI(width=1240, height=150)
        self.timeline = TimelineUI(self.app.track_manager, width=1240, height=155)
        self.messages = deque(maxlen=5)
        self.messages.append('Vyber MIDI vstup alebo spusti DEMO. Zvuk vyžaduje MIDI výstup.')
        self.running = True
        self.dirty = False
        self.confirm_until = 0.0
        self.confirm_action = None
        self.demo = demo
        self.demo_start = None
        self.demo_index = 0
        self.frame_count = 0
        self.devices = []
        self.outputs = []
        self.input_index = 0
        self.output_index = -1
        self.input_name = input_name
        self._load_dialog = None
        if not headless:
            self.refresh_devices()
        self.buttons = []
        if midi_file:
            self.load(midi_file)
        if input_name:
            if input_name not in self.devices:
                self.messages.append('Požadovaný MIDI vstup nie je dostupný.')
            else:
                self.input_index = self.devices.index(input_name)
                self.connect()
        if demo:
            self.start_demo()

    def refresh_devices(self):
        try:
            self.devices = mido.get_input_names()
            self.outputs = mido.get_output_names()
            self.input_index = min(self.input_index, max(0, len(self.devices)-1))
        except Exception as error:
            self.devices = self.outputs = []
            self.messages.append('MIDI zariadenia: ' + str(error))

    def connect(self):
        self.playback.stop()
        self.playback.events = []
        if not self.devices:
            self.messages.append('Žiadny MIDI vstup. Pripoj klaviatúru a stlač Obnoviť.')
            return
        if self.app.start(self.devices[self.input_index]):
            self.app.set_recording(True)
            self.messages.append('Pripojené: ' + self.devices[self.input_index])

    def select_input(self):
        if self.devices:
            self.app.stop_input()
            self.input_index = (self.input_index + 1) % len(self.devices)
            self.messages.append('Vybraný vstup: ' + self.devices[self.input_index])

    def select_output(self):
        self.playback.stop()
        if self.playback.output is not None:
            self.playback.output.close()
            self.playback.output = None
        self.output_index += 1
        if self.output_index >= len(self.outputs):
            self.output_index = -1
        if self.output_index >= 0:
            try:
                self.playback.output = mido.open_output(self.outputs[self.output_index])
            except Exception as error:
                self.output_index = -1
                self.messages.append(str(error))

    def start_demo(self):
        self.playback.stop()
        self.playback.events = []
        self.app.stop_input()
        self.demo_start = time.monotonic()
        self.demo_index = 0
        self.app.set_recording(True)
        self.messages.append('DEMO: simulovaný C dur / A mol, dva MIDI kanály.')

    def _demo_tick(self):
        if self.demo_start is None:
            return
        events = [(0.0,0,'note_on',60), (0.0,0,'note_on',64), (0.0,0,'note_on',67),
                  (0.6,0,'note_off',60), (0.6,0,'note_off',64), (0.6,0,'note_off',67),
                  (0.8,1,'note_on',57), (0.8,1,'note_on',60), (0.8,1,'note_on',64),
                  (1.4,1,'note_off',57), (1.4,1,'note_off',60), (1.4,1,'note_off',64)]
        elapsed = time.monotonic() - self.demo_start
        while self.demo_index < len(events) and events[self.demo_index][0] <= elapsed:
            offset,channel,kind,pitch = events[self.demo_index]
            self.app.inject(mido.Message(kind,channel=channel,note=pitch,velocity=90 if kind=='note_on' else 0),self.demo_start+offset)
            self.demo_index += 1
            self.dirty = True
        if self.demo_index == len(events):
            self.demo_start = None

    def export(self):
        destination = Path('exports') / time.strftime('session-%Y%m%d-%H%M%S.mid')
        if destination.exists():
            destination = destination.with_name(destination.stem+'-'+str(time.time_ns())+'.mid')
        self.app.export_midi(destination,bpm=self.settings['bpm'])
        self.messages.append('Uložené: ' + str(destination.resolve()))
        self.dirty = False

    def load(self, filename):
        self.playback.stop()
        self.playback.events = []
        self.app.stop_input()
        self.demo_start = None
        self.app.notation_processor.import_midi(filename)
        self.app.set_recording(False)
        self.dirty = False
        self.messages.append('Načítané: ' + str(filename))

    def open_dialog(self):
        if self.dirty and (self.confirm_action != 'open' or time.monotonic() > self.confirm_until):
            self.confirm_action = 'open'
            self.confirm_until = time.monotonic()+4
            self.messages.append('Najprv Export, alebo klikni Otvoriť znovu do 4 sekúnd.')
            return
        from tkinter import Tk, filedialog
        root = Tk()
        root.withdraw()
        try:
            selected = filedialog.askopenfilename(filetypes=[('MIDI files','*.mid *.midi')])
        finally:
            root.destroy()
        if selected:
            self.load(selected)

    def toggle_playback(self):
        if self.playback.playing:
            self.playback.pause()
        else:
            self.demo_start = None
            self.app.stop_input()
            self.app.set_recording(False)
            if not self.playback.events or self.playback.index >= len(self.playback.events):
                self.playback.load_recording(self.app.track_system)
            self.playback.play()

    def clear(self):
        if self.dirty and (self.confirm_action != 'clear' or time.monotonic() > self.confirm_until):
            self.confirm_action = 'clear'
            self.confirm_until = time.monotonic()+4
            self.messages.append('Najprv Export, alebo klikni Nové znovu do 4 sekúnd.')
            return
        self.playback.stop()
        self.playback.events = []
        self.demo_start = None
        self.app.reset()
        self.dirty = False

    def toggle_mute(self, track_id):
        muted = not self.app.track_manager.mute[track_id]
        self.app.track_manager.set_mute(track_id,muted)
        if muted:
            self.playback.release_channel(track_id-1)

    def quit(self):
        if self.dirty and (self.confirm_action != 'quit' or time.monotonic() > self.confirm_until):
            self.confirm_action = 'quit'
            self.confirm_until = time.monotonic()+4
            self.messages.append('Neuložená hra: Export alebo ukonči znovu do 4 sekúnd.')
            return
        self.running = False

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            self.quit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                self.toggle_playback()
            elif event.key == pygame.K_ESCAPE:
                self.quit()
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for rect, action in self.buttons:
                if rect.collidepoint(event.pos):
                    action()
                    break
        elif event.type == pygame.DROPFILE:
            if self.dirty:
                self.messages.append('Pred otvorením MIDI najprv Export alebo Nové.')
            else:
                self.load(event.file)

    def tick(self):
        self._demo_tick()
        before = sum(len(es) for es in self.app.track_system.recorded_events.values())
        self.app.drain()
        after = sum(len(es) for es in self.app.track_system.recorded_events.values())
        self.dirty = self.dirty or after > before
        while not self.app.errors.empty():
            self.messages.append(self.app.errors.get_nowait())
        try:
            self.playback.update()
        except Exception as error:
            self.messages.append('MIDI výstup zastavený: '+str(error))
            port = self.playback.output
            self.playback.output = None
            self.output_index = -1
            self.playback.stop()
            if port is not None:
                try:
                    port.close()
                except Exception:
                    pass
        self.frame_count += 1

    def _text(self, text, x, y, color=(220,230,235), small=False):
        self.screen.blit((self.small if small else self.font).render(str(text),True,color),(x,y))

    def render(self):
        self.screen.fill((17,22,30))
        self._text('SIRIUS MIDI | Notácia, záznam a MIDI prehrávanie',20,12,(80,220,235))
        self.buttons = []
        actions = [('Obnoviť',self.refresh_devices),('Vstup >',self.select_input),('Pripojiť',self.connect),
                   ('Stop vstup',self.app.stop_input),('DEMO',self.start_demo),('Export',self.export),
                   ('Otvoriť',self.open_dialog),('Hrať/Pauza',self.toggle_playback),
                   ('Stop',self.playback.stop),('Výstup >',self.select_output),('Nové',self.clear)]
        for index,(label,action) in enumerate(actions):
            rect = pygame.Rect(20+index*112,45,105,32)
            pygame.draw.rect(self.screen,(35,60,75),rect,border_radius=4)
            self._text(label,rect.x+7,rect.y+6,small=True)
            self.buttons.append((rect,action))
        device = self.devices[self.input_index] if self.devices else 'bez zariadenia'
        output = self.outputs[self.output_index] if self.output_index >= 0 else 'iba vizuálne'
        self._text('Vstup: '+device[:55]+'   |   Výstup: '+output[:45],20,86,small=True)
        model = self.app.track_system
        self._text(f'Noty: {len(model.notes)}  Akord: {self.app.current_chord or "—"}  Odhad tóniny: {self.app.current_key or "—"}  Velocity: {self.app.last_velocity or "—"} (nie dB)',20,110)
        self._text('MIDI vstup: '+('pripojený' if self.app.listener and self.app.listener.running else 'zastavený')+f' | Stratené udalosti: {self.app.dropped}',20,137,small=True)
        self._draw_staff(model)
        self.timeline.draw(self.screen,model.notes,self.playback.position_sec if self.playback.events else max(model.last_time,model.clock()-model.origin),(20,360))
        active = set(model.active)
        if self.playback.events:
            active = set(self.playback.active)
        self.piano.clear()
        for channel,pitch in active:
            if self.app.track_manager.is_effectively_active(channel+1):
                self.piano.highlight_key(pitch)
        self.piano.draw(self.screen.subsurface(pygame.Rect(20,530,1240,150)))
        for i in range(16):
            x = 20+i*77
            color = model.get_track_color(i+1)
            self._text(str(i+1),x,687,color,small=True)
            self._text(str(len(model.recorded_events[i+1])),x+23,687,small=True)
            rect = pygame.Rect(x,684,72,28)
            if self.app.track_manager.mute[i+1]:
                pygame.draw.line(self.screen,(240,80,80),rect.topleft,rect.bottomright,2)
            self.buttons.append((rect,lambda tid=i+1: self.toggle_mute(tid)))
        for i,message in enumerate(self.messages):
            self._text(message[:150],20,716+i*18,small=True)
        pygame.display.flip()

    def _draw_staff(self, model):
        # Basic note preview, not a complete engraving or accidental spelling engine.
        for base in (245,350):
            for line in range(5):
                y = base-line*10
                pygame.draw.line(self.screen,(100,120,140),(25,y),(1250,y))
        pitch_steps = [0,0,1,1,2,3,3,4,4,5,5,6]
        notes = model.notes[-38:]
        for index,note in enumerate(notes):
            pitch = note['pitch']
            # C4 is one ledger line below the treble staff; C3 uses the bass staff.
            step = (pitch//12-5)*7+pitch_steps[pitch%12]
            if pitch >= 60:
                y = 255-step*5
            else:
                y = 335-(step+7)*5
            x = 48+index*31
            color = model.get_track_color(note['track_id'])
            names = ['C','C#','D','D#','E','F','F#','G','G#','A','A#','B']
            label = names[pitch%12]+str(pitch//12-1)
            if not 175 <= y <= 355:
                self._text(label,x,175,(240,180,80),small=True)
                continue
            pygame.draw.ellipse(self.screen,color,(x,y-4,12,8))
            pygame.draw.line(self.screen,color,(x+11,y),(x+11,y-25),2)
            if pitch%12 in (1,3,6,8,10):
                self._text('#',x-10,y-10,small=True)
            if pitch == 60:
                pygame.draw.line(self.screen,color,(x-3,y),(x+15,y))
            self._text(label,x-2,178,color,small=True)

    def run(self, max_frames=None):
        clock = pygame.time.Clock()
        try:
            while self.running:
                for event in pygame.event.get():
                    try:
                        self.handle_event(event)
                    except Exception as error:
                        self.messages.append('Chyba: '+str(error))
                self.tick()
                self.render()
                if max_frames and self.frame_count >= max_frames:
                    self.running = False
                clock.tick(60)
        finally:
            try:
                self.playback.shutdown()
            finally:
                self.app.shutdown()
                pygame.quit()
