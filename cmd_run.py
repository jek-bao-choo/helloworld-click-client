# src/helloworld_click_client/cmd_run.py
"""
Provides a reusable helper function for running shell commands reliably.
"""
import subprocess
import shlex
import sys

def run_command(command_str: str):
    """
    Runs a command string safely using subprocess.

    Args:
        command_str: The command to execute as a string.

    Returns:
        A tuple containing (stdout: str | None, stderr: str | None, returncode: int).
        Returns None for stdout/stderr on major execution errors (like FileNotFoundError).
    """
    print(f"Attempting to run command: {command_str}")
    try:
        # Use shlex.split for basic safety against shell injection if command_str
        # might ever come from less trusted sources (like LLM output without validation).
        # If commands are always constructed internally, using a list is safer:
        # args = ['ls', '-l'] etc.
        args = shlex.split(command_str)

        if not args:
            print("Warning: Empty command string provided.", file=sys.stderr)
            return "", "Empty command string", -1 # Indicate error

        # Determine if shell=True is needed (use with caution!)
        # Generally avoid shell=True. Only use if command relies on shell features
        # like pipes, wildcards, environment variable expansion *within the command string itself*.
        # If you need pipes etc., consider using multiple subprocess calls in Python.
        use_shell = False
        # Example check (adapt as needed, but prefer avoiding shell=True):
        # if any(c in command_str for c in ['|', '*', '>', '<', '$', '&&', '||']):
        #    print("Warning: Command may use shell features. Consider alternative approaches.", file=sys.stderr)
        #    # use_shell = True # Uncomment ONLY if absolutely necessary and understand risks

        result = subprocess.run(
            args if not use_shell else command_str, # Pass string if shell=True
            capture_output=True,
            text=True,    # Capture output as text (decodes based on system default)
            check=False,  # Do not raise exception on non-zero exit code
            shell=use_shell # DANGEROUS if command_str comes from external input
        )
        print(f"Command finished with exit code: {result.returncode}")
        return result.stdout.strip(), result.stderr.strip(), result.returncode

    except FileNotFoundError:
        err_msg = f"Error: Command not found: '{args[0]}'. Is it installed and in PATH?"
        print(err_msg, file=sys.stderr)
        # Return code convention for "command not found" is often 127
        return None, err_msg, 127
    except PermissionError:
        err_msg = f"Error: Permission denied executing command: '{args[0]}'."
        print(err_msg, file=sys.stderr)
        # Return code convention for "permission denied" is often 126
        return None, err_msg, 126
    except Exception as e:
        err_msg = f"Error running command '{command_str}': {type(e).__name__}: {e}"
        print(err_msg, file=sys.stderr)
        return None, err_msg, -1 # General error