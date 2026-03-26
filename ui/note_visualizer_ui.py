import pygame
import time
import math

# ---------------------------------------------------------
# Pomocné tabuľky pre harmóniu
# ---------------------------------------------------------

NOTE_TO_SEMITONE = {
    "C": 0,  "C#": 1, "Db": 1,
    "D": 2,  "D#": 3, "Eb": 3,
    "E": 4,
    "F": 5,  "F#": 6, "Gb": 6,
    "G": 7,  "G#": 8, "Ab": 8,
    "A": 9,  "A#": 10, "Bb": 10,
    "B": 11
}

CHORD_PATTERNS = {
    (0, 4, 7): ("Dur", (255, 220, 50)),        # žltá
    (0, 3, 7): ("Mol", (80, 140, 255)),        # modrá
    (0, 3, 6): ("Dim", (180, 80, 255)),        # fialová
    (0, 4, 8): ("Aug", (255, 140, 60)),        # oranžová
    (0, 2, 7): ("Sus2", (80, 255, 220)),       # tyrkysová
    (0, 5, 7): ("Sus4", (80, 255, 220)),       # tyrkysová
    (0, 7):    ("Power", (230, 230, 230)),     # biela
    (0, 4, 7, 10): ("7", (255, 80, 80)),       # červená
}

def normalize_intervals(semitones):
    root = min(semitones)
    return tuple(sorted((s - root) % 12 for s in semitones))


class NoteVisualizerUI:
    def __init__(self, width=1400, height=200):
        self.width = width
        self.height = height

        # Multi-note systém
        self.active_notes = []

        # Fade parametre
        self.fade_duration = 0.25
        self.fade_in_duration = 0.12

        # BPM pulz
        self.pulse_strength = 1.0

        # Trail buffer (jemné doznievanie)
        self.trail_surface = pygame.Surface((width, height), pygame.SRCALPHA)

        # Color morphing (KROK 11)
        self.current_chord_color = (255, 255, 255)
        self.target_chord_color = (255, 255, 255)
        self.color_morph_speed = 0.12

        pygame.font.init()
        self.font_size = 64
        self.font = pygame.font.SysFont("Arial", self.font_size, bold=True)

    # ---------------------------------------------------------
    # BPM PULSE
    # ---------------------------------------------------------
    def update_bpm_pulse(self, bpm, timestamp):
        if bpm is None:
            self.pulse_strength = 1.0
            return

        beat_interval = 60.0 / bpm
        phase = (timestamp % beat_interval) / beat_interval
        self.pulse_strength = 1.0 + 0.15 * math.sin(phase * math.pi * 2)

    # ---------------------------------------------------------
    # NOTE ON
    # ---------------------------------------------------------
    def on_note(self, event):
        note_name = event.get("note_name") or str(event.get("note", "?"))
        color = event.get("track_color", (255, 255, 255))
        velocity = event.get("velocity", 100)
        velocity_factor = min(1.0, velocity / 127)
        pitch = event.get("note")  # MIDI pitch, ak je k dispozícii

        note_data = {
            "note": note_name,
            "color": color,

            "fade_in_start": time.time(),
            "fade_start": None,

            "bounce": 1.0 * velocity_factor,
            "glow": 1.0 * velocity_factor,
            "halo_strength": 1.0 * velocity_factor,

            "pitch": pitch,
        }

        self.active_notes.append(note_data)

    # ---------------------------------------------------------
    # NOTE OFF
    # ---------------------------------------------------------
    def on_note_off(self, event):
        note_name = event.get("note_name") or str(event.get("note", "?"))

        for n in self.active_notes:
            if n["note"] == note_name and n["fade_start"] is None:
                n["fade_start"] = time.time()
                break

    # ---------------------------------------------------------
    # HARMONICKÁ ANALÝZA
    # ---------------------------------------------------------
    def detect_chord_color(self):
        if len(self.active_notes) < 2:
            return None

        semitones = []
        for n in self.active_notes:
            name = ''.join([c for c in n["note"] if c.isalpha() or c in "#b"])
            if name in NOTE_TO_SEMITONE:
                semitones.append(NOTE_TO_SEMITONE[name])

        if not semitones:
            return None

        intervals = normalize_intervals(semitones)

        if intervals in CHORD_PATTERNS:
            _, color = CHORD_PATTERNS[intervals]
            return color

        return None

    # ---------------------------------------------------------
    # HALO EFEKT
    # ---------------------------------------------------------
    def draw_halo(self, surface, text_surface, rect, color, strength):
        halo_surface = pygame.Surface((rect.width + 40, rect.height + 40), pygame.SRCALPHA)

        halo_color = (
            min(255, color[0]),
            min(255, color[1]),
            min(255, color[2]),
            int(80 * strength)
        )

        for dx in range(-4, 5):
            for dy in range(-4, 5):
                halo_surface.blit(
                    text_surface,
                    (20 + dx, 20 + dy),
                    special_flags=pygame.BLEND_RGBA_ADD
                )

        halo_surface.fill(halo_color, special_flags=pygame.BLEND_RGBA_MULT)
        surface.blit(halo_surface, (rect.x - 20, rect.y - 20))

    # ---------------------------------------------------------
    # VÝPOČET HĹBKY PODĽA PITCH
    # ---------------------------------------------------------
    def compute_depth(self, pitch):
        if pitch is None:
            return 1.0
        # normalizácia približne pre rozsah 36–84
        norm = max(0.0, min(1.0, (pitch - 36) / 48.0))
        # nízke tóny bližšie (väčšie), vysoké ďalej (menšie)
        depth = 1.3 - norm * 0.6  # 1.3 → 0.7
        return depth

    # ---------------------------------------------------------
    # COLOR LERP (KROK 11)
    # ---------------------------------------------------------
    def lerp_color(self, a, b, t):
        return (
            int(a[0] + (b[0] - a[0]) * t),
            int(a[1] + (b[1] - a[1]) * t),
            int(a[2] + (b[2] - a[2]) * t),
        )

    # ---------------------------------------------------------
    # INTERVALY – výpočet intervalov medzi pitch hodnotami
    # ---------------------------------------------------------
    def compute_intervals(self, notes_with_depth):
        pitches = [n["pitch"] for _, n in notes_with_depth if n.get("pitch") is not None]
        if len(pitches) < 2:
            return []

        pitches = sorted(pitches)
        intervals = []

        for i in range(len(pitches) - 1):
            interval = abs(pitches[i + 1] - pitches[i])
            intervals.append(interval)

        return intervals

    # ---------------------------------------------------------
    # INTERVALY – prepočet vizuálnych rozostupov
    # ---------------------------------------------------------
    def compute_interval_offsets(self, intervals):
        offsets = []

        for interval in intervals:
            if interval in (3,):          # malá tercia
                offsets.append(40)
            elif interval in (4,):        # veľká tercia
                offsets.append(55)
            elif interval in (5,):        # kvarta
                offsets.append(70)
            elif interval in (7,):        # kvinta
                offsets.append(90)
            elif interval >= 12:          # oktáva
                offsets.append(120)
            else:
                offsets.append(50)        # default

        return offsets

    # ---------------------------------------------------------
    # KRESLENIE
    # ---------------------------------------------------------
    def draw(self, surface):
        if not self.active_notes:
            return

        # Jemné trail doznievanie
        self.trail_surface.fill((0, 0, 0, 40), special_flags=pygame.BLEND_RGBA_SUB)
        surface.blit(self.trail_surface, (0, 0))

        # Harmónia → cieľová farba akordu
        chord_color = self.detect_chord_color()
        if chord_color:
            self.target_chord_color = chord_color

        # Color morphing – plynulý prechod medzi farbami akordov
        self.current_chord_color = self.lerp_color(
            self.current_chord_color,
            self.target_chord_color,
            self.color_morph_speed
        )

        notes_to_remove = []

        # Pripravíme si zoznam s hĺbkou
        notes_with_depth = []
        for n in self.active_notes:
            depth = self.compute_depth(n.get("pitch"))
            notes_with_depth.append((depth, n))

        # Zoradenie podľa hĺbky (vzdialenejšie najprv, bližšie nakoniec)
        notes_with_depth.sort(key=lambda x: x[0])

        count = len(notes_with_depth)
        y_base = self.height // 2

        # Intervaly a offsety pre aktuálny akord
        intervals = self.compute_intervals(notes_with_depth)
        offsets = self.compute_interval_offsets(intervals) if intervals else []

        for index, (depth, n) in enumerate(notes_with_depth):
            # základná farba z color morphingu
            color = self.current_chord_color

            # Fade-out
            if n["fade_start"] is not None:
                elapsed = time.time() - n["fade_start"]
                t = max(0.0, 1.0 - elapsed / self.fade_duration)

                if t <= 0:
                    notes_to_remove.append(n)
                    continue

                color = (
                    int(color[0] * t),
                    int(color[1] * t),
                    int(color[2] * t)
                )

            # Fade-in
            if n["fade_in_start"] is not None:
                t = (time.time() - n["fade_in_start"]) / self.fade_in_duration
                if t < 1.0:
                    alpha = max(0.0, min(1.0, t))
                    color = (
                        int(color[0] * alpha),
                        int(color[1] * alpha),
                        int(color[2] * alpha)
                    )
                else:
                    n["fade_in_start"] = None

            # BPM pulz + hĺbka
            scale = self.pulse_strength * depth

            # Bounce
            if n["bounce"] > 0:
                scale += n["bounce"] * 0.25
                n["bounce"] *= 0.85

            # Glow
            if n["glow"] > 0:
                glow_strength = int(80 * n["glow"] * depth)
                color = (
                    min(255, color[0] + glow_strength),
                    min(255, color[1] + glow_strength),
                    min(255, color[2] + glow_strength)
                )
                n["glow"] *= 0.85

            # Render textu
            scaled_font = pygame.font.SysFont("Arial", int(self.font_size * scale), bold=True)
            text_surface = scaled_font.render(n["note"], True, color)

            # Intervalové rozostupy (KROK 12)
            base_x = self.width // 2
            x_pos = base_x

            if count > 1:
                left = index - (count - 1) / 2
                if index > 0 and index - 1 < len(offsets):
                    x_pos += sum(offsets[:index]) * 0.8
                x_pos += int(left * 20)

            # Vertikálny posun podľa hĺbky (parallax)
            y_pos = int(y_base - (depth - 1.0) * 25)

            text_rect = text_surface.get_rect(center=(x_pos, y_pos))

            # HALO so zohľadnením hĺbky, farba z current_chord_color
            halo_strength = n["halo_strength"] * depth
            self.draw_halo(surface, text_surface, text_rect, self.current_chord_color, halo_strength)

            # Text
            surface.blit(text_surface, text_rect)

            # Trail buffer
            self.trail_surface.blit(text_surface, text_rect)

        # Odstránenie zaniknutých nôt
        for n in notes_to_remove:
            if n in self.active_notes:
                self.active_notes.remove(n)
