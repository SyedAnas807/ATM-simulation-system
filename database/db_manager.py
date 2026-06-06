"""
database/db_manager.py — SQLite database access layer.

Handles all CRUD operations for accounts, transactions, and admin users.
All SQL queries use parameterized statements to prevent injection.
The database file is created automatically on first run.
"""

import sqlite3
from datetime import date
from config import DATABASE_PATH
from models.account import Account
from models.transaction import Transaction


class DatabaseManager:
    """
    Manages the SQLite database connection and provides methods
    for account, transaction, and admin data operations.
    """

    def __init__(self, db_path: str = DATABASE_PATH):
        """
        Initialize the database manager and create tables if needed.
        
        Args:
            db_path: Path to the SQLite database file.
        """
        self.db_path = db_path
        self._create_tables()

    def _connect(self) -> sqlite3.Connection:
        """Open a new database connection with row factory."""
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA journal_mode=WAL;")  # Better concurrency
        conn.execute("PRAGMA foreign_keys=ON;")
        return conn

    def _create_tables(self):
        """Create all required tables if they don't exist."""
        conn = self._connect()
        try:
            cursor = conn.cursor()

            # Accounts table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS accounts (
                    card_number         TEXT PRIMARY KEY,
                    holder_name         TEXT NOT NULL,
                    pin_hash            TEXT NOT NULL,
                    balance             REAL NOT NULL DEFAULT 0.0,
                    account_type        TEXT NOT NULL CHECK(account_type IN ('savings', 'current')),
                    status              TEXT NOT NULL DEFAULT 'active' CHECK(status IN ('active', 'locked')),
                    daily_withdrawal_limit REAL NOT NULL DEFAULT 50000.0,
                    withdrawn_today     REAL NOT NULL DEFAULT 0.0,
                    last_withdrawal_date TEXT DEFAULT '',
                    failed_attempts     INTEGER NOT NULL DEFAULT 0
                );
            """)

            # Transactions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS transactions (
                    id              INTEGER PRIMARY KEY AUTOINCREMENT,
                    card_number     TEXT NOT NULL,
                    timestamp       TEXT NOT NULL,
                    txn_type        TEXT NOT NULL,
                    amount          REAL NOT NULL DEFAULT 0.0,
                    balance_after   REAL NOT NULL DEFAULT 0.0,
                    recipient_card  TEXT,
                    status          TEXT NOT NULL DEFAULT 'success',
                    description     TEXT DEFAULT '',
                    FOREIGN KEY (card_number) REFERENCES accounts(card_number)
                );
            """)

            # Index for faster transaction lookups
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_txn_card 
                ON transactions(card_number);
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_txn_timestamp 
                ON transactions(timestamp);
            """)

            # Admin users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS admin_users (
                    username    TEXT PRIMARY KEY,
                    password_hash TEXT NOT NULL
                );
            """)

            # ATM state table (tracks machine cash)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS atm_state (
                    key     TEXT PRIMARY KEY,
                    value   REAL NOT NULL
                );
            """)

            conn.commit()
        finally:
            conn.close()

    # ──────────────────────────────────────────
    # Account Operations
    # ──────────────────────────────────────────

    def get_account(self, card_number: str):
        """
        Retrieve an account by card number.
        
        Args:
            card_number: The card number to look up.
            
        Returns:
            Account subclass instance or None if not found.
        """
        conn = self._connect()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT holder_name, card_number, pin_hash, balance,
                       account_type, status, daily_withdrawal_limit,
                       withdrawn_today, last_withdrawal_date, failed_attempts
                FROM accounts WHERE card_number = ?
            """, (card_number,))
            row = cursor.fetchone()
            if row:
                return Account.from_db_row(row)
            return None
        finally:
            conn.close()

    def account_exists(self, card_number: str) -> bool:
        """Check if an account with the given card number exists."""
        conn = self._connect()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT 1 FROM accounts WHERE card_number = ?",
                (card_number,)
            )
            return cursor.fetchone() is not None
        finally:
            conn.close()

    def update_balance(self, card_number: str, new_balance: float):
        """Update the balance for an account."""
        conn = self._connect()
        try:
            conn.execute(
                "UPDATE accounts SET balance = ? WHERE card_number = ?",
                (new_balance, card_number)
            )
            conn.commit()
        finally:
            conn.close()

    def update_pin(self, card_number: str, new_pin_hash: str):
        """Update the PIN hash for an account."""
        conn = self._connect()
        try:
            conn.execute(
                "UPDATE accounts SET pin_hash = ? WHERE card_number = ?",
                (new_pin_hash, card_number)
            )
            conn.commit()
        finally:
            conn.close()

    def update_failed_attempts(self, card_number: str, attempts: int):
        """Update the failed login attempt counter."""
        conn = self._connect()
        try:
            conn.execute(
                "UPDATE accounts SET failed_attempts = ? WHERE card_number = ?",
                (attempts, card_number)
            )
            conn.commit()
        finally:
            conn.close()

    def lock_account(self, card_number: str):
        """Lock an account (set status to 'locked')."""
        conn = self._connect()
        try:
            conn.execute(
                "UPDATE accounts SET status = 'locked', failed_attempts = ? WHERE card_number = ?",
                (0, card_number)
            )
            conn.commit()
        finally:
            conn.close()

    def unlock_account(self, card_number: str):
        """Unlock an account (set status to 'active', reset attempts)."""
        conn = self._connect()
        try:
            conn.execute(
                "UPDATE accounts SET status = 'active', failed_attempts = 0 WHERE card_number = ?",
                (card_number,)
            )
            conn.commit()
        finally:
            conn.close()

    def update_daily_withdrawal(self, card_number: str, amount: float):
        """
        Add to today's withdrawal total. Resets if the date has changed.
        
        Args:
            card_number: Card to update.
            amount: Amount being withdrawn now.
        """
        today = date.today().isoformat()
        conn = self._connect()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT withdrawn_today, last_withdrawal_date FROM accounts WHERE card_number = ?",
                (card_number,)
            )
            row = cursor.fetchone()
            if row:
                current_withdrawn, last_date = row
                # Reset daily total if it's a new day
                if last_date != today:
                    current_withdrawn = 0.0
                new_withdrawn = current_withdrawn + amount
                conn.execute(
                    "UPDATE accounts SET withdrawn_today = ?, last_withdrawal_date = ? WHERE card_number = ?",
                    (new_withdrawn, today, card_number)
                )
                conn.commit()
        finally:
            conn.close()

    def set_daily_limit(self, card_number: str, limit: float):
        """Set the daily withdrawal limit for an account (admin use)."""
        conn = self._connect()
        try:
            conn.execute(
                "UPDATE accounts SET daily_withdrawal_limit = ? WHERE card_number = ?",
                (limit, card_number)
            )
            conn.commit()
        finally:
            conn.close()

    def get_all_accounts(self) -> list:
        """
        Retrieve all accounts (for admin panel).
        
        Returns:
            List of Account subclass instances.
        """
        conn = self._connect()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT holder_name, card_number, pin_hash, balance,
                       account_type, status, daily_withdrawal_limit,
                       withdrawn_today, last_withdrawal_date, failed_attempts
                FROM accounts ORDER BY holder_name
            """)
            rows = cursor.fetchall()
            return [Account.from_db_row(row) for row in rows]
        finally:
            conn.close()

    def add_account(self, holder_name: str, card_number: str,
                    pin_hash: str, balance: float, account_type: str,
                    status: str = "active",
                    daily_limit: float = 50000.0) -> bool:
        """
        Insert a new account into the database.
        
        Returns:
            True if successful, False if card number already exists.
        """
        conn = self._connect()
        try:
            conn.execute("""
                INSERT INTO accounts 
                    (card_number, holder_name, pin_hash, balance, 
                     account_type, status, daily_withdrawal_limit)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (card_number, holder_name, pin_hash, balance,
                  account_type, status, daily_limit))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False  # Duplicate card number
        finally:
            conn.close()

    def delete_account(self, card_number: str) -> bool:
        """
        Remove an account and its transactions from the database.
        
        Returns:
            True if the account was deleted, False if not found.
        """
        conn = self._connect()
        try:
            # Delete transactions first (foreign key)
            conn.execute(
                "DELETE FROM transactions WHERE card_number = ?",
                (card_number,)
            )
            cursor = conn.execute(
                "DELETE FROM accounts WHERE card_number = ?",
                (card_number,)
            )
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()

    # ──────────────────────────────────────────
    # Transaction Operations
    # ──────────────────────────────────────────

    def add_transaction(self, txn: Transaction):
        """
        Log a transaction to the database.
        
        Args:
            txn: Transaction instance to persist.
        """
        conn = self._connect()
        try:
            conn.execute("""
                INSERT INTO transactions 
                    (card_number, timestamp, txn_type, amount,
                     balance_after, recipient_card, status, description)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (txn.card_number, txn.timestamp, txn.txn_type,
                  txn.amount, txn.balance_after, txn.recipient_card,
                  txn.status, txn.description))
            conn.commit()
        finally:
            conn.close()

    def get_recent_transactions(self, card_number: str, limit: int = 10) -> list:
        """
        Get the most recent transactions for an account.
        
        Args:
            card_number: Card number to query.
            limit: Maximum number of transactions to return.
            
        Returns:
            List of Transaction instances, newest first.
        """
        conn = self._connect()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, card_number, timestamp, txn_type, amount,
                       balance_after, recipient_card, status, description
                FROM transactions 
                WHERE card_number = ?
                ORDER BY timestamp DESC, id DESC
                LIMIT ?
            """, (card_number, limit))
            rows = cursor.fetchall()
            return [Transaction.from_db_row(row) for row in rows]
        finally:
            conn.close()

    def get_filtered_transactions(self, card_number: str = None,
                                   txn_type: str = None,
                                   date_from: str = None,
                                   date_to: str = None) -> list:
        """
        Get transactions with optional filters (admin use).
        
        Args:
            card_number: Filter by card number (optional).
            txn_type:    Filter by transaction type (optional).
            date_from:   Start date 'YYYY-MM-DD' (optional).
            date_to:     End date 'YYYY-MM-DD' (optional).
            
        Returns:
            List of Transaction instances matching filters.
        """
        conn = self._connect()
        try:
            query = """
                SELECT id, card_number, timestamp, txn_type, amount,
                       balance_after, recipient_card, status, description
                FROM transactions WHERE 1=1
            """
            params = []

            if card_number:
                query += " AND card_number = ?"
                params.append(card_number)
            if txn_type:
                query += " AND txn_type = ?"
                params.append(txn_type)
            if date_from:
                query += " AND timestamp >= ?"
                params.append(date_from)
            if date_to:
                query += " AND timestamp <= ?"
                params.append(date_to + " 23:59:59")

            query += " ORDER BY timestamp DESC, id DESC LIMIT 200"

            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [Transaction.from_db_row(row) for row in rows]
        finally:
            conn.close()

    # ──────────────────────────────────────────
    # Admin Operations
    # ──────────────────────────────────────────

    def get_admin(self, username: str) -> tuple:
        """
        Retrieve admin credentials.
        
        Returns:
            (username, password_hash) tuple or None.
        """
        conn = self._connect()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT username, password_hash FROM admin_users WHERE username = ?",
                (username,)
            )
            return cursor.fetchone()
        finally:
            conn.close()

    def add_admin(self, username: str, password_hash: str) -> bool:
        """Insert an admin user. Returns False if already exists."""
        conn = self._connect()
        try:
            conn.execute(
                "INSERT INTO admin_users (username, password_hash) VALUES (?, ?)",
                (username, password_hash)
            )
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()

    # ──────────────────────────────────────────
    # ATM State
    # ──────────────────────────────────────────

    def get_atm_cash(self) -> float:
        """Get the current cash available in the ATM machine."""
        conn = self._connect()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT value FROM atm_state WHERE key = 'cash_available'"
            )
            row = cursor.fetchone()
            return row[0] if row else 0.0
        finally:
            conn.close()

    def set_atm_cash(self, amount: float):
        """Set the ATM machine's cash level."""
        conn = self._connect()
        try:
            conn.execute("""
                INSERT OR REPLACE INTO atm_state (key, value) 
                VALUES ('cash_available', ?)
            """, (amount,))
            conn.commit()
        finally:
            conn.close()

    def reset_daily_withdrawals(self):
        """
        Reset withdrawn_today for all accounts (called when date changes).
        This is a maintenance operation.
        """
        today = date.today().isoformat()
        conn = self._connect()
        try:
            conn.execute(
                "UPDATE accounts SET withdrawn_today = 0.0 WHERE last_withdrawal_date != ?",
                (today,)
            )
            conn.commit()
        finally:
            conn.close()
