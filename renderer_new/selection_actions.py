# =========================================================
# selection_actions.py v2.0.0
# Stabilné operácie nad vybranými notami (immutable workflow)
# =========================================================

from typing import List, Dict, Any, Tuple


# -------------------------------------------------------------
# HELPERS
# -------------------------------------------------------------
def clone_note(note: Dict[str, Any]) -> Dict[str, Any]:
    """Bezpečne klonuje notu (immutable workflow)."""
    return dict(note) if isinstance(note, dict) else {}


# -------------------------------------------------------------
# DELETE
# -------------------------------------------------------------
def delete_selected_notes(
    notes: List[Dict[str, Any]],
    selected_indices: List[int]
) -> List[Dict[str, Any]]:
    """Vymaže noty podľa indexov. Vracia nový zoznam nôt."""
    if not notes or not selected_indices:
        return notes

    selected_set = set(selected_indices)
    return [n for i, n in enumerate(notes) if i not in selected_set]


# -------------------------------------------------------------
# MOVE
# -------------------------------------------------------------
def move_selected_notes(
    notes: List[Dict[str, Any]],
    selected_indices: List[int],
    dx: int,
    dy: int
) -> List[Dict[str, Any]]:
    """Posunie vybrané noty o dx, dy. Vracia nový zoznam nôt."""
    if not notes or not selected_indices:
        return notes

    new_notes: List[Dict[str, Any]] = []
    selected_set = set(selected_indices)

    for i, note in enumerate(notes):
        if i in selected_set:
            nn = clone_note(note)
            nn["x"] = int(note.get("x", 0)) + dx
            nn["y"] = int(note.get("y", 0)) + dy
            new_notes.append(nn)
        else:
            new_notes.append(note)

    return new_notes


# -------------------------------------------------------------
# TRANSPOSE
# -------------------------------------------------------------
def transpose_selected_notes(
    notes: List[Dict[str, Any]],
    selected_indices: List[int],
    semitones: int
) -> List[Dict[str, Any]]:
    """Transponuje pitch vybraných nôt."""
    if not notes or not selected_indices:
        return notes

    new_notes: List[Dict[str, Any]] = []
    selected_set = set(selected_indices)

    for i, note in enumerate(notes):
        if i in selected_set:
            nn = clone_note(note)
            nn["pitch"] = int(note.get("pitch", 60)) + semitones
            new_notes.append(nn)
        else:
            new_notes.append(note)

    return new_notes


# -------------------------------------------------------------
# VELOCITY
# -------------------------------------------------------------
def velocity_selected_notes(
    notes: List[Dict[str, Any]],
    selected_indices: List[int],
    delta: int
) -> List[Dict[str, Any]]:
    """Zmení velocity vybraných nôt (1–127)."""
    if not notes or not selected_indices:
        return notes

    new_notes: List[Dict[str, Any]] = []
    selected_set = set(selected_indices)

    for i, note in enumerate(notes):
        if i in selected_set:
            nn = clone_note(note)
            vel = int(note.get("velocity", 100)) + delta
            nn["velocity"] = max(1, min(127, vel))
            new_notes.append(nn)
        else:
            new_notes.append(note)

    return new_notes


# -------------------------------------------------------------
# STRETCH
# -------------------------------------------------------------
def stretch_selected_notes(
    notes: List[Dict[str, Any]],
    selected_indices: List[int],
    factor: float
) -> List[Dict[str, Any]]:
    """Natiahne alebo skráti duration vybraných nôt."""
    if not notes or not selected_indices:
        return notes

    new_notes: List[Dict[str, Any]] = []
    selected_set = set(selected_indices)

    for i, note in enumerate(notes):
        if i in selected_set:
            nn = clone_note(note)
            dur = float(note.get("duration", 1.0))
            nn["duration"] = max(0.05, dur * factor)
            new_notes.append(nn)
        else:
            new_notes.append(note)

    return new_notes


# -------------------------------------------------------------
# MULTI-ACTION PIPELINE
# -------------------------------------------------------------
def apply_actions(
    notes: List[Dict[str, Any]],
    selected_indices: List[int],
    actions: List[Tuple]
) -> List[Dict[str, Any]]:
    """
    Umožňuje aplikovať viac akcií naraz.
    actions = [
        ("move", dx, dy),
        ("transpose", semitones),
        ("velocity", delta),
        ("stretch", factor),
        ("delete",),
    ]
    """
    if not notes or not actions:
        return notes

    result = notes

    for action in actions:
        if not isinstance(action, tuple) or not action:
            continue

        name = action[0]

        if name == "move" and len(action) == 3:
            result = move_selected_notes(result, selected_indices, action[1], action[2])

        elif name == "transpose" and len(action) == 2:
            result = transpose_selected_notes(result, selected_indices, action[1])

        elif name == "velocity" and len(action) == 2:
            result = velocity_selected_notes(result, selected_indices, action[1])

        elif name == "stretch" and len(action) == 2:
            result = stretch_selected_notes(result, selected_indices, action[1])

        elif name == "delete":
            result = delete_selected_notes(result, selected_indices)

    return result
