# real_time_processing/stream_handler.py

from notation_engine.chord_detector import detect_chord

class StreamHandler:
    def __init__(self, piano_roll_ui=None, staff_ui=None, note_visualizer=None, track_system=None):
        """
        piano_roll_ui = inštancia PianoRollUI
        staff_ui = inštancia StaffUI
        note_visualizer = inštancia NoteVisualizerUI
        track_system = TrackSystem (16 MIDI stôp)
        """
        self.active_notes = []
        self.piano_roll = piano_roll_ui
        self.staff_ui = staff_ui
        self.note_visualizer = note_visualizer
        self.track_system = track_system

    # ---------------------------------------------------------
    # HLAVNÉ SPRACOVANIE MIDI SPRÁV
    # ---------------------------------------------------------
    def process_midi_message(self, message):
        """
        message.type: "note_on" / "note_off"
        message.note: MIDI nota (0–127)
        message.velocity: 0–127
        message.channel: MIDI kanál (0–15)
        """

        midi_channel = message.channel + 1  # MIDI kanály sú 1–16

        # ---------------------------------------------------------
        # 🔥 AUTOMATICKÉ PREPNUTIE TRACKU PODĽA KANÁLA
        # ---------------------------------------------------------
        if self.track_system:
            self.track_system.set_active_track_by_channel(midi_channel)

        # ---------------------------------------------------------
        # NOTE ON
        # ---------------------------------------------------------
        if message.type == "note_on" and message.velocity > 0:

            # pridaj do aktívnych nôt
            if message.note not in self.active_notes:
                self.active_notes.append(message.note)

            # 🔥 vytvorenie eventu v TrackSysteme
            if self.track_system:
                event = self.track_system.build_note_event_for_active_track(
                    note=message.note,
                    velocity=message.velocity,
                    event_type="note_on"
                )
            else:
                event = None

            # 🔥 Piano Roll UI
            if self.piano_roll:
                color = event["track_color"] if event else (255, 80, 80)
                self.piano_roll.highlight_key(
                    midi_note=message.note,
                    color=color
                )

            # 🔥 Staff UI
            if self.staff_ui and event:
                self.staff_ui.add_note(event)

            # 🔥 Note Visualizer
            if self.note_visualizer and event:
                self.note_visualizer.on_note(event)

        # ---------------------------------------------------------
        # NOTE OFF
        # ---------------------------------------------------------
        elif message.type == "note_off" or (message.type == "note_on" and message.velocity == 0):

            # odstráň z aktívnych nôt
            if message.note in self.active_notes:
                self.active_notes.remove(message.note)

            # 🔥 vytvorenie eventu v TrackSysteme
            if self.track_system:
                event = self.track_system.build_note_event_for_active_track(
                    note=message.note,
                    velocity=0,
                    event_type="note_off"
                )
            else:
                event = None

            # 🔥 Piano Roll UI
            if self.piano_roll:
                self.piano_roll.unhighlight_key(message.note)

            # 🔥 Staff UI
            if self.staff_ui and event:
                self.staff_ui.remove_note(event)

            # 🔥 Note Visualizer
            if self.note_visualizer and event:
                self.note_visualizer.on_note_off(event)

        # ---------------------------------------------------------
        # DETEKCIA AKORDU
        # ---------------------------------------------------------
        chord = detect_chord(self.active_notes)
        if chord:
            print(f"Detected chord: {chord.name}")
        else:
            print("No chord detected")

    # Hook pre budúce použitie
    def _on_note_created(self, note):
        pass
