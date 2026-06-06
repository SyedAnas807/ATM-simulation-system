"""
models/transaction.py — Transaction data model.

Represents a single ATM transaction (withdrawal, deposit, transfer, etc.)
with all metadata needed for logging and mini-statement display.
"""

from datetime import datetime


class Transaction:
    """
    Immutable record of a single ATM transaction.
    
    Attributes:
        id              (int|None): Auto-assigned database row ID.
        card_number     (str):      Card that initiated the transaction.
        timestamp       (str):      ISO-format datetime string.
        txn_type        (str):      One of: 'withdrawal', 'deposit',
                                    'transfer_out', 'transfer_in',
                                    'pin_change', 'balance_inquiry'.
        amount          (float):    Monetary value (0 for non-monetary ops).
        balance_after   (float):    Account balance after this transaction.
        recipient_card  (str|None): Destination card for transfers.
        status          (str):      'success' or 'failed'.
        description     (str):      Human-readable summary.
    """

    def __init__(self, card_number: str, txn_type: str,
                 amount: float = 0.0, balance_after: float = 0.0,
                 recipient_card: str = None, status: str = "success",
                 description: str = "", timestamp: str = None,
                 txn_id: int = None):
        self.id = txn_id
        self.card_number = card_number
        self.timestamp = timestamp or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.txn_type = txn_type
        self.amount = amount
        self.balance_after = balance_after
        self.recipient_card = recipient_card
        self.status = status
        self.description = description

    @classmethod
    def from_db_row(cls, row: tuple):
        """
        Create a Transaction from a database row tuple.
        
        Expected order:
            id, card_number, timestamp, txn_type, amount,
            balance_after, recipient_card, status, description
        """
        return cls(
            txn_id=row[0],
            card_number=row[1],
            timestamp=row[2],
            txn_type=row[3],
            amount=row[4],
            balance_after=row[5],
            recipient_card=row[6],
            status=row[7],
            description=row[8],
        )

    def format_for_statement(self) -> dict:
        """
        Return a dictionary formatted for mini-statement display.
        """
        return {
            "date": self.timestamp,
            "type": self.txn_type.replace("_", " ").title(),
            "amount": self.amount,
            "balance": self.balance_after,
            "status": self.status,
        }

    def format_receipt(self) -> str:
        """
        Generate a formatted text receipt for this transaction.
        """
        lines = [
            "═" * 40,
            "         ATM TRANSACTION RECEIPT",
            "═" * 40,
            f"  Date    : {self.timestamp}",
            f"  Type    : {self.txn_type.replace('_', ' ').title()}",
            f"  Amount  : Rs.{self.amount:,.2f}",
            f"  Balance : Rs.{self.balance_after:,.2f}",
            f"  Status  : {self.status.upper()}",
        ]
        if self.recipient_card:
            lines.append(f"  To Card : ***{self.recipient_card[-4:]}")
        if self.description:
            lines.append(f"  Note    : {self.description}")
        lines.append("═" * 40)
        lines.append("  Thank you for using our ATM!")
        lines.append("═" * 40)
        return "\n".join(lines)

    def __repr__(self) -> str:
        return (
            f"<Transaction #{self.id} {self.txn_type} "
            f"Rs.{self.amount:,.2f} [{self.status}]>"
        )
