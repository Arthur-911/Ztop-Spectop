"""System metrics collection engine using psutil with process caching."""

import os
import platform
import socket
import time
from collections import deque
from dataclasses import dataclass
from typing import Dict, List, Optional, Set
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
    status: str
    threads: int


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

    # Processes
    processes: List[ProcessInfo]


class MetricsCollector:
    """Collects and smooths system performance metrics."""

    def __init__(self, history_size: int = 40):
        self.history_size = history_size
        self.cpu_history: deque[float] = deque(maxlen=history_size)
        
        # System metadata
        try:
            self.hostname = socket.gethostname()
        except Exception:
            self.hostname = "localhost"

        self.os_name = f"{platform.system()} {platform.release()}"
        self.architecture = platform.machine()
        
        try:
            self.boot_time = psutil.boot_time()
        except Exception:
            self.boot_time = time.time()

        # Cache of persistent Process instances for accurate CPU delta calculations
        self._procs: Dict[int, psutil.Process] = {}

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

        # Prime psutil overall & core CPU stats
        try:
            psutil.cpu_percent(interval=None, percpu=True)
            psutil.cpu_percent(interval=None)
        except Exception:
            pass

        # Prime initial processes so next poll has valid CPU deltas
        self._prime_processes()
        time.sleep(0.05)

    def _prime_processes(self) -> None:
        """Prime active processes to initialize CPU delta counters."""
        try:
            for p in psutil.process_iter(['pid', 'name']):
                if p.pid == 0:
                    continue
                try:
                    p.cpu_percent(interval=None)
                    self._procs[p.pid] = p
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
        except Exception:
            pass

    def collect(self, sort_by: str = "cpu", limit_processes: int = 10) -> SystemSnapshot:
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

        # CPU Frequency (safely handled for VM/ARM/WSL setups)
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

        # 3. Disks & Disk I/O (with mount deduplication)
        disks: List[DiskInfo] = []
        seen_mounts: Set[str] = set()
        try:
            partitions = psutil.disk_partitions(all=False)
        except Exception:
            partitions = []

        for part in partitions:
            # Skip virtual/unready mounts
            if "cdrom" in part.opts or part.fstype == "" or part.mountpoint in seen_mounts:
                continue
            try:
                usage = psutil.disk_usage(part.mountpoint)
                seen_mounts.add(part.mountpoint)
                disks.append(
                    DiskInfo(
                        mountpoint=part.mountpoint,
                        fstype=part.fstype,
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

        # 6. Process Monitoring (with caching & PID 0 filtering)
        processes: List[ProcessInfo] = []
        cpu_count = psutil.cpu_count(logical=True) or 1

        try:
            active_pids = set(psutil.pids())
        except Exception:
            active_pids = set(self._procs.keys())

        # Prune terminated processes from cache
        self._procs = {pid: p for pid, p in self._procs.items() if pid in active_pids}

        # Iterate active processes
        for pid in active_pids:
            if pid == 0:
                continue  # Skip System Idle Process

            proc = self._procs.get(pid)
            if proc is None:
                try:
                    proc = psutil.Process(pid)
                    proc.cpu_percent(interval=None)  # prime
                    self._procs[pid] = proc
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue

            try:
                with proc.oneshot():
                    name = proc.name() or "unknown"
                    raw_cpu = proc.cpu_percent(interval=None)
                    # Normalize CPU to 0-100% scale
                    cpu_p = max(0.0, min(100.0, raw_cpu / cpu_count))
                    mem_p = proc.memory_percent() or 0.0
                    status = proc.status() or "?"
                    threads = proc.num_threads() or 1

                    processes.append(
                        ProcessInfo(
                            pid=pid,
                            name=name,
                            cpu_percent=cpu_p,
                            memory_percent=mem_p,
                            status=str(status).upper(),
                            threads=threads,
                        )
                    )
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                self._procs.pop(pid, None)
                continue

        # Sort processes according to selected metric
        if sort_by.lower() in ("ram", "mem"):
            processes.sort(key=lambda p: p.memory_percent, reverse=True)
        else:
            processes.sort(key=lambda p: p.cpu_percent, reverse=True)

        processes = processes[:limit_processes]

        # Update timing reference
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
            processes=processes,
        )
