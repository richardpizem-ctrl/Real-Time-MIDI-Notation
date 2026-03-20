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

    def note_on(self, note):
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

    def note_off(self, note):
        if note not in self.active_notes:
            return

        data = self.active_notes[note]
        duration = time.time() - data["start"]

        # odstránime bodku
        self.canvas.delete(data["id"])

        # rytmický symbol
        if duration > 0.60:
            symbol = "○"
        elif duration > 0.30:
            symbol = "●"
        elif duration > 0.15:
            symbol = "♪"
        else:
            symbol = "♫"

        # akord ešte nie je kompletný
        if note in self.active_chord:
            self.active_chord.remove(note)

        # čakáme, kým všetky noty akordu dostanú note_off
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

        # hotové rytmické symboly (aj akordy)
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
