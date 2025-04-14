# src/helloworld_click_client/sys_detect.py -> sys_detect.py
import platform
import os
import sys
import json
import shutil

# Direct import for cmd_run
from cmd_run import run_command

def _safe_run_command(command_str):
    """Wrapper for run_command returning only stdout if successful."""
    stdout, stderr, returncode = run_command(command_str)
    if returncode == 0:
        return stdout
    else:
        # Optionally log stderr here if needed for debugging detection failures
        # print(f"Warning: Command '{command_str}' failed: {stderr}", file=sys.stderr)
        return None

def _check_command_exists(command_name):
    """Checks if a command exists using shutil.which (cross-platform)."""
    return shutil.which(command_name) is not None

def _get_tool_version(command_name, version_flag="--version"):
    """Attempts to get the version of a command-line tool."""
    if not _check_command_exists(command_name):
        return None
    # Common version flags: --version, -V, version
    common_flags = [version_flag, "-V", "version", "-v"] # Add more if needed
    version_str = None
    for flag in common_flags:
        stdout, stderr, returncode = run_command(f"{command_name} {flag}")
        # Check stdout first, then stderr (some tools print version to stderr)
        output_to_check = stdout if stdout else stderr
        if returncode == 0 and output_to_check:
            # Basic version extraction (might need refinement per tool)
            # Look for patterns like 'v1.2.3', '1.2.3', 'version 1.2.3'
            lines = output_to_check.splitlines()
            if lines:
                 version_str = lines[0].strip() # Often version is on the first line
                 break # Found a version

    return version_str

def get_system_info():
    """Gathers various system details."""
    info = {}

    # Basic OS Info (platform module)
    info['os_info'] = {
        "system": platform.system(),
        "node_name": platform.node(),
        "release": platform.release(),
        "version": platform.version(),
        "machine": platform.machine(),
        "processor": platform.processor(),
    }

    # Linux Distro Info (requires lsb_release command or /etc/os-release)
    distro_info = {}
    if platform.system() == "Linux":
        # Try lsb_release first
        lsb_output = _safe_run_command("lsb_release -a")
        if lsb_output:
            for line in lsb_output.splitlines():
                if ":" in line:
                    key, val = line.split(":", 1)
                    distro_info[key.strip().lower().replace(" ", "_")] = val.strip()
        else:
            # Fallback to /etc/os-release (more modern)
            try:
                with open("/etc/os-release", "r") as f:
                    for line in f:
                        line = line.strip()
                        if "=" in line:
                             key, val = line.split("=", 1)
                             # Remove quotes from value if present
                             val = val.strip('"').strip("'")
                             distro_info[key.lower()] = val
            except FileNotFoundError:
                distro_info['error'] = "Could not determine Linux distribution."
    info['distro'] = distro_info

    # Architecture (redundant with machine, but common)
    info['architecture'] = platform.machine()

    # Memory (Linux specific example, needs cross-platform implementation)
    # This is complex to do reliably cross-platform without external libraries like psutil
    # Placeholder:
    info['memory_gb'] = "N/A (Requires platform-specific implementation or libraries)"
    if platform.system() == "Linux":
         mem_output = _safe_run_command("free -g") # Requires 'free' command
         if mem_output:
              lines = mem_output.splitlines()
              if len(lines) > 1 and lines[1].startswith("Mem:"):
                   parts = lines[1].split()
                   if len(parts) > 1:
                        info['memory_gb'] = parts[1] # Total GB approx

    # CPU Info (Placeholder - complex without libraries)
    info['cpu_info'] = {"model": platform.processor(), "cores": os.cpu_count()}

    # Terminal Info (Environment variables - might not be reliable)
    info['terminal'] = {
        "type": os.environ.get('TERM'),
        "program": os.environ.get('TERM_PROGRAM'),
        # Encoding is tricky, sys.stdout.encoding can vary
        "encoding": getattr(sys.stdout, 'encoding', None),
    }

    # Shell Info
    info['shell'] = os.environ.get('SHELL') # Common on Unix-like
    if not info['shell'] and platform.system() == 'Windows':
         info['shell'] = os.environ.get('ComSpec') # Command Prompt/PowerShell path

    # Tool Availability & Versions
    info['kubectl'] = {
        "available": _check_command_exists("kubectl"),
        "version": _get_tool_version("kubectl", "version --client -o json") # Example specific flags
    }
    info['helm'] = {
        "available": _check_command_exists("helm"),
        "version": _get_tool_version("helm", "version --short")
    }
    info['curl'] = {
        "available": _check_command_exists("curl"),
        "version": _get_tool_version("curl", "--version") # Curl prints version info differently
    }


    # Running Services (Very platform-specific - placeholder)
    # Requires parsing 'ps', 'tasklist', 'systemctl', 'launchctl' etc. Highly complex.
    info['running_services'] = ["N/A (Requires platform-specific implementation)"]

    # Common Log Locations (Examples - adjust per need)
    log_locations = []
    system = platform.system()
    if system == "Linux":
        common_logs = ["/var/log/syslog", "/var/log/messages", "/var/log/auth.log", "/var/log/kern.log"]
        log_locations.extend([log for log in common_logs if os.path.exists(log)])
    elif system == "Darwin": # macOS
        common_logs = ["/var/log/system.log"] # Older macOS, unified logging is complex
        log_locations.extend([log for log in common_logs if os.path.exists(log)])
    elif system == "Windows":
        # Windows uses Event Log, not simple files usually.
        log_locations.append("Windows Event Log (not file paths)")

    info['log_locations'] = log_locations

    return info

def get_system_info_json():
    """Returns the gathered system info as a JSON string."""
    try:
        data = get_system_info()
        return json.dumps(data, indent=2)
    except Exception as e:
        print(f"Error generating system info JSON: {e}", file=sys.stderr)
        return json.dumps({"error": "Failed to gather system information", "details": str(e)})

# Example usage (for testing this module directly)
if __name__ == '__main__':
    print(get_system_info_json())