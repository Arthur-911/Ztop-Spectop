"""NeonTop - Modern Terminal & Web System Monitor

Entry point for starting the terminal application, web dashboard, or exporting snapshots.
"""

import argparse
import sys

# Ensure UTF-8 output on Windows consoles
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from rich.console import Console

from src import __version__
from src.app import NeonTopApp
from src.dashboard import build_dashboard
from src.metrics import MetricsCollector
from src.themes import THEME_ORDER, get_theme


def parse_args():
    parser = argparse.ArgumentParser(
        description="NeonTop - Modern Themed Terminal & Web System Monitor",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "-i", "--interval",
        type=float,
        default=1.0,
        help="Refresh interval in seconds (minimum 0.5s)",
    )
    parser.add_argument(
        "-s", "--sort",
        type=str,
        choices=["cpu", "ram"],
        default="cpu",
        help="Initial sort order for the process list ('cpu' or 'ram')",
    )
    parser.add_argument(
        "-t", "--theme",
        type=str.lower,
        choices=THEME_ORDER,
        default="slate",
        help="Color theme palette (choices: slate, cyberpunk, matrix, nord, dracula, catppuccin, monochrome)",
    )
    parser.add_argument(
        "--web",
        action="store_true",
        help="Launch the Snowfield Web Dashboard in your default browser with live snow particle animation",
    )
    parser.add_argument(
        "-p", "--port",
        type=int,
        default=5000,
        help="Port for the web dashboard server",
    )
    parser.add_argument(
        "--snapshot",
        action="store_true",
        help="Print a single formatted snapshot to standard output and exit (non-interactive)",
    )
    parser.add_argument(
        "-v", "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    if args.web:
        from src.web_server import start_web_server
        start_web_server(port=args.port, theme=args.theme)
        return

    selected_theme = get_theme(args.theme)

    if args.snapshot:
        console = Console()
        collector = MetricsCollector()
        snapshot = collector.collect(sort_by=args.sort)
        dashboard = build_dashboard(
            snapshot,
            theme=selected_theme,
            sort_by=args.sort,
            pulse=True,
        )
        console.print(dashboard)
        sys.exit(0)

    app = NeonTopApp(
        interval=args.interval,
        sort_by=args.sort,
        theme=args.theme,
    )
    app.run()


if __name__ == "__main__":
    main()
