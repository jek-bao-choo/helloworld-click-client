# helloworld-click-client/orchestrator_comm.py
import sys
import os
from typing import Optional, Callable

# --- Dynamic Path Calculation ---
# Calculate the absolute path to the sibling 'helloworld-agentic-middleware' directory
_MIDDLEWARE_DIR_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', 'helloworld-agentic-middleware')
)

# --- Add Middleware Path and Attempt Import ---
_middleware_func: Optional[Callable] = None # Initialize function holder

# Add middleware path to sys.path if not already present
if _MIDDLEWARE_DIR_PATH not in sys.path:
    # Using append worked, stick with it for simplicity unless conflicts arise
    print(f"Info: Adding middleware path to sys.path: {_MIDDLEWARE_DIR_PATH}", file=sys.stderr)
    sys.path.append(_MIDDLEWARE_DIR_PATH)

try:
    # Try importing the specific function directly
    from llm_workflow import handle_request
    if callable(handle_request):
        _middleware_func = handle_request
        print("Info: Successfully imported middleware 'handle_request' function.")
    else:
        print(f"Error: Imported 'handle_request' from middleware, but it's not callable.", file=sys.stderr)

except ImportError as e:
    print(f"Error: Failed to import 'handle_request' from middleware path: {_MIDDLEWARE_DIR_PATH}", file=sys.stderr)
    print(f"ImportError details: {e}", file=sys.stderr)
    # Optional: uncomment below for full traceback during development if needed
    # traceback.print_exc(file=sys.stderr)
except Exception as e:
    print(f"Error: An unexpected error occurred during middleware import: {type(e).__name__}: {e}", file=sys.stderr)
    # Optional: uncomment below for full traceback during development if needed
    # traceback.print_exc(file=sys.stderr)


# --- Communication Function ---
def call_llm_workflow(
    product: str,
    operation: str,
    mode: str,
    msg: Optional[str] = None,
    system_info_json: Optional[str] = None
) -> Optional[str]:
    """
    Calls the dynamically imported handle_request function from the middleware.
    """
    if _middleware_func is None:
        print("Error: Middleware function 'handle_request' could not be loaded. Cannot communicate.", file=sys.stderr)
        return None

    # --- Prepare Message Payload ---
    final_message = ""
    if system_info_json and system_info_json != "{}":
        final_message += f"System Information:\n```json\n{system_info_json}\n```\n---"
    if msg:
        if final_message:
            final_message += "\nUser Context/Message:\n"
        final_message += msg
    elif not final_message:
        # Use a default message if both system_info and msg are empty/None
        final_message = "Initial request."

    try:
        # Directly call the dynamically loaded function object.
        # Ensure the arguments match what handle_request expects.
        response = _middleware_func(
            product=product,
            operation=operation,
            target='local', # Still assuming 'local' target, adjust if needed
            mode=mode,
            msg=final_message
        )
        return response

    except Exception as e:
        print(f"Error during call to middleware function 'handle_request': {type(e).__name__}: {e}", file=sys.stderr)
        return None