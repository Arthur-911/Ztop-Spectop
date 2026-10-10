# Ztop Spectop

> A clean, minimalist terminal system monitor with custom background palettes, live sparklines, per-core telemetry, and real-time process monitoring.

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-blueviolet)](https://github.com/)
[![Built with Rich](https://img.shields.io/badge/UI-Rich-blue)](https://github.com/Textualize/rich)

---

## ✨ Features

- 🖤 **Minimalist & Card Backgrounds**: Understated slate and pure black backgrounds (`#0a0c10`, `#000000`, `#1e222a`) with subtle card borders. No loud clashing neon colors or noisy emojis.
- 🧠 **CPU Telemetry**: Overall CPU load, clock frequency, per-core utilization meters, and smooth historical trend sparklines (` ▂▃▄▅▆▇█`).
- 💾 **Memory & Storage**: Physical RAM, Swap/Pagefile usage, and multi-drive partition tracking (e.g. `C:`).
- 🌐 **Network & Disk I/O**: Real-time download/upload transfer rates, total throughput, and live disk read/write metrics.
- ⚙️ **Process Explorer**: Clean, distraction-free active process list with individual process runtime tracking and one-key toggle to sort by **CPU%** or **RAM%**.
- ⏱️ **Background Session & App Runtime**: Dedicated panel tracking how long Ztop Spectop has been running, monitor memory/CPU footprint, and battery power status.
- 🔋 **Battery & Uptime**: Subtle battery indicator and system uptime counters with accurate desktop AC power fallback.
- ⌨️ **Interactive Controls**: Non-blocking keyboard hotkeys (`q` to quit, `s` to toggle sort, `t` to cycle themes, `space` to pause).
- 📸 **Snapshot Mode**: Single-shot output mode (`--snapshot`) for fast terminal logs or CLI piping.
- 🌐 **Snowfield Web Dashboard**: High-performance browser monitor with customizable themes and particle animation (`--web`).

---

## 📸 Preview

```text
┌────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│  ztop spectop ● · ArthursLaptop (Windows 11 25H2 x64) · up: 1d 0h 47m · bat: 100% · theme: Minimal Slate ·  │
└────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
┌─ cpu ───────────────────────────────────────────────┐┌─ memory & storage ──────────────────────────────────┐
│ util:  14.6%  clk: 3.30 GHz  trend:  ▂              ││ ram          ━━━━━━───   74% · 5.8/7.8 GB           │
│ c00 ━━━━━─ 57.1%     c04 ──────  0.0%               ││ swap         ━━━──────   39% · 3.7/9.5 GB           │
│ c01 ━───── 16.7%     c05 ━───── 14.3%               ││                                                     │
│ c02 ──────  0.0%     c06 ──────  0.0%               ││ disk C:      ━━━━─────   45% · 212/476 GB           │
│ c03 ━───── 16.7%     c07 ──────  0.0%               ││                                                     │
└─────────────────────────────────────────────────────┘└─────────────────────────────────────────────────────┘
┌─ network & disk io ─────────────────────────────────┐┌─ processes (sort: cpu) ─────────────────────────────┐
│ net down       ↓ 0.0 B/s (630.8 MB)                 ││    pid   process                 cpu%   mem%    time│
│ net up         ↑ 0.0 B/s (109.3 MB)                 ││  ───────────────────────────────────────────────────│
│ disk r/w       r: 0.0 B/s · w: 0.0 B/s              ││      0   System Idle Process     0.0%   0.0%      0s│
│                                                     ││      4   System                  0.0%   0.0%   1d 0h│
│                                                     ││    140   Unknown                 0.0%   0.5%  12m 4s│
│                                                     ││    184   Registry                0.0%   0.1%  14m 2s│
│                                                     ││    604   csrss.exe               0.0%   0.0%   1d 0h│
└─────────────────────────────────────────────────────┘└─────────────────────────────────────────────────────┘
┌────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│  [live]  ·  q quit  ·  t theme: Minimal Slate  ·  s sort: cpu  ·  space pause                              │
└────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quickstart

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Launch

#### One-Click Launch (Windows):
Double-click **`run.bat`** (or **`ztop_spectop.bat`**).

#### Terminal Monitor:
```bash
python main.py
```

#### Snowfield Web Dashboard (with live snow particle physics):
```bash
python main.py --web
```
*(Automatically opens in your browser at `http://127.0.0.1:5000`)*

---

## 🕹️ Keyboard Controls

| Key | Action |
| :---: | :--- |
| **`T`** | **Cycle Color Theme live** (Slate ➔ Cyberpunk ➔ Matrix ➔ Nord ➔ Dracula ➔ Catppuccin ➔ Monochrome) |
| **`S`** | Toggle process sort mode (**CPU%** ↔ **RAM%**) |
| **`Space`** | Pause / Resume live data refreshing |
| **`Q`** | Quit application |

---

## 🎨 Built-In Minimalist Themes

| Theme | Background & Aesthetic |
| :--- | :--- |
| **`slate`** *(default)* | Deep charcoal-slate background (`#0a0c10`), soft slate card surfaces, and subtle sky-blue accents. |
| **`cyberpunk`** | High-contrast dark cyberpunk palette with neon cyan and magenta accents. |
| **`matrix`** | Phosphor terminal green on deep black background. |
| **`nord`** | Polar night background (`#1e222a`), Arctic blue frost accents, and aurora highlights. |
| **`dracula`** | Deep dark background (`#191a21`) with muted purple and green accents. |
| **`catppuccin`** | Deep crust background (`#11111b`) with cozy muted pastels. |
| **`monochrome`** | True OLED black background (`#000000`), dark graphite card surfaces, and crisp grayscale typography. |

---

## 🛠️ CLI Options

```text
usage: main.py [-h] [-i INTERVAL] [-s {cpu,ram}] [-t {slate,cyberpunk,matrix,nord,dracula,catppuccin,monochrome}] [--web] [-p PORT] [--snapshot] [-v]

Ztop Spectop - Modern Themed Terminal System Monitor

options:
  -h, --help            Show this help message and exit
  -i, --interval        Refresh interval in seconds (default: 1.0)
  -s, --sort            Initial process sort order ('cpu' or 'ram', default: cpu)
  -t, --theme           Theme palette (default: slate)
  --web                 Launch the Snowfield Web Dashboard in your browser
  -p, --port            Port for the web dashboard server (default: 5000)
  --snapshot            Print a single formatted snapshot to standard output and exit
  -v, --version         Show program's version number and exit
```

---

## 📂 Project Structure

```text
ztop_spectop/
├── src/
│   ├── __init__.py      # Package metadata
│   ├── app.py           # Interactive loop & non-blocking key event handler
│   ├── dashboard.py     # Minimalist layout generation, panels & tables
│   ├── metrics.py       # psutil hardware, network, disk & process collector
│   ├── themes.py        # Dedicated background colors & minimalist palettes
│   ├── visualizer.py    # Sparkline curves, progress bars & formatters
│   └── web_server.py    # Snowfield web dashboard & REST telemetry API
├── main.py              # CLI argument parser & application entry point
├── run.bat              # One-click Windows launcher (double-click to run)
├── requirements.txt     # Dependencies (psutil, rich, flask)
├── LICENSE              # MIT License
├── OPTIMIZATION_TIPS.md # Windows performance & system tuning guide
└── README.md            # Documentation
```

---

## 📜 License

Distributed under the **MIT License**. See [LICENSE](LICENSE) for details.
