"""
gui/screens/deposit_screen.py — Cash Deposit screen.

Allows the user to enter a deposit amount with confirmation.
"""

import tkinter as tk
from gui.theme import Colors, Fonts, Sizing
from gui.widgets import ATMButton, StatusLabel, CardFrame, HeaderBar, TimerBar


class DepositScreen(tk.Frame):
    """Cash deposit screen with amount entry and confirmation."""

    def __init__(self, parent, app, **kwargs):
        super().__init__(parent, bg=Colors.BG_DARK, **kwargs)
        self.app = app
        self._build_ui()

    def _build_ui(self):
        # Timer
        self.timer = TimerBar(self)
        self.timer.pack(anchor="ne", padx=Sizing.PAD_LG, pady=(Sizing.PAD_SM, 0))

        # Header
        header = HeaderBar(self, title="Deposit Cash", subtitle="Enter the amount to deposit")
        header.pack(fill="x", pady=(10, 20))

        # Balance display
        self.balance_label = tk.Label(
            self, text="Current Balance: Rs. ---",
            font=Fonts.BODY_LG,
            bg=Colors.BG_DARK, fg=Colors.TEXT_SECONDARY,
        )
        self.balance_label.pack(pady=(10, 20))

        # Amount entry card
        deposit_card = CardFrame(self)
        deposit_card.pack(pady=10, padx=180)
        inner = deposit_card.get_inner()

        tk.Label(
            inner, text="Deposit Amount",
            font=Fonts.TITLE_SM,
            bg=Colors.BG_CARD, fg=Colors.ACCENT,
        ).pack(pady=(Sizing.PAD_XL, Sizing.PAD_MD))

        entry_row = tk.Frame(inner, bg=Colors.BG_CARD)
        entry_row.pack(pady=Sizing.PAD_SM)

        tk.Label(
            entry_row, text="Rs.",
            font=Fonts.TITLE_MD,
            bg=Colors.BG_CARD, fg=Colors.ACCENT,
        ).pack(side="left", padx=(Sizing.PAD_LG, 8))

        self.amount_entry = tk.Entry(
            entry_row,
            font=Fonts.TITLE_MD,
            bg=Colors.BG_INPUT,
            fg=Colors.TEXT_PRIMARY,
            insertbackground=Colors.ACCENT,
            bd=0, width=18,
            highlightthickness=2,
            highlightcolor=Colors.ACCENT,
            highlightbackground=Colors.BORDER,
        )
        self.amount_entry.pack(side="left", ipady=8, padx=(0, Sizing.PAD_LG))
        self.amount_entry.bind("<Return>", lambda e: self._on_deposit())

        # Deposit button
        ATMButton(
            inner, text="DEPOSIT",
            variant="primary", width=20,
            command=self._on_deposit,
        ).pack(pady=(Sizing.PAD_LG, Sizing.PAD_XL))

        # Status
        self.status = StatusLabel(self)
        self.status.pack(pady=Sizing.PAD_MD)

        # Confirmation frame (hidden)
        self.confirm_frame = tk.Frame(self, bg=Colors.BG_DARK)
        self.confirm_label = tk.Label(
            self.confirm_frame, text="",
            font=Fonts.TITLE_SM,
            bg=Colors.BG_DARK, fg=Colors.WARNING,
        )
        self.confirm_label.pack(pady=5)

        confirm_btns = tk.Frame(self.confirm_frame, bg=Colors.BG_DARK)
        confirm_btns.pack()
        ATMButton(
            confirm_btns, text="CONFIRM",
            variant="primary", width=12,
            command=self._confirm_deposit,
        ).pack(side="left", padx=8)
        ATMButton(
            confirm_btns, text="CANCEL",
            variant="danger", width=12,
            command=self._cancel,
        ).pack(side="left", padx=8)

        # Back button
        self.back_btn = ATMButton(
            self, text="BACK TO MENU",
            variant="secondary", width=16,
            command=lambda: self.app.show_screen("main_menu"),
        )
        self.back_btn.pack(pady=(20, 10))

    def on_show(self, **kwargs):
        self.amount_entry.delete(0, tk.END)
        self.status.clear()
        self.confirm_frame.pack_forget()
        self.back_btn.pack(pady=(20, 10))
        self._pending_amount = 0

        account = self.app.get_account()
        if account:
            self.balance_label.config(
                text=f"Current Balance: Rs. {account.balance:,.2f}"
            )
        self.amount_entry.focus_set()

    def update_timer(self, seconds: int):
        self.timer.update_time(seconds)

    def _on_deposit(self):
        from security.utils import validate_amount
        valid, result = validate_amount(self.amount_entry.get())
        if not valid:
            self.status.show_error(result)
            return

        self._pending_amount = result
        self.confirm_label.config(text=f"Deposit Rs. {result:,.0f}?")
        self.back_btn.pack_forget()
        self.confirm_frame.pack(pady=5)
        self.status.clear()

    def _confirm_deposit(self):
        account = self.app.get_account()
        if not account:
            self.status.show_error("Session error.")
            return

        success, message, txn = self.app.atm.deposit(account, self._pending_amount)

        self.confirm_frame.pack_forget()
        self.back_btn.pack(pady=(20, 10))

        if success:
            self.status.show_success(message)
            account = self.app.get_account()
            if account:
                self.balance_label.config(
                    text=f"Current Balance: Rs. {account.balance:,.2f}"
                )
            if txn:
                self.after(1000, lambda: self.app.show_screen("receipt", transaction=txn))
        else:
            self.status.show_error(message)

    def _cancel(self):
        self.confirm_frame.pack_forget()
        self.back_btn.pack(pady=(20, 10))
        self.status.clear()
