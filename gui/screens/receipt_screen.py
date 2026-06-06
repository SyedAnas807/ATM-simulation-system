"""
gui/screens/receipt_screen.py — Transaction Receipt screen.

Displays a formatted receipt after each transaction with
all relevant details. Offers 'Done' to return to menu.
"""

import tkinter as tk
from gui.theme import Colors, Fonts, Sizing
from gui.widgets import ATMButton, CardFrame, HeaderBar


class ReceiptScreen(tk.Frame):
    """Formatted transaction receipt display."""

    def __init__(self, parent, app, **kwargs):
        super().__init__(parent, bg=Colors.BG_DARK, **kwargs)
        self.app = app
        self._build_ui()

    def _build_ui(self):
        # Header
        header = HeaderBar(self, title="Transaction Receipt", subtitle="")
        header.pack(fill="x", pady=(30, 20))

        # Receipt card
        receipt_card = CardFrame(self)
        receipt_card.pack(pady=10, padx=150)
        inner = receipt_card.get_inner()

        self.receipt_text = tk.Text(
            inner,
            font=Fonts.RECEIPT,
            bg=Colors.BG_CARD,
            fg=Colors.ACCENT,
            width=44, height=16,
            bd=0,
            highlightthickness=0,
            state="disabled",
            wrap="word",
        )
        self.receipt_text.pack(padx=Sizing.PAD_LG, pady=Sizing.PAD_LG)

        # Buttons
        btn_frame = tk.Frame(self, bg=Colors.BG_DARK)
        btn_frame.pack(pady=Sizing.PAD_LG)

        ATMButton(
            btn_frame, text="NEW TRANSACTION",
            variant="primary", width=18,
            command=lambda: self.app.show_screen("main_menu"),
        ).pack(side="left", padx=Sizing.PAD_SM)

        ATMButton(
            btn_frame, text="LOGOUT",
            variant="danger", width=12,
            command=self.app.logout,
        ).pack(side="left", padx=Sizing.PAD_SM)

    def on_show(self, transaction=None, **kwargs):
        """Display the receipt for the given transaction."""
        self.receipt_text.config(state="normal")
        self.receipt_text.delete("1.0", tk.END)

        if transaction:
            receipt = transaction.format_receipt()
            self.receipt_text.insert("1.0", receipt)
        else:
            self.receipt_text.insert("1.0", "No transaction data available.")

        self.receipt_text.config(state="disabled")

    def update_timer(self, seconds: int):
        pass  # No timer needed on receipt screen
