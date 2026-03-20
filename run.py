from notation_engine.notation_processor import NotationProcessor
from core.track_manager import TrackSystem
import mido
import keyboard
import threading
import tkinter as tk


# --- UI INDIKÁTOR AKTÍVNEHO TRAKTU ---
class TrackIndicatorUI:
    def __init__(self, track_system: TrackSystem):
        self.tracks = track_system

        self.root = tk.Tk()
        self.root.title("Aktívny trakt")
        self.root.geometry("220x90")
        self.root.resizable(False, False)

        self.label = tk.Label(
            self.root,
            text=f"Aktívny trakt: {self.tracks.active_track_id}",
            font=("Arial", 22)
        )
        self.label.pack(expand=True)

        threading.Thread(target=self.root.mainloop, daemon=True).start()

    def update(self):
        self.label.config(text=f"Aktívny trakt: {self.tracks.active_track_id}")


# --- REALTIME VIZUALIZÁCIA NÔT ---
class NoteVisualizerUI:
    def __init__(self):
        self.active_notes = set()

        self.root = tk.Toplevel()
        self.root.title("Realtime noty")
        self.root.geometry("300x200")
        self.root.resizable(False, False)

        self.label = tk.Label(
            self.root,
            text="Aktívne noty:\n(nic nehrá)",
            font=("Arial", 14),
            justify="left"
        )
        self.label.pack(expand=True)

        threading.Thread(target=self.root.mainloop, daemon=True).start()

    def note_on(self, note):
        self.active_notes.add(note)
        self.update()

    def note_off(self, note):
        if note in self.active_notes:
            self.active_notes.remove(note)
        self.update()

    def update(self):
        if not self.active_notes:
            text = "Aktívne noty:\n(nic nehrá)"
        else:
            sorted_notes = sorted(list(self.active_notes))
            text = "Aktívne noty:\n" + ", ".join(str(n) for n in sorted_notes)

        self.label.config(text=text)


def main():
    processor = NotationProcessor()
    tracks = TrackSystem()

    # UI okná
    ui_track = TrackIndicatorUI(tracks)
    ui_notes = NoteVisualizerUI()

    print("Prepínanie traktu: 1–9 alebo SHIFT+1–6 (10–16)")
    print("Čakám na MIDI vstup...")

    # MIDI vstup
    inputs = mido.get_input_names()
    if not inputs:
        print("Žiadny MIDI vstup nenájdený!")
        return

    midi_in = mido.open_input(inputs[0])
    print(f"Pripojené k MIDI zariadeniu: {inputs[0]}")

    # Hlavná slučka
    for msg in midi_in:

        # --- PREPÍNAČ TRAKTU ---
        for i in range(1, 10):
            if keyboard.is_pressed(str(i)):
                tracks.set_active_track(i)
                ui_track.update()

        for i in range(1, 7):
            if keyboard.is_pressed("shift+" + str(i)):
                tracks.set_active_track(9 + i)
                ui_track.update()

        # --- SPRACOVANIE MIDI ---
        if msg.type == "note_on" and msg.velocity > 0:
            ui_notes.note_on(msg.note)

            event = tracks.build_note_event_for_active_track(
                note=msg.note,
                velocity=msg.velocity,
                event_type="note_on",
                time=0.0
            )
            processor.process_midi_event(event)

        elif msg.type == "note_off" or (msg.type == "note_on" and msg.velocity == 0):
            ui_notes.note_off(msg.note)

            event = tracks.build_note_event_for_active_track(
                note=msg.note,
                velocity=0,
                event_type="note_off",
                time=0.0
            )
            processor.process_midi_event(event)

        print(f"MIDI {msg.type} → nota {msg.note} → trakt {tracks.active_track_id}")


if __name__ == "__main__":
    main()
