import pygame
import math
import time


class NoteVisualizerUI:
    """
    Jednoduchý vizualizér MIDI nôt s pulzovaním podľa BPM.
    Každá nota vytvorí farebný pulz, ktorý postupne mizne.
    """

    def __init__(self, width=1400, height=200):
        self.width = width
        self.height = height

        # aktívne pulzy: midi -> {color, timestamp}
        self.active_notes = {}

        # BPM pulz
        self.bpm = 120
        self.last_pulse_time = time.time()

        pygame.font.init()
        try:
            self.font = pygame.font.SysFont("Arial", 14)
        except Exception:
            self.font = None

    # ---------------------------------------------------------
    # PUBLIC API (pre UIManager – bezpečné no-op metódy)
    # ---------------------------------------------------------
    def update_color(self, track_index: int, color_hex: str):
        return

    def update_visibility(self, track_index: int, visible: bool):
        return

    def set_active_track(self, track_index: int):
        return

    # ---------------------------------------------------------
    # BPM PULSE
    # ---------------------------------------------------------
    def update_bpm_pulse(self, bpm, timestamp):
        """Aktualizuje BPM pulz (volané z UIManager)."""
        try:
            self.bpm = max(1, int(bpm))
        except Exception:
            self.bpm = 120

        self.last_pulse_time = timestamp

    # ---------------------------------------------------------
    # NOTE EVENTS
    # ---------------------------------------------------------
    def on_note(self, event):
        """
        event:
            note
            track_color
            time
        """
        midi = event.get("note")
        if midi is None:
            return

        color = event.get("track_color", (255, 80, 80))
        if not isinstance(color, (tuple, list)) or len(color) != 3:
            color = (255, 80, 80)

        self.active_notes[midi] = {
            "color": color,
            "timestamp": time.time()
        }

    def on_note_off(self, event):
        midi = event.get("note")
        if midi in self.active_notes:
            del self.active_notes[midi]

    # ---------------------------------------------------------
    # DRAW
    # ---------------------------------------------------------
    def draw(self, surface):
        if surface is None:
            return

        surface.fill((20, 20, 20))
        now = time.time()

        # BPM pulz (globálny)
        beat_interval = 60.0 / max(1, self.bpm)
        beat_phase = (now - self.last_pulse_time) / beat_interval
        beat_strength = max(0.0, 1.0 - beat_phase)

        # pozadie pulzu
        bg_intensity = int(beat_strength * 40)
        pygame.draw.rect(surface, (bg_intensity, bg_intensity, bg_intensity),
                         (0, 0, self.width, self.height))

        # NOTE PULZY
        for midi, data in list(self.active_notes.items()):
            color = data.get("color", (255, 80, 80))
            t = data.get("timestamp", now)

            fade = max(0.0, 1.0 - (now - t) * 1.2)

            if fade <= 0:
                del self.active_notes[midi]
                continue

            # pozícia podľa MIDI výšky
            y = int(self.height - (midi - 36) * 2.2)
            y = max(0, min(self.height, y))

            x = int((midi * 37) % self.width)

            radius = int(20 + fade * 40)

            pulsed_color = (
                int(color[0] * fade),
                int(color[1] * fade),
                int(color[2] * fade),
            )

            pygame.draw.circle(surface, pulsed_color, (x, y), radius)

        # oddelovacia čiara
        pygame.draw.line(surface, (80, 80, 80),
                         (0, self.height - 2),
                         (self.width, self.height - 2), 2)
