from notation_engine.chord_detector import detect_chord

print(detect_chord([60, 64, 67]))  # C E G
print(detect_chord([57, 60, 64]))  # A C E
print(detect_chord([62, 65, 69]))  # D F# A
