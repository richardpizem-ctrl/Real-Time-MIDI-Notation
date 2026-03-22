# Rhythm Analyzer – timing, patterns, swing, groove

from collections import defaultdict, Counter
from math import fabs

from ..core.logger import Logger


class RhythmAnalyzerConfig:
    def __init__(
        self,
        bpm=120.0,
        ppq=480,
        quant_grid=0.25,          # základná kvantizačná mriežka (štvrťová = 0.25, osminová = 0.125)
        swing_threshold=0.08,     # minimálna odchýlka (v beat fraction) pre swing detekciu
        timing_loose_threshold=0.02,
        timing_laidback_threshold=0.03,
        velocity_accent_threshold=0.75,
        velocity_ghost_threshold=0.25,
        min_pattern_bars=2,
        max_pattern_length_beats=4.0,
    ):
        self.bpm = bpm
        self.ppq = ppq
        self.quant_grid = quant_grid
        self.swing_threshold = swing_threshold
        self.timing_loose_threshold = timing_loose_threshold
        self.timing_laidback_threshold = timing_laidback_threshold
        self.velocity_accent_threshold = velocity_accent_threshold
        self.velocity_ghost_threshold = velocity_ghost_threshold
        self.min_pattern_bars = min_pattern_bars
        self.max_pattern_length_beats = max_pattern_length_beats


class RhythmAnalyzer:
    """
    Vstup: timeline – zoznam nôt so 'start', 'duration', 'velocity', 'track_type', 'bar_index', 'beat_in_bar' (ak máš).
    Výstup: slovník s analýzou rytmu, swingom, patternmi, groove, timingom a dynamikou.
    """

    def __init__(self, config=None):
        self.config = config or RhythmAnalyzerConfig()
        Logger.info("RhythmAnalyzer initialized with config.")

    # -------------------------------------------------
    # Public API
    # -------------------------------------------------

    def analyze(self, timeline):
        """
        Hlavný vstupný bod.
        timeline: list[dict] – každý prvok má aspoň:
            - 'start' (v beatoch alebo sekundách – predpokladáme beats)
            - 'duration'
            - 'velocity' (0–127)
            - 'bar_index' (int) – ak je k dispozícii
            - 'beat_in_bar' (float) – ak je k dispozícii
        """
        if not timeline:
            Logger.warning("RhythmAnalyzer.analyze called with empty timeline.")
            return {}

        # 1) Kvantizácia a základné metriky
        quantized = self._quantize_timeline(timeline)
        timing_stats = self._analyze_timing_deviation(timeline, quantized)
        velocity_stats = self._analyze_velocity_patterns(timeline)
        swing_info = self._detect_swing(timeline, quantized)
        patterns = self._detect_rhythm_patterns(quantized)
        downbeats = self._detect_downbeats(timeline, velocity_stats, timing_stats)
        groove = self._classify_groove(swing_info, patterns, velocity_stats, timing_stats)

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
            start = note.get("start", 0.0)
            duration = note.get("duration", grid)
            velocity = note.get("velocity", 80)

            q_start = round(start / grid) * grid
            q_duration = round(duration / grid) * grid

            quantized.append({
                **note,
                "q_start": q_start,
                "q_duration": q_duration,
            })

        return quantized

    # -------------------------------------------------
    # 2) Timing deviation analyzer (microtiming)
    # -------------------------------------------------

    def _analyze_timing_deviation(self, timeline, quantized):
        deviations = []
        for orig, q in zip(timeline, quantized):
            start = orig.get("start", 0.0)
            q_start = q.get("q_start", start)
            dev = start - q_start
            deviations.append(dev)

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
        if not timeline:
            return {
                "avg_velocity": 0.0,
                "accents": [],
                "ghost_notes": [],
                "dynamic_range": 0.0,
                "velocity_profile": [],
            }

        velocities = [n.get("velocity", 80) for n in timeline]
        max_v = max(velocities)
        min_v = min(velocities)
        avg_v = sum(velocities) / len(velocities)
        dyn_range = max_v - min_v

        accents = []
        ghosts = []
        profile = []

        for idx, n in enumerate(timeline):
            v = n.get("velocity", 80)
            norm = v / 127.0
            is_accent = norm >= self.config.velocity_accent_threshold
            is_ghost = norm <= self.config.velocity_ghost_threshold

            profile.append({
                "index": idx,
                "velocity": v,
                "normalized": norm,
                "is_accent": is_accent,
                "is_ghost": is_ghost,
            })

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
        """
        Hľadá páry osmin (alebo menších jednotiek) a porovnáva ich pomer.
        Predpoklad: 'start' je v beatoch, grid = 1/8 alebo 1/16.
        """
        if not timeline:
            return {"type": "unknown", "ratio": 0.0}

        grid = self.config.quant_grid
        # berieme páry not v rámci 1 beat-u (napr. dve osminy)
        pairs = []
        by_bar = defaultdict(list)

        for n in timeline:
            bar = n.get("bar_index", 0)
            by_bar[bar].append(n)

        for bar, notes in by_bar.items():
            notes_sorted = sorted(notes, key=lambda x: x.get("start", 0.0))
            # prejdeme po dvojiciach v rámci beatu
            for i in range(len(notes_sorted) - 1):
                a = notes_sorted[i]
                b = notes_sorted[i + 1]
                sa = a.get("start", 0.0)
                sb = b.get("start", 0.0)
                # ak sú v tom istom beate (rozdiel < 1.0) a sú to "osminy"
                if 0 < (sb - sa) <= 0.5 + 1e-6:
                    pairs.append((sa, sb))

        if not pairs:
            return {"type": "straight", "ratio": 0.0}

        ratios = []
        for sa, sb in pairs:
            diff = sb - sa
            # očakávané rovné osminy = 0.5 beat
            # swing = prvá dlhšia, druhá kratšia
            # ratio = first_part / (first_part + second_part)
            total = 0.5
            first = diff
            second = max(total - first, 1e-6)
            ratio = first / (first + second)
            ratios.append(ratio)

        avg_ratio = sum(ratios) / len(ratios)

        # 0.5 = straight, 0.66 = typický swing, 0.75 = silný shuffle
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
    # 5) Pattern recognition (rhythmic patterns)
    # -------------------------------------------------

    def _detect_rhythm_patterns(self, quantized):
        """
        Hľadá opakujúce sa rytmické patterny v rámci taktov.
        Predpoklad: 'bar_index' a 'q_start' sú k dispozícii.
        """
        if not quantized:
            return {"patterns": [], "bar_patterns": {}}

        bars = defaultdict(list)
        for n in quantized:
            bar = n.get("bar_index", 0)
            bars[bar].append(n)

        bar_patterns = {}
        pattern_counter = Counter()

        for bar_idx, notes in bars.items():
            notes_sorted = sorted(notes, key=lambda x: x.get("q_start", 0.0))
            # pattern = rozdiely medzi po sebe idúcimi q_start
            starts = [n.get("q_start", 0.0) for n in notes_sorted]
            if len(starts) < 2:
                bar_patterns[bar_idx] = ()
                continue

            diffs = []
            for i in range(len(starts) - 1):
                d = round(starts[i + 1] - starts[i], 3)
                diffs.append(d)

            pattern = tuple(diffs)
            bar_patterns[bar_idx] = pattern
            pattern_counter[pattern] += 1

        # vyberieme patterny, ktoré sa opakujú aspoň 2x
        patterns = []
        for pat, count in pattern_counter.items():
            if count >= self.config.min_pattern_bars and len(pat) > 0:
                patterns.append({
                    "pattern": pat,
                    "occurrences": count,
                })

        patterns_sorted = sorted(patterns, key=lambda x: x["occurrences"], reverse=True)

        return {
            "patterns": patterns_sorted,
            "bar_patterns": bar_patterns,
        }

    # -------------------------------------------------
    # 6) Downbeat detection
    # -------------------------------------------------

    def _detect_downbeats(self, timeline, velocity_stats, timing_stats):
        """
        Heuristika: downbeat = silný akcent + malá timing odchýlka + začiatok taktu.
        Ak nemáme bar_index, vrátime prázdny zoznam.
        """
        if not timeline:
            return {"downbeats": []}

        has_bar = any("bar_index" in n for n in timeline)
        if not has_bar:
            return {"downbeats": []}

        avg_v = velocity_stats.get("avg_velocity", 80)
        accents = set(velocity_stats.get("accents", []))

        downbeats = []
        for idx, n in enumerate(timeline):
            bar = n.get("bar_index", 0)
            beat_in_bar = n.get("beat_in_bar", 0.0)
            v = n.get("velocity", 80)

            # downbeat kandidát: prvá nota v takte alebo beat_in_bar blízko 0
            if beat_in_bar is not None and fabs(beat_in_bar) < 0.05:
                is_accent = idx in accents or v >= avg_v + 10
                if is_accent:
                    downbeats.append({
                        "index": idx,
                        "bar_index": bar,
                        "velocity": v,
                    })

        return {"downbeats": downbeats}

    # -------------------------------------------------
    # 7) Groove classifier
    # -------------------------------------------------

    def _classify_groove(self, swing_info, patterns, velocity_stats, timing_stats):
        """
        Jednoduchý heuristický klasifikátor groove-u.
        """
        swing_type = swing_info.get("type", "straight")
        ratio = swing_info.get("ratio", 0.5)
        timing_feel = timing_stats.get("timing_feel", "tight")
        dyn_range = velocity_stats.get("dynamic_range", 0.0)
        patterns_list = patterns.get("patterns", [])

        label = "unknown"
        tags = []

        # základ: straight vs swing/shuffle
        if swing_type == "straight":
            tags.append("straight")
        elif swing_type == "swing":
            tags.append("swing")
        elif swing_type == "shuffle":
            tags.append("shuffle")

        # timing feel
        tags.append(timing_feel)

        # dynamika
        if dyn_range > 40:
            tags.append("dynamic")
        elif dyn_range < 15:
            tags.append("flat")

        # pattern-based hints
        if patterns_list:
            most_common = patterns_list[0]
            pat = most_common["pattern"]
            occ = most_common["occurrences"]

            # jednoduché heuristiky
            if len(pat) == 3 and occ >= 3:
                tags.append("3_grouping")
            if any(abs(d - 0.5) < 0.01 for d in pat):
                tags.append("eighth_based")
            if any(abs(d - 0.25) < 0.01 for d in pat):
                tags.append("sixteenth_based")

        # finálny label
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
