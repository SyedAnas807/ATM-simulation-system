"""
gui/screens/withdraw_screen.py — Cash Withdrawal screen.

Allows denomination selection or custom amount entry.
Shows confirmation before processing. Enforces all withdrawal rules.
"""

import tkinter as tk
from gui.theme import Colors, Fonts, Sizing
from gui.widgets import ATMButton, StatusLabel, CardFrame, HeaderBar, TimerBar
from config import DENOMINATIONS


class WithdrawScreen(tk.Frame):
    """Cash withdrawal with denomination buttons and custom amount."""

    def __init__(self, parent, app, **kwargs):
        super().__init__(parent, bg=Colors.BG_DARK, **kwargs)
        self.app = app
        self.selected_amount = 0
        self._confirming = False
        self._build_ui()

    def _build_ui(self):
        """Construct the withdrawal screen layout."""
        # Timer
        self.timer = TimerBar(self)
        self.timer.pack(anchor="ne", padx=Sizing.PAD_LG, pady=(Sizing.PAD_SM, 0))

        # Header
        header = HeaderBar(self, title="Withdraw Cash", subtitle="Select amount or enter custom amount")
        header.pack(fill="x", pady=(10, 15))

        # Balance display
        self.balance_label = tk.Label(
            self, text="Available: Rs. ---",
            font=Fonts.BODY_LG,
            bg=Colors.BG_DARK, fg=Colors.TEXT_SECONDARY,
        )
        self.balance_label.pack(pady=(5, 10))

        # ── Denomination Buttons ─────────────
        denom_frame = tk.Frame(self, bg=Colors.BG_DARK)
        denom_frame.pack(pady=5)

        tk.Label(
            denom_frame, text="Quick Amounts",
            font=Fonts.TITLE_SM,
            bg=Colors.BG_DARK, fg=Colors.TEXT_PRIMARY,
        ).grid(row=0, column=0, columnspan=3, pady=(0, 10))

        for idx, amount in enumerate(DENOMINATIONS):
            row = (idx // 3) + 1
            col = idx % 3
            btn = ATMButton(
                denom_frame,
                text=f"Rs. {amount:,}",
                variant="menu",
                width=14, height=2,
                font=Fonts.BUTTON,
                command=lambda a=amount: self._select_amount(a),
            )
            btn.grid(row=row, column=col, padx=6, pady=4)

        # ── Custom Amount Entry ──────────────
        custom_frame = CardFrame(self)
        custom_frame.pack(pady=15, padx=200)
        inner = custom_frame.get_inner()

        tk.Label(
            inner, text="Or Enter Custom Amount",
            font=Fonts.BODY_MD,
            bg=Colors.BG_CARD, fg=Colors.TEXT_SECONDARY,
        ).pack(pady=(Sizing.PAD_MD, Sizing.PAD_SM))

        entry_row = tk.Frame(inner, bg=Colors.BG_CARD)
        entry_row.pack(pady=(0, Sizing.PAD_MD))

        tk.Label(
            entry_row, text="Rs.",
            font=Fonts.TITLE_SM,
            bg=Colors.BG_CARD, fg=Colors.ACCENT,
        ).pack(side="left", padx=(Sizing.PAD_LG, 5))

        self.amount_entry = tk.Entry(
            entry_row,
            font=Fonts.TITLE_SM,
            bg=Colors.BG_INPUT,
            fg=Colors.TEXT_PRIMARY,
            insertbackground=Colors.ACCENT,
            bd=0, width=15,
            highlightthickness=2,
            highlightcolor=Colors.ACCENT,
            highlightbackground=Colors.BORDER,
        )
        self.amount_entry.pack(side="left", ipady=6)
        self.amount_entry.bind("<Return>", lambda e: self._custom_amount())

        ATMButton(
            entry_row, text="GO",
            variant="primary", width=6, height=1,
            command=self._custom_amount,
        ).pack(side="left", padx=(10, Sizing.PAD_LG))

        # ── Status & Confirmation ────────────
        self.status = StatusLabel(self)
        self.status.pack(pady=Sizing.PAD_SM)

        # Confirmation frame (hidden by default)
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
            command=self._confirm_withdraw,
        ).pack(side="left", padx=8)

        ATMButton(
            confirm_btns, text="CANCEL",
            variant="danger", width=12,
            command=self._cancel_confirm,
        ).pack(side="left", padx=8)

        # ── Back Button ──────────────────────
        self.back_btn = ATMButton(
            self, text="BACK TO MENU",
            variant="secondary", width=16,
            command=lambda: self.app.show_screen("main_menu"),
        )
        self.back_btn.pack(pady=(10, 10))

    def on_show(self, **kwargs):
        """Reset state and show current balance."""
        self.selected_amount = 0
        self._confirming = False
        self.amount_entry.delete(0, tk.END)
        self.status.clear()
        self.confirm_frame.pack_forget()
        self.back_btn.pack(pady=(10, 10))

        account = self.app.get_account()
        if account:
            self.balance_label.config(
                text=f"Available: Rs. {account.balance:,.2f}"
            )

    def update_timer(self, seconds: int):
        self.timer.update_time(seconds)

    def _select_amount(self, amount: int):
        """Select a preset denomination amount."""
        self.selected_amount = amount
        self.amount_entry.delete(0, tk.END)
        self._show_confirmation(amount)

    def _custom_amount(self):
        """Validate and select custom amount."""
        from security.utils import validate_amount
        valid, result = validate_amount(self.amount_entry.get())
        if not valid:
            self.status.show_error(result)
            return
        
        self.selected_amount = result
        self._show_confirmation(result)

    def _show_confirmation(self, amount):
        """Show confirmation prompt before withdrawal."""
        self._confirming = True
        self.confirm_label.config(
            text=f"Withdraw Rs. {amount:,.0f}?"
        )
        self.back_btn.pack_forget()
        self.confirm_frame.pack(pady=5)
        self.status.clear()

    def _confirm_withdraw(self):
        """Execute the withdrawal after confirmation."""
        account = self.app.get_account()
        if not account:
            self.status.show_error("Session error. Please login again.")
            return

        success, message, txn = self.app.atm.withdraw(account, self.selected_amount)

        self.confirm_frame.pack_forget()
        self.back_btn.pack(pady=(10, 10))
        self._confirming = False

        if success:
            self.status.show_success(message)
            # Update balance display
            account = self.app.get_account()
            if account:
                self.balance_label.config(
                    text=f"Available: Rs. {account.balance:,.2f}"
                )
            # Show receipt after delay
            if txn:
                self.after(1000, lambda: self.app.show_screen("receipt", transaction=txn))
        else:
            self.status.show_error(message)

    def _cancel_confirm(self):
        """Cancel the confirmation prompt."""
        self.confirm_frame.pack_forget()
        self.back_btn.pack(pady=(10, 10))
        self._confirming = False
        self.status.clear()
