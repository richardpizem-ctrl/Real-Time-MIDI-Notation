from notation_engine.note_mapper import NoteMapper
from notation_engine.layout_engine import LayoutEngine
from ui_components.text_renderer import TextRenderer

# Testovacie symboly (simulujeme výstup z NotationEngine)
test_symbols = [
    {"type": "note", "pitch": 60, "duration": 0.25},
    {"type": "note", "pitch": 62, "duration": 0.5},
    {"type": "note", "pitch": 64, "duration": 1.0},
    {"type": "barline"},
    {"type": "note", "pitch": 65, "duration": 0.25},
    {"type": "note", "pitch": 67, "duration": 0.25},
]

def main():
    print("=== TEST BEZ MIDI ===")

    # 1) Mapovanie nôt (ak by bolo treba)
    mapper = NoteMapper()
    mapped = [mapper.map_symbol(s) for s in test_symbols]

    # 2) Layout engine
    layout = LayoutEngine()
    laid_out = layout.apply_layout(mapped)

    # 3) Text renderer
    renderer = TextRenderer()
    output = renderer.render(laid_out)

    print("\n=== VÝSTUP ===")
    print(output)

if __name__ == "__main__":
    main()
