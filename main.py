# src/helloworld_click_client/main.py -> main.py
"""
Minimal main entry point for the CLI application.
Imports and runs the Click command from cli.py.
"""
# Direct import since cli.py is in the same directory
from cli import cli_entry_point

if __name__ == '__main__':
    cli_entry_point()