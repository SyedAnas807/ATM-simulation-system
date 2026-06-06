"""
gui/screens/transfer_screen.py — Fund Transfer screen.

Allows transfer to another account by card number with
recipient validation and confirmation step.
"""

import tkinter as tk
from gui.theme import Colors, Fonts, Sizing
from gui.widgets import ATMButton, StatusLabel, CardFrame, HeaderBar, TimerBar


class TransferScreen(tk.Frame):
    """Fund transfer screen with recipient card + amount entry."""

    def __init__(self, parent, app, **kwargs):
        super().__init__(parent, bg=Colors.BG_DARK, **kwargs)
        self.app = app
        self._pending_card = ""
        self._pending_amount = 0
        self._build_ui()

    def _build_ui(self):
        # Timer
        self.timer = TimerBar(self)
        self.timer.pack(anchor="ne", padx=Sizing.PAD_LG, pady=(Sizing.PAD_SM, 0))

        # Header
        header = HeaderBar(self, title="Fund Transfer", subtitle="Transfer funds to another account")
        header.pack(fill="x", pady=(10, 15))

        # Balance
        self.balance_label = tk.Label(
            self, text="Available: Rs. ---",
            font=Fonts.BODY_LG,
            bg=Colors.BG_DARK, fg=Colors.TEXT_SECONDARY,
        )
        self.balance_label.pack(pady=(5, 10))

        # Transfer form card
        form_card = CardFrame(self)
        form_card.pack(pady=5, padx=150)
        inner = form_card.get_inner()

        # Recipient card number
        tk.Label(
            inner, text="Recipient Card Number",
            font=Fonts.BODY_MD,
            bg=Colors.BG_CARD, fg=Colors.TEXT_SECONDARY,
        ).pack(pady=(Sizing.PAD_LG, Sizing.PAD_XS))

        self.card_entry = tk.Entry(
            inner,
            font=Fonts.TITLE_SM,
            bg=Colors.BG_INPUT,
            fg=Colors.TEXT_PRIMARY,
            insertbackground=Colors.ACCENT,
            bd=0, width=22, justify="center",
            highlightthickness=2,
            highlightcolor=Colors.ACCENT,
            highlightbackground=Colors.BORDER,
        )
        self.card_entry.pack(pady=Sizing.PAD_SM, ipady=6)

        # Amount
        tk.Label(
            inner, text="Transfer Amount",
            font=Fonts.BODY_MD,
            bg=Colors.BG_CARD, fg=Colors.TEXT_SECONDARY,
        ).pack(pady=(Sizing.PAD_MD, Sizing.PAD_XS))

        amt_row = tk.Frame(inner, bg=Colors.BG_CARD)
        amt_row.pack(pady=Sizing.PAD_SM)

        tk.Label(
            amt_row, text="Rs.",
            font=Fonts.TITLE_SM,
            bg=Colors.BG_CARD, fg=Colors.ACCENT,
        ).pack(side="left", padx=(0, 8))

        self.amount_entry = tk.Entry(
            amt_row,
            font=Fonts.TITLE_SM,
            bg=Colors.BG_INPUT,
            fg=Colors.TEXT_PRIMARY,
            insertbackground=Colors.ACCENT,
            bd=0, width=16,
            highlightthickness=2,
            highlightcolor=Colors.ACCENT,
            highlightbackground=Colors.BORDER,
        )
        self.amount_entry.pack(side="left", ipady=6)

        # Transfer button
        ATMButton(
            inner, text="TRANSFER",
            variant="primary", width=20,
            command=self._on_transfer,
        ).pack(pady=(Sizing.PAD_LG, Sizing.PAD_XL))

        # Status
        self.status = StatusLabel(self)
        self.status.pack(pady=Sizing.PAD_SM)

        # Confirmation frame (hidden)
        self.confirm_frame = tk.Frame(self, bg=Colors.BG_DARK)
        self.confirm_label = tk.Label(
            self.confirm_frame, text="",
            font=Fonts.BODY_LG,
            bg=Colors.BG_DARK, fg=Colors.WARNING,
            wraplength=500, justify="center",
        )
        self.confirm_label.pack(pady=5)

        confirm_btns = tk.Frame(self.confirm_frame, bg=Colors.BG_DARK)
        confirm_btns.pack()
        ATMButton(
            confirm_btns, text="CONFIRM",
            variant="primary", width=12,
            command=self._confirm_transfer,
        ).pack(side="left", padx=8)
        ATMButton(
            confirm_btns, text="CANCEL",
            variant="danger", width=12,
            command=self._cancel,
        ).pack(side="left", padx=8)

        # Back
        self.back_btn = ATMButton(
            self, text="BACK TO MENU",
            variant="secondary", width=16,
            command=lambda: self.app.show_screen("main_menu"),
        )
        self.back_btn.pack(pady=(15, 10))

    def on_show(self, **kwargs):
        self.card_entry.delete(0, tk.END)
        self.amount_entry.delete(0, tk.END)
        self.status.clear()
        self.confirm_frame.pack_forget()
        self.back_btn.pack(pady=(15, 10))

        account = self.app.get_account()
        if account:
            self.balance_label.config(
                text=f"Available: Rs. {account.balance:,.2f}"
            )
        self.card_entry.focus_set()

    def update_timer(self, seconds: int):
        self.timer.update_time(seconds)

    def _on_transfer(self):
        from security.utils import validate_card_number, validate_amount

        # Validate recipient card
        card = self.card_entry.get().strip()
        valid, error = validate_card_number(card)
        if not valid:
            self.status.show_error(f"Recipient: {error}")
            return

        # Validate amount
        valid, result = validate_amount(self.amount_entry.get())
        if not valid:
            self.status.show_error(result)
            return

        # Check recipient exists
        recipient = self.app.db.get_account(card)
        if recipient is None:
            self.status.show_error("Recipient card number not found.")
            return

        self._pending_card = card
        self._pending_amount = result

        self.confirm_label.config(
            text=f"Transfer Rs. {result:,.0f} to {recipient.holder_name} (***{card[-4:]})?"
        )
        self.back_btn.pack_forget()
        self.confirm_frame.pack(pady=5)
        self.status.clear()

    def _confirm_transfer(self):
        account = self.app.get_account()
        if not account:
            self.status.show_error("Session error.")
            return

        success, message, txn = self.app.atm.transfer(
            account, self._pending_card, self._pending_amount
        )

        self.confirm_frame.pack_forget()
        self.back_btn.pack(pady=(15, 10))

        if success:
            self.status.show_success(message)
            account = self.app.get_account()
            if account:
                self.balance_label.config(
                    text=f"Available: Rs. {account.balance:,.2f}"
                )
            if txn:
                self.after(1000, lambda: self.app.show_screen("receipt", transaction=txn))
        else:
            self.status.show_error(message)

    def _cancel(self):
        self.confirm_frame.pack_forget()
        self.back_btn.pack(pady=(15, 10))
        self.status.clear()
