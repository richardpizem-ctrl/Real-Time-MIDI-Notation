import time
from notation_engine.midi_note_mapper import MidiNoteMapper
from renderer.notation_renderer import NotationRenderer

class StreamHandler:
    def __init__(self):
        # MIDI → Note mapper
        self.mapper = MidiNoteMapper()

        # Renderer pre zobrazovanie nôt
        self.renderer = NotationRenderer()

        # Callback keď mapper vytvorí hotovú notu
        self.mapper.on_note_created = self._on_note_created

    def _on_note_created(self, note):
        # Odovzdáme hotovú notu rendereru
        self.renderer.add_note(note)

    def process_midi_message(self, msg):
        """
        msg: objekt z mido alebo rtmidi
        msg.type: 'note_on' alebo 'note_off'
        msg.note: pitch
        msg.velocity: 0–127
        msg.channel: 0–15
        """

        timestamp = time.time()

        # NOTE ON (velocity > 0)
        if msg.type == "note_on" and msg.velocity > 0:
            self.mapper.handle_note_on(
                pitch=msg.note,
                velocity=msg.velocity,
                channel=msg.channel,
                timestamp=timestamp
            )

        # NOTE OFF (alebo note_on s velocity 0)
        elif msg.type in ("note_off", "note_on") and msg.velocity == 0:
            self.mapper.handle_note_off(
                pitch=msg.note,
                channel=msg.channel,
                timestamp=timestamp
            )
