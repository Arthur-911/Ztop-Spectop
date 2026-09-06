"""Minimalist dashboard layout with custom background styling."""

import datetime
from rich.box import ROUNDED, SIMPLE
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from src.metrics import SystemSnapshot
from src.themes import Theme, get_theme
from src.visualizer import (
    format_bytes,
    format_speed,
    format_uptime,
    make_bar,
    make_sparkline,
)


def create_header(snapshot: SystemSnapshot, theme: Theme, pulse: bool = True) -> Panel:
    """Render the minimalist header bar."""
    pulse_dot = f"[{theme.low}]●[/{theme.low}]" if pulse else f"[{theme.bar_track}]○[/{theme.bar_track}]"
    now_str = datetime.datetime.now().strftime("%H:%M:%S")

    bat_str = ""
    if snapshot.has_battery:
        bat_str = f" · [{theme.text_muted}]bat:[/] [{theme.accent}]{snapshot.battery_percent:.0f}%[/]"

    header_text = Text.from_markup(
        f" [bold {theme.text_main}]ztop spectop[/bold {theme.text_main}] {pulse_dot} "
        f"[{theme.text_muted}]·[/] [{theme.text_muted}]{snapshot.hostname}[/] "
        f"[{theme.text_muted}]({snapshot.os_name} {snapshot.architecture})[/] "
        f"· [{theme.text_muted}]up:[/] [{theme.text_main}]{format_uptime(snapshot.uptime_seconds)}[/]"
        f"{bat_str} "
        f"· [{theme.text_muted}]theme:[/] [{theme.accent}]{theme.display_name}[/] "
        f"· [{theme.text_muted}]{now_str}[/]"
    )
    return Panel(
        header_text,
        box=ROUNDED,
        border_style=theme.border,
        style=f"{theme.text_main} on {theme.panel_bg}",
        padding=(0, 1),
    )


def create_cpu_panel(snapshot: SystemSnapshot, theme: Theme) -> Panel:
    """Render the minimalist CPU panel."""
    color = theme.get_color_for_percent(snapshot.cpu_percent)
    freq_str = f"{snapshot.cpu_freq_current / 1000.0:.2f} GHz" if snapshot.cpu_freq_current > 0 else "N/A"

    content = []
    sparkline = make_sparkline(snapshot.cpu_history, theme=theme, max_val=100.0, length=20)
    content.append(
        f"[{theme.text_muted}]utilization:[/] [{color}]{snapshot.cpu_percent:5.1f}%[/{color}]  "
        f"[{theme.text_muted}]freq:[/] [{theme.text_main}]{freq_str}[/]  "
        f"[{theme.text_muted}]history:[/] {sparkline}\n"
    )

    core_table = Table.grid(expand=True, padding=(0, 1))
    core_table.add_column("C1", ratio=1)
    core_table.add_column("C2", ratio=1)

    cores = snapshot.cpu_cores
    num_cores = len(cores)
    max_display_cores = min(num_cores, 16)
    half = (max_display_cores + 1) // 2

    for i in range(half):
        c1_idx = i
        c2_idx = i + half

        c1_text = f"[{theme.text_muted}]c{c1_idx:02d}[/] {make_bar(cores[c1_idx], theme=theme, width=10)}"
        if c2_idx < num_cores:
            c2_text = f"[{theme.text_muted}]c{c2_idx:02d}[/] {make_bar(cores[c2_idx], theme=theme, width=10)}"
        else:
            c2_text = ""

        core_table.add_row(c1_text, c2_text)

    panel_text = Text.from_markup("".join(content))

    cpu_layout = Layout()
    cpu_layout.split_column(
        Layout(panel_text, size=2),
        Layout(core_table, ratio=1),
    )

    return Panel(
        cpu_layout,
        title=f"[{theme.text_muted}]cpu[/{theme.text_muted}]",
        title_align="left",
        box=ROUNDED,
        border_style=theme.border,
        style=f"{theme.text_main} on {theme.panel_bg}",
        padding=(0, 1),
    )


def create_memory_panel(snapshot: SystemSnapshot, theme: Theme) -> Panel:
    """Render the minimalist RAM and Storage panel."""
    table = Table.grid(expand=True, padding=(0, 1))
    table.add_column("Label", justify="left", width=12)
    table.add_column("Bar", ratio=1)
    table.add_column("Details", justify="right", width=20)

    # Physical RAM
    ram_bar = make_bar(snapshot.ram_percent, theme=theme, width=10)
    ram_details = f"[{theme.text_muted}]{format_bytes(snapshot.ram_used).strip()} / {format_bytes(snapshot.ram_total).strip()}[/]"
    table.add_row(f"[{theme.text_main}]ram[/{theme.text_main}]", ram_bar, ram_details)

    # Swap
    swap_bar = make_bar(snapshot.swap_percent, theme=theme, width=10)
    swap_details = f"[{theme.text_muted}]{format_bytes(snapshot.swap_used).strip()} / {format_bytes(snapshot.swap_total).strip()}[/]"
    table.add_row(f"[{theme.text_main}]swap[/{theme.text_main}]", swap_bar, swap_details)

    table.add_row("", "", "")

    # Storage Partitions
    for disk in snapshot.disks:
        disk_bar = make_bar(disk.percent, theme=theme, width=10)
        disk_details = f"[{theme.text_muted}]{format_bytes(disk.used).strip()} / {format_bytes(disk.total).strip()}[/]"
        clean_mount = disk.mountpoint.replace("\\", "/")
        mount_label = f"[{theme.accent}]disk {clean_mount}[/{theme.accent}]"
        table.add_row(mount_label, disk_bar, disk_details)

    return Panel(
        table,
        title=f"[{theme.text_muted}]memory & storage[/{theme.text_muted}]",
        title_align="left",
        box=ROUNDED,
        border_style=theme.border,
        style=f"{theme.text_main} on {theme.panel_bg}",
        padding=(0, 1),
    )


def create_io_panel(snapshot: SystemSnapshot, theme: Theme) -> Panel:
    """Render the minimalist Network and Disk I/O panel."""
    table = Table(box=SIMPLE, expand=True, show_header=False, padding=(0, 1))
    table.add_column("Label", ratio=1)
    table.add_column("Speed", ratio=1)
    table.add_column("Total", ratio=1)

    dl_color = theme.accent if snapshot.net_download_speed > 0 else theme.text_muted
    ul_color = theme.low if snapshot.net_upload_speed > 0 else theme.text_muted

    table.add_row(
        f"[{theme.text_main}]network download[/{theme.text_main}]",
        f"[{dl_color}]↓ {format_speed(snapshot.net_download_speed)}[/{dl_color}]",
        f"[{theme.text_muted}]tot: {format_bytes(snapshot.net_bytes_recv)}[/{theme.text_muted}]"
    )
    table.add_row(
        f"[{theme.text_main}]network upload[/{theme.text_main}]",
        f"[{ul_color}]↑ {format_speed(snapshot.net_upload_speed)}[/{ul_color}]",
        f"[{theme.text_muted}]tot: {format_bytes(snapshot.net_bytes_sent)}[/{theme.text_muted}]"
    )

    read_color = theme.accent if snapshot.disk_read_speed > 0 else theme.text_muted
    write_color = theme.low if snapshot.disk_write_speed > 0 else theme.text_muted

    table.add_row(
        f"[{theme.text_main}]disk read[/{theme.text_main}]",
        f"[{read_color}]r: {format_speed(snapshot.disk_read_speed)}[/{read_color}]",
        ""
    )
    table.add_row(
        f"[{theme.text_main}]disk write[/{theme.text_main}]",
        f"[{write_color}]w: {format_speed(snapshot.disk_write_speed)}[/{write_color}]",
        ""
    )

    return Panel(
        table,
        title=f"[{theme.text_muted}]network & disk io[/{theme.text_muted}]",
        title_align="left",
        box=ROUNDED,
        border_style=theme.border,
        style=f"{theme.text_main} on {theme.panel_bg}",
        padding=(0, 1),
    )


def create_session_panel(snapshot: SystemSnapshot, theme: Theme) -> Panel:
    """Render the dedicated App Background Session & Laptop Runtime panel."""
    table = Table(box=SIMPLE, expand=True, show_header=False, padding=(0, 1))
    table.add_column("Property", ratio=1)
    table.add_column("Value", ratio=1)

    app_time_str = format_uptime(snapshot.app_uptime_seconds)
    start_time_str = datetime.datetime.fromtimestamp(snapshot.app_start_time).strftime("%H:%M:%S")

    power_status = "Plugged In" if snapshot.battery_plugged else "On Battery"
    if snapshot.has_battery:
        power_str = f"{power_status} ({snapshot.battery_percent:.0f}%)"
    else:
        power_str = f"{power_status}"

    footprint_str = f"{snapshot.app_cpu_percent:4.1f}% cpu · {snapshot.app_memory_mb:4.1f} MB"

    table.add_row(
        f"[{theme.text_main}]app background time[/{theme.text_main}]",
        f"[bold {theme.accent}]{app_time_str}[/bold {theme.accent}]",
    )
    table.add_row(
        f"[{theme.text_main}]session started[/{theme.text_main}]",
        f"[{theme.text_muted}]{start_time_str}[/{theme.text_muted}]",
    )
    table.add_row(
        f"[{theme.text_main}]app footprint[/{theme.text_main}]",
        f"[{theme.low}]{footprint_str}[/{theme.low}]",
    )
    table.add_row(
        f"[{theme.text_main}]laptop power state[/{theme.text_main}]",
        f"[{theme.text_muted}]{power_str}[/{theme.text_muted}]",
    )

    return Panel(
        table,
        title=f"[{theme.text_muted}]app background session[/{theme.text_muted}]",
        title_align="left",
        box=ROUNDED,
        border_style=theme.border,
        style=f"{theme.text_main} on {theme.panel_bg}",
        padding=(0, 1),
    )


def create_process_panel(snapshot: SystemSnapshot, theme: Theme, sort_by: str = "cpu") -> Panel:
    """Render the minimalist process monitor table."""
    table = Table(box=SIMPLE, expand=True, padding=(0, 1))
    table.add_column("pid", justify="right", style=theme.text_muted, width=6)
    table.add_column("process", justify="left", ratio=3, no_wrap=True)
    table.add_column("cpu%", justify="right", style=f"bold {theme.accent}" if sort_by == "cpu" else theme.text_main, width=7)
    table.add_column("mem%", justify="right", style=f"bold {theme.accent}" if sort_by == "ram" else theme.text_main, width=7)
    table.add_column("time", justify="right", style=theme.text_muted, width=8)

    for proc in snapshot.processes:
        cpu_color = theme.get_color_for_percent(proc.cpu_percent)
        mem_color = theme.get_color_for_percent(proc.memory_percent)
        time_str = format_uptime(proc.runtime_seconds)

        table.add_row(
            str(proc.pid),
            proc.name,
            f"[{cpu_color}]{proc.cpu_percent:5.1f}%[/{cpu_color}]",
            f"[{mem_color}]{proc.memory_percent:5.1f}%[/{mem_color}]",
            f"[{theme.text_muted}]{time_str}[/{theme.text_muted}]",
        )

    return Panel(
        table,
        title=f"[{theme.text_muted}]processes (sort: {sort_by})[/{theme.text_muted}]",
        title_align="left",
        box=ROUNDED,
        border_style=theme.border,
        style=f"{theme.text_main} on {theme.panel_bg}",
        padding=(0, 1),
    )


def create_footer(theme: Theme, is_paused: bool = False, sort_by: str = "cpu") -> Panel:
    """Render the minimalist footer controls bar."""
    status_tag = f"[{theme.high}]paused[/{theme.high}]" if is_paused else f"[{theme.low}]live[/{theme.low}]"

    footer_text = Text.from_markup(
        f" [{status_tag}]  "
        f"[{theme.text_muted}]·[/]  [bold {theme.accent}]q[/bold {theme.accent}] [{theme.text_muted}]quit[/]  "
        f"[{theme.text_muted}]·[/]  [bold {theme.accent}]t[/bold {theme.accent}] [{theme.text_muted}]theme: [bold {theme.text_main}]{theme.display_name}[/bold {theme.text_main}][/]  "
        f"[{theme.text_muted}]·[/]  [bold {theme.accent}]s[/bold {theme.accent}] [{theme.text_muted}]sort: [bold {theme.text_main}]{sort_by}[/bold {theme.text_main}][/]  "
        f"[{theme.text_muted}]·[/]  [bold {theme.accent}]space[/bold {theme.accent}] [{theme.text_muted}]pause[/]"
    )
    return Panel(
        footer_text,
        box=ROUNDED,
        border_style=theme.border,
        style=f"{theme.text_main} on {theme.panel_bg}",
        padding=(0, 1),
    )


def build_dashboard(
    snapshot: SystemSnapshot,
    theme: Theme | None = None,
    sort_by: str = "cpu",
    pulse: bool = True,
    is_paused: bool = False,
) -> Layout:
    """Assemble the minimalist terminal dashboard."""
    if theme is None:
        theme = get_theme("slate")

    layout = Layout()

    # Split into Header, Main, Footer
    layout.split_column(
        Layout(name="header", size=3),
        Layout(name="main", ratio=1),
        Layout(name="footer", size=3),
    )

    layout["header"].update(create_header(snapshot, theme=theme, pulse=pulse))
    layout["footer"].update(create_footer(theme=theme, is_paused=is_paused, sort_by=sort_by))

    # Split Main into two rows
    layout["main"].split_column(
        Layout(name="top_row", ratio=1),
        Layout(name="bottom_row", ratio=1),
    )

    # Top row: CPU & Memory
    layout["top_row"].split_row(
        Layout(create_cpu_panel(snapshot, theme=theme), name="cpu", ratio=1),
        Layout(create_memory_panel(snapshot, theme=theme), name="memory", ratio=1),
    )

    # Bottom row: Left column (Network/IO + App Session) & Right column (Processes)
    layout["bottom_row"].split_row(
        Layout(name="bottom_left", ratio=1),
        Layout(create_process_panel(snapshot, theme=theme, sort_by=sort_by), name="processes", ratio=1),
    )

    layout["bottom_left"].split_column(
        Layout(create_io_panel(snapshot, theme=theme), name="io", ratio=1),
        Layout(create_session_panel(snapshot, theme=theme), name="session", ratio=1),
    )

    return layout
