#!/usr/bin/env python3
import os
import subprocess
import sys
import time
import requests
import shutil
from tqdm import tqdm
import argparse
import psutil  # For system health checks

# ANSI color codes for vibrant hacking theme
GREEN = "\033[92m"
RED = "\033[91m"
CYAN = "\033[96m"
MAGENTA = "\033[95m"
RESET = "\033[0m"
BOLD = "\033[1m"

def print_logo():
    """Display vibrant Xploit Poison ASCII logo with animation effect."""
    logo = f"""{MAGENTA}{BOLD}
    ╔════════════════════════════════════════════╗
    ║                                            ║
    ║   Xploit Poison Metasploit Installer v2.0   ║
    ║                                            ║
    ║   Created by: Xploit Poison                ║
    ║   Telegram: t.me/xploitpoison              ║
    ║   YouTube: youtube.com/@xploitpoison       ║
    ║                                            ║
    ╚════════════════════════════════════════════╝
    {RESET}"""
    for line in logo.split("\n"):
        print(line)
        time.sleep(0.1)  # Subtle animation effect
    print()

def system_health_check():
    """Check system resources for Metasploit installation."""
    print(f"{CYAN}[*] Checking system health...{RESET}")
    # Check storage (~1GB needed)
    total, used, free = shutil.disk_usage("/data/data/com.termux/files/home")
    free_mb = free // (2**20)
    if free_mb < 1000:
        print(f"{RED}[-] Error: Need at least 1000MB free space. Only {free_mb}MB available.{RESET}")
        sys.exit(1)
    print(f"{GREEN}[+] {free_mb}MB free space available.{RESET}")
    
    # Check CPU
    cpu_count = psutil.cpu_count()
    print(f"{GREEN}[+] CPU cores: {cpu_count}{RESET}")
    
    # Check memory
    mem = psutil.virtual_memory()
    free_mem_mb = mem.available // (2**20)
    if free_mem_mb < 512:
        print(f"{RED}[-] Warning: Low memory ({free_mem_mb}MB available). Installation may be slow.{RESET}")
    else:
        print(f"{GREEN}[+] {free_mem_mb}MB memory available.{RESET}")

def run_command(command, verbose=False, capture_output=False):
    """Execute a shell command with error handling."""
    try:
        if capture_output:
            process = subprocess.Popen(command, shell=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return process
        result = subprocess.run(command, shell=True, check=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if verbose:
            print(f"{CYAN}Output: {result.stdout}{RESET}")
        return result.stdout
    except subprocess.CalledProcessError as e:
        with open('metasploit_install.log', 'a') as f:
            f.write(f"Error in {command}: {e.stderr}\n")
        print(f"{RED}[-] Error: {command} failed. Check metasploit_install.log.{RESET}")
        raise

def check_dependencies():
    """Check and install required Termux packages and Python libraries."""
    print(f"{CYAN}[*] Checking dependencies...{RESET}")
    packages = ['wget', 'curl', 'git', 'python', 'pip']
    for pkg in packages:
        if shutil.which(pkg) is None:
            print(f"{CYAN}[-] Installing {pkg}...{RESET}")
            run_command(f"pkg install {pkg} -y")
        else:
            print(f"{GREEN}[+] {pkg} installed.{RESET}")
    
    try:
        import requests
        import tqdm
        import psutil
        print(f"{GREEN}[+] Python libraries (requests, tqdm, psutil) installed.{RESET}")
    except ImportError:
        print(f"{CYAN}[-] Installing Python libraries...{RESET}")
        run_command("pip install requests tqdm psutil")

def download_with_progress(url, filename, retries=3):
    """Download file with real-time progress and retry logic."""
    print(f"{CYAN}[*] Downloading {filename}...{RESET}")
    for attempt in range(retries):
        try:
            response = requests.get(url, stream=True)
            total_size = int(response.headers.get('content-length', 0))
            if total_size == 0:
                print(f"{RED}[-] Cannot determine file size. Downloading without progress.{RESET}")
                with open(filename, 'wb') as file:
                    file.write(response.content)
                print(f"{GREEN}[+] Downloaded {filename}{RESET}")
                return
            block_size = 1024
            progress_bar = tqdm(total=total_size, unit='iB', unit_scale=True, desc=f"{CYAN}Download{RESET}", bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]")
            
            with open(filename, 'wb') as file:
                for data in response.iter_content(block_size):
                    progress_bar.update(len(data))
                    file.write(data)
            progress_bar.close()
            print(f"{GREEN}[+] Downloaded {filename}{RESET}")
            return
        except requests.RequestException as e:
            print(f"{RED}[-] Attempt {attempt + 1} failed: {e}{RESET}")
            if attempt + 1 == retries:
                print(f"{RED}[-] Download failed after {retries} attempts.{RESET}")
                sys.exit(1)
            time.sleep(2)

def install_metasploit(silent=False):
    """Run Metasploit installation with milestone-based progress."""
    print(f"{CYAN}[*] Installing Metasploit...{RESET}")
    command = "./metasploit.sh"
    process = run_command(command, capture_output=True)
    
    milestones = ["Downloading", "Installing ruby", "Extracting", "Configuring", "Done"]
    progress_per_milestone = 100 // len(milestones)
    current_progress = 0
    
    while process.poll() is None:
        line = process.stdout.readline().strip()
        if line and not silent:
            for i, milestone in enumerate(milestones):
                if milestone.lower() in line.lower():
                    current_progress = (i + 1) * progress_per_milestone
                    print(f"\r{CYAN}[{('=' * (current_progress // 5)) + (' ' * (20 - current_progress // 5))}] {current_progress}% ({milestone}){RESET}", end="", flush=True)
        time.sleep(0.1)
    
    process.communicate()
    if process.returncode != 0:
        print(f"\n{RED}[-] Installation failed. Check metasploit_install.log.{RESET}")
        with open('metasploit_install.log', 'a') as f:
            f.write(f"Error in {command}: {process.stderr.read()}\n")
        raise subprocess.CalledProcessError(process.returncode, command)
    
    print(f"\r{CYAN}[{('=' * 20)}] 100% (Done){' ' * 30}{RESET}")
    print(f"{GREEN}[+] Installing Metasploit completed!{RESET}")

def simulated_progress(task_name, duration=5, silent=False):
    """Simulate progress bar for tasks without native progress."""
    if silent:
        run_command(task_name)
        return
    print(f"{CYAN}[*] {task_name}...{RESET}")
    for i in range(101):
        print(f"\r{CYAN}[{('=' * (i // 5)) + (' ' * (20 - i // 5))}] {i}%{RESET}", end="", flush=True)
        time.sleep(duration / 100)
    print(f"\r{GREEN}[+] {task_name} completed!{' ' * 30}{RESET}")

def rollback():
    """Clean up partial installation files."""
    print(f"{CYAN}[*] Rolling back installation...{RESET}")
    temp_files = ["metasploit.sh", "/data/data/com.termux/files/usr/opt/metasploit-framework"]
    for file in temp_files:
        if os.path.exists(file):
            if os.path.isdir(file):
                shutil.rmtree(file, ignore_errors=True)
            else:
                os.remove(file)
            print(f"{GREEN}[+] Removed {file}{RESET}")

def confirm_install():
    """Prompt user to confirm ethical use."""
    print(f"{CYAN}This script installs Metasploit for ethical hacking. Use only on systems you own or have permission to test.{RESET}")
    response = input(f"{CYAN}[?] Proceed? (y/n): {RESET}").lower()
    if response != 'y':
        print(f"{RED}[-] Installation cancelled.{RESET}")
        sys.exit(0)

def main():
    parser = argparse.ArgumentParser(description="Xploit Poison Metasploit Installer")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    parser.add_argument("--silent", action="store_true", help="Minimal output, no progress bars")
    args = parser.parse_args()
    
    print_logo()
    confirm_install()
    system_health_check()
    check_dependencies()
    
    # Update Termux
    simulated_progress("Updating Termux packages", 5, args.silent)
    run_command("pkg update -y && pkg upgrade -y", args.verbose)
    
    # Download Metasploit installer
    metasploit_url = "https://raw.githubusercontent.com/gushmazuko/metasploit_in_termux/master/metasploit.sh"
    download_with_progress(metasploit_url, "metasploit.sh")
    
    # Set permissions
    simulated_progress("Setting permissions", 1, args.silent)
    run_command("chmod +x metasploit.sh", args.verbose)
    
    # Install Metasploit
    install_metasploit(args.silent)
    
    # Verify installation
    simulated_progress("Verifying installation", 3, args.silent)
    run_command("msfconsole -v", args.verbose)
    
    print(f"{GREEN}[+] Metasploit installed successfully! Run 'msfconsole' to start.{RESET}")
    print(f"{MAGENTA}Join t.me/xploitpoison | Star github.com/<your-username>/metasploit-termux-installer{RESET}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{RED}[-] Installation cancelled.{RESET}")
        rollback()
        sys.exit(1)
    except Exception as e:
        print(f"\n{RED}[-] Error: {e}. Check metasploit_install.log.{RESET}")
        rollback()
        sys.exit(1)
