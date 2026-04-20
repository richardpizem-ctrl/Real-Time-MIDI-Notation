class AIEngine:
    """
    Central AI manager for Real-Time MIDI Notation Engine.
    Routes data to quantizer, interpretation and notation modules.
    """

    def __init__(self, quantizer=None, interpreter=None, notation_engine=None):
        self.quantizer = quantizer
        self.interpreter = interpreter
        self.notation_engine = notation_engine

    def process_quantization(self, midi_events):
        if self.quantizer:
            return self.quantizer.process(midi_events)
        return midi_events

    def analyze_performance(self, performance_data):
        if self.interpreter:
            return self.interpreter.analyze(performance_data)
        return performance_data

    def generate_notation(self, score_data):
        if self.notation_engine:
            return self.notation_engine.generate(score_data)
        return score_data
