# Rhythm Analyzer – timing, patterns, swing, groove

from collections import defaultdict, Counter
from math import fabs
from ..core.logger import Logger


class RhythmAnalyzerConfig:
    def __init__(
        self,
        bpm=120.0,
        ppq=480,
        quant_grid=0.25,
        swing_threshold=0.08,
        timing_loose_threshold=0.02,
        timing_laidback_threshold=0.03,
        velocity_accent_threshold=0.75,
        velocity_ghost_threshold=0.25,
        min_pattern_bars=2,
        max_pattern_length_beats=4.0,
    ):
        self.bpm = float(bpm)
        self.ppq = int(ppq)
        self.quant_grid = float(quant_grid)
        self.swing_threshold = float(swing_threshold)
        self.timing_loose_threshold = float(timing_loose_threshold)
        self.timing_laidback_threshold = float(timing_laidback_threshold)
        self.velocity_accent_threshold = float(velocity_accent_threshold)
        self.velocity_ghost_threshold = float(velocity_ghost_threshold)
        self.min_pattern_bars = int(min_pattern_bars)
        self.max_pattern_length_beats = float(max_pattern_length_beats)


class RhythmAnalyzer:
    """
    Vstup: timeline – zoznam nôt so 'start', 'duration', 'velocity',
    'track_type', 'bar_index', 'beat_in_bar'
    Výstup: slovník s analýzou rytmu, swingom, patternmi, groove, timingom a dynamikou.
    """

    def __init__(self, config=None):
        self.config = config or RhythmAnalyzerConfig()
        Logger.info("RhythmAnalyzer initialized with config.")

    # -------------------------------------------------
    # PUBLIC API
    # -------------------------------------------------

    def analyze(self, timeline):
        if not isinstance(timeline, list) or not timeline:
            Logger.warning("RhythmAnalyzer.analyze called with empty or invalid timeline.")
            return {}

        try:
            quantized = self._quantize_timeline(timeline)
            timing_stats = self._analyze_timing_deviation(timeline, quantized)
            velocity_stats = self._analyze_velocity_patterns(timeline)
            swing_info = self._detect_swing(timeline, quantized)
            patterns = self._detect_rhythm_patterns(quantized)
            downbeats = self._detect_downbeats(timeline, velocity_stats, timing_stats)
            groove = self._classify_groove(
                swing_info, patterns, velocity_stats, timing_stats
            )
        except Exception as e:
            Logger.error(f"RhythmAnalyzer.analyze error: {e}")
            return {}

        result = {
            "quantized": quantized,
            "timing": timing_stats,
            "velocity": velocity_stats,
            "swing": swing_info,
            "patterns": patterns,
            "downbeats": downbeats,
            "groove": groove,
        }

        Logger.info(
            f"RhythmAnalyzer: swing={swing_info.get('type')}, "
            f"groove={groove.get('label')}, "
            f"avg_timing_dev={timing_stats.get('avg_abs_deviation_beats', 0):.4f}"
        )

        return result

    # -------------------------------------------------
    # 1) Kvantizácia
    # -------------------------------------------------

    def _quantize_timeline(self, timeline):
        grid = self.config.quant_grid
        quantized = []

        for note in timeline:
            if not isinstance(note, dict):
                continue

            start = note.get("start", 0.0)
            duration = note.get("duration", grid)
            velocity = note.get("velocity", 80)

            try:
                start = float(start)
            except Exception:
                start = 0.0

            try:
                duration = float(duration)
            except Exception:
                duration = grid

            q_start = round(start / grid) * grid
            q_duration = round(duration / grid) * grid

            quantized.append(
                {
                    **note,
                    "q_start": q_start,
                    "q_duration": q_duration,
                    "velocity": velocity,
                }
            )

        return quantized

    # -------------------------------------------------
    # 2) Timing deviation analyzer (microtiming)
    # -------------------------------------------------

    def _analyze_timing_deviation(self, timeline, quantized):
        deviations = []

        for orig, q in zip(timeline, quantized):
            if not isinstance(orig, dict) or not isinstance(q, dict):
                continue

            start = orig.get("start", 0.0)
            q_start = q.get("q_start", start)

            try:
                start = float(start)
            except Exception:
                start = 0.0

            try:
                q_start = float(q_start)
            except Exception:
                q_start = start

            deviations.append(start - q_start)

        if not deviations:
            return {
                "avg_deviation_beats": 0.0,
                "avg_abs_deviation_beats": 0.0,
                "timing_feel": "unknown",
            }

        avg_dev = sum(deviations) / len(deviations)
        avg_abs = sum(abs(d) for d in deviations) / len(deviations)

        feel = "tight"
        if avg_dev > self.config.timing_laidback_threshold:
            feel = "laid_back"
        elif avg_dev < -self.config.timing_laidback_threshold:
            feel = "pushed"
        elif avg_abs > self.config.timing_loose_threshold:
            feel = "loose"

        return {
            "avg_deviation_beats": avg_dev,
            "avg_abs_deviation_beats": avg_abs,
            "timing_feel": feel,
            "deviations": deviations,
        }

    # -------------------------------------------------
    # 3) Velocity pattern analyzer
    # -------------------------------------------------

    def _analyze_velocity_patterns(self, timeline):
        velocities = []

        for n in timeline:
            if not isinstance(n, dict):
                continue
            v = n.get("velocity", 80)
            try:
                v = int(v)
            except Exception:
                v = 80
            velocities.append(v)

        if not velocities:
            return {
                "avg_velocity": 0.0,
                "accents": [],
                "ghost_notes": [],
                "dynamic_range": 0.0,
                "velocity_profile": [],
            }

        max_v = max(velocities)
        min_v = min(velocities)
        avg_v = sum(velocities) / len(velocities)
        dyn_range = max_v - min_v

        accents = []
        ghosts = []
        profile = []

        for idx, n in enumerate(timeline):
            if not isinstance(n, dict):
                continue

            v = n.get("velocity", 80)
            try:
                v = int(v)
            except Exception:
                v = 80

            norm = v / 127.0
            is_accent = norm >= self.config.velocity_accent_threshold
            is_ghost = norm <= self.config.velocity_ghost_threshold

            profile.append(
                {
                    "index": idx,
                    "velocity": v,
                    "normalized": norm,
                    "is_accent": is_accent,
                    "is_ghost": is_ghost,
                }
            )

            if is_accent:
                accents.append(idx)
            if is_ghost:
                ghosts.append(idx)

        return {
            "avg_velocity": avg_v,
            "max_velocity": max_v,
            "min_velocity": min_v,
            "dynamic_range": dyn_range,
            "accents": accents,
            "ghost_notes": ghosts,
            "velocity_profile": profile,
        }

    # -------------------------------------------------
    # 4) Swing / shuffle detection
    # -------------------------------------------------

    def _detect_swing(self, timeline, quantized):
        if not timeline:
            return {"type": "unknown", "ratio": 0.0}

        pairs = []
        by_bar = defaultdict(list)

        for n in timeline:
            if not isinstance(n, dict):
                continue
            bar = n.get("bar_index", 0)
            by_bar[bar].append(n)

        for bar, notes in by_bar.items():
            notes_sorted = sorted(
                [x for x in notes if isinstance(x, dict)],
                key=lambda x: x.get("start", 0.0),
            )
            for i in range(len(notes_sorted) - 1):
                a = notes_sorted[i]
                b = notes_sorted[i + 1]
                try:
                    sa = float(a.get("start", 0.0))
                    sb = float(b.get("start", 0.0))
                except Exception:
                    continue

                if 0 < (sb - sa) <= 0.5 + 1e-6:
                    pairs.append((sa, sb))

        if not pairs:
            return {"type": "straight", "ratio": 0.0}

        ratios = []
        for sa, sb in pairs:
            diff = sb - sa
            total = 0.5
            first = diff
            second = max(total - first, 1e-6)
            ratios.append(first / (first + second))

        if not ratios:
            return {"type": "straight", "ratio": 0.0}

        avg_ratio = sum(ratios) / len(ratios)

        swing_type = "straight"
        if fabs(avg_ratio - 0.5) < self.config.swing_threshold:
            swing_type = "straight"
        elif avg_ratio >= 0.7:
            swing_type = "shuffle"
        elif avg_ratio >= 0.6:
            swing_type = "swing"

        return {
            "type": swing_type,
            "ratio": avg_ratio,
            "pairs_analyzed": len(pairs),
        }

    # -------------------------------------------------
    # 5) Pattern recognition
    # -------------------------------------------------

    def _detect_rhythm_patterns(self, quantized):
        if not quantized:
            return {"patterns": [], "bar_patterns": {}}

        bars = defaultdict(list)
        for n in quantized:
            if not isinstance(n, dict):
                continue
            bar = n.get("bar_index", 0)
            bars[bar].append(n)

        bar_patterns = {}
        pattern_counter = Counter()

        for bar_idx, notes in bars.items():
            notes_sorted = sorted(
                [x for x in notes if isinstance(x, dict)],
                key=lambda x: x.get("q_start", 0.0),
            )

            starts = []
            for n in notes_sorted:
                try:
                    qs = float(n.get("q_start", 0.0))
                except Exception:
                    qs = 0.0
                starts.append(qs)

            if len(starts) < 2:
                bar_patterns[bar_idx] = ()
                continue

            diffs = []
            for i in range(len(starts) - 1):
                diffs.append(round(starts[i + 1] - starts[i], 3))

            pattern = tuple(diffs)
            bar_patterns[bar_idx] = pattern
            pattern_counter[pattern] += 1

        patterns = []
        for pat, count in pattern_counter.items():
            if count >= self.config.min_pattern_bars and len(pat) > 0:
                patterns.append(
                    {
                        "pattern": pat,
                        "occurrences": count,
                    }
                )

        patterns_sorted = sorted(patterns, key=lambda x: x["occurrences"], reverse=True)

        return {
            "patterns": patterns_sorted,
            "bar_patterns": bar_patterns,
        }

    # -------------------------------------------------
    # 6) Downbeat detection
    # -------------------------------------------------

    def _detect_downbeats(self, timeline, velocity_stats, timing_stats):
        if not timeline:
            return {"downbeats": []}

        has_bar = any(isinstance(n, dict) and "bar_index" in n for n in timeline)
        if not has_bar:
            return {"downbeats": []}

        avg_v = velocity_stats.get("avg_velocity", 80)
        accents = set(velocity_stats.get("accents", []))

        downbeats = []
        for idx, n in enumerate(timeline):
            if not isinstance(n, dict):
                continue

            bar = n.get("bar_index", 0)
            beat_in_bar = n.get("beat_in_bar", 0.0)
            v = n.get("velocity", 80)

            try:
                beat_val = float(beat_in_bar) if beat_in_bar is not None else 0.0
            except Exception:
                beat_val = 0.0

            try:
                v = int(v)
            except Exception:
                v = 80

            if fabs(beat_val) < 0.05:
                is_accent = idx in accents or v >= avg_v + 10
                if is_accent:
                    downbeats.append(
                        {
                            "index": idx,
                            "bar_index": bar,
                            "velocity": v,
                        }
                    )

        return {"downbeats": downbeats}

    # -------------------------------------------------
    # 7) Groove classifier
    # -------------------------------------------------

    def _classify_groove(self, swing_info, patterns, velocity_stats, timing_stats):
        swing_type = swing_info.get("type", "straight")
        ratio = swing_info.get("ratio", 0.5)
        timing_feel = timing_stats.get("timing_feel", "tight")
        dyn_range = velocity_stats.get("dynamic_range", 0.0)
        patterns_list = patterns.get("patterns", [])

        label = "unknown"
        tags = []

        if swing_type == "straight":
            tags.append("straight")
        elif swing_type == "swing":
            tags.append("swing")
        elif swing_type == "shuffle":
            tags.append("shuffle")

        tags.append(timing_feel)

        if dyn_range > 40:
            tags.append("dynamic")
        elif dyn_range < 15:
            tags.append("flat")

        if patterns_list:
            most_common = patterns_list[0]
            pat = most_common.get("pattern", ())
            occ = most_common.get("occurrences", 0)

            if len(pat) == 3 and occ >= 3:
                tags.append("3_grouping")
            if any(abs(d - 0.5) < 0.01 for d in pat):
                tags.append("eighth_based")
            if any(abs(d - 0.25) < 0.01 for d in pat):
                tags.append("sixteenth_based")

        if "swing" in tags or "shuffle" in tags:
            if "sixteenth_based" in tags:
                label = "16th_swing"
            else:
                label = "8th_swing"
        elif "straight" in tags:
            if "sixteenth_based" in tags:
                label = "16th_straight"
            else:
                label = "8th_straight"

        if "3_grouping" in tags and "straight" in tags:
            label = "3_3_2_style"

        return {
            "label": label,
            "tags": tags,
            "swing_type": swing_type,
            "swing_ratio": ratio,
            "timing_feel": timing_feel,
            "dynamic_range": dyn_range,
        }
