<img width="1038" height="662" alt="logo" src="https://github.com/user-attachments/assets/81358575-d555-49f4-ba57-38a6149b7db5" />

# DARK-MARIJUANA (V1)

DARK-MARIJUANA is a command-line tool installer and manager designed to organize, clone, and execute various security, network analysis, OSINT, and research utilities from a centralized interface.



## Features

- **Categorized Management:** Seamlessly browse tools by category (OSINT, Network, Web Hacking, Social-Media, Dark-Web).
- **Automated Directory Handling:** Clones target repositories directly to `/home/kali/<tool_name>`.
- **Auto-Execution:** Detects and launches executable Python (`.py`) and Shell (`.sh`) entry points upon selection.
- **Minimal Dependencies:** Operates out-of-the-box using Python standard libraries (`os`, `subprocess`).

---

## Prerequisites

- **OS:** Linux (Designed for Kali Linux environment)
- **Python:** Python 3.6+
- **Git:** Installed and configured in system PATH

---

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/DarkRagheb/DARK-MARIJUANA.git
   cd DARK-MARIJUANA
   ```

2. **(Optional) Install enhanced dependencies:**
   While the core script runs using standard Python libraries, you can install optional UI and Git management packages:
   ```bash
   pip install -r requirements.txt
   ```

---

## Usage
#Launch via excutable code:
ذذذذذذذ
```bash
chmod +x run.sh
```
##Then

```bash
./run.sh
```
#OR

##Launch the tool using Python 3:
```bash
python3 Main.py
```
### Navigation

1. **Select Category:** Enter the corresponding menu number to choose a tool category.
2. **Select Tool:** Choose the desired tool from the list to clone and launch.
3. **Return / Exit:** Enter `0` to return to the previous menu or exit the application.

---

## Tool Categories Included

- **OSINT Tools:** theHarvester, Recon-ng, Amass, Cr3dOv3r, etc.
- **Network Tools:** Nmap, Netcat, Wireshark, Aircrack-ng, Sublist3r, etc.
- **Web Hacking Tools:** Nikto, SQLMap, XSStrike, NucleiScanner, Red-Hawk, etc.
- **Social-Media Phishing Tools:** ZPhisher, ADV-Phishing, Instaloader, etc.
- **Dark-Web Tools:** Tor, TorBot, OnionShare, Onion-Peeler, etc.

---

## Disclaimer

This project is developed for educational, operational security, and authorized research purposes only. Users are responsible for complying with all applicable local, state, and federal laws regarding network testing and security assessment tools.
