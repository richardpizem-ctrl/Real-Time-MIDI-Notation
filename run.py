from notation_engine.notation_processor import NotationProcessor
from core.track_manager import TrackSystem
import mido
import keyboard
import threading
import tkinter as tk
import time


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


# --- GRAFICKÁ NOTOVÁ OSNOVA S POSÚVANÍM A FAREBNÝMI AKORDMI ---
class StaffUI:
    def __init__(self):
        self.root = tk.Toplevel()
        self.root.title("Notová osnova")
        self.root.geometry("500x200")
        self.root.resizable(False, False)

        self.canvas_width = 500
        self.canvas_height = 200
        self.canvas = tk.Canvas(self.root, width=self.canvas_width, height=self.canvas_height, bg="white")
        self.canvas.pack()

        # 5 liniek
        self.staff_y = [40, 60, 80, 100, 120]
        for y in self.staff_y:
            self.canvas.create_line(20, y, self.canvas_width - 20, y, width=2)

        # Aktívne noty: note -> {id, x, color}
        self.drawn_notes = {}

        # Posúvanie
        self.scroll_speed = 3
        self.root.after(50, self.scroll)

        threading.Thread(target=self.root.mainloop, daemon=True).start()

    def midi_to_y(self, note):
        base_y = 80
        offset = (60 - note) * 5
        return base_y + offset

    def note_on(self, note):
        y = self.midi_to_y(note)
        x = self.canvas_width - 30

        # akord = viac nôt naraz → farba červená
        color = "red" if len(self.drawn_notes) > 0 else "black"

        dot_id = self.canvas.create_oval(x-6, y-6, x+6, y+6, fill=color, outline=color)
        self.drawn_notes[note] = {"id": dot_id, "x": x, "color": color}

    def note_off(self, note):
        # necháme notu dobehnúť – rytmika bude ďalší krok
        pass

    def scroll(self):
        to_delete = []

        for note, data in list(self.drawn_notes.items()):
            new_x = data["x"] - self.scroll_speed
            dx = -self.scroll_speed

            self.canvas.move(data["id"], dx, 0)
            data["x"] = new_x

            if new_x < 0:
                to_delete.append(note)

        for note in to_delete:
            self.canvas.delete(self.drawn_notes[note]["id"])
            del self.drawn_notes[note]

        self.root.after(50, self.scroll)


def main():
    processor = NotationProcessor()
    tracks = TrackSystem()

    ui_track = TrackIndicatorUI(tracks)
    ui_notes = NoteVisualizerUI()
    ui_staff = StaffUI()

    print("Prepínanie traktu: 1–9 alebo SHIFT+1–6 (10–16)")
    print("Čakám na MIDI vstup...")

    inputs = mido.get_input_names()
    if not inputs:
        print("Žiadny MIDI vstup nenájdený!")
        return

    midi_in = mido.open_input(inputs[0])
    print(f"Pripojené k MIDI zariadeniu: {inputs[0]}")

    for msg in midi_in:

        # Prepínač traktu
        for i in range(1, 10):
            if keyboard.is_pressed(str(i)):
                tracks.set_active_track(i)
                ui_track.update()

        for i in range(1, 7):
            if keyboard.is_pressed("shift+" + str(i)):
                tracks.set_active_track(9 + i)
                ui_track.update()

        # MIDI správy
        if msg.type == "note_on" and msg.velocity > 0:
            ui_notes.note_on(msg.note)
            ui_staff.note_on(msg.note)

            event = tracks.build_note_event_for_active_track(
                note=msg.note,
                velocity=msg.velocity,
                event_type="note_on",
                time=0.0
            )
            processor.process_midi_event(event)

        elif msg.type == "note_off" or (msg.type == "note_on" and msg.velocity == 0):
            ui_notes.note_off(msg.note)
            ui_staff.note_off(msg.note)

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
