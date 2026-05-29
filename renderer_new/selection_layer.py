# =========================================================
# selection_actions.py v4.3.0
# Stabilné operácie nad vybranými notami (immutable workflow)
# Optimalizované pre Runtime 4.3.0
# =========================================================

from typing import List, Dict, Any, Tuple


# -------------------------------------------------------------
# HELPERS
# -------------------------------------------------------------
def clone_note(note: Dict[str, Any]) -> Dict[str, Any]:
    """Bezpečne klonuje notu (immutable workflow)."""
    try:
        return dict(note)
    except Exception:
        return {}


def _safe_indices(selected_indices: List[int], length: int) -> List[int]:
    """Bezpečne normalizuje indexy (odstráni nevalidné)."""
    if not selected_indices or length <= 0:
        return []
    try:
        return [i for i in selected_indices if isinstance(i, int) and 0 <= i < length]
    except Exception:
        return []


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

    valid = set(_safe_indices(selected_indices, len(notes)))
    if not valid:
        return notes

    return [n for i, n in enumerate(notes) if i not in valid]


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

    valid = set(_safe_indices(selected_indices, len(notes)))
    if not valid:
        return notes

    new_notes: List[Dict[str, Any]] = []
    dx = int(dx)
    dy = int(dy)

    for i, note in enumerate(notes):
        if i in valid:
            nn = clone_note(note)
            try:
                nn["x"] = int(note.get("x", 0)) + dx
                nn["y"] = int(note.get("y", 0)) + dy
            except Exception:
                nn["x"] = note.get("x", 0)
                nn["y"] = note.get("y", 0)
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

    valid = set(_safe_indices(selected_indices, len(notes)))
    if not valid:
        return notes

    new_notes: List[Dict[str, Any]] = []
    semitones = int(semitones)

    for i, note in enumerate(notes):
        if i in valid:
            nn = clone_note(note)
            try:
                nn["pitch"] = int(note.get("pitch", 60)) + semitones
            except Exception:
                nn["pitch"] = note.get("pitch", 60)
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

    valid = set(_safe_indices(selected_indices, len(notes)))
    if not valid:
        return notes

    new_notes: List[Dict[str, Any]] = []
    delta = int(delta)

    for i, note in enumerate(notes):
        if i in valid:
            nn = clone_note(note)
            try:
                vel = int(note.get("velocity", 100)) + delta
                nn["velocity"] = max(1, min(127, vel))
            except Exception:
                nn["velocity"] = note.get("velocity", 100)
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

    valid = set(_safe_indices(selected_indices, len(notes)))
    if not valid:
        return notes

    new_notes: List[Dict[str, Any]] = []

    try:
        factor = float(factor)
    except Exception:
        return notes

    for i, note in enumerate(notes):
        if i in valid:
            nn = clone_note(note)
            try:
                dur = float(note.get("duration", 1.0))
                nn["duration"] = max(0.05, dur * factor)
            except Exception:
                nn["duration"] = note.get("duration", 1.0)
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

    valid = _safe_indices(selected_indices, len(notes))
    if not valid:
        return notes

    result = notes

    for action in actions:
        if not isinstance(action, tuple) or not action:
            continue

        name = action[0]

        if name == "move" and len(action) == 3:
            result = move_selected_notes(result, valid, action[1], action[2])

        elif name == "transpose" and len(action) == 2:
            result = transpose_selected_notes(result, valid, action[1])

        elif name == "velocity" and len(action) == 2:
            result = velocity_selected_notes(result, valid, action[1])

        elif name == "stretch" and len(action) == 2:
            result = stretch_selected_notes(result, valid, action[1])

        elif name == "delete":
            result = delete_selected_notes(result, valid)

    return result
