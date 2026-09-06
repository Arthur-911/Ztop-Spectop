# 🚀 Windows PC Performance Optimization & Tuning Guide

This guide explains how to interpret the telemetry from **Ztop Spectop** and which settings or adjustments you can make on your Windows computer to boost performance, lower latency, reduce RAM usage, and prevent CPU/disk bottlenecks.

---

## 🧭 Quick Diagnostic Map (Ztop Spectop ➔ System Fix)

| Ztop Spectop Metric | Warning Sign | What It Means | Where to Adjust in Windows |
| :--- | :--- | :--- | :--- |
| **RAM Usage** | > 80% with few apps open | Bloatware, startup programs, or memory leaks | `Task Manager` ➔ **Startup apps**, disable unused startup tasks |
| **CPU Utilization** | High % while idle | Background telemetry, updates, or indexing | `Settings` ➔ **Privacy & security** ➔ Background apps & indexing |
| **CPU Frequency** | Stays lower than base clock | CPU is thermal throttling or on Power Saver | `Power Options` (`powercfg.cpl`) ➔ **High Performance** / Clean dust / Elevate laptop |
| **Disk % / I/O** | Constant high read/write | Heavy paging file thrashing, SysMain, or Antivirus scan | `cleanmgr` (Disk Cleanup), trim SSD, or adjust virtual memory |
| **Swap Usage** | High swap % | Physical RAM is exhausted; Windows is paging to disk | Upgrade RAM or close high-memory background browser tabs |

---

## 🛠️ Step-by-Step Optimizations You Can Apply

### 1. 🛑 Disable Unnecessary Startup Programs
*Startup apps silently consume RAM and CPU cycles from the moment you turn on your PC.*
- **Shortcut:** Press `Ctrl + Shift + Esc` to open **Task Manager**, then click the **Startup apps** tab.
- **Action:** Look for high-impact apps you don't need immediately (e.g., Spotify, Discord, Steam, OneDrive, browser updaters, launcher helpers) and set them to **Disabled**.
- **Result:** Faster boot time and 500 MB to 2+ GB of free RAM saved.

---

### 2. ⚡ Select the Optimal Windows Power Plan
*Windows often defaults to "Balanced" or power-saver modes that throttle CPU frequency states even when plugged in.*
- **Shortcut:** Press `Win + R`, type `powercfg.cpl`, and hit Enter.
- **Action:**
  - On desktops or plugged-in laptops: Choose **High Performance** or **Ultimate Performance**.
  - If on laptop battery: Switch back to **Balanced** to preserve battery longevity.
- **Result:** Keeps CPU clocks responsive and eliminates micro-stutters during heavy tasks.

---

### 3. 🧹 Clean Up Temporary Files & Free Disk Space
*Solid State Drives (SSDs) slow down dramatically when they exceed 80-85% capacity.*
- **Shortcut:** Press `Win + R`, type `cleanmgr`, and hit Enter.
  - Select drive `C:`, click **Clean up system files**, and check:
    - *Temporary files*
    - *Previous Windows installations (Windows.old)*
    - *DirectX Shader Cache*
    - *Delivery Optimization Files*
- **Settings Storage Sense:** Go to `Settings` ➔ **System** ➔ **Storage** and turn on **Storage Sense** to automatically purge temp files.

---

### 4. 💨 Optimize Windows Visual Effects & Animations
*Windows animations, transparency effects, and shadows consume GPU/RAM resources, especially on integrated graphics.*
- **Shortcut:** Press `Win + R`, type `sysdm.cpl`, and hit Enter.
- Go to the **Advanced** tab ➔ Under *Performance*, click **Settings...**.
- Choose **Adjust for best performance**, or select **Custom** and keep only:
  - *Show thumbnails instead of icons*
  - *Smooth edges of screen fonts*
- **Result:** Instantaneous window opening and reduced DWM (Desktop Window Manager) overhead.

---

### 5. 🔕 Disable Windows Telemetry & Background Activity
- **Background Apps:** Go to `Settings` ➔ **Apps** ➔ **Installed apps**, select apps you rarely use, click the three dots ➔ **Advanced options**, and set *Background apps permissions* to **Never**.
- **Transparency:** Go to `Settings` ➔ **Accessibility** ➔ **Visual effects** ➔ Turn off **Transparency effects**.
- **Game Mode:** Go to `Settings` ➔ **Gaming** ➔ **Game Mode** ➔ Ensure **Game Mode** is toggled **ON** (this prioritizes CPU/GPU threads for foreground tasks).

---

### 6. 🧠 Configure Virtual Memory (Paging File)
*If Ztop Spectop shows excessive swap usage or your system runs low on memory:*
- **Shortcut:** Press `Win + R`, type `sysdm.cpl`, go to **Advanced** ➔ **Performance Settings** ➔ **Advanced** tab ➔ Under *Virtual memory*, click **Change...**.
- Ensure the paging file is placed on your **fastest NVMe/SSD** (never on a mechanical HDD).
- It is generally recommended to let Windows **Automatically manage paging file size for all drives**, unless you have limited disk space, in which case set a custom initial size (1.5x RAM) and maximum size (3x RAM).

---

### 7. 🌡️ Hardware & Thermal Maintenance
- **Laptop Airflow:** If Ztop Spectop shows high CPU usage accompanied by thermal throttling (CPU frequency drops under load), ensure laptop vents are clean and elevated 1-2 cm off flat surfaces.
- **XMP / DOCP in BIOS:** If you're on a desktop PC, enter BIOS and verify that **XMP** (Intel) or **DOCP / EXPO** (AMD) is enabled so your RAM runs at its advertised MHz speed rather than default JEDEC speeds (e.g. 2133 MHz).

---

## 💡 Using Ztop Spectop to Verify Your Improvements
1. **Before tweaking:** Run `python main.py` or `python main.py --web` and note your idle RAM %, CPU load %, and active background processes.
2. **Apply optimizations:** Disable startup programs and reboot your machine.
3. **After tweaking:** Run `python main.py` again. Press `s` to sort processes by RAM% or CPU% to verify that bloat processes are gone.
