"""
admin/admin_manager.py — Admin module for bank staff operations.

Provides privileged operations: view/lock/unlock accounts, reset PINs,
set withdrawal limits, filter transaction logs, and manage accounts.
Requires separate admin authentication (username + password).
"""

from database.db_manager import DatabaseManager
from security.utils import hash_pin, verify_pin, validate_card_number, validate_pin_format


class AdminManager:
    """
    Handles all admin-only operations.
    
    Attributes:
        db             (DatabaseManager): Database access layer.
        is_logged_in   (bool):            Whether an admin is authenticated.
        admin_username (str|None):         Logged-in admin's username.
    """

    def __init__(self, db: DatabaseManager):
        self.db = db
        self.is_logged_in = False
        self.admin_username = None

    def login(self, username: str, password: str) -> tuple:
        """
        Authenticate an admin user.
        
        Args:
            username: Admin username.
            password: Plain-text password.
        
        Returns:
            (success: bool, message: str)
        """
        if not username or not password:
            return False, "Username and password are required."

        admin = self.db.get_admin(username)
        if admin is None:
            return False, "Invalid admin credentials."

        stored_hash = admin[1]
        if verify_pin(password, stored_hash):
            self.is_logged_in = True
            self.admin_username = username
            return True, f"Admin login successful. Welcome, {username}."
        else:
            return False, "Invalid admin credentials."

    def logout(self):
        """End the admin session."""
        self.is_logged_in = False
        self.admin_username = None

    def require_login(self) -> tuple:
        """Check that an admin is logged in. Returns (ok, message)."""
        if not self.is_logged_in:
            return False, "Admin login required."
        return True, ""

    # ──────────────────────────────────────────
    # Account Management
    # ──────────────────────────────────────────

    def get_all_accounts(self) -> list:
        """Retrieve all accounts for the admin dashboard."""
        return self.db.get_all_accounts()

    def lock_account(self, card_number: str) -> tuple:
        """
        Lock an account (prevent all transactions).
        
        Returns:
            (success: bool, message: str)
        """
        ok, msg = self.require_login()
        if not ok:
            return ok, msg

        account = self.db.get_account(card_number)
        if account is None:
            return False, "Account not found."
        if not account.is_active():
            return False, "Account is already locked."

        self.db.lock_account(card_number)
        return True, f"Account {card_number} locked successfully."

    def unlock_account(self, card_number: str) -> tuple:
        """
        Unlock a locked account.
        
        Returns:
            (success: bool, message: str)
        """
        ok, msg = self.require_login()
        if not ok:
            return ok, msg

        account = self.db.get_account(card_number)
        if account is None:
            return False, "Account not found."
        if account.is_active():
            return False, "Account is already active."

        self.db.unlock_account(card_number)
        return True, f"Account {card_number} unlocked successfully."

    def reset_pin(self, card_number: str, new_pin: str) -> tuple:
        """
        Admin override to reset a user's PIN.
        
        Args:
            card_number: Target account.
            new_pin:     New PIN (plain text, will be hashed).
        
        Returns:
            (success: bool, message: str)
        """
        ok, msg = self.require_login()
        if not ok:
            return ok, msg

        account = self.db.get_account(card_number)
        if account is None:
            return False, "Account not found."

        valid, error = validate_pin_format(new_pin)
        if not valid:
            return False, f"Invalid PIN: {error}"

        self.db.update_pin(card_number, hash_pin(new_pin))
        return True, f"PIN reset for account {card_number}."

    def set_daily_limit(self, card_number: str, limit: float) -> tuple:
        """
        Set the daily withdrawal limit for an account.
        
        Args:
            card_number: Target account.
            limit:       New daily limit in PKR.
        
        Returns:
            (success: bool, message: str)
        """
        ok, msg = self.require_login()
        if not ok:
            return ok, msg

        if limit <= 0:
            return False, "Limit must be greater than zero."

        account = self.db.get_account(card_number)
        if account is None:
            return False, "Account not found."

        self.db.set_daily_limit(card_number, limit)
        return True, f"Daily limit for {card_number} set to Rs.{limit:,.0f}."

    def get_transaction_log(self, card_number: str = None,
                            txn_type: str = None,
                            date_from: str = None,
                            date_to: str = None) -> list:
        """
        Retrieve filtered transaction logs.
        
        All parameters are optional — omit for unfiltered results.
        
        Returns:
            List of Transaction instances.
        """
        return self.db.get_filtered_transactions(
            card_number=card_number,
            txn_type=txn_type,
            date_from=date_from,
            date_to=date_to,
        )

    def add_account(self, holder_name: str, card_number: str,
                    pin: str, balance: float, account_type: str) -> tuple:
        """
        Create a new bank account.
        
        Args:
            holder_name:  Full name of the account holder.
            card_number:  Unique card number (8–16 digits).
            pin:          Initial PIN (plain text, will be hashed).
            balance:      Opening balance.
            account_type: 'savings' or 'current'.
        
        Returns:
            (success: bool, message: str)
        """
        ok, msg = self.require_login()
        if not ok:
            return ok, msg

        # Validate inputs
        if not holder_name.strip():
            return False, "Holder name is required."

        valid, error = validate_card_number(card_number)
        if not valid:
            return False, error

        valid, error = validate_pin_format(pin)
        if not valid:
            return False, error

        if balance < 0:
            return False, "Balance cannot be negative."

        if account_type not in ("savings", "current"):
            return False, "Account type must be 'savings' or 'current'."

        success = self.db.add_account(
            holder_name=holder_name.strip(),
            card_number=card_number,
            pin_hash=hash_pin(pin),
            balance=balance,
            account_type=account_type,
        )

        if success:
            return True, f"Account created for {holder_name.strip()}."
        else:
            return False, "Card number already exists."

    def remove_account(self, card_number: str) -> tuple:
        """
        Delete an account and all its transactions.
        
        Returns:
            (success: bool, message: str)
        """
        ok, msg = self.require_login()
        if not ok:
            return ok, msg

        success = self.db.delete_account(card_number)
        if success:
            return True, f"Account {card_number} removed."
        else:
            return False, "Account not found."
