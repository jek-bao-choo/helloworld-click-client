# src/helloworld_click_client/resp_fmt.py
"""
Handles formatting LLM responses, focusing on extracting code blocks.
"""
import re
from typing import List

def extract_code_blocks(response_text: str) -> list[str]:
    """
    Extracts code blocks fenced by triple backticks.

    Args:
        response_text: The raw text response from the chat model.

    Returns:
        A list of strings, where each string is a matched code block
        (including the backticks). Returns an empty list if none found.
    """
    # Pattern for triple-backtick blocks (captures full block in group 0)
    # Allows optional language identifier and flexible whitespace/newlines
    triple_tick_pattern = r"```(?:[\w-]+)?\s*?\n(.*?)\n?\s*?```"

    # Use findall to get all non-overlapping matches of the pattern
    # re.DOTALL makes '.' match newline characters as well
    matches = re.findall(triple_tick_pattern, response_text, re.DOTALL | re.IGNORECASE)

    # Construct full block matches including backticks for context
    # Note: findall with groups returns the content *inside* the outer group if groups exist.
    # We need to re-find the full match for context or use finditer. Let's use finditer.

    full_blocks = []
    for match_obj in re.finditer(triple_tick_pattern, response_text, re.DOTALL | re.IGNORECASE):
        full_blocks.append(match_obj.group(0)) # group(0) is the entire match

    return full_blocks


def extract_command_text(code_block: str) -> str:
    """
    Removes backticks (triple) and optional language identifier
    from a code block string to get the raw command(s).
    """
    # Try matching triple backticks first
    # Group 1 captures the content inside the backticks
    match = re.search(r"```(?:[\w-]+)?\s*?\n?(.*?)\n?\s*?```", code_block, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()

    # Fallback: If no triple backticks found, maybe LLM used single backticks?
    # This is less common for multi-line commands but could happen.
    match_single = re.search(r"`([^`]+)`", code_block)
    if match_single:
         # Be cautious, this might grab unintended inline code snippets
         return match_single.group(1).strip()

    # If no backticks found, return the original block, stripped of whitespace.
    # This might indicate the LLM response format was unexpected.
    return code_block.strip()


def format_code_blocks_for_display(code_blocks: List[str], raw_response: str) -> str:
    """
    Formats the response for display. Prioritizes showing code blocks if found.

    Args:
        code_blocks: A list of extracted code block strings (including backticks).
        raw_response: The full raw response string from the LLM.

    Returns:
        A formatted string ready for printing to the console.
    """
    if not code_blocks:
        # If no code blocks, return the raw response cleanly
        return f"{raw_response.strip()}" # Removed extra "Orchestrator response:" label here

    output_parts = []
    # Optionally add introductory text before the code blocks if desired
    # output_parts.append("The orchestrator suggests the following command(s):")

    for i, block in enumerate(code_blocks):
         # Extract the clean command text for display emphasis if needed
         # command_text = extract_command_text(block)
         # output_parts.append(f"\n--- Command Block {i+1} ---")
         # output_parts.append(command_text) # Display extracted command
         # output_parts.append("-------------------------")
         # OR just display the raw block as returned by LLM:
         output_parts.append(f"\n--- Code Block {i+1} ---")
         output_parts.append(block.strip()) # Show the full block with backticks
         output_parts.append("----------------------")


    # Decide if you want to include non-code parts of the raw_response as well.
    # This requires more complex parsing to isolate text outside the found code blocks.
    # For simplicity now, we are just displaying the code blocks.

    return "\n".join(output_parts)