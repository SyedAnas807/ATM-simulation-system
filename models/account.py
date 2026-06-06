"""
models/account.py — Account data models with OOP inheritance.

Defines the base Account class and two subclasses:
  - SavingsAccount: interest-bearing, enforces minimum balance.
  - CurrentAccount: no minimum balance restriction.

Instances are created from database rows via the `from_db_row()` 
class method and carry all fields needed for transaction logic.
"""

from config import MIN_SAVINGS_BALANCE, SAVINGS_INTEREST_RATE, DEFAULT_DAILY_WITHDRAWAL_LIMIT


class Account:
    """
    Base class representing a bank account linked to an ATM card.
    
    Attributes:
        holder_name          (str):   Full name of the account holder.
        card_number          (str):   Unique 8–16 digit card number.
        pin_hash             (str):   SHA-256 hash of the PIN (never plain text).
        balance              (float): Current available balance in PKR.
        account_type         (str):   'savings' or 'current'.
        status               (str):   'active' or 'locked'.
        daily_withdrawal_limit (float): Max withdrawal per day.
        withdrawn_today      (float): Amount already withdrawn today.
        last_withdrawal_date (str):   ISO date of last withdrawal (for daily reset).
        failed_attempts      (int):   Consecutive failed PIN entries.
    """

    def __init__(self, holder_name: str, card_number: str, pin_hash: str,
                 balance: float = 0.0, account_type: str = "savings",
                 status: str = "active",
                 daily_withdrawal_limit: float = DEFAULT_DAILY_WITHDRAWAL_LIMIT,
                 withdrawn_today: float = 0.0,
                 last_withdrawal_date: str = "",
                 failed_attempts: int = 0):
        self.holder_name = holder_name
        self.card_number = card_number
        self.pin_hash = pin_hash
        self.balance = balance
        self.account_type = account_type
        self.status = status
        self.daily_withdrawal_limit = daily_withdrawal_limit
        self.withdrawn_today = withdrawn_today
        self.last_withdrawal_date = last_withdrawal_date
        self.failed_attempts = failed_attempts

    @classmethod
    def from_db_row(cls, row: tuple):
        """
        Factory method to create the correct Account subclass 
        from a database row tuple.
        
        Expected row order:
            holder_name, card_number, pin_hash, balance, account_type,
            status, daily_withdrawal_limit, withdrawn_today,
            last_withdrawal_date, failed_attempts
        """
        (holder_name, card_number, pin_hash, balance, account_type,
         status, daily_limit, withdrawn, last_date, failed) = row

        # Pick the right subclass based on account_type
        if account_type == "savings":
            return SavingsAccount(
                holder_name=holder_name, card_number=card_number,
                pin_hash=pin_hash, balance=balance,
                status=status, daily_withdrawal_limit=daily_limit,
                withdrawn_today=withdrawn, last_withdrawal_date=last_date or "",
                failed_attempts=failed,
            )
        else:
            return CurrentAccount(
                holder_name=holder_name, card_number=card_number,
                pin_hash=pin_hash, balance=balance,
                status=status, daily_withdrawal_limit=daily_limit,
                withdrawn_today=withdrawn, last_withdrawal_date=last_date or "",
                failed_attempts=failed,
            )

    def is_active(self) -> bool:
        """Check if the account is active (not locked)."""
        return self.status == "active"

    def can_withdraw(self, amount: float) -> tuple:
        """
        Check if a withdrawal of `amount` is permitted.
        Base implementation checks balance and daily limit.
        Subclasses may add additional rules.
        
        Returns:
            (allowed: bool, reason: str)
        """
        if not self.is_active():
            return False, "Account is locked. Please contact your bank."
        if amount > self.balance:
            return False, "Insufficient funds."
        if self.withdrawn_today + amount > self.daily_withdrawal_limit:
            remaining = self.daily_withdrawal_limit - self.withdrawn_today
            return False, (
                f"Daily withdrawal limit exceeded. "
                f"Remaining today: Rs.{remaining:,.0f}"
            )
        return True, ""

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__} "
            f"holder='{self.holder_name}' "
            f"card='***{self.card_number[-4:]}' "
            f"balance={self.balance:,.2f} "
            f"status={self.status}>"
        )


class SavingsAccount(Account):
    """
    Savings account — interest-bearing with a minimum balance rule.
    
    Withdrawals that would drop the balance below MIN_SAVINGS_BALANCE
    are rejected.
    """

    def __init__(self, **kwargs):
        super().__init__(account_type="savings", **kwargs)
        self.interest_rate = SAVINGS_INTEREST_RATE
        self.min_balance = MIN_SAVINGS_BALANCE

    def can_withdraw(self, amount: float) -> tuple:
        """Extend base check with minimum-balance enforcement."""
        allowed, reason = super().can_withdraw(amount)
        if not allowed:
            return allowed, reason

        if self.balance - amount < self.min_balance:
            return False, (
                f"Savings account requires a minimum balance of "
                f"Rs.{self.min_balance:,.0f}. "
                f"Maximum you can withdraw: Rs.{self.balance - self.min_balance:,.0f}"
            )
        return True, ""


class CurrentAccount(Account):
    """
    Current / Checking account — no minimum balance restriction.
    Can withdraw up to the full balance (subject to daily limit).
    """

    def __init__(self, **kwargs):
        super().__init__(account_type="current", **kwargs)
