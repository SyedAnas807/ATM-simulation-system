"""
config.py — Central configuration for the ATM Simulation System.

All tunable constants are defined here so they can be adjusted
without touching business logic. Values use Pakistani Rupee (PKR).
"""

import os

# ──────────────────────────────────────────────
# Paths
# ──────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.path.join(BASE_DIR, "atm.db")

# ──────────────────────────────────────────────
# Authentication
# ──────────────────────────────────────────────
MAX_PIN_ATTEMPTS = 3          # Failed attempts before lockout
PIN_MIN_LENGTH = 4            # Minimum PIN digits
PIN_MAX_LENGTH = 6            # Maximum PIN digits
CARD_MIN_LENGTH = 8           # Minimum card number digits
CARD_MAX_LENGTH = 16          # Maximum card number digits
SESSION_TIMEOUT_SECONDS = 60  # Auto-logout after inactivity

# ──────────────────────────────────────────────
# Transactions
# ──────────────────────────────────────────────
DEFAULT_DAILY_WITHDRAWAL_LIMIT = 50_000   # PKR per day
DENOMINATIONS = [500, 1000, 2000, 5000, 10000]  # Available note values
MIN_SAVINGS_BALANCE = 1000                # Savings account floor
SAVINGS_INTEREST_RATE = 0.04              # 4% annual (informational)

# ──────────────────────────────────────────────
# ATM Machine
# ──────────────────────────────────────────────
ATM_INITIAL_CASH = 500_000   # Cash loaded in the machine at start

# ──────────────────────────────────────────────
# Admin
# ──────────────────────────────────────────────
DEFAULT_ADMIN_USERNAME = "admin"
DEFAULT_ADMIN_PASSWORD = "admin123"       # Hashed before storage

# ──────────────────────────────────────────────
# UI
# ──────────────────────────────────────────────
CURRENCY_SYMBOL = "Rs."
APP_TITLE = "ATM Simulation System"
WINDOW_WIDTH = 900
WINDOW_HEIGHT = 720
MINI_STATEMENT_LIMIT = 10    # Number of recent transactions to show
