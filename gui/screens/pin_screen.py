"""
gui/screens/pin_screen.py — PIN Entry screen with virtual keypad.

Displays a masked PIN entry field and a numeric keypad.
Handles authentication, attempt tracking, and lockout messaging.
"""

import tkinter as tk
from gui.theme import Colors, Fonts, Sizing
from gui.widgets import ATMButton, ATMKeypad, StatusLabel, CardFrame
from security.utils import mask_card_number


class PinScreen(tk.Frame):
    """
    PIN entry screen with keypad interface.
    
    Shows:
        - Masked card number
        - PIN dots display
        - Numeric keypad
        - Attempt counter
        
    Transitions:
        → MainMenuScreen (on successful auth)
        → WelcomeScreen (on cancel or lockout)
    """

    def __init__(self, parent, app, **kwargs):
        super().__init__(parent, bg=Colors.BG_DARK, **kwargs)
        self.app = app
        self.card_number = ""
        self.pin_digits = ""
        self.max_pin_len = 6
        self._build_ui()

    def _build_ui(self):
        """Construct the PIN entry layout."""
        # ── Header ────────────────────────────
        header = tk.Label(
            self, text="Enter Your PIN",
            font=Fonts.TITLE_LG,
            bg=Colors.BG_DARK, fg=Colors.ACCENT,
        )
        header.pack(pady=(15, 5))

        # ── Masked Card Display ──────────────
        self.card_label = tk.Label(
            self, text="Card: ******1234",
            font=Fonts.BODY_LG,
            bg=Colors.BG_DARK, fg=Colors.TEXT_SECONDARY,
        )
        self.card_label.pack(pady=(0, 10))

        # ── PIN Display Card ─────────────────
        pin_card = CardFrame(self)
        pin_card.pack(pady=(0, 10), padx=200)
        inner = pin_card.get_inner()

        self.pin_display = tk.Label(
            inner, text="",
            font=Fonts.PIN_DISPLAY,
            bg=Colors.BG_CARD, fg=Colors.ACCENT,
            width=12,
            anchor="center",
        )
        self.pin_display.pack(pady=Sizing.PAD_LG, padx=Sizing.PAD_XL)

        # PIN format hint
        self.hint_label = tk.Label(
            inner, text="Enter 4-6 digit PIN",
            font=Fonts.BODY_SM,
            bg=Colors.BG_CARD, fg=Colors.TEXT_SECONDARY,
        )
        self.hint_label.pack(pady=(0, Sizing.PAD_MD))

        # ── Keypad ───────────────────────────
        self.keypad = ATMKeypad(
            self,
            on_key=self._on_digit,
            on_clear=self._on_clear,
            on_backspace=self._on_backspace,
            on_enter=self._on_enter,
        )
        self.keypad.pack(pady=5)

        # ── Status Message ───────────────────
        self.status = StatusLabel(self)
        self.status.pack(pady=Sizing.PAD_SM)

        # ── Cancel Button ────────────────────
        cancel_btn = ATMButton(
            self, text="CANCEL",
            variant="secondary", width=14,
            command=self._on_cancel,
        )
        cancel_btn.pack(pady=(5, 15))

    def on_show(self, card_number: str = "", **kwargs):
        """Called when screen becomes visible. Resets PIN state."""
        self.card_number = card_number
        self.pin_digits = ""
        self._update_display()
        self.status.clear()
        
        # Show masked card number
        if card_number:
            masked = mask_card_number(card_number)
            self.card_label.config(text=f"Card: {masked}")

    def _on_digit(self, digit: str):
        """Handle keypad digit press."""
        if len(self.pin_digits) < self.max_pin_len:
            self.pin_digits += digit
            self._update_display()
            self.status.clear()

    def _on_clear(self):
        """Clear all PIN digits."""
        self.pin_digits = ""
        self._update_display()
        self.status.clear()

    def _on_backspace(self):
        """Remove the last PIN digit."""
        if self.pin_digits:
            self.pin_digits = self.pin_digits[:-1]
            self._update_display()

    def _on_enter(self):
        """Submit PIN for authentication."""
        if len(self.pin_digits) < 4:
            self.status.show_error("PIN must be at least 4 digits.")
            return

        success, message, account = self.app.auth.authenticate(
            self.card_number, self.pin_digits
        )

        if success:
            self.status.show_success(message)
            # Brief delay before showing main menu
            self.after(600, lambda: self.app.show_screen("main_menu"))
        else:
            self.status.show_error(message)
            self.pin_digits = ""
            self._update_display()
            
            # If account got locked, return to welcome after delay
            if "LOCKED" in message.upper():
                self.after(3000, self._on_cancel)

    def _update_display(self):
        """Update the PIN dots display."""
        dots = " ".join(["*"] * len(self.pin_digits))
        placeholders = " ".join(["_"] * (4 - len(self.pin_digits)))
        if len(self.pin_digits) < 4:
            self.pin_display.config(text=dots + " " + placeholders if dots else placeholders)
        else:
            self.pin_display.config(text=dots)

    def _on_cancel(self):
        """Return to welcome screen."""
        self.pin_digits = ""
        self.app.show_screen("welcome")
