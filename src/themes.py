"""Theme definitions with distinct visual borders, backgrounds, and accents for Ztop Spectop."""

from dataclasses import dataclass
from typing import Dict, List


@dataclass
class Theme:
    name: str
    display_name: str
    bg: str           # Screen background
    panel_bg: str     # Card / panel background
    border: str       # Distinct card border
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
    "cyberpunk": Theme(
        name="cyberpunk",
        display_name="Cyberpunk Neon",
        bg="#080410",
        panel_bg="#100820",
        border="#ff0055",      # Electric pink
        text_main="#f8fafc",
        text_muted="#9d4edd",
        accent="#00f0ff",      # Electric cyan
        low="#00ff9f",         # Neon green
        med="#ffe600",         # Neon yellow
        high="#ff0055",        # Hot pink
        bar_track="#260f38",
    ),
    "matrix": Theme(
        name="matrix",
        display_name="Matrix Terminal",
        bg="#000a02",
        panel_bg="#021405",
        border="#00cc44",      # Phosphor green
        text_main="#e6ffe6",
        text_muted="#227733",
        accent="#00ff66",      # Bright green
        low="#22cc44",
        med="#88ff44",
        high="#ff3333",
        bar_track="#06260c",
    ),
    "nord": Theme(
        name="nord",
        display_name="Nord Arctic",
        bg="#1e222a",
        panel_bg="#242933",
        border="#88c0d0",      # Frost blue
        text_main="#eceff4",
        text_muted="#707c93",
        accent="#88c0d0",      # Frost cyan
        low="#a3be8c",         # Aurora green
        med="#ebcb8b",         # Aurora yellow
        high="#bf616a",        # Aurora red
        bar_track="#3b4252",
    ),
    "dracula": Theme(
        name="dracula",
        display_name="Dracula Dark",
        bg="#191a21",
        panel_bg="#21222c",
        border="#bd93f9",      # Vampire purple
        text_main="#f8f8f2",
        text_muted="#6272a4",
        accent="#ff79c6",      # Hot pink
        low="#50fa7b",         # Neon green
        med="#ffb86c",         # Orange
        high="#ff5555",        # Red
        bar_track="#343746",
    ),
    "catppuccin": Theme(
        name="catppuccin",
        display_name="Catppuccin Mocha",
        bg="#11111b",
        panel_bg="#181825",
        border="#cba6f7",      # Mauve lavender
        text_main="#cdd6f4",
        text_muted="#6c7086",
        accent="#89b4fa",      # Blue
        low="#a6e3a1",         # Green
        med="#fab387",         # Peach
        high="#f38ba8",        # Red
        bar_track="#313244",
    ),
    "monochrome": Theme(
        name="monochrome",
        display_name="Monochrome Minimal",
        bg="#000000",
        panel_bg="#0a0a0a",
        border="#ffffff",      # High contrast white
        text_main="#ffffff",
        text_muted="#777777",
        accent="#ffffff",
        low="#cccccc",
        med="#888888",
        high="#ffffff",
        bar_track="#222222",
    ),
}

THEME_ORDER: List[str] = [
    "slate",
    "cyberpunk",
    "matrix",
    "nord",
    "dracula",
    "catppuccin",
    "monochrome",
]


def get_theme(name: str) -> Theme:
    """Retrieve theme by name, fallback to 'slate'."""
    clean_name = str(name).strip().lower()
    return THEMES.get(clean_name, THEMES["slate"])


def next_theme(current_name: str) -> Theme:
    """Get the next theme in the cycle."""
    clean_name = str(current_name).strip().lower()
    try:
        idx = THEME_ORDER.index(clean_name)
        next_idx = (idx + 1) % len(THEME_ORDER)
    except ValueError:
        next_idx = 0
    return THEMES[THEME_ORDER[next_idx]]
