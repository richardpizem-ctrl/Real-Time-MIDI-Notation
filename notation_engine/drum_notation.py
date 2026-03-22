# drum_notation.py
# Profesionálna notácia bicích – mapping, tvary hlavičiek, stonky, layering

from collections import defaultdict
from dataclasses import dataclass
from typing import List, Dict, Any


@dataclass
class DrumSymbolSpec:
    name: str
    notehead: str          # "normal", "x", "diamond", "triangle", "circle"
    stem: str              # "up", "down", "none"
    is_cymbal: bool = False
    is_hat: bool = False
    is_kick: bool = False
    is_snare: bool = False
    is_tom: bool = False
    is_percussion: bool = False
    default_layer_offset: float = 0.0


# GM Drum Map – profesionálny mapping
DRUM_PITCH_MAP: Dict[int, DrumSymbolSpec] = {
    36: DrumSymbolSpec("Kick", "normal", "none", is_kick=True),
    35: DrumSymbolSpec("Kick 2", "normal", "none", is_kick=True),

    38: DrumSymbolSpec("Snare", "normal", "up", is_snare=True),
    40: DrumSymbolSpec("Snare Rimshot", "diamond", "up", is_snare=True),

    37: DrumSymbolSpec("Side Stick", "x", "up", is_snare=True, is_percussion=True),

    41: DrumSymbolSpec("Low Floor Tom", "normal", "up", is_tom=True),
    43: DrumSymbolSpec("High Floor Tom", "normal", "up", is_tom=True),
    45: DrumSymbolSpec("Low Tom", "normal", "up", is_tom=True),
    47: DrumSymbolSpec("Low-Mid Tom", "normal", "up", is_tom=True),
    48: DrumSymbolSpec("High-Mid Tom", "normal", "up", is_tom=True),
    50: DrumSymbolSpec("High Tom", "normal", "up", is_tom=True),

    42: DrumSymbolSpec("Closed Hi-Hat", "x", "up", is_hat=True, is_cymbal=True),
    44: DrumSymbolSpec("Pedal Hi-Hat", "x", "up", is_hat=True, is_cymbal=True),
    46: DrumSymbolSpec("Open Hi-Hat", "x", "up", is_hat=True, is_cymbal=True),

    49: DrumSymbolSpec("Crash 1", "x", "up", is_cymbal=True),
    57: DrumSymbolSpec("Crash 2", "x", "up", is_cymbal=True),
    51: DrumSymbolSpec("Ride 1", "x", "up", is_cymbal=True),
    59: DrumSymbolSpec("Ride 2", "x", "up", is_cymbal=True),
    53: DrumSymbolSpec("Ride Bell", "diamond", "up", is_cymbal=True),

    39: DrumSymbolSpec("Hand Clap", "triangle", "up", is_percussion=True),
    54: DrumSymbolSpec("Tambourine", "triangle", "up", is_percussion=True),
    56: DrumSymbolSpec("Cowbell", "diamond", "up", is_percussion=True),
    58: DrumSymbolSpec("Vibra Slap", "triangle", "up", is_percussion=True),
}


def get_drum_spec(pitch: int) -> DrumSymbolSpec:
    return DRUM_PITCH_MAP.get(pitch, DrumSymbolSpec(f"Drum {pitch}", "normal", "up"))


def is_ghost_velocity(velocity: int, ghost_threshold: float = 0.3) -> bool:
    return (velocity / 127.0) <= ghost_threshold


def is_accent_velocity(velocity: int, accent_threshold: float = 0.8) -> bool:
    return (velocity / 127.0) >= accent_threshold


def annotate_drum_note(note: Dict[str, Any]) -> Dict[str, Any]:
    pitch = note.get("pitch", 38)
    velocity = note.get("velocity", 80)
    spec = get_drum_spec(pitch)

    is_ghost = is_ghost_velocity(velocity)
    is_accent = is_accent_velocity(velocity)

    is_hat = spec.is_hat
    is_open_hat = is_hat and pitch in (46,)
    is_closed_hat = is_hat and pitch in (42, 44)

    annotated = {
        **note,
        "drum": {
            "name": spec.name,
            "notehead_type": spec.notehead,
            "stem_direction": spec.stem,
            "is_cymbal": spec.is_cymbal,
            "is_hat": spec.is_hat,
            "is_open_hat": is_open_hat,
            "is_closed_hat": is_closed_hat,
            "is_kick": spec.is_kick,
            "is_snare": spec.is_snare,
            "is_tom": spec.is_tom,
            "is_percussion": spec.is_percussion,
            "is_ghost": is_ghost,
            "is_accent": is_accent,
        },
    }

    return annotated


def group_drum_notes_by_time(timeline: List[Dict[str, Any]], time_epsilon: float = 1e-3):
    groups = []
    current_group = []
    last_start = None

    for note in timeline:
        if note.get("track_type") != "drums":
            continue

        start = note.get("start", 0.0)
        if last_start is None or abs(start - last_start) <= time_epsilon:
            current_group.append(note)
            last_start = start
        else:
            if current_group:
                groups.append(current_group)
            current_group = [note]
            last_start = start

    if current_group:
        groups.append(current_group)

    return groups


def assign_layer_offsets_to_group(group: List[Dict[str, Any]], base_offset: float = 4.0):
    if len(group) <= 1:
        for n in group:
            n["drum_layer_offset"] = 0.0
        return

    if all("y" in n for n in group):
        sorted_group = sorted(group, key=lambda n: n["y"])
    else:
        sorted_group = sorted(group, key=lambda n: n.get("pitch", 0))

    center_index = (len(sorted_group) - 1) / 2.0

    for idx, n in enumerate(sorted_group):
        offset_index = idx - center_index
        n["drum_layer_offset"] = offset_index * base_offset


def annotate_drum_timeline(timeline: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    annotated = []
    for note in timeline:
        if note.get("track_type") == "drums":
            annotated.append(annotate_drum_note(note))
        else:
            annotated.append(note)

    groups = group_drum_notes_by_time(annotated)
    for g in groups:
        assign_layer_offsets_to_group(g)

    return annotated
