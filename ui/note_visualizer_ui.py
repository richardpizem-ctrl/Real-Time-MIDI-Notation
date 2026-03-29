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

    def update_bpm_pulse(self, bpm, timestamp):
        if bpm is None:
            self.pulse_strength = 1.0
            return

        beat_interval = 60.0 / bpm
        phase = (timestamp % beat_interval) / beat_interval
        self.pulse_strength = 1.0 + 0.15 * math.sin(phase * math.pi * 2)

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

    def draw(self, surface):
        if not self.active_notes:
            return
