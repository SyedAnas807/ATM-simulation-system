"""
gui/screens/statement_screen.py — Mini Statement screen.

Displays the last 10 transactions in a scrollable table format
with date, type, amount, balance, and status columns.
"""

import tkinter as tk
from gui.theme import Colors, Fonts, Sizing
from gui.widgets import ATMButton, HeaderBar, TimerBar, CardFrame
from config import MINI_STATEMENT_LIMIT


class StatementScreen(tk.Frame):
    """Mini statement showing recent transactions in a table."""

    def __init__(self, parent, app, **kwargs):
        super().__init__(parent, bg=Colors.BG_DARK, **kwargs)
        self.app = app
        self._build_ui()

    def _build_ui(self):
        # Timer
        self.timer = TimerBar(self)
        self.timer.pack(anchor="ne", padx=Sizing.PAD_LG, pady=(Sizing.PAD_SM, 0))

        # Header
        header = HeaderBar(
            self, title="Mini Statement",
            subtitle=f"Last {MINI_STATEMENT_LIMIT} transactions"
        )
        header.pack(fill="x", pady=(10, 15))

        # ── Table Header ─────────────────────
        table_frame = tk.Frame(self, bg=Colors.BG_DARK)
        table_frame.pack(fill="both", expand=True, padx=30, pady=5)

        # Column headers
        header_frame = tk.Frame(table_frame, bg=Colors.BG_HEADER)
        header_frame.pack(fill="x")

        headers = [
            ("Date/Time", 18),
            ("Type", 14),
            ("Amount", 12),
            ("Balance", 12),
            ("Status", 8),
        ]

        for text, width in headers:
            tk.Label(
                header_frame, text=text,
                font=Fonts.BODY_MD,
                bg=Colors.BG_HEADER, fg=Colors.ACCENT,
                width=width, anchor="w",
            ).pack(side="left", padx=4, pady=6)

        # Scrollable transaction list
        scroll_frame = tk.Frame(table_frame, bg=Colors.BG_DARK)
        scroll_frame.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(
            scroll_frame, bg=Colors.BG_DARK,
            highlightthickness=0,
        )
        scrollbar = tk.Scrollbar(
            scroll_frame, orient="vertical",
            command=self.canvas.yview,
        )
        self.scrollable = tk.Frame(self.canvas, bg=Colors.BG_DARK)

        self.scrollable.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Mouse wheel scrolling
        self.canvas.bind_all("<MouseWheel>",
            lambda e: self.canvas.yview_scroll(int(-1*(e.delta/120)), "units")
        )

        # No transactions label
        self.empty_label = tk.Label(
            self, text="",
            font=Fonts.BODY_LG,
            bg=Colors.BG_DARK, fg=Colors.TEXT_SECONDARY,
        )

        # Back button
        ATMButton(
            self, text="BACK TO MENU",
            variant="primary", width=16,
            command=lambda: self.app.show_screen("main_menu"),
        ).pack(pady=(10, 15))

    def on_show(self, **kwargs):
        """Load and display recent transactions."""
        # Clear existing rows
        for widget in self.scrollable.winfo_children():
            widget.destroy()
        self.empty_label.pack_forget()

        account = self.app.get_account()
        if not account:
            return

        transactions = self.app.atm.get_mini_statement(
            account, MINI_STATEMENT_LIMIT
        )

        if not transactions:
            self.empty_label.config(text="No transactions found.")
            self.empty_label.pack(pady=20)
            return

        # Add transaction rows
        for idx, txn in enumerate(transactions):
            bg = Colors.BG_CARD if idx % 2 == 0 else Colors.BG_DARK
            row = tk.Frame(self.scrollable, bg=bg)
            row.pack(fill="x")

            # Date
            tk.Label(
                row, text=txn.timestamp,
                font=Fonts.BODY_SM, bg=bg, fg=Colors.TEXT_PRIMARY,
                width=18, anchor="w",
            ).pack(side="left", padx=4, pady=4)

            # Type
            txn_type = txn.txn_type.replace("_", " ").title()
            tk.Label(
                row, text=txn_type,
                font=Fonts.BODY_SM, bg=bg, fg=Colors.TEXT_PRIMARY,
                width=14, anchor="w",
            ).pack(side="left", padx=4, pady=4)

            # Amount
            amount_text = f"Rs.{txn.amount:,.0f}" if txn.amount > 0 else "-"
            amount_color = Colors.ERROR if "out" in txn.txn_type or txn.txn_type == "withdrawal" else Colors.SUCCESS
            tk.Label(
                row, text=amount_text,
                font=Fonts.BODY_SM, bg=bg, fg=amount_color,
                width=12, anchor="w",
            ).pack(side="left", padx=4, pady=4)

            # Balance after
            tk.Label(
                row, text=f"Rs.{txn.balance_after:,.0f}",
                font=Fonts.BODY_SM, bg=bg, fg=Colors.TEXT_PRIMARY,
                width=12, anchor="w",
            ).pack(side="left", padx=4, pady=4)

            # Status
            status_color = Colors.SUCCESS if txn.status == "success" else Colors.ERROR
            tk.Label(
                row, text=txn.status.title(),
                font=Fonts.BODY_SM, bg=bg, fg=status_color,
                width=8, anchor="w",
            ).pack(side="left", padx=4, pady=4)

    def update_timer(self, seconds: int):
        self.timer.update_time(seconds)
