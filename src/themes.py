"""Theme definitions with dedicated background and foreground palettes for NeonTop."""

from dataclasses import dataclass
from typing import Dict, List


@dataclass
class Theme:
    name: str
    display_name: str
    bg: str           # Background color for root screen
    panel_bg: str     # Card / panel background color
    border: str       # Subtle card border
    text_main: str    # Primary readable text
    text_muted: str   # Dim/subtle labels
    accent: str       # Primary key accent
    low: str          # Normal load (< 45%)
    med: str          # Moderate load (45-75%)
    high: str         # High load (> 75%)
    bar_track: str    # Empty progress bar track

    def get_color_for_percent(self, percent: float) -> str:
        if percent < 45.0:
            return self.low
        elif percent < 75.0:
            return self.med
        else:
            return self.high


THEMES: Dict[str, Theme] = {
    "slate": Theme(
        name="slate",
        display_name="Minimal Slate",
        bg="#0a0c10",
        panel_bg="#0e131b",
        border="#202734",
        text_main="#e2e8f0",
        text_muted="#64748b",
        accent="#38bdf8",      # Sky blue
        low="#34d399",         # Emerald
        med="#fbbf24",         # Amber
        high="#f87171",        # Rose
        bar_track="#1a2230",
    ),
    "monochrome": Theme(
        name="monochrome",
        display_name="Minimal Black",
        bg="#000000",
        panel_bg="#080808",
        border="#222222",
        text_main="#f5f5f5",
        text_muted="#666666",
        accent="#e5e5e5",
        low="#cccccc",
        med="#999999",
        high="#ffffff",
        bar_track="#1a1a1a",
    ),
    "nord": Theme(
        name="nord",
        display_name="Nord Arctic",
        bg="#1e222a",
        panel_bg="#242933",
        border="#383f4f",
        text_main="#eceff4",
        text_muted="#707c93",
        accent="#88c0d0",      # Frost cyan
        low="#a3be8c",         # Aurora green
        med="#ebcb8b",         # Aurora yellow
        high="#bf616a",        # Aurora red
        bar_track="#2e3440",
    ),
    "catppuccin": Theme(
        name="catppuccin",
        display_name="Catppuccin Dark",
        bg="#11111b",
        panel_bg="#181825",
        border="#313244",
        text_main="#cdd6f4",
        text_muted="#6c7086",
        accent="#cba6f7",      # Mauve
        low="#a6e3a1",         # Green
        med="#fab387",         # Peach
        high="#f38ba8",        # Red
        bar_track="#242638",
    ),
    "dracula": Theme(
        name="dracula",
        display_name="Dracula Dark",
        bg="#191a21",
        panel_bg="#21222c",
        border="#343746",
        text_main="#f8f8f2",
        text_muted="#6272a4",
        accent="#bd93f9",      # Purple
        low="#50fa7b",         # Green
        med="#ffb86c",         # Orange
        high="#ff5555",        # Red
        bar_track="#2d303e",
    ),
}

THEME_ORDER: List[str] = ["slate", "monochrome", "nord", "catppuccin", "dracula"]


def get_theme(name: str) -> Theme:
    """Retrieve theme by name, fallback to 'slate'."""
    return THEMES.get(name.lower(), THEMES["slate"])


def next_theme(current_name: str) -> Theme:
    """Get the next theme in the cycle."""
    try:
        idx = THEME_ORDER.index(current_name.lower())
        next_idx = (idx + 1) % len(THEME_ORDER)
    except ValueError:
        next_idx = 0
    return THEMES[THEME_ORDER[next_idx]]
