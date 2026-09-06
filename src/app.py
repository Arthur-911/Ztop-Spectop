import sys
import time

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from rich.console import Console
from rich.live import Live

from src.dashboard import build_dashboard
from src.metrics import MetricsCollector
from src.themes import Theme, get_theme, next_theme


def get_keypress() -> str | None:
    """Non-blocking keyboard reader (cross-platform)."""
    if sys.platform == "win32":
        import msvcrt
        if msvcrt.kbhit():
            try:
                char = msvcrt.getch()
                if char in (b"\x00", b"\xe0"):
                    msvcrt.getch()
                    return None
                if char == b"\x03":
                    return "q"
                return char.decode("utf-8", errors="ignore").lower()
            except Exception:
                return None
        return None
    else:
        import select
        dr, _, _ = select.select([sys.stdin], [], [], 0)
        if dr:
            try:
                return sys.stdin.read(1).lower()
            except Exception:
                return None
        return None


class ZtopSpectopApp:
    """Ztop Spectop interactive terminal system monitor application."""

    def __init__(self, interval: float = 1.0, sort_by: str = "cpu", theme: str = "slate"):
        self.interval = max(0.5, interval)
        self.sort_by = "cpu" if sort_by not in ("cpu", "ram") else sort_by
        self.theme = get_theme(theme)
        self.collector = MetricsCollector()
        self.console = Console()
        self.is_paused = False
        self.pulse = True
        self.running = True

    def run(self):
        """Start the live updating monitor dashboard with ultra-responsive input."""
        # Start background telemetry collector thread
        self.collector.start_background(interval=self.interval)
        snapshot = self.collector.get_latest_snapshot(sort_by=self.sort_by)

        with Live(
            build_dashboard(
                snapshot,
                theme=self.theme,
                sort_by=self.sort_by,
                pulse=self.pulse,
                is_paused=self.is_paused,
            ),
            console=self.console,
            screen=True,
            auto_refresh=False,
        ) as live:
            last_pulse_time = time.time()
            needs_render = False

            try:
                while self.running:
                    now = time.time()

                    # 1. Non-blocking keyboard check (instant response!)
                    key = get_keypress()
                    if key:
                        if key == "q":
                            self.running = False
                            break
                        elif key == "t":
                            # Cycle through available themes live
                            self.theme = next_theme(self.theme.name)
                            needs_render = True
                        elif key == "s":
                            self.sort_by = "ram" if self.sort_by == "cpu" else "cpu"
                            snapshot = self.collector.get_latest_snapshot(sort_by=self.sort_by)
                            needs_render = True
                        elif key == " ":
                            self.is_paused = not self.is_paused
                            needs_render = True

                    # 2. Check for new background metrics update
                    if not self.is_paused and self.collector._update_event.is_set():
                        self.collector._update_event.clear()
                        snapshot = self.collector.get_latest_snapshot(sort_by=self.sort_by)
                        needs_render = True

                    # 3. Pulse indicator cycle
                    if not self.is_paused and (now - last_pulse_time >= self.interval):
                        self.pulse = not self.pulse
                        last_pulse_time = now
                        needs_render = True

                    # 4. Render only when state or data changed
                    if needs_render:
                        live.update(
                            build_dashboard(
                                snapshot,
                                theme=self.theme,
                                sort_by=self.sort_by,
                                pulse=self.pulse,
                                is_paused=self.is_paused,
                            ),
                            refresh=True,
                        )
                        needs_render = False

                    # Responsive 30 FPS sleep - zero CPU spin, instant key detection
                    time.sleep(0.03)

            except KeyboardInterrupt:
                pass
            finally:
                self.running = False
                self.collector.stop_background()


# Backward compatibility alias
NeonTopApp = ZtopSpectopApp
