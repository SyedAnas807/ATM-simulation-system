"""
core/atm.py — ATM controller (main business logic).

Orchestrates all transaction operations: balance inquiry, withdrawal,
deposit, fund transfer, PIN change, and mini-statement generation.
Tracks the ATM machine's physical cash level.
"""

from datetime import date
from database.db_manager import DatabaseManager
from models.transaction import Transaction
from security.utils import hash_pin, verify_pin, validate_amount, validate_card_number
from config import DENOMINATIONS, MIN_SAVINGS_BALANCE


class ATMController:
    """
    Central controller for all ATM operations.
    
    Manages the ATM machine's cash pool and delegates database
    operations to the DatabaseManager.
    
    Attributes:
        db          (DatabaseManager): Database access layer.
        atm_cash    (float):           Cash currently in the machine.
    """

    def __init__(self, db: DatabaseManager):
        self.db = db
        self.atm_cash = db.get_atm_cash()

    def _refresh_cash(self):
        """Reload ATM cash from database."""
        self.atm_cash = self.db.get_atm_cash()

    # ──────────────────────────────────────────
    # Balance Inquiry
    # ──────────────────────────────────────────

    def check_balance(self, account) -> tuple:
        """
        Retrieve the current balance for the given account.
        Logs the inquiry as a transaction.
        
        Args:
            account: Account instance.
            
        Returns:
            (success: bool, balance: float, message: str)
        """
        try:
            # Refresh from DB to get latest
            fresh = self.db.get_account(account.card_number)
            if fresh is None:
                return False, 0.0, "Account not found."

            # Log the inquiry
            txn = Transaction(
                card_number=account.card_number,
                txn_type="balance_inquiry",
                amount=0.0,
                balance_after=fresh.balance,
                description="Balance inquiry",
            )
            self.db.add_transaction(txn)

            return True, fresh.balance, "Balance retrieved successfully."
        except Exception as e:
            return False, 0.0, f"Error retrieving balance: {str(e)}"

    # ──────────────────────────────────────────
    # Withdrawal
    # ──────────────────────────────────────────

    def withdraw(self, account, amount: float) -> tuple:
        """
        Process a cash withdrawal.
        
        Checks:
            - Amount is positive and valid
            - Denomination is dispensable
            - Sufficient account balance
            - Savings minimum balance rule
            - Daily withdrawal limit
            - ATM has enough cash
        
        Args:
            account: Account instance.
            amount:  Amount to withdraw in PKR.
            
        Returns:
            (success: bool, message: str, transaction: Transaction|None)
        """
        try:
            # Refresh account data
            fresh = self.db.get_account(account.card_number)
            if fresh is None:
                return False, "Account not found.", None

            # Reset daily total if new day
            today = date.today().isoformat()
            if fresh.last_withdrawal_date != today:
                fresh.withdrawn_today = 0.0

            # Check withdrawal rules
            allowed, reason = fresh.can_withdraw(amount)
            if not allowed:
                # Log failed attempt
                txn = Transaction(
                    card_number=account.card_number,
                    txn_type="withdrawal",
                    amount=amount,
                    balance_after=fresh.balance,
                    status="failed",
                    description=reason,
                )
                self.db.add_transaction(txn)
                return False, reason, None

            # Check ATM cash availability
            self._refresh_cash()
            if amount > self.atm_cash:
                txn = Transaction(
                    card_number=account.card_number,
                    txn_type="withdrawal",
                    amount=amount,
                    balance_after=fresh.balance,
                    status="failed",
                    description="ATM has insufficient cash.",
                )
                self.db.add_transaction(txn)
                return False, "ATM does not have enough cash. Please try a smaller amount.", None

            # Check denomination validity (must be divisible by smallest)
            min_denom = min(DENOMINATIONS)
            if amount % min_denom != 0:
                return False, f"Amount must be in multiples of Rs.{min_denom}.", None

            # Process withdrawal
            new_balance = fresh.balance - amount
            self.db.update_balance(account.card_number, new_balance)
            self.db.update_daily_withdrawal(account.card_number, amount)

            # Update ATM cash
            new_atm_cash = self.atm_cash - amount
            self.db.set_atm_cash(new_atm_cash)
            self.atm_cash = new_atm_cash

            # Update the account object in-place for the caller
            account.balance = new_balance

            # Log transaction
            txn = Transaction(
                card_number=account.card_number,
                txn_type="withdrawal",
                amount=amount,
                balance_after=new_balance,
                description=f"Cash withdrawal of Rs.{amount:,.0f}",
            )
            self.db.add_transaction(txn)

            return True, f"Rs.{amount:,.0f} dispensed successfully.", txn

        except Exception as e:
            return False, f"Transaction error: {str(e)}", None

    # ──────────────────────────────────────────
    # Deposit
    # ──────────────────────────────────────────

    def deposit(self, account, amount: float) -> tuple:
        """
        Process a cash deposit.
        
        Args:
            account: Account instance.
            amount:  Amount to deposit in PKR.
            
        Returns:
            (success: bool, message: str, transaction: Transaction|None)
        """
        try:
            if amount <= 0:
                return False, "Deposit amount must be greater than zero.", None

            fresh = self.db.get_account(account.card_number)
            if fresh is None:
                return False, "Account not found.", None

            new_balance = fresh.balance + amount
            self.db.update_balance(account.card_number, new_balance)

            # Add to ATM cash pool
            self._refresh_cash()
            self.db.set_atm_cash(self.atm_cash + amount)
            self.atm_cash += amount

            # Update account object
            account.balance = new_balance

            txn = Transaction(
                card_number=account.card_number,
                txn_type="deposit",
                amount=amount,
                balance_after=new_balance,
                description=f"Cash deposit of Rs.{amount:,.0f}",
            )
            self.db.add_transaction(txn)

            return True, f"Rs.{amount:,.0f} deposited successfully.", txn

        except Exception as e:
            return False, f"Deposit error: {str(e)}", None

    # ──────────────────────────────────────────
    # Fund Transfer
    # ──────────────────────────────────────────

    def transfer(self, from_account, to_card: str, amount: float) -> tuple:
        """
        Transfer funds from one account to another.
        
        Checks:
            - Recipient exists and is active
            - Sender has sufficient balance
            - Sender is not transferring to themselves
            - Savings minimum balance rule
        
        Args:
            from_account: Sender's Account instance.
            to_card:      Recipient's card number.
            amount:       Amount to transfer.
            
        Returns:
            (success: bool, message: str, transaction: Transaction|None)
        """
        try:
            if amount <= 0:
                return False, "Transfer amount must be greater than zero.", None

            # Validate recipient card
            valid, error = validate_card_number(to_card)
            if not valid:
                return False, f"Recipient card error: {error}", None

            # Check self-transfer
            if from_account.card_number == to_card:
                return False, "Cannot transfer to your own account.", None

            # Check recipient exists and is active
            recipient = self.db.get_account(to_card)
            if recipient is None:
                return False, "Recipient card number not found.", None
            if not recipient.is_active():
                return False, "Recipient account is locked.", None

            # Refresh sender balance
            sender = self.db.get_account(from_account.card_number)
            if sender is None:
                return False, "Your account was not found.", None

            # Check sender balance
            if amount > sender.balance:
                txn = Transaction(
                    card_number=from_account.card_number,
                    txn_type="transfer_out",
                    amount=amount,
                    balance_after=sender.balance,
                    recipient_card=to_card,
                    status="failed",
                    description="Insufficient funds for transfer.",
                )
                self.db.add_transaction(txn)
                return False, "Insufficient funds for this transfer.", None

            # Savings minimum balance check
            if sender.account_type == "savings":
                if sender.balance - amount < MIN_SAVINGS_BALANCE:
                    return False, (
                        f"Transfer would drop below minimum balance of "
                        f"Rs.{MIN_SAVINGS_BALANCE:,.0f}."
                    ), None

            # Execute transfer
            new_sender_balance = sender.balance - amount
            new_recipient_balance = recipient.balance + amount

            self.db.update_balance(from_account.card_number, new_sender_balance)
            self.db.update_balance(to_card, new_recipient_balance)

            # Update sender account object
            from_account.balance = new_sender_balance

            # Log outgoing transaction (sender)
            txn_out = Transaction(
                card_number=from_account.card_number,
                txn_type="transfer_out",
                amount=amount,
                balance_after=new_sender_balance,
                recipient_card=to_card,
                description=f"Transfer to ***{to_card[-4:]}",
            )
            self.db.add_transaction(txn_out)

            # Log incoming transaction (recipient)
            txn_in = Transaction(
                card_number=to_card,
                txn_type="transfer_in",
                amount=amount,
                balance_after=new_recipient_balance,
                recipient_card=from_account.card_number,
                description=f"Transfer from ***{from_account.card_number[-4:]}",
            )
            self.db.add_transaction(txn_in)

            return True, (
                f"Rs.{amount:,.0f} transferred to ***{to_card[-4:]} successfully."
            ), txn_out

        except Exception as e:
            return False, f"Transfer error: {str(e)}", None

    # ──────────────────────────────────────────
    # Change PIN
    # ──────────────────────────────────────────

    def change_pin(self, account, old_pin: str, new_pin: str,
                   confirm_pin: str) -> tuple:
        """
        Change the user's PIN.
        
        Validates old PIN, checks new PIN format, confirms match,
        and updates the hash in the database.
        
        Args:
            account:     Account instance.
            old_pin:     Current PIN (plain text).
            new_pin:     New PIN (plain text).
            confirm_pin: Confirmation of new PIN.
            
        Returns:
            (success: bool, message: str)
        """
        try:
            # Verify old PIN
            fresh = self.db.get_account(account.card_number)
            if fresh is None:
                return False, "Account not found."

            if not verify_pin(old_pin, fresh.pin_hash):
                txn = Transaction(
                    card_number=account.card_number,
                    txn_type="pin_change",
                    amount=0.0,
                    balance_after=fresh.balance,
                    status="failed",
                    description="Incorrect current PIN.",
                )
                self.db.add_transaction(txn)
                return False, "Current PIN is incorrect."

            # Validate new PIN format
            from security.utils import validate_pin_format
            valid, error = validate_pin_format(new_pin)
            if not valid:
                return False, f"New PIN invalid: {error}"

            # Check confirmation match
            if new_pin != confirm_pin:
                return False, "New PIN and confirmation do not match."

            # Check not same as old
            if old_pin == new_pin:
                return False, "New PIN must be different from current PIN."

            # Update PIN
            self.db.update_pin(account.card_number, hash_pin(new_pin))

            txn = Transaction(
                card_number=account.card_number,
                txn_type="pin_change",
                amount=0.0,
                balance_after=fresh.balance,
                description="PIN changed successfully.",
            )
            self.db.add_transaction(txn)

            return True, "PIN changed successfully."

        except Exception as e:
            return False, f"PIN change error: {str(e)}"

    # ──────────────────────────────────────────
    # Mini Statement
    # ──────────────────────────────────────────

    def get_mini_statement(self, account, limit: int = 10) -> list:
        """
        Retrieve the last `limit` transactions for the account.
        
        Args:
            account: Account instance.
            limit:   Maximum number of transactions.
            
        Returns:
            List of Transaction instances, newest first.
        """
        return self.db.get_recent_transactions(account.card_number, limit)

    # ──────────────────────────────────────────
    # ATM Status
    # ──────────────────────────────────────────

    def get_atm_cash(self) -> float:
        """Return the current cash available in the ATM."""
        self._refresh_cash()
        return self.atm_cash
