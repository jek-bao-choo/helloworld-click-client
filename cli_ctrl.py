# src/helloworld_click_client/cli_ctrl.py -> cli_ctrl.py
import click
import sys
import json

# Direct imports for sibling modules
import cli_menu
import sys_detect
import cmd_run
# Import specific functions directly from sibling modules
from resp_fmt import extract_code_blocks, extract_command_text, format_code_blocks_for_display
import orchestrator_comm

# --- Helper Functions for Different Workflow States ---

def _handle_no_code_blocks():
    """
    Handles the workflow path when the LLM response contains no code blocks.
    Prompts the user for next steps (chat or exit).

    Returns:
        Tuple[str | None, str | None, bool]: (next_mode, next_message, exit_flag)
    """
    user_input = click.prompt(
        "How can I help further? (Max 256 chars, press Enter to exit)",
        default="", show_default=False, err=True # Prompt on stderr for visibility
    )
    if not user_input:
        return None, None, True # mode, message, exit_flag=True
    else:
        next_message = user_input[:256] # Limit input length
        next_mode = 'chat'
        return next_mode, next_message, False # exit_flag=False

def _handle_command_confirmation(code_block):
    """
    Handles asking the user to confirm command execution, runs the command
    if confirmed, and determines the next state based on the outcome.

    Args:
        code_block (str): The code block extracted from the LLM response.
        product (str): The current product context.
        operation (str): The current operation context.
        system_info_json (str): System information as a JSON string.

    Returns:
        Tuple[str | None, str | None, bool]: (next_mode, next_message, exit_flag)
    """
    command_text = extract_command_text(code_block)
    if not command_text:
         click.secho("Warning: Could not extract command text from code block.", fg='yellow', err=True)
         # Treat as if no command was runnable -> ask user what next
         return _handle_no_code_blocks()

    click.echo("The orchestrator provided the following command:")
    # Use secho for colored output, helps distinguish command from other text
    click.secho(command_text, fg='yellow')

    # Prompt user for confirmation on stderr
    if not click.confirm("\nDo you want to execute this command?", default=False, err=True):
        # --- User Confirmed NO ---
        click.echo("Command execution skipped.")
        # Ask user what next (reuse no code block logic)
        return _handle_no_code_blocks()

    # --- User Confirmed YES ---
    click.echo("Executing command...")
    stdout, stderr, returncode = cmd_run.run_command(command_text)

    if returncode == 0:
        # --- SUCCESS ---
        return _handle_command_success(stdout, stderr, command_text)
    else:
        # --- ERROR ---
        return _handle_command_error(stdout, stderr, returncode, command_text)

def _handle_command_success(stdout, stderr, executed_command):
    """
    Formats the message for the LLM after successful command execution.

    Returns:
        Tuple[str, str, bool]: ('execute', success_message, False)
    """
    click.secho("Command executed successfully.", fg='green')
    # Display output clearly
    if stdout: click.echo(f"\n--- Output stdout ---\n{stdout}\n---------------------")
    if stderr: click.echo(f"\n--- Output stderr ---\n{stderr}\n---------------------") # Show stderr even on success

    # Prepare context message for the next LLM call
    next_message = (
        f"The following command executed successfully:\n"
        f"```\n{executed_command}\n```\n"
        f"Output (stdout):\n{stdout or '[No stdout]'}\n"
        f"Output (stderr):\n{stderr or '[No stderr]'}\n\n"
        f"Please provide the next command or instruction based on this result."
    )
    next_mode = 'execute'
    return next_mode, next_message, False # exit_flag=False

def _handle_command_error(stdout, stderr, returncode, executed_command):
    """
    Formats the message for the LLM after failed command execution.

    Returns:
        Tuple[str, str, bool]: ('fix', error_message, False)
    """
    click.secho(f"Command failed (Exit Code: {returncode}).", fg='red', err=True)
    if stdout: click.echo(f"\n--- Output stdout ---\n{stdout}\n---------------------")
    if stderr: click.echo(f"\n--- Error Output stderr ---\n{stderr}\n-------------------------")

    # Prepare context message for the next LLM call ('fix' mode)
    next_message = (
        f"The following command failed:\n"
        f"```\n{executed_command}\n```\n"
        f"Exit Code: {returncode}\n"
        f"Output (stdout):\n{stdout or '[No stdout]'}\n"
        f"Error Output (stderr):\n{stderr or '[No stderr]'}\n\n"
        f"Please provide corrected commands or troubleshooting steps."
    )
    next_mode = 'fix'
    return next_mode, next_message, False # exit_flag=False

# --- Main CLI Entry Point ---

# Use context_settings to allow help options like -h
@click.command(context_settings=dict(help_option_names=['-h', '--help']))
def cli_entry_point():
    """Helloworld Click Client - Your AI-Powered Ops Assistant"""
    click.echo("Welcome! Starting system detection...")

    # 1. System Detection
    try:
        system_info_dict = sys_detect.get_system_info()
        # Ensure JSON is compact for sending, pretty print only if debugging
        system_info_json = json.dumps(system_info_dict)
        click.echo("System detection complete.")
        # Display minimal info to user
        click.echo(f"OS: {system_info_dict.get('os_info', {}).get('system', 'N/A')}")
    except Exception as e:
        click.secho(f"Error during system detection: {e}", fg='red', err=True)
        # Send empty JSON, middleware should handle potentially missing info
        system_info_json = "{}"

    # 2. Display Menu and Get Use Case
    selected_product, selected_operation = cli_menu.display_and_select_use_case()
    if not selected_product: # User chose to exit from menu
        click.echo("No use case selected. Exiting.")
        sys.exit(0)
    click.echo(f"\nYou selected: {selected_operation} {selected_product}")

    # --- Main Interaction Loop ---
    current_mode = 'execute'  # Start with execute mode
    user_message = None     # No initial user message
    exit_app = False        # Loop control flag

    while not exit_app:
        # Use stderr for status messages to keep stdout cleaner for potential scripting
        click.echo(f"\n[{current_mode.upper()} Mode] Calling Orchestrator...", err=True)

        # 3. Call Middleware
        llm_response = orchestrator_comm.call_llm_workflow(
            product=selected_product,
            operation=selected_operation,
            mode=current_mode,
            msg=user_message,
            system_info_json=system_info_json
        )

        # Handle communication failure
        if llm_response is None:
            click.secho("Error: Failed to get response from orchestrator. Cannot continue.", fg='red', err=True)
            break # Exit loop

        # 4. Display LLM Response
        code_blocks = extract_code_blocks(llm_response)
        # Display formatted output (might just be text or include formatted blocks)
        display_output = format_code_blocks_for_display(code_blocks, llm_response)
        click.echo("\n--- Orchestrator Response ---")
        click.echo(display_output.strip()) # Print the formatted/raw response
        click.echo("---------------------------\n")

        # 5. Decide Next Step based on Code Blocks
        if not code_blocks:
            # No Code Blocks Path
            current_mode, user_message, exit_app = _handle_no_code_blocks()
        else:
            # Code Blocks Found Path - handle the first one
            # Pass necessary context to the handler
            current_mode, user_message, exit_app = _handle_command_confirmation(
                code_blocks[0] # Process first block
            )
        # Loop continues with updated mode, message, or exits

    click.echo("\nExiting application.")