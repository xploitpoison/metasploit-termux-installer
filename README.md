# Xploit Poison Metasploit Installer v2.0
A colorful, powerful Python script to install Metasploit on Termux with a hacking-themed interface.

## Screenshot
![Metasploit Installer Screenshot](1.jpg)

![Metasploit Installer Screenshot](2.jpg)

## Features
- Vibrant hacker theme with green, red, cyan, and magenta colors.
- Real-time download and installation progress with percentages.
- System health checks for CPU, memory, and storage.
- Auto-retry for failed downloads.
- Verbose and silent modes: `--verbose` or `--silent`.
- Error logging and rollback on failure.
- 

## Requirements

```bash
pkg install wget curl git python -y
pip install requests tqdm psutil'''

## Usage
```bash
wget https://raw.githubusercontent.com/xploitpoison/metasploit-termux-installer/main/metasploit_installer_v2.0.py
python metasploit_installer_v2.0.py
# Verbose mode:
python metasploit_installer_v2.0.py --verbose
# Silent mode:
python metasploit_installer_v2.0.py --silent'''
