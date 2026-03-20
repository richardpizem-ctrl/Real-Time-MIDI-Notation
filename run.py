# --- GRAFICKÁ NOTOVÁ OSNOVA S POSÚVANÍM, AKORDAMI, RYTMICKÝMI HODNOTAMI A TAKTOVÝMI ČIARAMI ---
class StaffUI:
    def __init__(self):
        self.root = tk.Toplevel()
        self.root.title("Notová osnova")
        self.root.geometry("600x240")
        self.root.resizable(False, False)

        self.canvas_width = 600
        self.canvas_height = 240
        self.canvas = tk.Canvas(self.root, width=self.canvas_width, height=self.canvas_height, bg="white")
        self.canvas.pack()

        # 5 liniek
        self.staff_y = [60, 80, 100, 120, 140]
        for y in self.staff_y:
            self.canvas.create_line(20, y, self.canvas_width - 20, y, width=2)

        # Aktívne noty: note -> {id, x, y, color, start}
        self.active_notes = {}

        # Hotové rytmické symboly
        self.finished_notes = []

        # Taktové čiary
        self.bar_lines = []
        self.bar_spacing = 120  # px medzi taktmi
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

        # akord = viac nôt naraz → farba červená
        color = "red" if len(self.active_notes) > 0 else "black"

        dot_id = self.canvas.create_oval(x-6, y-6, x+6, y+6, fill=color, outline=color)

        self.active_notes[note] = {
            "id": dot_id,
            "x": x,
            "y": y,
            "color": color,
            "start": time.time()
        }

    def note_off(self, note):
        if note not in self.active_notes:
            return

        data = self.active_notes[note]
        duration = time.time() - data["start"]

        # Vymažeme pôvodnú bodku
        self.canvas.delete(data["id"])

        # Určíme rytmický symbol
        if duration > 0.60:
            symbol = "○"   # polová
        elif duration > 0.30:
            symbol = "●"   # štvrťová
        elif duration > 0.15:
            symbol = "♪"   # osminová
        else:
            symbol = "♫"   # šestnástinová

        text_id = self.canvas.create_text(
            data["x"], data["y"],
            text=symbol,
            font=("Arial", 20),
            fill=data["color"]
        )

        self.finished_notes.append({
            "id": text_id,
            "x": data["x"],
            "y": data["y"]
        })

        del self.active_notes[note]

    def scroll(self):
        # Posúvame aktívne noty
        for note, data in list(self.active_notes.items()):
            new_x = data["x"] - self.scroll_speed
            dx = -self.scroll_speed
            self.canvas.move(data["id"], dx, 0)
            data["x"] = new_x

            if new_x < 0:
                self.canvas.delete(data["id"])
                del self.active_notes[note]

        # Posúvame hotové rytmické symboly
        to_delete = []
        for item in self.finished_notes:
            new_x = item["x"] - self.scroll_speed
            dx = -self.scroll_speed
            self.canvas.move(item["id"], dx, 0)
            item["x"] = new_x

            if new_x < 0:
                to_delete.append(item)

        for item in to_delete:
            self.canvas.delete(item["id"])
            self.finished_notes.remove(item)

        # Posúvame taktové čiary
        bar_delete = []
        for bar in self.bar_lines:
            new_x = bar["x"] - self.scroll_speed
            dx = -self.scroll_speed
            self.canvas.move(bar["id"], dx, 0)
            bar["x"] = new_x

            if new_x < 0:
                bar_delete.append(bar)

        # Odstránenie starých taktových čiar
        for bar in bar_delete:
            self.canvas.delete(bar["id"])
            self.bar_lines.remove(bar)

        # Pridanie novej taktovej čiary na pravý okraj
        if len(self.bar_lines) == 0 or self.bar_lines[-1]["x"] < self.canvas_width - self.bar_spacing:
            new_x = self.canvas_width - 20
            line_id = self.canvas.create_line(new_x, 50, new_x, 150, width=2)
            self.bar_lines.append({"id": line_id, "x": new_x})

        self.root.after(50, self.scroll)
