import pygame
from typing import Tuple, Optional, Any
from ..core.logger import Logger


class StatusBar:
    """
    StatusBar (Status Bar)
    ----------------------
    FÁZA 4 – Stabilizovaná verzia

    Účel:
        - Zobrazuje stavové správy (status messages)
        - Používa sa na informácie o pipeline, MIDI, trackoch, systéme
        - Real‑time safe, neblokuje renderovaciu slučku

    Vlastnosti:
        - Jednoduchý textový UI prvok
        - Bezpečné vykresľovanie
        - Možnosť zapnúť/vypnúť
        - Automatické skracovanie textu pri pretečení
    """

    def __init__(
        self,
        width: int,
        height: int = 24,
        font_size: int = 18,
        enabled: bool = True,
        bg_color: Tuple[int, int, int] = (30, 30, 30),
        text_color: Tuple[int, int, int] = (220, 220, 220)
    ) -> None:

        self.enabled = bool(enabled)
        self.width = int(width)
        self.height = int(height)
        self.bg_color = bg_color
        self.text_color = text_color

        pygame.font.init()
        try:
            self.font = pygame.font.SysFont("Consolas", font_size)
        except Exception:
            self.font = pygame.font.Font(None, font_size)

        self.current_message: str = ""
        self.surface = pygame.Surface((self.width, self.height))

        if self.enabled:
            Logger.info("StatusBar initialized.")

    # ---------------------------------------------------------
    # ENABLE / DISABLE
    # ---------------------------------------------------------
    def toggle(self) -> bool:
        """Prepína viditeľnosť status baru a vráti nový stav."""
        self.enabled = not self.enabled
        Logger.info(f"StatusBar toggled: {self.enabled}")
        return self.enabled

    # ---------------------------------------------------------
    # SET MESSAGE
    # ---------------------------------------------------------
    def set_message(self, message: Any) -> None:
        """Nastaví novú správu (set status message)."""
        try:
            safe_message = self._safe_format(message)
            self.current_message = safe_message
            Logger.info(f"StatusBar message set: {safe_message}")

        except Exception as e:
            Logger.error(f"StatusBar set_message error: {e}")

    # ---------------------------------------------------------
    # RENDER
    # ---------------------------------------------------------
    def render(self) -> Optional[pygame.Surface]:
        """Vykreslí status bar a vráti surface (render status bar)."""
        if not self.enabled:
            return None

        try:
            self.surface.fill(self.bg_color)

            text_surface = self.font.render(
                self._truncate(self.current_message),
                True,
                self.text_color
            )

            self.surface.blit(text_surface, (6, 3))
            return self.surface

        except Exception as e:
            Logger.error(f"StatusBar render error: {e}")
            return None

    # ---------------------------------------------------------
    # SAFE FORMATTER
    # ---------------------------------------------------------
    def _safe_format(self, obj: Any) -> str:
        """Bezpečne konvertuje objekt na text (safe string conversion)."""
        try:
            return str(obj)
        except Exception:
            return "<unprintable>"

    # ---------------------------------------------------------
    # TRUNCATE LONG TEXT
    # ---------------------------------------------------------
    def _truncate(self, text: str) -> str:
        """Skráti text, ak je príliš dlhý (truncate long text)."""
        max_chars = max(4, int(self.width / 10))  # bezpečný limit
        if len(text) > max_chars:
            return text[:max_chars - 3] + "..."
        return text
