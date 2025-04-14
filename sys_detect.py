# helloworld-click-client/sys_detect.py
"""
Gathers basic, reliable system information.
Focuses on OS, architecture, and tool availability.
"""
import platform
import os
import sys
import json
import shutil # Used for checking command existence

# No dependency on cmd_run needed for this simplified version

def _check_command_exists(command_name: str) -> bool:
    """Checks if a command exists using shutil.which (cross-platform)."""
    return shutil.which(command_name) is not None

def get_system_info() -> dict:
    """Gathers essential cross-platform system details."""
    info = {}

    # --- Core OS Info (platform module) ---
    info['os_info'] = {
        "system": platform.system(),        # e.g., 'Linux', 'Darwin', 'Windows'
        "release": platform.release(),      # e.g., '5.15.0-78-generic', '22.6.0'
        "version": platform.version(),      # More detailed version info
        "machine": platform.machine(),      # e.g., 'x86_64', 'arm64'
        "processor": platform.processor(),    # Often generic, e.g., 'x86_64', 'arm'
        "python_version": platform.python_version(), # Version of Python interpreter
    }
    # Add node name (hostname) directly to top level for clarity
    info['hostname'] = platform.node()

    # --- Environment Info (os module) ---
    info['environment'] = {
        "shell": os.environ.get('SHELL'),  # Common on Unix-like
        "terminal": os.environ.get('TERM'), # Terminal type
    }
    # Add Windows command prompt/powershell if shell is not set
    if not info['environment']['shell'] and platform.system() == 'Windows':
        info['environment']['shell'] = os.environ.get('ComSpec')

    # --- Tool Availability ---
    # List tools to check
    tools_to_check = ["kubectl", "helm", "curl", "docker", "git"] # Add/remove as needed
    info['tools_available'] = {
        tool: _check_command_exists(tool) for tool in tools_to_check
    }

    return info

def get_system_info_json() -> str:
    """Returns the gathered system info as a JSON string."""
    try:
        data = get_system_info()
        # Use separators for compact JSON, indent=None for no newlines/spaces
        return json.dumps(data, separators=(',', ':'))
    except Exception as e:
        print(f"Error generating system info JSON: {e}", file=sys.stderr)
        # Return minimal error JSON
        return json.dumps({"error": "Failed to gather system information", "details": str(e)})

# Example usage (for testing this module directly)
if __name__ == '__main__':
    print(json.dumps(get_system_info(), indent=2)) # Pretty print for testing
    # print(get_system_info_json()) # Test compact output