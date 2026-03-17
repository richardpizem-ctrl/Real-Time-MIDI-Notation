# Stream Handler – orchestrates real-time MIDI → notation pipeline

from ..core.logger import Logger
from ..midi_input.event_router import EventRouter
from ..notation_engine.note_mapper import NoteMapper
from ..notation_engine.rhythm_analyzer import RhythmAnalyzer
from ..notation_engine.notation_renderer import NotationRenderer

class StreamHandler:
    def __init__(self, event_bus, tempo_bpm=120):
        self.event_bus = event_bus
        self.router = EventRouter(event_bus)
        self.mapper = NoteMapper()
        self.analyzer = RhythmAnalyzer(tempo_bpm)
        self.renderer = NotationRenderer()

        self.buffer = []  # stores note events with timestamps

        Logger.info("StreamHandler initialized.")

    def process_event(self, midi_event):
        """Main entry point for real-time MIDI events."""
        try:
            # Route raw event
            self.router.route(midi_event)

            # Only process note_on events for notation
            if midi_event.get("type") == "note_on":
                mapped = NoteMapper.midi_to_note(midi_event["note"])
                if mapped:
                    mapped["timestamp"] = midi_event["timestamp"]
                    self.buffer.append(mapped)

            # If we have at least 2 notes, analyze rhythm
            if len(self.buffer) >= 2:
                analyzed = self.analyzer.analyze(self.buffer)
                rendered = self.renderer.render(analyzed)
                return rendered

            return None

        except Exception as e:
            Logger.error(f"StreamHandler error: {e}")
            return None

