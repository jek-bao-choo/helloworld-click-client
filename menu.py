# src/helloworld_click_client/menu.py
"""
Handles displaying the menu of available use cases and getting user selection.
"""
import click

# Define available use cases (Product, Operation)
# Match these with keys/logic expected by your middleware
USE_CASES = {
    "1": ("Splunk-OTel-Collector", "Install"),
    "2": ("Splunk-OTel-Collector", "Uninstall"),
    "3": ("curl", "Install"),
    # Add more use cases here
}

def display_and_select_use_case():
    """Displays the menu and returns the selected (product, operation) tuple."""
    click.echo("\nPlease select a use case:")
    for key, (product, operation) in USE_CASES.items():
        click.echo(f"  {key}. {operation} {product}")
    click.echo("  0. Exit")

    while True:
        choice = click.prompt("Enter your choice", type=click.Choice(list(USE_CASES.keys()) + ['0']))

        if choice == '0':
            return None, None # Indicate user chose to exit

        if choice in USE_CASES:
            product, operation = USE_CASES[choice]
            return product, operation
        else:
            # Should not happen with click.Choice, but good practice
            click.echo("Invalid choice, please try again.")

# Example usage (for testing this module directly)
if __name__ == '__main__':
    prod, op = display_and_select_use_case()
    if prod:
        print(f"\nYou selected: Product='{prod}', Operation='{op}'")
    else:
        print("\nYou chose to exit.")