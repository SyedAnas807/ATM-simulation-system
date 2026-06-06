"""
gui/screens/balance_screen.py — Check Balance screen.

Displays the current account balance with currency formatting.
"""

import tkinter as tk
from gui.theme import Colors, Fonts, Sizing
from gui.widgets import ATMButton, StatusLabel, CardFrame, HeaderBar, TimerBar


class BalanceScreen(tk.Frame):
    """Balance inquiry screen showing current balance."""

    def __init__(self, parent, app, **kwargs):
        super().__init__(parent, bg=Colors.BG_DARK, **kwargs)
        self.app = app
        self._build_ui()

    def _build_ui(self):
        """Construct the balance screen layout."""
        # Timer
        self.timer = TimerBar(self)
        self.timer.pack(anchor="ne", padx=Sizing.PAD_LG, pady=(Sizing.PAD_SM, 0))

        # Header
        header = HeaderBar(self, title="Account Balance", subtitle="Your current available balance")
        header.pack(fill="x", pady=(10, 30))

        # Balance Card
        balance_card = CardFrame(self)
        balance_card.pack(pady=20, padx=100)
        inner = balance_card.get_inner()

        tk.Label(
            inner, text="Available Balance",
            font=Fonts.BODY_LG,
            bg=Colors.BG_CARD, fg=Colors.TEXT_SECONDARY,
        ).pack(pady=(Sizing.PAD_XL, Sizing.PAD_SM))

        self.balance_label = tk.Label(
            inner, text="Rs. 0.00",
            font=Fonts.BALANCE,
            bg=Colors.BG_CARD, fg=Colors.ACCENT,
        )
        self.balance_label.pack(pady=Sizing.PAD_MD)

        self.account_type_label = tk.Label(
            inner, text="Savings Account",
            font=Fonts.BODY_MD,
            bg=Colors.BG_CARD, fg=Colors.TEXT_SECONDARY,
        )
        self.account_type_label.pack(pady=(0, Sizing.PAD_XL))

        # Status
        self.status = StatusLabel(self)
        self.status.pack(pady=Sizing.PAD_MD)

        # Buttons
        btn_frame = tk.Frame(self, bg=Colors.BG_DARK)
        btn_frame.pack(pady=Sizing.PAD_LG)

        ATMButton(
            btn_frame, text="PRINT RECEIPT",
            variant="secondary", width=16,
            command=self._print_receipt,
        ).pack(side="left", padx=Sizing.PAD_SM)

        ATMButton(
            btn_frame, text="BACK TO MENU",
            variant="primary", width=16,
            command=lambda: self.app.show_screen("main_menu"),
        ).pack(side="left", padx=Sizing.PAD_SM)

    def on_show(self, **kwargs):
        """Query balance and display it."""
        account = self.app.get_account()
        if account:
            success, balance, message = self.app.atm.check_balance(account)
            if success:
                self.balance_label.config(text=f"Rs. {balance:,.2f}")
                self.account_type_label.config(
                    text=f"{account.account_type.title()} Account"
                )
                self.status.clear()
            else:
                self.status.show_error(message)

    def update_timer(self, seconds: int):
        self.timer.update_time(seconds)

    def _print_receipt(self):
        """Show the balance as a receipt."""
        account = self.app.get_account()
        if account:
            from models.transaction import Transaction
            txn = Transaction(
                card_number=account.card_number,
                txn_type="balance_inquiry",
                amount=0.0,
                balance_after=account.balance,
                description="Balance inquiry",
            )
            self.app.show_screen("receipt", transaction=txn)
