"""
seed_data.py — Pre-loads demo accounts and admin user.

Run this script to initialize the database with 3 sample accounts
and an admin user. Safe to run multiple times (idempotent).

Demo Accounts:
  1. Ali Hassan     | Card: 1234567890 | PIN: 1111 | Rs.25,000 | Savings | Active
  2. Sara Khan      | Card: 9876543210 | PIN: 2222 | Rs.75,000 | Current | Active
  3. Usman Ahmed    | Card: 1111222233 | PIN: 3333 | Rs.5,000  | Savings | Locked

Admin:
  Username: admin | Password: admin123
"""

from database.db_manager import DatabaseManager
from security.utils import hash_pin
from config import ATM_INITIAL_CASH, DEFAULT_ADMIN_USERNAME, DEFAULT_ADMIN_PASSWORD


def seed_database():
    """
    Insert demo accounts and admin user into the database.
    Skips any records that already exist (idempotent).
    """
    db = DatabaseManager()

    # ── Demo Accounts ──────────────────────────
    demo_accounts = [
        {
            "holder_name": "Ali Hassan",
            "card_number": "1234567890",
            "pin": "1111",
            "balance": 25000.0,
            "account_type": "savings",
            "status": "active",
        },
        {
            "holder_name": "Sara Khan",
            "card_number": "9876543210",
            "pin": "2222",
            "balance": 75000.0,
            "account_type": "current",
            "status": "active",
        },
        {
            "holder_name": "Usman Ahmed",
            "card_number": "1111222233",
            "pin": "3333",
            "balance": 5000.0,
            "account_type": "savings",
            "status": "locked",
        },
    ]

    accounts_added = 0
    for acct in demo_accounts:
        success = db.add_account(
            holder_name=acct["holder_name"],
            card_number=acct["card_number"],
            pin_hash=hash_pin(acct["pin"]),
            balance=acct["balance"],
            account_type=acct["account_type"],
            status=acct["status"],
        )
        if success:
            accounts_added += 1
            print(f"  + Added account: {acct['holder_name']} ({acct['card_number']})")
        else:
            print(f"  - Skipped (exists): {acct['holder_name']} ({acct['card_number']})")

    # ── Admin User ─────────────────────────────
    admin_added = db.add_admin(
        username=DEFAULT_ADMIN_USERNAME,
        password_hash=hash_pin(DEFAULT_ADMIN_PASSWORD),
    )
    if admin_added:
        print(f"  + Added admin user: {DEFAULT_ADMIN_USERNAME}")
    else:
        print(f"  - Skipped (exists): admin user '{DEFAULT_ADMIN_USERNAME}'")

    # ── ATM Cash ───────────────────────────────
    current_cash = db.get_atm_cash()
    if current_cash == 0.0:
        db.set_atm_cash(ATM_INITIAL_CASH)
        print(f"  + ATM loaded with Rs.{ATM_INITIAL_CASH:,.0f}")
    else:
        print(f"  - ATM cash already set: Rs.{current_cash:,.0f}")

    print(f"\n  Seed complete. {accounts_added} new account(s) added.")


if __name__ == "__main__":
    print("\n-- ATM Database Seeding ------------------\n")
    seed_database()
