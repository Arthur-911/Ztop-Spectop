"""System metrics collection engine using psutil with process caching."""

import dataclasses
import os
import platform
import socket
import sys
import threading
import time
from collections import deque
from dataclasses import dataclass
from typing import Dict, List, Optional, Set, Tuple
import psutil


@dataclass
class DiskInfo:
    mountpoint: str
    fstype: str
    total: int
    used: int
    free: int
    percent: float


@dataclass
class ProcessInfo:
    pid: int
    name: str
    cpu_percent: float
    memory_percent: float
    status: str = "RUNNING"
    threads: int = 1
    runtime_seconds: float = 0.0


@dataclass
class SystemSnapshot:
    # CPU
    cpu_percent: float
    cpu_cores: List[float]
    cpu_freq_current: float
    cpu_history: List[float]

    # Memory
    ram_total: int
    ram_used: int
    ram_free: int
    ram_percent: float
    swap_total: int
    swap_used: int
    swap_percent: float

    # Disks & Disk I/O
    disks: List[DiskInfo]
    disk_read_speed: float  # bytes / sec
    disk_write_speed: float  # bytes / sec

    # Network
    net_download_speed: float  # bytes / sec
    net_upload_speed: float  # bytes / sec
    net_bytes_recv: int
    net_bytes_sent: int

    # Battery
    has_battery: bool
    battery_percent: float
    battery_plugged: bool

    # Host & Uptime
    hostname: str
    os_name: str
    architecture: str
    uptime_seconds: float

    # App Session & Background Runtime
    app_uptime_seconds: float
    app_start_time: float
    app_cpu_percent: float
    app_memory_mb: float

    # Processes
    processes: List[ProcessInfo]


def _detect_os_name() -> str:
    """Detect human-friendly operating system name and version (e.g. Windows 11 25H2)."""
    system = platform.system()
    if system == "Windows":
        try:
            build = sys.getwindowsversion().build
            # Windows 11 kernel builds begin at 22000
            base = "Windows 11" if build >= 22000 else f"Windows {platform.release()}"
            try:
                import winreg
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows NT\CurrentVersion") as key:
                    dv, _ = winreg.QueryValueEx(key, "DisplayVersion")
                    if dv:
                        return f"{base} {dv}"
            except Exception:
                pass
            return base
        except Exception:
            return f"Windows {platform.release()}"
    elif system == "Darwin":
        return f"macOS {platform.mac_ver()[0]}"
    elif system == "Linux":
        try:
            with open("/etc/os-release") as f:
                for line in f:
                    if line.startswith("PRETTY_NAME="):
                        return line.split("=", 1)[1].strip().strip('"')
        except Exception:
            pass
        return f"Linux {platform.release()}"
    return f"{system} {platform.release()}"


def _detect_architecture() -> str:
    """Detect clean system architecture string (e.g. x64, ARM64)."""
    mach = platform.machine()
    if mach.upper() in ("AMD64", "X86_64"):
        return "x64"
    elif mach.upper() in ("ARM64", "AARCH64"):
        return "ARM64"
    elif mach.upper() in ("X86", "I386", "I686"):
        return "x86"
    return mach


class MetricsCollector:
    """Collects and smooths system performance metrics with high efficiency."""

    def __init__(self, history_size: int = 40):
        self.history_size = history_size
        self.cpu_history: deque[float] = deque(maxlen=history_size)
        self.app_start_time = time.time()
        try:
            self._self_proc = psutil.Process(os.getpid())
            self._self_proc.cpu_percent(interval=None)
        except Exception:
            self._self_proc = None

        # System metadata
        try:
            self.hostname = socket.gethostname()
        except Exception:
            self.hostname = "localhost"

        self.os_name = _detect_os_name()
        self.architecture = _detect_architecture()

        try:
            self.boot_time = psutil.boot_time()
        except Exception:
            self.boot_time = time.time()

        self.cpu_count = psutil.cpu_count(logical=True) or 1

        # Previous snapshot references for rate calculations
        self._last_time = time.time()
        try:
            self._last_net_io = psutil.net_io_counters()
        except Exception:
            self._last_net_io = None

        try:
            self._last_disk_io = psutil.disk_io_counters()
        except Exception:
            self._last_disk_io = None

        # Cache disk partitions to avoid expensive WMI/kernel device scans every tick
        self._cached_partitions: List[str] = []
        self._last_partition_scan: float = 0.0

        # Raw process snapshot cache for instantaneous sort switching
        self._raw_procs: List[Tuple[int, str, float, float, psutil.Process]] = []

        # Threading & Background Worker
        self._lock = threading.RLock()
        self._bg_thread: Optional[threading.Thread] = None
        self._bg_running = False
        self._latest_snapshot: Optional[SystemSnapshot] = None
        self._update_event = threading.Event()
        self._stop_event = threading.Event()
        self.interval = 1.0

        # Prime psutil counters
        try:
            psutil.cpu_percent(interval=None, percpu=True)
            psutil.cpu_percent(interval=None)
            list(psutil.process_iter(attrs=['name', 'cpu_percent', 'memory_percent']))
        except Exception:
            pass

    def start_background(self, interval: float = 1.0) -> None:
        """Start a background daemon thread that periodically collects snapshots."""
        with self._lock:
            if self._bg_running:
                return
            self._bg_running = True
            self._stop_event.clear()
            self.interval = max(0.2, interval)

        # Initial collection outside lock
        initial_snap = self.collect(sort_by="cpu")
        with self._lock:
            self._latest_snapshot = initial_snap
            self._bg_thread = threading.Thread(
                target=self._bg_worker,
                daemon=True,
                name="MetricsWorkerThread",
            )
            self._bg_thread.start()

    def stop_background(self) -> None:
        """Stop the background collection thread."""
        with self._lock:
            self._bg_running = False
        self._stop_event.set()
        if self._bg_thread and self._bg_thread.is_alive():
            self._bg_thread.join(timeout=1.0)

    def _bg_worker(self) -> None:
        while self._bg_running:
            t0 = time.time()
            try:
                snap = self.collect(sort_by="cpu")
                with self._lock:
                    self._latest_snapshot = snap
                self._update_event.set()
            except Exception:
                pass
            elapsed = time.time() - t0
            sleep_time = max(0.05, self.interval - elapsed)
            if self._stop_event.wait(sleep_time):
                break

    def get_latest_snapshot(self, sort_by: str = "cpu", limit_processes: int = 10) -> SystemSnapshot:
        """Get the latest snapshot immediately with zero latency and requested sort."""
        with self._lock:
            if self._latest_snapshot is None:
                self._latest_snapshot = self.collect(sort_by=sort_by, limit_processes=limit_processes)
                return self._latest_snapshot

            snap = self._latest_snapshot
            raw = list(self._raw_procs)

        if not raw:
            return snap

        # Fast in-memory process sorting and extraction
        if sort_by.lower() in ("ram", "mem"):
            raw.sort(key=lambda x: x[3], reverse=True)
        else:
            raw.sort(key=lambda x: x[2], reverse=True)

        selected = raw[:limit_processes]
        now = time.time()
        procs: List[ProcessInfo] = []

        for pid, name, cpu_p, mem_p, p in selected:
            runtime_s = 0.0
            try:
                ct = p.create_time()
                runtime_s = max(0.0, now - (ct if ct > self.boot_time else self.boot_time))
            except Exception:
                pass
            procs.append(
                ProcessInfo(
                    pid=pid,
                    name=name,
                    cpu_percent=cpu_p,
                    memory_percent=mem_p,
                    status="RUNNING",
                    threads=1,
                    runtime_seconds=runtime_s,
                )
            )

        return dataclasses.replace(snap, processes=procs)

    def collect(self, sort_by: str = "cpu", limit_processes: int = 10) -> SystemSnapshot:
        """Collect all system telemetry quickly with minimal CPU overhead."""
        now = time.time()
        dt = max(now - self._last_time, 0.001)

        # 1. Overall & Per-Core CPU
        try:
            cpu_overall = psutil.cpu_percent(interval=None)
        except Exception:
            cpu_overall = 0.0

        self.cpu_history.append(cpu_overall)

        try:
            cpu_cores = psutil.cpu_percent(interval=None, percpu=True)
        except Exception:
            cpu_cores = [cpu_overall]

        try:
            freq = psutil.cpu_freq()
            cpu_freq_current = freq.current if freq else 0.0
        except Exception:
            cpu_freq_current = 0.0

        # 2. Virtual & Swap Memory
        try:
            vmem = psutil.virtual_memory()
            ram_total = vmem.total
            ram_used = vmem.used
            ram_free = vmem.available
            ram_percent = vmem.percent
        except Exception:
            ram_total = ram_used = ram_free = 0
            ram_percent = 0.0

        try:
            swap = psutil.swap_memory()
            swap_total = swap.total
            swap_used = swap.used
            swap_percent = swap.percent
        except Exception:
            swap_total = swap_used = 0
            swap_percent = 0.0

        # 3. Disks & Disk I/O (Cached partitions to prevent drive-scanning lag)
        if not self._cached_partitions or (now - self._last_partition_scan > 60.0):
            try:
                self._cached_partitions = [
                    p.mountpoint
                    for p in psutil.disk_partitions(all=False)
                    if "cdrom" not in p.opts and p.fstype != ""
                ]
                self._last_partition_scan = now
            except Exception:
                self._cached_partitions = ["C:\\"] if sys.platform == "win32" else ["/"]
                self._last_partition_scan = now

        disks: List[DiskInfo] = []
        seen_mounts: Set[str] = set()
        for mountpoint in self._cached_partitions:
            if mountpoint in seen_mounts:
                continue
            try:
                usage = psutil.disk_usage(mountpoint)
                seen_mounts.add(mountpoint)
                disks.append(
                    DiskInfo(
                        mountpoint=mountpoint,
                        fstype="",
                        total=usage.total,
                        used=usage.used,
                        free=usage.free,
                        percent=usage.percent,
                    )
                )
            except (PermissionError, OSError):
                continue

        # Disk I/O Rates
        try:
            current_disk_io = psutil.disk_io_counters()
        except Exception:
            current_disk_io = None

        if current_disk_io and self._last_disk_io:
            read_bytes = max(0, current_disk_io.read_bytes - self._last_disk_io.read_bytes)
            write_bytes = max(0, current_disk_io.write_bytes - self._last_disk_io.write_bytes)
            disk_read_speed = max(0.0, read_bytes / dt)
            disk_write_speed = max(0.0, write_bytes / dt)
        else:
            disk_read_speed = 0.0
            disk_write_speed = 0.0

        if current_disk_io:
            self._last_disk_io = current_disk_io

        # 4. Network Rates & Totals
        try:
            current_net_io = psutil.net_io_counters()
        except Exception:
            current_net_io = None

        if current_net_io and self._last_net_io:
            recv_bytes = max(0, current_net_io.bytes_recv - self._last_net_io.bytes_recv)
            sent_bytes = max(0, current_net_io.bytes_sent - self._last_net_io.bytes_sent)
            net_download_speed = max(0.0, recv_bytes / dt)
            net_upload_speed = max(0.0, sent_bytes / dt)
        else:
            net_download_speed = 0.0
            net_upload_speed = 0.0

        if current_net_io:
            self._last_net_io = current_net_io

        # 5. Battery Status
        try:
            battery = psutil.sensors_battery()
            has_battery = battery is not None
            battery_percent = battery.percent if battery else 0.0
            battery_plugged = battery.power_plugged if battery else False
        except Exception:
            has_battery = False
            battery_percent = 0.0
            battery_plugged = False

        # 6. High-Performance Process Monitoring
        raw_procs: List[Tuple[int, str, float, float, psutil.Process]] = []
        try:
            for p in psutil.process_iter(attrs=['name', 'cpu_percent', 'memory_percent']):
                try:
                    info = p.info
                    name = info.get('name')
                    if not name or name == 'System Idle Process' or p.pid == 0:
                        continue
                    raw_cpu = info.get('cpu_percent') or 0.0
                    cpu_p = max(0.0, min(100.0, raw_cpu / self.cpu_count))
                    mem_p = info.get('memory_percent') or 0.0
                    raw_procs.append((p.pid, name, cpu_p, mem_p, p))
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
                except Exception:
                    continue
        except Exception:
            pass

        with self._lock:
            self._raw_procs = raw_procs

        # Sort according to requested metric
        if sort_by.lower() in ("ram", "mem"):
            raw_procs.sort(key=lambda x: x[3], reverse=True)
        else:
            raw_procs.sort(key=lambda x: x[2], reverse=True)

        selected = raw_procs[:limit_processes]
        processes: List[ProcessInfo] = []

        for pid, name, cpu_p, mem_p, p in selected:
            runtime_s = 0.0
            try:
                ct = p.create_time()
                runtime_s = max(0.0, now - (ct if ct > self.boot_time else self.boot_time))
            except Exception:
                pass

            processes.append(
                ProcessInfo(
                    pid=pid,
                    name=name,
                    cpu_percent=cpu_p,
                    memory_percent=mem_p,
                    status="RUNNING",
                    threads=1,
                    runtime_seconds=runtime_s,
                )
            )

        # 7. App Footprint (Ztop Spectop running in background)
        app_cpu = 0.0
        app_mem = 0.0
        if self._self_proc:
            try:
                app_mem = self._self_proc.memory_info().rss / (1024 * 1024)
                raw_app_cpu = self._self_proc.cpu_percent(interval=None)
                app_cpu = max(0.0, min(100.0, raw_app_cpu / self.cpu_count))
            except Exception:
                pass

        self._last_time = now

        return SystemSnapshot(
            cpu_percent=cpu_overall,
            cpu_cores=cpu_cores,
            cpu_freq_current=cpu_freq_current,
            cpu_history=list(self.cpu_history),
            ram_total=ram_total,
            ram_used=ram_used,
            ram_free=ram_free,
            ram_percent=ram_percent,
            swap_total=swap_total,
            swap_used=swap_used,
            swap_percent=swap_percent,
            disks=disks,
            disk_read_speed=disk_read_speed,
            disk_write_speed=disk_write_speed,
            net_download_speed=net_download_speed,
            net_upload_speed=net_upload_speed,
            net_bytes_recv=current_net_io.bytes_recv if current_net_io else 0,
            net_bytes_sent=current_net_io.bytes_sent if current_net_io else 0,
            has_battery=has_battery,
            battery_percent=battery_percent,
            battery_plugged=battery_plugged,
            hostname=self.hostname,
            os_name=self.os_name,
            architecture=self.architecture,
            uptime_seconds=max(0.0, now - self.boot_time),
            app_uptime_seconds=max(0.0, now - self.app_start_time),
            app_start_time=self.app_start_time,
            app_cpu_percent=app_cpu,
            app_memory_mb=app_mem,
            processes=processes,
        )
