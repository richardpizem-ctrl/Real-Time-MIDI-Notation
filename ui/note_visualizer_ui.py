import pygame
import time
import math

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
    (0, 4, 7): ("Dur", (255, 220, 50)),
    (0, 3, 7): ("Mol", (80, 140, 255)),
    (0, 3, 6): ("Dim", (180, 80, 255)),
    (0, 4, 8): ("Aug", (255, 140, 60)),
    (0, 2, 7): ("Sus2", (80, 255, 220)),
    (0, 5, 7): ("Sus4", (80, 255, 220)),
    (0, 7):    ("Power", (230, 230, 230)),
    (0, 4, 7, 10): ("7", (255, 80, 80)),
}


def normalize_intervals(semitones):
    root = min(semitones)
    return tuple(sorted((s - root) % 12 for s in semitones))


class NoteVisualizerUI:
    def __init__(self, width=1400, height=200):
        self.width = width
        self.height = height

        self.active_notes = []

        self.fade_duration = 0.25
        self.fade_in_duration = 0.12

        self.pulse_strength = 1.0

        self.trail_surface = pygame.Surface((width, height), pygame.SRCALPHA)

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
    # NOTE EVENTS
    # ---------------------------------------------------------
    def on_note(self, event):
        note_name = event.get("note_name") or str(event.get("note", "?"))
        color = event.get("track_color", (255, 255, 255))
        velocity = event.get("velocity", 100)
        velocity_factor = min(1.0, velocity / 127)
        pitch = event.get("note")

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

    def on_note_off(self, event):
        note_name = event.get("note_name") or str(event.get("note", "?"))

        for n in self.active_notes:
            if n["note"] == note_name and n["fade_start"] is None:
                n["fade_start"] = time.time()
                break

    # ---------------------------------------------------------
    # CHORD COLOR
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
    # HALO / DEPTH / COLOR HELPERS
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

    def compute_depth(self, pitch):
        if pitch is None:
            return 1.0
        norm = max(0.0, min(1.0, (pitch - 36) / 48.0))
        depth = 1.3 - norm * 0.6
        return depth

    def lerp_color(self, a, b, t):
        return (
            int(a[0] + (b[0] - a[0]) * t),
            int(a[1] + (b[1] - a[1]) * t),
            int(a[2] + (b[2] - a[2]) * t),
        )

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

    def compute_interval_offsets(self, intervals):
        offsets = []

        for interval in intervals:
            if interval in (3,):
                offsets.append(40)
            elif interval in (4,):
                offsets.append(55)
            elif interval in (5,):
                offsets.append(70)
            elif interval in (7,):
                offsets.append(90)
            elif interval >= 12:
                offsets.append(120)
            else:
                offsets.append(50)

        return offsets

    # ---------------------------------------------------------
    # DRAW
    # ---------------------------------------------------------
    def draw(self, surface):
        if surface is None:
            return

        now = time.time()

        # Jemné vyblednutie trail vrstvy
        self.trail_surface.fill((0, 0, 0, 40), special_flags=pygame.BLEND_RGBA_SUB)

        # Vyčistenie hlavnej plochy
        surface.fill((10, 10, 10))

        # Chord color morph
        chord_color = self.detect_chord_color()
        if chord_color is not None:
            self.target_chord_color = chord_color

        self.current_chord_color = self.lerp_color(
            self.current_chord_color,
            self.target_chord_color,
            self.color_morph_speed
        )

        # Príprava textov pre noty
        notes_with_depth = []
        for n in self.active_notes:
            depth = self.compute_depth(n.get("pitch"))
            notes_with_depth.append((depth, n))

        # Zoradenie podľa hĺbky
        notes_with_depth.sort(key=lambda x: x[0])

        # Intervalové offsety (pripravené pre budúce efekty)
        intervals = self.compute_intervals(notes_with_depth)
        _interval_offsets = self.compute_interval_offsets(intervals)

        # Kreslenie aktívnych nôt
        remaining_notes = []
        center_x = self.width // 2
        center_y = self.height // 2

        for idx, (depth, n) in enumerate(notes_with_depth):
            fade_in_start = n["fade_in_start"]
            fade_start = n["fade_start"]

            # Fade-in
            t_in = (now - fade_in_start) / self.fade_in_duration
            t_in = max(0.0, min(1.0, t_in))

            # Fade-out
            if fade_start is not None:
                t_out = (now - fade_start) / self.fade_duration
                if t_out >= 1.0:
                    continue
                fade_factor = 1.0 - t_out
            else:
                fade_factor = 1.0

            total_alpha = t_in * fade_factor
            if total_alpha <= 0.01:
                continue

            remaining_notes.append(n)

            note_text = n["note"]
            base_color = n["color"]

            # Spojenie chord color + track color
            mixed_color = self.lerp_color(base_color, self.current_chord_color, 0.35)

            # Pulse + depth
            scale = depth * self.pulse_strength * (0.9 + 0.2 * total_alpha)

            text_surface = self.font.render(note_text, True, mixed_color)
            text_rect = text_surface.get_rect()
            text_rect.centerx = center_x
            text_rect.centery = center_y

            # Jemný offset podľa indexu
            text_rect.x += (idx - len(notes_with_depth) // 2) * 40

            # Halo
            self.draw_halo(
                self.trail_surface,
                text_surface,
                text_rect,
                mixed_color,
                n["halo_strength"] * total_alpha
            )

            # Hlavný text
            scaled_surface = pygame.transform.smoothscale(
                text_surface,
                (int(text_rect.width * scale), int(text_rect.height * scale))
            )
            scaled_rect = scaled_surface.get_rect(center=text_rect.center)

            surface.blit(self.trail_surface, (0, 0))
            surface.blit(scaled_surface, scaled_rect)

        # Aktualizuj zoznam aktívnych nôt
        self.active_notes = remaining_notes
