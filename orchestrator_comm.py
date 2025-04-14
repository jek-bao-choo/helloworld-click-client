# src/helloworld_click_client/orchestrator_comm.py
"""
Handles direct communication with the helloworld-agentic-middleware logic
by importing and calling its functions.
"""
import sys
from typing import Optional

# --- Direct Import Assumption ---
# This assumes 'helloworld_agentic_middleware' package is available.
# Adjust the import based on your actual project structure or installation method.
try:
    # Ensure the middleware's main processing function is correctly referenced
    from helloworld_agentic_middleware.llm_workflow import handle_request as call_middleware_function

except ImportError as e:
    print(f"CRITICAL ERROR: Could not import middleware function: {e}", file=sys.stderr)
    print("Ensure 'helloworld-agentic-middleware' is installed or its 'src' directory is in PYTHONPATH.", file=sys.stderr)
    # Define a dummy function to prevent NameError later, but signal failure
    def call_middleware_function(*args, **kwargs):
        print("Middleware function not available due to import error.", file=sys.stderr)
        return None
    # Or consider exiting immediately:
    # sys.exit("Middleware dependency missing.")

except AttributeError:
    print(f"CRITICAL ERROR: Could not find 'handle_request' function in helloworld_agentic_middleware.llm_workflow.", file=sys.stderr)
    def call_middleware_function(*args, **kwargs):
         print("Middleware function not available due to attribute error.", file=sys.stderr)
         return None
    # sys.exit("Middleware function signature mismatch or missing.")


# --- Communication Function ---

def call_llm_workflow(
    product: str,
    operation: str,
    mode: str,
    msg: Optional[str] = None,
    system_info_json: Optional[str] = None
) -> Optional[str]:
    """
    Directly calls the imported function from the agentic middleware.

    Args:
        product: The target product.
        operation: The operation to perform.
        mode: The interaction mode ('execute', 'fix', 'chat').
        msg: Optional message (chat, error details, command output context).
        system_info_json: JSON string containing detected system information.

    Returns:
        The raw response string from the middleware, or None on error.
    """
    if call_middleware_function is None : # Check if import failed
        return None

    # --- Prepare Message Payload ---
    # The middleware's handle_request expects a single 'msg'.
    # Prepend system info JSON string to the actual message/context.
    final_message = ""
    if system_info_json and system_info_json != "{}": # Avoid sending empty JSON
        final_message += f"System Information:\n```json\n{system_info_json}\n```\n---"
    if msg:
        if final_message: # Add separator if system info was added
            final_message += "\nUser Context/Message:\n"
        final_message += msg
    elif not final_message:
        # Ensure msg is not None if no system info and no user message
        final_message = "Initial request." # Or some default if needed by middleware

    try:
        # Directly call the imported function.
        # ASSUMPTION: The middleware's handle_request function has the signature:
        # handle_request(product: str, operation: str, target: str, mode: str, msg: Optional[str])
        # We provide a placeholder 'target' or modify middleware if 'target' isn't needed for direct calls.
        response = call_middleware_function(
            product=product,
            operation=operation,
            target='direct_call', # Indicate communication method, or make optional in middleware
            mode=mode,
            msg=final_message
        )
        return response # Return the raw string response

    except Exception as e:
        print(f"Error during direct call to middleware function: {type(e).__name__}: {e}", file=sys.stderr)
        # You might want to capture more details from the exception traceback here
        # import traceback
        # print(traceback.format_exc(), file=sys.stderr)
        return None