"""Minimalist Web Dashboard with Snow Field Background, Snow Particle Physics & Theme Switcher."""

import os
from flask import Flask, jsonify, render_template_string
from src.metrics import MetricsCollector

collector = MetricsCollector()
app = Flask(__name__)
app.config["DEFAULT_THEME"] = "slate"

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>NeonTop - Snowfield Monitor</title>
  <style>
    /* Default Theme: Slate */
    :root, body[data-theme="slate"] {
      --bg-color: #0a0c10;
      --card-bg: rgba(14, 19, 27, 0.72);
      --card-border: rgba(56, 189, 248, 0.22);
      --text-main: #f8fafc;
      --text-muted: #94a3b8;
      --accent: #38bdf8;
      --low: #34d399;
      --med: #fbbf24;
      --high: #f87171;
    }

    body[data-theme="cyberpunk"] {
      --bg-color: #080410;
      --card-bg: rgba(16, 8, 32, 0.78);
      --card-border: rgba(255, 0, 85, 0.45);
      --text-main: #ffffff;
      --text-muted: #c084fc;
      --accent: #00f0ff;
      --low: #00ff9f;
      --med: #ffe600;
      --high: #ff0055;
    }

    body[data-theme="matrix"] {
      --bg-color: #000a02;
      --card-bg: rgba(2, 20, 5, 0.82);
      --card-border: rgba(0, 204, 68, 0.4);
      --text-main: #e6ffe6;
      --text-muted: #4ade80;
      --accent: #00ff66;
      --low: #22cc44;
      --med: #88ff44;
      --high: #ff3333;
    }

    body[data-theme="nord"] {
      --bg-color: #1e222a;
      --card-bg: rgba(36, 41, 51, 0.78);
      --card-border: rgba(136, 192, 208, 0.35);
      --text-main: #eceff4;
      --text-muted: #88c0d0;
      --accent: #88c0d0;
      --low: #a3be8c;
      --med: #ebcb8b;
      --high: #bf616a;
    }

    body[data-theme="dracula"] {
      --bg-color: #191a21;
      --card-bg: rgba(33, 34, 44, 0.8);
      --card-border: rgba(189, 147, 249, 0.4);
      --text-main: #f8f8f2;
      --text-muted: #bd93f9;
      --accent: #ff79c6;
      --low: #50fa7b;
      --med: #ffb86c;
      --high: #ff5555;
    }

    body[data-theme="catppuccin"] {
      --bg-color: #11111b;
      --card-bg: rgba(24, 24, 37, 0.8);
      --card-border: rgba(203, 166, 247, 0.35);
      --text-main: #cdd6f4;
      --text-muted: #a6adc8;
      --accent: #cba6f7;
      --low: #a6e3a1;
      --med: #fab387;
      --high: #f38ba8;
    }

    body[data-theme="monochrome"] {
      --bg-color: #000000;
      --card-bg: rgba(10, 10, 10, 0.85);
      --card-border: rgba(255, 255, 255, 0.35);
      --text-main: #ffffff;
      --text-muted: #a3a3a3;
      --accent: #ffffff;
      --low: #e5e5e5;
      --med: #a3a3a3;
      --high: #ffffff;
    }

    * {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }

    body {
      background-color: var(--bg-color);
      background-image: url('/background.jpg');
      background-repeat: no-repeat;
      background-position: center center;
      background-attachment: fixed;
      background-size: cover;
      color: var(--text-main);
      min-height: 100vh;
      overflow-x: hidden;
      position: relative;
      transition: background-color 0.3s ease;
    }

    /* Ambient dark overlay for maximum readability */
    .backdrop-overlay {
      position: fixed;
      inset: 0;
      background: radial-gradient(circle at center, rgba(10, 15, 28, 0.55) 0%, rgba(6, 10, 18, 0.85) 100%);
      z-index: 0;
      pointer-events: none;
    }

    /* Snow Particle Canvas */
    #snow-canvas {
      position: fixed;
      inset: 0;
      width: 100%;
      height: 100%;
      z-index: 1;
      pointer-events: none;
    }

    /* Main Container */
    .container {
      position: relative;
      z-index: 2;
      max-width: 1200px;
      margin: 0 auto;
      padding: 24px 20px;
      display: flex;
      flex-direction: column;
      gap: 18px;
    }

    /* Frosted Glass Cards */
    .glass-card {
      background: var(--card-bg);
      backdrop-filter: blur(18px);
      -webkit-backdrop-filter: blur(18px);
      border: 1px solid var(--card-border);
      border-radius: 14px;
      padding: 18px 22px;
      box-shadow: 0 10px 30px rgba(0, 0, 0, 0.35);
      transition: border-color 0.3s ease, background-color 0.3s ease;
    }

    .glass-card:hover {
      border-color: rgba(255, 255, 255, 0.25);
    }

    /* Header */
    header.glass-card {
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 12px;
      padding: 14px 22px;
    }

    .brand {
      display: flex;
      align-items: center;
      gap: 10px;
      font-weight: 600;
      font-size: 1.15rem;
      letter-spacing: -0.02em;
    }

    .status-dot {
      width: 9px;
      height: 9px;
      background: var(--low);
      border-radius: 50%;
      display: inline-block;
      box-shadow: 0 0 10px var(--low);
      animation: pulse 2s infinite ease-in-out;
    }

    @keyframes pulse {
      0%, 100% { opacity: 1; transform: scale(1); }
      50% { opacity: 0.4; transform: scale(0.85); }
    }

    .meta-info {
      display: flex;
      align-items: center;
      gap: 14px;
      font-size: 0.85rem;
      color: var(--text-muted);
      flex-wrap: wrap;
    }

    .meta-info span b {
      color: var(--text-main);
      font-weight: 500;
    }

    /* Dashboard Grid */
    .grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(360px, 1fr));
      gap: 18px;
    }

    .card-title {
      font-size: 0.8rem;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      color: var(--text-muted);
      margin-bottom: 14px;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    /* CPU Section */
    .big-stat {
      font-size: 2.2rem;
      font-weight: 700;
      letter-spacing: -0.03em;
      color: var(--text-main);
      margin-bottom: 8px;
      display: flex;
      align-items: baseline;
      gap: 10px;
    }

    .big-stat small {
      font-size: 0.9rem;
      font-weight: 400;
      color: var(--text-muted);
    }

    /* Progress Bars */
    .bar-container {
      width: 100%;
      height: 6px;
      background: rgba(255, 255, 255, 0.08);
      border-radius: 999px;
      overflow: hidden;
      margin: 6px 0 14px;
    }

    .bar-fill {
      height: 100%;
      background: var(--accent);
      border-radius: 999px;
      transition: width 0.4s ease, background-color 0.4s ease;
    }

    /* Core Mini Grid */
    .cores-grid {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 8px;
      margin-top: 10px;
    }

    .core-box {
      background: rgba(255, 255, 255, 0.03);
      border: 1px solid rgba(255, 255, 255, 0.05);
      border-radius: 8px;
      padding: 6px 8px;
      text-align: center;
    }

    .core-box span {
      display: block;
      font-size: 0.7rem;
      color: var(--text-muted);
    }

    .core-box b {
      font-size: 0.85rem;
      color: var(--text-main);
    }

    /* Stat Rows */
    .stat-row {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 4px;
      font-size: 0.85rem;
    }

    .stat-row .label {
      color: var(--text-muted);
    }

    .stat-row .val {
      font-weight: 500;
    }

    /* Process Table */
    table {
      width: 100%;
      border-collapse: collapse;
      font-size: 0.82rem;
    }

    th {
      text-align: left;
      color: var(--text-muted);
      font-weight: 500;
      padding-bottom: 8px;
      border-bottom: 1px solid rgba(255, 255, 255, 0.08);
    }

    td {
      padding: 8px 0;
      border-bottom: 1px solid rgba(255, 255, 255, 0.04);
    }

    td:last-child, th:last-child {
      text-align: right;
    }

    .btn-toggle {
      background: rgba(255, 255, 255, 0.08);
      border: 1px solid rgba(255, 255, 255, 0.18);
      color: var(--text-main);
      padding: 5px 12px;
      border-radius: 6px;
      font-size: 0.78rem;
      font-weight: 500;
      cursor: pointer;
      transition: background 0.2s, border-color 0.2s;
    }

    .btn-toggle:hover {
      background: rgba(255, 255, 255, 0.18);
      border-color: var(--accent);
    }
  </style>
</head>
<body data-theme="slate">
  <div class="backdrop-overlay"></div>
  <canvas id="snow-canvas"></canvas>

  <div class="container">
    <header class="glass-card">
      <div class="brand">
        <span class="status-dot"></span>
        <span>neontop</span>
        <span style="font-size: 0.75rem; color: var(--accent); background: rgba(56, 189, 248, 0.12); padding: 2px 8px; border-radius: 999px;">snowfield</span>
      </div>
      <div class="meta-info">
        <span>host: <b id="host">--</b></span>
        <span>os: <b id="os">--</b></span>
        <span>uptime: <b id="uptime">--</b></span>
        <span id="battery-box" style="display:none;">battery: <b id="battery">--</b></span>
        <button id="theme-btn" class="btn-toggle" onclick="cycleTheme()">🎨 Theme: Slate</button>
        <button id="snow-btn" class="btn-toggle" onclick="toggleSnow()">❄ Snow: On</button>
      </div>
    </header>

    <div class="grid">
      <!-- CPU Card -->
      <div class="glass-card">
        <div class="card-title">
          <span>Processor Telemetry</span>
          <span id="freq">-- GHz</span>
        </div>
        <div class="big-stat">
          <span id="cpu-total">0.0%</span>
          <small>Load Average</small>
        </div>
        <div class="bar-container">
          <div class="bar-fill" id="cpu-bar" style="width: 0%;"></div>
        </div>
        <div class="cores-grid" id="cores-container"></div>
      </div>

      <!-- Memory & Storage Card -->
      <div class="glass-card">
        <div class="card-title">Memory & Storage</div>
        <div class="stat-row">
          <span class="label">Physical Memory (RAM)</span>
          <span class="val" id="ram-val">0 / 0 GB</span>
        </div>
        <div class="bar-container">
          <div class="bar-fill" id="ram-bar" style="width: 0%;"></div>
        </div>

        <div class="stat-row">
          <span class="label">Swap Space</span>
          <span class="val" id="swap-val">0 / 0 GB</span>
        </div>
        <div class="bar-container">
          <div class="bar-fill" id="swap-bar" style="width: 0%;"></div>
        </div>

        <div id="disks-container" style="margin-top: 6px;"></div>
      </div>

      <!-- Network & Disk IO -->
      <div class="glass-card">
        <div class="card-title">Network & Disk Throughput</div>
        <div class="stat-row" style="margin-bottom: 12px;">
          <div>
            <div class="label">Download Bandwidth</div>
            <div style="font-size: 1.25rem; font-weight: 600; color: var(--accent);" id="net-down">0.0 KB/s</div>
          </div>
          <div style="text-align: right;">
            <div class="label">Total Rx</div>
            <div class="val" id="net-down-tot">0 MB</div>
          </div>
        </div>

        <div class="stat-row" style="margin-bottom: 16px;">
          <div>
            <div class="label">Upload Bandwidth</div>
            <div style="font-size: 1.25rem; font-weight: 600; color: var(--low);" id="net-up">0.0 KB/s</div>
          </div>
          <div style="text-align: right;">
            <div class="label">Total Tx</div>
            <div class="val" id="net-up-tot">0 MB</div>
          </div>
        </div>

        <div class="stat-row">
          <span class="label">Disk Read Throughput</span>
          <span class="val" id="disk-read">0.0 B/s</span>
        </div>
        <div class="stat-row">
          <span class="label">Disk Write Throughput</span>
          <span class="val" id="disk-write">0.0 B/s</span>
        </div>
      </div>

      <!-- App Background Session Card -->
      <div class="glass-card">
        <div class="card-title">
          <span>App Background Session</span>
          <span style="font-size: 0.72rem; color: var(--low); background: rgba(52, 211, 153, 0.12); padding: 2px 8px; border-radius: 999px; font-weight: 500;">Running</span>
        </div>
        <div class="big-stat">
          <span id="app-session-time">0s</span>
          <small>In Background</small>
        </div>
        <div class="stat-row">
          <span class="label">Session Started</span>
          <span class="val" id="app-session-start">--:--:--</span>
        </div>
        <div class="stat-row">
          <span class="label">Monitor Footprint</span>
          <span class="val" id="app-session-footprint">0.0% CPU · 0.0 MB</span>
        </div>
        <div class="stat-row">
          <span class="label">Laptop Power State</span>
          <span class="val" id="app-power-state">Plugged In</span>
        </div>
      </div>

      <!-- Process Monitor -->
      <div class="glass-card">
        <div class="card-title">
          <span>Active Processes</span>
          <button class="btn-toggle" onclick="toggleSort()" id="sort-btn">Sort: CPU</button>
        </div>
        <table>
          <thead>
            <tr>
              <th>PID</th>
              <th>Process Name</th>
              <th style="text-align: right;">CPU%</th>
              <th style="text-align: right;">RAM%</th>
              <th style="text-align: right;">Time</th>
            </tr>
          </thead>
          <tbody id="proc-table"></tbody>
        </table>
      </div>
    </div>
  </div>

  <script>
    /* Theme Engine */
    const THEMES = ["slate", "cyberpunk", "matrix", "nord", "dracula", "catppuccin", "monochrome"];
    let currentThemeIndex = 0;

    function setTheme(name) {
      const idx = THEMES.indexOf(String(name).toLowerCase());
      if (idx !== -1) currentThemeIndex = idx;
      const themeName = THEMES[currentThemeIndex];
      document.body.setAttribute('data-theme', themeName);
      const btn = document.getElementById('theme-btn');
      if (btn) {
        btn.textContent = `🎨 Theme: ${themeName.charAt(0).toUpperCase() + themeName.slice(1)}`;
      }
    }

    function cycleTheme() {
      currentThemeIndex = (currentThemeIndex + 1) % THEMES.length;
      setTheme(THEMES[currentThemeIndex]);
    }

    // Initialize theme from URL query or server default
    const urlParams = new URLSearchParams(window.location.search);
    const initialTheme = urlParams.get('theme') || "{{ default_theme }}";
    setTheme(initialTheme);

    /* Snow Particle Physics Simulation */
    const canvas = document.getElementById('snow-canvas');
    const ctx = canvas.getContext('2d');
    let snowActive = true;
    let width = (canvas.width = window.innerWidth);
    let height = (canvas.height = window.innerHeight);

    window.addEventListener('resize', () => {
      width = canvas.width = window.innerWidth;
      height = canvas.height = window.innerHeight;
    });

    const FLAKE_COUNT = 90;
    const flakes = [];

    for (let i = 0; i < FLAKE_COUNT; i++) {
      flakes.push({
        x: Math.random() * width,
        y: Math.random() * height,
        r: Math.random() * 2.8 + 0.8,
        d: Math.random() * FLAKE_COUNT,
        speed: Math.random() * 0.8 + 0.5,
        opacity: Math.random() * 0.6 + 0.25,
      });
    }

    let angle = 0;
    function renderSnow() {
      if (!snowActive) {
        ctx.clearRect(0, 0, width, height);
        requestAnimationFrame(renderSnow);
        return;
      }

      ctx.clearRect(0, 0, width, height);
      angle += 0.008;

      for (let i = 0; i < FLAKE_COUNT; i++) {
        const f = flakes[i];
        f.y += f.speed;
        f.x += Math.sin(angle + f.d) * 0.6;

        if (f.y > height) {
          f.y = -5;
          f.x = Math.random() * width;
        }

        ctx.fillStyle = `rgba(255, 255, 255, ${f.opacity})`;
        ctx.beginPath();
        ctx.arc(f.x, f.y, f.r, 0, Math.PI * 2, true);
        ctx.fill();
      }

      requestAnimationFrame(renderSnow);
    }
    requestAnimationFrame(renderSnow);

    function toggleSnow() {
      snowActive = !snowActive;
      const btn = document.getElementById('snow-btn');
      if (btn) {
        btn.textContent = snowActive ? '❄ Snow: On' : '❄ Snow: Off';
      }
    }

    /* Live Metrics Polling */
    let currentSort = 'cpu';

    function toggleSort() {
      currentSort = currentSort === 'cpu' ? 'ram' : 'cpu';
      document.getElementById('sort-btn').textContent = `Sort: ${currentSort.toUpperCase()}`;
      updateMetrics();
    }

    function formatBytes(bytes) {
      if (!bytes || bytes <= 0) return '0.0 B';
      const k = 1024;
      const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
      let i = Math.floor(Math.log(bytes) / Math.log(k));
      if (i < 0) i = 0;
      if (i >= sizes.length) i = sizes.length - 1;
      return (bytes / Math.pow(k, i)).toFixed(1) + ' ' + sizes[i];
    }

    function formatSpeed(bytesPerSec) {
      return formatBytes(bytesPerSec) + '/s';
    }

    function formatUptime(seconds) {
      if (!seconds || seconds <= 0) return '0s';
      const d = Math.floor(seconds / 86400);
      const h = Math.floor((seconds % 86400) / 3600);
      const m = Math.floor((seconds % 3600) / 60);
      const s = Math.floor(seconds % 60);
      if (d > 0) return `${d}d ${h}h ${m}m`;
      if (h > 0) return `${h}h ${m}m ${s}s`;
      if (m > 0) return `${m}m ${s}s`;
      return `${s}s`;
    }

    function getColor(percent) {
      if (percent < 45) return 'var(--low)';
      if (percent < 75) return 'var(--med)';
      return 'var(--high)';
    }

    async function updateMetrics() {
      try {
        const res = await fetch(`/api/metrics?sort=${currentSort}`);
        const data = await res.json();

        // System
        document.getElementById('host').textContent = data.system.hostname;
        document.getElementById('os').textContent = data.system.os;
        document.getElementById('uptime').textContent = formatUptime(data.system.uptime);

        if (data.system.battery.has) {
          const batBox = document.getElementById('battery-box');
          batBox.style.display = 'inline';
          document.getElementById('battery').textContent = `${data.system.battery.percent.toFixed(0)}%`;
        }

        // CPU
        const cpuTotal = data.cpu.overall.toFixed(1) + '%';
        document.getElementById('cpu-total').textContent = cpuTotal;
        const cpuBar = document.getElementById('cpu-bar');
        cpuBar.style.width = cpuTotal;
        cpuBar.style.backgroundColor = getColor(data.cpu.overall);
        document.getElementById('freq').textContent = (data.cpu.freq / 1000).toFixed(2) + ' GHz';

        // Cores
        const coresContainer = document.getElementById('cores-container');
        coresContainer.innerHTML = data.cpu.cores.slice(0, 16).map((c, i) => `
          <div class="core-box">
            <span>C${i < 10 ? '0' + i : i}</span>
            <b style="color:${getColor(c)}">${c.toFixed(0)}%</b>
          </div>
        `).join('');

        // Memory
        document.getElementById('ram-val').textContent = `${formatBytes(data.memory.ram_used)} / ${formatBytes(data.memory.ram_total)}`;
        const ramBar = document.getElementById('ram-bar');
        ramBar.style.width = data.memory.ram_percent.toFixed(1) + '%';
        ramBar.style.backgroundColor = getColor(data.memory.ram_percent);

        document.getElementById('swap-val').textContent = `${formatBytes(data.memory.swap_used)} / ${formatBytes(data.memory.swap_total)}`;
        const swapBar = document.getElementById('swap-bar');
        swapBar.style.width = data.memory.swap_percent.toFixed(1) + '%';
        swapBar.style.backgroundColor = getColor(data.memory.swap_percent);

        // Disks
        const disksContainer = document.getElementById('disks-container');
        disksContainer.innerHTML = data.disks.map(d => `
          <div class="stat-row">
            <span class="label">Drive ${d.mount}</span>
            <span class="val">${formatBytes(d.used)} / ${formatBytes(d.total)}</span>
          </div>
          <div class="bar-container">
            <div class="bar-fill" style="width: ${d.percent}%; background-color: ${getColor(d.percent)};"></div>
          </div>
        `).join('');

        // Network & Disk IO
        document.getElementById('net-down').textContent = formatSpeed(data.io.download_speed);
        document.getElementById('net-down-tot').textContent = formatBytes(data.io.total_recv);
        document.getElementById('net-up').textContent = formatSpeed(data.io.upload_speed);
        document.getElementById('net-up-tot').textContent = formatBytes(data.io.total_sent);
        document.getElementById('disk-read').textContent = formatSpeed(data.io.disk_read_speed);
        document.getElementById('disk-write').textContent = formatSpeed(data.io.disk_write_speed);

        // App Background Session
        if (data.app_session) {
          document.getElementById('app-session-time').textContent = formatUptime(data.app_session.uptime_seconds);
          const startDate = new Date(data.app_session.start_time * 1000);
          document.getElementById('app-session-start').textContent = startDate.toLocaleTimeString();
          document.getElementById('app-session-footprint').textContent = `${data.app_session.cpu_percent.toFixed(1)}% CPU · ${data.app_session.memory_mb.toFixed(1)} MB`;

          let pState = data.system.battery.plugged ? "Plugged In (AC)" : "On Battery";
          if (data.system.battery.has) {
            pState += ` (${data.system.battery.percent.toFixed(0)}%)`;
          }
          document.getElementById('app-power-state').textContent = pState;
        }

        // Processes
        const procTable = document.getElementById('proc-table');
        procTable.innerHTML = data.processes.slice(0, 8).map(p => `
          <tr>
            <td style="color: var(--text-muted);">${p.pid}</td>
            <td style="font-weight: 500;">${p.name.length > 20 ? p.name.substring(0, 20) + '…' : p.name}</td>
            <td style="color: ${getColor(p.cpu)}; text-align: right;">${p.cpu.toFixed(1)}%</td>
            <td style="color: ${getColor(p.mem)}; text-align: right;">${p.mem.toFixed(1)}%</td>
            <td style="color: var(--text-muted); text-align: right;">${formatUptime(p.runtime || 0)}</td>
          </tr>
        `).join('');

      } catch (err) {
        console.error('Failed to update stats:', err);
      }
    }

    updateMetrics();
    setInterval(updateMetrics, 1000);
  </script>
</body>
</html>
"""

@app.route("/")
def index():
    default_theme = app.config.get("DEFAULT_THEME", "slate")
    return render_template_string(HTML_TEMPLATE, default_theme=default_theme)


@app.route("/api/metrics")
def api_metrics():
    from flask import request
    sort_by = request.args.get("sort", "cpu")
    s = collector.collect(sort_by=sort_by, limit_processes=10)

    return jsonify({
        "cpu": {
            "overall": s.cpu_percent,
            "cores": s.cpu_cores,
            "freq": s.cpu_freq_current,
            "history": s.cpu_history,
        },
        "memory": {
            "ram_total": s.ram_total,
            "ram_used": s.ram_used,
            "ram_percent": s.ram_percent,
            "swap_total": s.swap_total,
            "swap_used": s.swap_used,
            "swap_percent": s.swap_percent,
        },
        "disks": [
            {
                "mount": d.mountpoint.replace("\\", "/"),
                "total": d.total,
                "used": d.used,
                "percent": d.percent,
            }
            for d in s.disks
        ],
        "io": {
            "download_speed": s.net_download_speed,
            "upload_speed": s.net_upload_speed,
            "total_recv": s.net_bytes_recv,
            "total_sent": s.net_bytes_sent,
            "disk_read_speed": s.disk_read_speed,
            "disk_write_speed": s.disk_write_speed,
        },
        "processes": [
            {
                "pid": p.pid,
                "name": p.name,
                "cpu": p.cpu_percent,
                "mem": p.memory_percent,
                "runtime": p.runtime_seconds,
            }
            for p in s.processes
        ],
        "app_session": {
            "uptime_seconds": s.app_uptime_seconds,
            "start_time": s.app_start_time,
            "cpu_percent": s.app_cpu_percent,
            "memory_mb": s.app_memory_mb,
        },
        "system": {
            "hostname": s.hostname,
            "os": s.os_name,
            "arch": s.architecture,
            "uptime": s.uptime_seconds,
            "battery": {
                "has": s.has_battery,
                "percent": s.battery_percent,
                "plugged": s.battery_plugged,
            },
        },
    })


@app.route("/background.jpg")
def serve_bg():
    for name in ["background.jpg", "background.png", "background.webp", "snow.jpg"]:
        if os.path.exists(name):
            from flask import send_file
            return send_file(os.path.abspath(name))
    from flask import redirect
    return redirect("https://images.unsplash.com/photo-1517299321909-20b34934236a?auto=format&fit=crop&w=2160&q=85")


def start_web_server(port: int = 5000, host: str = "127.0.0.1", theme: str = "slate"):
    import logging
    import socket
    import webbrowser

    app.config["DEFAULT_THEME"] = theme.lower()

    # Silence noisy HTTP access logs
    log = logging.getLogger("werkzeug")
    log.setLevel(logging.ERROR)

    # Check port availability and auto-increment if taken
    for p in range(port, port + 10):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind((host, p))
            port = p
            break
        except OSError:
            continue

    url = f"http://{host}:{port}"
    print(f"❄ Starting NeonTop Snowfield Web Dashboard at {url}")
    print(f"  Theme: {theme.upper()} | Press Ctrl+C in terminal to stop.")
    try:
        webbrowser.open(url)
    except Exception:
        pass
    app.run(host=host, port=port, debug=False)
