# helloworld-click-client/orchestrator_comm.py
import sys
import os
import traceback # Import traceback module
from typing import Optional, Callable

# --- Dynamic Path Calculation (Keep this as is) ---
_MIDDLEWARE_DIR_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'helloworld-agentic-middleware'))

# --- Helper Function to Import Middleware Logic (Modified for better error reporting) ---

def _get_middleware_handle_request_func() -> Optional[Callable]:
    """
    Dynamically imports the 'handle_request' function from the middleware's
    'llm_workflow' module by adding its directory to sys.path. Includes enhanced error reporting.

    Returns:
        The handle_request function object if successful, None otherwise.
    """
    # Ensure the calculated path is added to sys.path
    if _MIDDLEWARE_DIR_PATH not in sys.path:
        print(f"Info: Temporarily appending middleware path to sys.path: {_MIDDLEWARE_DIR_PATH}", file=sys.stderr)
        sys.path.append(_MIDDLEWARE_DIR_PATH)

    try:
        # Debug: Print sys.path just before attempting import
        # print(f"DEBUG: Attempting to import 'llm_workflow'. Current sys.path: {sys.path}", file=sys.stderr)

        # Now try to import the specific module from the middleware
        import llm_workflow
        print(f"Info: Successfully imported llm_workflow from {_MIDDLEWARE_DIR_PATH}")

        # Attempt to get the function from the imported module
        handle_request_func = getattr(llm_workflow, 'handle_request', None)

        if handle_request_func and callable(handle_request_func):
            print(f"Info: Successfully imported 'handle_request' from {_MIDDLEWARE_DIR_PATH}/llm_workflow.py")
            return handle_request_func
        elif handle_request_func:
            print(f"Error: Found 'handle_request' in '{_MIDDLEWARE_DIR_PATH}/llm_workflow.py', but it is not callable.", file=sys.stderr)
            return None
        else:
             print(f"Error: Could not find 'handle_request' function within the imported 'llm_workflow' module from path: {_MIDDLEWARE_DIR_PATH}", file=sys.stderr)
             return None

    except ImportError as e:
        print("-------------------- IMPORT ERROR DETECTED --------------------", file=sys.stderr)
        print(f"Error: Could not import 'llm_workflow' module or one of its dependencies.", file=sys.stderr)
        print(f"Attempted to load from: {_MIDDLEWARE_DIR_PATH}", file=sys.stderr)
        print(f"Specific ImportError message: {e}", file=sys.stderr)
        print("\n--- Full Traceback ---", file=sys.stderr)
        traceback.print_exc(file=sys.stderr) # <<< Print the full traceback
        print("---------------------------------------------------------------", file=sys.stderr)
        print("Suggestion: Check the traceback above for the exact line causing the import failure.", file=sys.stderr)
        print("It might be within llm_workflow.py or a file it tries to import (e.g., llm_config, chatsend, etc.).", file=sys.stderr)
        print("Ensure all necessary files exist in the middleware directory and have no syntax errors.", file=sys.stderr)
        return None
    except Exception as e:
        # Catch other potential errors during import/getattr
        print("-------------------- UNEXPECTED ERROR DURING IMPORT --------------------", file=sys.stderr)
        print(f"Error dynamically importing middleware function: {type(e).__name__}: {e}", file=sys.stderr)
        print("\n--- Full Traceback ---", file=sys.stderr)
        traceback.print_exc(file=sys.stderr) # <<< Print the full traceback
        print("-----------------------------------------------------------------------", file=sys.stderr)
        return None

# --- Get the function object once when this module is loaded ---
# (Keep this as is)
_middleware_func: Optional[Callable] = _get_middleware_handle_request_func()

# --- Communication Function ---
# (Keep the rest of the file, including call_llm_workflow, as is)
def call_llm_workflow(
    product: str,
    operation: str,
    mode: str,
    msg: Optional[str] = None,
    system_info_json: Optional[str] = None
) -> Optional[str]:
    if _middleware_func is None:
        print("Error: Middleware function could not be loaded. Cannot communicate.", file=sys.stderr)
        return None

    final_message = ""
    if system_info_json and system_info_json != "{}":
        final_message += f"System Information:\n```json\n{system_info_json}\n```\n---"
    if msg:
        if final_message:
            final_message += "\nUser Context/Message:\n"
        final_message += msg
    elif not final_message:
        final_message = "Initial request."

    try:
        # Pass target='local' or 'openrouter' as appropriate, or modify middleware if not needed
        response = _middleware_func(
            product=product,
            operation=operation,
            target='local', # Example: Decide target here or modify middleware
            mode=mode,
            msg=final_message
        )
        return response

    except Exception as e:
        print(f"Error during call to dynamically imported middleware function: {type(e).__name__}: {e}", file=sys.stderr)
        # traceback.print_exc(file=sys.stderr) # Uncomment for more debug info if needed later
        return None