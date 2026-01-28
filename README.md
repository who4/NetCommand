# NetCommand

<div align="center">
  <img src="https://via.placeholder.com/800x400.png?text=NetCommand+Dashboard" alt="NetCommand Dashboard" width="100%" />

  **A Modern Network Command Center for Windows**
  
  [Features](#features) • [Installation](#installation) • [Usage](#usage)
</div>

---

## Overview

NetCommand is a robust desktop utility designed to give you complete control over your Windows network settings. Built with Python and CustomTkinter, it features a sleek "Dark Mode" UI (Gray/Purple theme) and powerful backend tools to manage DNS, Latency, and Connection Priority.

**Current Version:** v4.0 (Bento Grid Edition)

## Features

### 🔌 Connection Priority
- **One-Click Priority:** Instantly route all internet traffic through your preferred adapter (Ethernet vs. Wi-Fi).
- **Metric Management:** Automatically adjusts Windows Interface Metrics (Metric 1 for High Priority).

### 📊 Live Monitor
- **Real-Time Stats:** Updates every 15 seconds.
- **Data Points:**
    - Public IP Address
    - Location (City, Country)
    - ISP Name
    - Latency (Ping to Google DNS)
    - Packet Loss %

### 🌐 DNS Manager
- **Custom DNS:** Set your own Primary/Secondary nameservers.
- **Presets:** Quickly switch to Google DNS (8.8.8.8) or Cloudflare (1.1.1.1).
- **Auto/DHCP:** Revert changes to default with a single click.

### 🛠 Power Tools
- **Flush DNS:** Clear resolver cache to fix loading issues.
- **IP Release/Renew:** Refresh your local IP configuration.
- **Auto-Elevation:** The app automatically handles UAC requests to run with necessary Administrator privileges.

## Installation

### Prerequisites
- Windows 10 or 11
- Python 3.8+

### Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/netcommand.git
   cd netcommand
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   python main.py
   ```
   *Note: Accept the User Account Control (UAC) prompt to allow the app to manage network settings.*

## Requirements
- `customtkinter`
- `requests`
- `packaging`

## Legal / Disclaimer
This tool uses system commands (`netsh`, `ipconfig`). Use responsibly. The developer is not responsible for any connectivity issues caused by improper configuration.

---
*Built with ❤️ in Python*
