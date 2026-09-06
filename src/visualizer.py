"""Visual styling, sparklines, and formatting utilities for NeonTop."""

from typing import List, Optional
from src.themes import Theme, get_theme

SPARK_CHARS = [" ", "▂", "▃", "▄", "▅", "▆", "▇", "█"]


def make_sparkline(
    values: List[float],
    theme: Optional[Theme] = None,
    max_val: float = 100.0,
    length: int = 24,
) -> str:
    """Generate a clean minimalist sparkline string."""
    if not values:
        return "[dim]--[/dim]"

    if theme is None:
        theme = get_theme("slate")

    slice_data = values[-length:] if len(values) > length else values
    padding = " " * (length - len(slice_data))

    spark_parts = []
    for val in slice_data:
        val = max(0.0, min(val, max_val))
        ratio = val / max_val if max_val > 0 else 0
        idx = int(ratio * (len(SPARK_CHARS) - 1))
        char = SPARK_CHARS[idx]
        color = theme.get_color_for_percent(val)
        spark_parts.append(f"[{color}]{char}[/{color}]")

    return f"[{theme.text_muted}]{padding}[/{theme.text_muted}]" + "".join(spark_parts)


def make_bar(percent: float, theme: Optional[Theme] = None, width: int = 12) -> str:
    """Generate a clean minimalist progress bar."""
    if theme is None:
        theme = get_theme("slate")

    percent = max(0.0, min(percent, 100.0))
    filled_length = int(width * (percent / 100.0))
    empty_length = width - filled_length

    color = theme.get_color_for_percent(percent)
    bar_fill = f"[{color}]{'━' * filled_length}[/{color}]"
    bar_empty = f"[{theme.bar_track}]{'─' * empty_length}[/{theme.bar_track}]"

    return f"{bar_fill}{bar_empty} [{color}]{percent:5.1f}%[/{color}]"


def format_bytes(bytes_val: float) -> str:
    """Convert bytes into human readable format (B, KB, MB, GB, TB)."""
    if bytes_val <= 0:
        return "  0.0 B"
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if abs(bytes_val) < 1024.0:
            return f"{bytes_val:5.1f} {unit}"
        bytes_val /= 1024.0
    return f"{bytes_val:5.1f} PB"


def format_speed(bytes_per_sec: float) -> str:
    """Convert bytes/sec into transfer speed string."""
    return f"{format_bytes(bytes_per_sec).strip()}/s"


def format_uptime(seconds: float) -> str:
    """Convert raw seconds into a human-friendly uptime string."""
    if seconds <= 0:
        return "0s"

    days = int(seconds // 86400)
    hours = int((seconds % 86400) // 3600)
    mins = int((seconds % 3600) // 60)
    secs = int(seconds % 60)

    if days > 0:
        return f"{days}d {hours}h {mins}m"
    elif hours > 0:
        return f"{hours}h {mins}m {secs}s"
    elif mins > 0:
        return f"{mins}m {secs}s"
    else:
        return f"{secs}s"
