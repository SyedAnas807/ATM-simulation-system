"""
auth/auth_manager.py — Authentication and session management.

Handles user login (card + PIN verification), failed-attempt tracking,
account lockout after 3 failures, and session timeout (60 s inactivity).
"""

import time
from database.db_manager import DatabaseManager
from security.utils import verify_pin, validate_card_number, validate_pin_format
from config import MAX_PIN_ATTEMPTS, SESSION_TIMEOUT_SECONDS


class AuthManager:
    """
    Manages user authentication, session state, and lockout logic.
    
    Attributes:
        db              (DatabaseManager): Database access layer.
        current_account (Account|None):    Currently logged-in account.
        last_activity   (float):           Timestamp of last user action.
    """

    def __init__(self, db: DatabaseManager):
        self.db = db
        self.current_account = None
        self.last_activity = 0.0

    def authenticate(self, card_number: str, pin: str) -> tuple:
        """
        Attempt to authenticate a user with card number and PIN.
        
        Flow:
            1. Validate card format
            2. Check account exists
            3. Check account not locked
            4. Verify PIN hash
            5. Track failed attempts / lock on 3rd failure
        
        Args:
            card_number: User's card number.
            pin:         User's plain-text PIN.
        
        Returns:
            (success: bool, message: str, account: Account|None)
        """
        # Step 1: Validate card number format
        valid, error = validate_card_number(card_number)
        if not valid:
            return False, error, None

        # Step 2: Check account exists
        account = self.db.get_account(card_number)
        if account is None:
            return False, "Card number not recognized. Please try again.", None

        # Step 3: Check if account is locked
        if not account.is_active():
            return False, "This account is locked. Please contact your bank.", None

        # Step 4: Validate PIN format
        valid, error = validate_pin_format(pin)
        if not valid:
            return False, error, None

        # Step 5: Verify PIN
        if verify_pin(pin, account.pin_hash):
            # Success — reset failed attempts
            self.db.update_failed_attempts(card_number, 0)
            self.current_account = self.db.get_account(card_number)  # Refresh
            self.last_activity = time.time()
            return True, f"Welcome, {account.holder_name}!", self.current_account
        else:
            # Failed attempt
            new_attempts = account.failed_attempts + 1
            remaining = MAX_PIN_ATTEMPTS - new_attempts

            if new_attempts >= MAX_PIN_ATTEMPTS:
                # Lock the account
                self.db.lock_account(card_number)
                return False, (
                    "Incorrect PIN. Maximum attempts exceeded.\n"
                    "Your account has been LOCKED for security.\n"
                    "Please contact your bank to unlock it."
                ), None
            else:
                self.db.update_failed_attempts(card_number, new_attempts)
                return False, (
                    f"Incorrect PIN. {remaining} attempt(s) remaining."
                ), None

    def refresh_session(self):
        """Reset the inactivity timer. Call on every user action."""
        self.last_activity = time.time()

    def is_session_expired(self) -> bool:
        """
        Check if the current session has timed out due to inactivity.
        
        Returns:
            True if more than SESSION_TIMEOUT_SECONDS have elapsed
            since the last activity.
        """
        if self.last_activity == 0.0:
            return True
        return (time.time() - self.last_activity) > SESSION_TIMEOUT_SECONDS

    def get_remaining_time(self) -> int:
        """Return seconds remaining before session timeout."""
        if self.last_activity == 0.0:
            return 0
        elapsed = time.time() - self.last_activity
        remaining = SESSION_TIMEOUT_SECONDS - elapsed
        return max(0, int(remaining))

    def logout(self):
        """Clear the current session."""
        self.current_account = None
        self.last_activity = 0.0

    def is_logged_in(self) -> bool:
        """Check if a user is currently logged in with a valid session."""
        return self.current_account is not None and not self.is_session_expired()

    def refresh_account(self):
        """
        Reload the current account from the database to get 
        the latest balance and state.
        """
        if self.current_account:
            self.current_account = self.db.get_account(
                self.current_account.card_number
            )
