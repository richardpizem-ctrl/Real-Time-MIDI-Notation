# --- GRAFICKÁ NOTOVÁ OSNOVA S AKORDAMI, LIGATÚRAMI, RYTMICKÝMI HODNOTAMI A TAKTAMI ---
class StaffUI:
    def __init__(self):
        self.root = tk.Toplevel()
        self.root.title("Notová osnova")
        self.root.geometry("600x260")
        self.root.resizable(False, False)

        self.canvas_width = 600
        self.canvas_height = 260
        self.canvas = tk.Canvas(self.root, width=self.canvas_width, height=self.canvas_height, bg="white")
        self.canvas.pack()

        # 5 liniek
        self.staff_y = [60, 80, 100, 120, 140]
        for y in self.staff_y:
            self.canvas.create_line(20, y, self.canvas_width - 20, y, width=2)

        # Aktívne noty
        self.active_notes = {}

        # Aktívny akord (noty, ktoré prišli naraz)
        self.active_chord = []

        # Hotové rytmické symboly (aj akordy)
        self.finished_notes = []  # {ids:[], x, y_list, symbol}

        # Ligatúry
        self.ligatures = []

        # Taktové čiary
        self.bar_lines = []
        self.bar_spacing = 120
        self.generate_initial_barlines()

        self.scroll_speed = 3
        self.root.after(50, self.scroll)

        threading.Thread(target=self.root.mainloop, daemon=True).start()

    def generate_initial_barlines(self):
        x = 100
        while x < self.canvas_width:
            line_id = self.canvas.create_line(x, 50, x, 150, width=2)
            self.bar_lines.append({"id": line_id, "x": x})
            x += self.bar_spacing

    def midi_to_y(self, note):
        base_y = 100
        offset = (60 - note) * 5
        return base_y + offset

    def note_on(self, note, track_id=None, symbol="?"):
        """
        track_id = číslo traktu (1–16)
        symbol = rytmický symbol (○ ● ♪ ♫)
        """
        y = self.midi_to_y(note)
        x = self.canvas_width - 40

        color = "red" if len(self.active_notes) > 0 else "black"

        dot_id = self.canvas.create_oval(x-6, y-6, x+6, y+6, fill=color, outline=color)

        self.active_notes[note] = {
            "id": dot_id,
            "x": x,
            "y": y,
            "color": color,
            "start": time.time()
        }

        # pridáme do akordu
        self.active_chord.append(note)
        if note in self.active_chord:
            self.active_chord.remove(note)

        # čakáme na ukončenie akordu
        if len(self.active_chord) > 0:
            del self.active_notes[note]
            return

        # všetky noty akordu sú ukončené → vykreslíme akord
        chord_notes = list(self.active_notes.keys())
        chord_data = [self.active_notes[n] for n in chord_notes]

        ids = []
        y_list = []

        for d in chord_data:
            text_id = self.canvas.create_text(
                d["x"], d["y"],
                text=symbol,
                font=("Arial", 20),
                fill=d["color"]
            )
            ids.append(text_id)
            y_list.append(d["y"])

        # číslo traktu nad akordom
        if track_id is not None:
            num_x = chord_data[0]["x"]
            num_y = min(y_list) - 18
            num_id = self.canvas.create_text(
                num_x, num_y,
                text=str(track_id),
                font=("Arial", 10),
                fill="black"
            )
            ids.append(num_id)

        self.finished_notes.append({
            "ids": ids,
            "x": chord_data[0]["x"],
            "y_list": y_list,
            "symbol": symbol
        })

        # ligatúry
        self.try_create_ligature()

        # vyčistiť aktívne noty
        for n in chord_notes:
            del self.active_notes[n]

    def try_create_ligature(self):
        if len(self.finished_notes) < 2:
            return

        last = self.finished_notes[-1]
        prev = self.finished_notes[-2]

        s1 = prev["symbol"]
        s2 = last["symbol"]

        if s1 == "♪" and s2 == "♪":
            self.create_ligature(prev, last, double=False)

        if s1 == "♫" and s2 == "♫":
            self.create_ligature(prev, last, double=True)

    def create_ligature(self, n1, n2, double=False):
        y = min(n1["y_list"] + n2["y_list"]) - 15
        x1 = n1["x"]
        x2 = n2["x"]

        line1 = self.canvas.create_line(x1, y, x2, y, width=2)
        self.ligatures.append({"id": line1, "x1": x1, "x2": x2})

        if double:
            line2 = self.canvas.create_line(x1, y - 6, x2, y - 6, width=2)
            self.ligatures.append({"id": line2, "x1": x1, "x2": x2})

    def scroll(self):
        # aktívne noty
        for note, data in list(self.active_notes.items()):
            dx = -self.scroll_speed
            self.canvas.move(data["id"], dx, 0)
            data["x"] += dx
            if data["x"] < 0:
                self.canvas.delete(data["id"])
                del self.active_notes[note]

        # hotové rytmické symboly
        for item in list(self.finished_notes):
            dx = -self.scroll_speed
            for tid in item["ids"]:
                self.canvas.move(tid, dx, 0)
            item["x"] += dx
            if item["x"] < 0:
                for tid in item["ids"]:
                    self.canvas.delete(tid)
                self.finished_notes.remove(item)

        # ligatúry
        for lig in list(self.ligatures):
            dx = -self.scroll_speed
            self.canvas.move(lig["id"], dx, 0)
            lig["x1"] += dx
            lig["x2"] += dx
            if lig["x2"] < 0:
                self.canvas.delete(lig["id"])
                self.ligatures.remove(lig)

        # taktové čiary
        for bar in list(self.bar_lines):
            dx = -self.scroll_speed
            self.canvas.move(bar["id"], dx, 0)
            bar["x"] += dx
            if bar["x"] < 0:
                self.canvas.delete(bar["id"])
                self.bar_lines.remove(bar)

        # nová taktová čiara
        if len(self.bar_lines) == 0 or self.bar_lines[-1]["x"] < self.canvas_width - self.bar_spacing:
            new_x = self.canvas_width - 20
            line_id = self.canvas.create_line(new_x, 50, new_x, 150, width=2)
            self.bar_lines.append({"id": line_id, "x": new_x})

        self.root.after(50, self.scroll)
# --- REALTIME PIANOROLL ---
class PianoRollUI:
    def __init__(self):
        self.root = tk.Toplevel()
        self.root.title("Pianoroll")
        self.root.geometry("800x300")
        self.root.resizable(False, False)

        self.canvas_width = 800
        self.canvas_height = 300
        self.canvas = tk.Canvas(self.root, width=self.canvas_width, height=self.canvas_height, bg="#111")
        self.canvas.pack()

        # Aktívne bloky: note -> {id, x, y, start, track_id, text_id}
        self.active_blocks = {}

        # Hotové bloky
        self.finished_blocks = []

        self.scroll_speed = 3
        self.root.after(50, self.scroll)

        threading.Thread(target=self.root.mainloop, daemon=True).start()

    def note_to_y(self, note):
        return self.canvas_height - (note * 2)

    def note_on(self, note, track_id=None):
        """
        track_id = číslo traktu (1–16)
        """
        y = self.note_to_y(note)
        x = self.canvas_width - 40

        block_id = self.canvas.create_rectangle(
            x, y - 6, x + 20, y + 6,
            fill="#33ccff",
            outline="#33ccff"
        )

        # číslo traktu nad blokom
        text_id = None
        if track_id is not None:
            text_id = self.canvas.create_text(
                x + 10, y - 14,
                text=str(track_id),
                font=("Arial", 10),
                fill="white"
            )

        self.active_blocks[note] = {
            "id": block_id,
            "text_id": text_id,
            "x": x,
            "y": y,
            "start": time.time(),
            "track_id": track_id
        }

    def note_off(self, note):
        if note not in self.active_blocks:
            return

        data = self.active_blocks[note]
        duration = time.time() - data["start"]

        length = max(20, int(duration * 200))

        # predĺženie bloku
        self.canvas.coords(
            data["id"],
            data["x"], data["y"] - 6,
            data["x"] + length, data["y"] + 6
        )

        self.finished_blocks.append({
            "id": data["id"],
            "text_id": data["text_id"],
            "x": data["x"],
            "y": data["y"]
        })

        del self.active_blocks[note]

    def scroll(self):
        # Aktívne bloky
        for note, data in list(self.active_blocks.items()):
            dx = -self.scroll_speed
            self.canvas.move(data["id"], dx, 0)
            if data["text_id"]:
                self.canvas.move(data["text_id"], dx, 0)

            data["x"] += dx
            if data["x"] < -200:
                self.canvas.delete(data["id"])
                if data["text_id"]:
                    self.canvas.delete(data["text_id"])
                del self.active_blocks[note]

        # Hotové bloky
        for item in list(self.finished_blocks):
            dx = -self.scroll_speed
            self.canvas.move(item["id"], dx, 0)
            if item["text_id"]:
                self.canvas.move(item["text_id"], dx, 0)

            item["x"] += dx
            if item["x"] < -200:
                self.canvas.delete(item["id"])
                if item["text_id"]:
                    self.canvas.delete(item["text_id"])
                self.finished_blocks.remove(item)

        self.root.after(50, self.scroll)
def main():
    processor = NotationProcessor()
    tracks = TrackSystem()

    ui_track = TrackIndicatorUI(tracks)
    ui_notes = NoteVisualizerUI()
    ui_staff = StaffUI()
    ui_piano = PianoRollUI()

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
        for i in range(1, 9 + 1):
            if keyboard.is_pressed(str(i)):
                tracks.set_active_track(i)
                ui_track.update()

        for i in range(1, 6 + 1):
            if keyboard.is_pressed("shift+" + str(i)):
                tracks.set_active_track(9 + i)
                ui_track.update()

        # MIDI správy
        if msg.type == "note_on" and msg.velocity > 0:

            # 1) realtime text UI
            ui_notes.note_on(msg.note)

            # 2) symbol z NotationProcessor
            symbol = processor.get_symbol_for_note(msg.note)

            # 3) StaffUI + track ID + symbol
            ui_staff.note_on(
                note=msg.note,
                track_id=tracks.active_track_id,
                symbol=symbol
            )

            # 4) PianoRollUI + track ID
            ui_piano.note_on(
                note=msg.note,
                track_id=tracks.active_track_id
            )

            # 5) zápis do TrackSystem
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
            ui_piano.note_off(msg.note)

            event = tracks.build_note_event_for_active_track(
                note=msg.note,
                velocity=0,
                event_type="note_off",
                time=0.0
            )
            processor.process_midi_event(event)

        print(f"MIDI {msg.type} → nota {msg.note} → trakt {tracks.active_track_id}")
