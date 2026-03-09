## ArchSoftwareBrightness

This is a simple script to change the brightness of your computer, with hardware and software brightness control combined into one.
Very useful if your screen isn't dark enough.  

## Current support
- Arch Linux
- KDE Plasma
- X11 environment

## Install dependencies
sudo pacman -S python-pyqt6 brightnessctl xorg-xrandr

## Installation & Autostart
MAKE SURE THE SCREEN NAME IS SET CORRECTLY IN DISPLAY_NAME !

### 1. File Placement
Open your terminal, create the directory if it doesn't exist, move the script, and make it executable:
```bash
mkdir -p ~/.local/bin
mv dual_brightness.py ~/.local/bin/
chmod +x ~/.local/bin/dual_brightness.py
```

run it - nohup python ~/.local/bin/dual_brightness.py &

## Keyboard Integration (Overriding KDE Native Brightness)
If you try to map your keyboard's hardware brightness keys directly without disabling KDE's native handling, you will create a fatal race condition. KDE's PowerDevil will fight this script for control, desyncing the slider and breaking the software brightness layer completely.
To make this bulletproof, this app uses an Inter-Process Communication (IPC) socket. The main script runs as a background daemon. When you press a brightness key, it fires a temporary instance of the script that sends a signal (`--up` or `--down`) to the daemon and immediately dies, updating the central slider lag-free.

### Setup Instructions:
1. **Kill Native KDE Shortcuts:**
    - Open KDE System Settings -> Shortcuts.
    - Search for "Brightness" (usually under Power Management or Hardware).
    - Unbind the default actions for `Brightness Up` and `Brightness Down`.
2. **Create Custom IPC Shortcuts:**
    - In KDE Shortcuts, add two new Custom Commands.
    - **Brightness Up:**
        - Command: `python ~/.local/bin/dual_brightness.py --up`
        - Trigger: Press your physical Brightness Up key.
    - **Brightness Down:**
        - Command: `python ~/.local/bin/dual_brightness.py --down`
        - Trigger: Press your physical Brightness Down key.
**Note:** This architectural bypass will permanently disable the default KDE on-screen display (OSD) popup for brightness. This tray app becomes the absolute, sole source of truth for your screen's illumination state.