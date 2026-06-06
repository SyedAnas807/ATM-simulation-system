"""
gui/screens/main_menu_screen.py — Main operation menu after login.

Displays 6 transaction options + logout. Shows the account holder's
name, masked card number, and a session timeout countdown.
"""

import tkinter as tk
from gui.theme import Colors, Fonts, Sizing
from gui.widgets import ATMButton, TimerBar, CardFrame
from security.utils import mask_card_number


class MainMenuScreen(tk.Frame):
    """
    Main menu with 6 operations + logout.
    
    Options:
        1. Check Balance
        2. Withdraw Cash
        3. Deposit Cash
        4. Fund Transfer
        5. Mini Statement
        6. Change PIN
        7. Logout
    """

    def __init__(self, parent, app, **kwargs):
        super().__init__(parent, bg=Colors.BG_DARK, **kwargs)
        self.app = app
        self._build_ui()

    def _build_ui(self):
        """Construct the main menu layout."""
        # ── Timer Bar ─────────────────────────
        self.timer = TimerBar(self)
        self.timer.pack(anchor="ne", padx=Sizing.PAD_LG, pady=(Sizing.PAD_SM, 0))

        # ── Welcome Header ───────────────────
        self.welcome_label = tk.Label(
            self, text="Welcome!",
            font=Fonts.TITLE_LG,
            bg=Colors.BG_DARK, fg=Colors.ACCENT,
        )
        self.welcome_label.pack(pady=(10, 2))

        self.card_info = tk.Label(
            self, text="",
            font=Fonts.BODY_MD,
            bg=Colors.BG_DARK, fg=Colors.TEXT_SECONDARY,
        )
        self.card_info.pack(pady=(0, 5))

        # ── Menu Title ───────────────────────
        menu_title = tk.Label(
            self, text="Select a Transaction",
            font=Fonts.TITLE_SM,
            bg=Colors.BG_DARK, fg=Colors.TEXT_PRIMARY,
        )
        menu_title.pack(pady=(5, 15))

        # ── Menu Grid ────────────────────────
        menu_frame = tk.Frame(self, bg=Colors.BG_DARK)
        menu_frame.pack(pady=5)

        # Define menu options with icons (emoji-like text)
        options = [
            ("1  Check Balance", "balance", 0, 0),
            ("2  Withdraw Cash", "withdraw", 0, 1),
            ("3  Deposit Cash", "deposit", 1, 0),
            ("4  Fund Transfer", "transfer", 1, 1),
            ("5  Mini Statement", "statement", 2, 0),
            ("6  Change PIN", "change_pin", 2, 1),
        ]

        for text, screen, row, col in options:
            btn = ATMButton(
                menu_frame, text=text,
                variant="menu",
                width=24, height=3,
                font=Fonts.MENU_BUTTON,
                command=lambda s=screen: self.app.show_screen(s),
            )
            btn.grid(
                row=row, column=col,
                padx=Sizing.PAD_MD, pady=Sizing.PAD_SM,
            )

        # ── Account Info Card ────────────────
        info_card = CardFrame(self)
        info_card.pack(pady=(20, 10), padx=120)
        inner = info_card.get_inner()

        self.account_type_label = tk.Label(
            inner, text="Account Type: ---",
            font=Fonts.BODY_MD,
            bg=Colors.BG_CARD, fg=Colors.TEXT_SECONDARY,
        )
        self.account_type_label.pack(side="left", padx=Sizing.PAD_LG, pady=Sizing.PAD_MD)

        self.balance_hint = tk.Label(
            inner, text="Balance: Rs.---",
            font=Fonts.BODY_MD,
            bg=Colors.BG_CARD, fg=Colors.TEXT_SECONDARY,
        )
        self.balance_hint.pack(side="right", padx=Sizing.PAD_LG, pady=Sizing.PAD_MD)

        # ── Logout Button ────────────────────
        logout_btn = ATMButton(
            self, text="LOGOUT & EJECT CARD",
            variant="danger", width=24,
            command=self._on_logout,
        )
        logout_btn.pack(pady=(15, 10))

    def on_show(self, **kwargs):
        """Refresh account info when screen is shown."""
        account = self.app.get_account()
        if account:
            self.welcome_label.config(
                text=f"Welcome, {account.holder_name}!"
            )
            masked = mask_card_number(account.card_number)
            self.card_info.config(text=f"Card: {masked}")
            self.account_type_label.config(
                text=f"Account: {account.account_type.title()}"
            )
            self.balance_hint.config(
                text=f"Balance: Rs.{account.balance:,.2f}"
            )

    def update_timer(self, seconds: int):
        """Update the session timeout countdown."""
        self.timer.update_time(seconds)

    def _on_logout(self):
        """Log out and return to welcome screen."""
        self.app.logout()
