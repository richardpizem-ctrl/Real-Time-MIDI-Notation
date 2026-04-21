"""
selection_actions.py – FÁZA 4
Modul pre operácie nad vybranými notami:
    - delete
    - move
    - transpose
    - velocity adjust
    - stretch (optional)
Bez zásahu do NotesLayer – pracuje len s dátovou štruktúrou nôt.
"""


def delete_selected_notes(notes: list, selected_indices: list) -> list:
    """
    Vymaže noty podľa indexov.
    Vracia NOVÝ zoznam nôt (immutabilita pre bezpečnosť).
    """
    if not notes or not selected_indices:
        return notes

    selected_set = set(selected_indices)
    return [n for i, n in enumerate(notes) if i not in selected_set]


def move_selected_notes(notes: list, selected_indices: list, dx: int, dy: int) -> list:
    """
    Posunie vybrané noty o dx, dy.
    Vracia nový zoznam nôt.
    """
    if not notes or not selected_indices:
        return notes

    new_notes = []
    selected_set = set(selected_indices)

    for i, note in enumerate(notes):
        if i in selected_set:
            nn = dict(note)
            nn["x"] = note.get("x", 0) + dx
            nn["y"] = note.get("y", 0) + dy
            new_notes.append(nn)
        else:
            new_notes.append(note)

    return new_notes


def transpose_selected_notes(notes: list, selected_indices: list, semitones: int) -> list:
    """
    Transponuje pitch vybraných nôt.
    Očakáva, že nota má kľúč 'pitch'.
    """
    if not notes or not selected_indices:
        return notes

    new_notes = []
    selected_set = set(selected_indices)

    for i, note in enumerate(notes):
        if i in selected_set:
            nn = dict(note)
            nn["pitch"] = note.get("pitch", 60) + semitones
            new_notes.append(nn)
        else:
            new_notes.append(note)

    return new_notes


def velocity_selected_notes(notes: list, selected_indices: list, delta: int) -> list:
    """
    Zmení velocity vybraných nôt.
    """
    if not notes or not selected_indices:
        return notes

    new_notes = []
    selected_set = set(selected_indices)

    for i, note in enumerate(notes):
        if i in selected_set:
            nn = dict(note)
            nn["velocity"] = max(1, min(127, note.get("velocity", 100) + delta))
            new_notes.append(nn)
        else:
            new_notes.append(note)

    return new_notes


def stretch_selected_notes(notes: list, selected_indices: list, factor: float) -> list:
    """
    Natiahne alebo skráti dĺžku nôt (duration).
    """
    if not notes or not selected_indices:
        return notes

    new_notes = []
    selected_set = set(selected_indices)

    for i, note in enumerate(notes):
        if i in selected_set:
            nn = dict(note)
            dur = note.get("duration", 1.0)
            nn["duration"] = max(0.05, dur * factor)
            new_notes.append(nn)
        else:
            new_notes.append(note)

    return new_notes
