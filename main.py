"""
main.py — Entry point for the ATM Simulation System.

Initializes the database with seed data (if first run),
then launches the Tkinter GUI application.

Usage:
    python main.py
"""

import sys
import os

# Ensure the project root is on the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def main():
    """Initialize the system and launch the ATM GUI."""
    print("=" * 50)
    print("  ATM Simulation System")
    print("  Starting up...")
    print("=" * 50)

    # Step 1: Seed the database with demo accounts
    try:
        from seed_data import seed_database
        print("\n[1/2] Checking database...")
        seed_database()
    except Exception as e:
        print(f"  Warning: Seed error - {e}")
        print("  Continuing with existing data...")

    # Step 2: Launch GUI
    try:
        print("\n[2/2] Launching ATM interface...\n")
        from gui.app import ATMApp
        app = ATMApp()
        app.mainloop()
    except Exception as e:
        print(f"\nFatal error: {e}")
        print("Please ensure Python 3.8+ with tkinter is installed.")
        sys.exit(1)

    print("\nATM System shut down. Goodbye!")


if __name__ == "__main__":
    main()
