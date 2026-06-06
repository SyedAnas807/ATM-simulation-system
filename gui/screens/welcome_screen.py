"""
gui/screens/welcome_screen.py — ATM Welcome / Card Insertion screen.

Shows the ASCII art ATM banner and prompts the user to enter 
their card number. Includes a card-slot animation effect and
an admin access button.
"""

import tkinter as tk
from gui.theme import Colors, Fonts, Sizing, ATM_BANNER_SMALL
from gui.widgets import ATMButton, StatusLabel, CardFrame


class WelcomeScreen(tk.Frame):
    """
    Initial screen — displays ATM branding and card number entry.
    
    Transitions:
        → PinScreen (on valid card entry)
        → AdminScreen (on admin button click)
    """

    def __init__(self, parent, app, **kwargs):
        super().__init__(parent, bg=Colors.BG_DARK, **kwargs)
        self.app = app
        self._build_ui()

    def _build_ui(self):
        """Construct the welcome screen layout."""
        # ── ATM Banner ────────────────────────
        banner_frame = tk.Frame(self, bg=Colors.BG_DARK)
        banner_frame.pack(pady=(30, 10))

        banner_label = tk.Label(
            banner_frame,
            text=ATM_BANNER_SMALL,
            font=Fonts.BANNER,
            bg=Colors.BG_DARK,
            fg=Colors.ACCENT,
            justify="center",
        )
        banner_label.pack()

        # ── Welcome Message ───────────────────
        welcome_label = tk.Label(
            self, text="Welcome to ATM Services",
            font=Fonts.TITLE_LG,
            bg=Colors.BG_DARK, fg=Colors.TEXT_PRIMARY,
        )
        welcome_label.pack(pady=(10, 5))

        sub_label = tk.Label(
            self, text="Please insert your card to begin",
            font=Fonts.BODY_LG,
            bg=Colors.BG_DARK, fg=Colors.TEXT_SECONDARY,
        )
        sub_label.pack(pady=(0, 20))

        # ── Card Entry Card ──────────────────
        card_panel = CardFrame(self)
        card_panel.pack(pady=10, padx=60)
        inner = card_panel.get_inner()

        # Card icon + label
        card_label = tk.Label(
            inner, text="Enter Card Number",
            font=Fonts.TITLE_SM, bg=Colors.BG_CARD,
            fg=Colors.ACCENT,
        )
        card_label.pack(pady=(Sizing.PAD_LG, Sizing.PAD_SM))

        # Card number entry
        self.card_entry = tk.Entry(
            inner,
            font=Fonts.TITLE_MD,
            bg=Colors.BG_INPUT,
            fg=Colors.TEXT_PRIMARY,
            insertbackground=Colors.ACCENT,
            bd=0,
            width=22,
            justify="center",
            highlightthickness=2,
            highlightcolor=Colors.ACCENT,
            highlightbackground=Colors.BORDER,
        )
        self.card_entry.pack(pady=Sizing.PAD_MD, ipady=8)
        self.card_entry.bind("<Return>", lambda e: self._on_insert_card())

        # Card format hint
        hint_label = tk.Label(
            inner, text="8-16 digit card number",
            font=Fonts.BODY_SM, bg=Colors.BG_CARD,
            fg=Colors.TEXT_SECONDARY,
        )
        hint_label.pack(pady=(0, Sizing.PAD_SM))

        # Insert Card button
        self.insert_btn = ATMButton(
            inner, text="INSERT CARD",
            variant="primary", width=20,
            command=self._on_insert_card,
        )
        self.insert_btn.pack(pady=(Sizing.PAD_SM, Sizing.PAD_LG))

        # ── Status Message ───────────────────
        self.status = StatusLabel(self)
        self.status.pack(pady=Sizing.PAD_SM)

        # ── Card Slot Animation Bar ──────────
        self.slot_frame = tk.Frame(self, bg=Colors.BORDER, height=4)
        self.slot_frame.pack(fill="x", padx=100, pady=(10, 0))
        self.slot_indicator = tk.Frame(
            self.slot_frame, bg=Colors.ACCENT, height=4, width=0
        )
        self.slot_indicator.place(x=0, y=0, height=4)

        # ── Admin Access ─────────────────────
        admin_btn = ATMButton(
            self, text="ADMIN LOGIN",
            variant="secondary", width=14,
            font=Fonts.BODY_SM,
            command=self._on_admin_login,
        )
        admin_btn.pack(pady=(20, 10))

    def on_show(self, **kwargs):
        """Called when this screen becomes visible."""
        self.card_entry.delete(0, tk.END)
        self.status.clear()
        self.card_entry.focus_set()
        # Reset slot animation
        self.slot_indicator.place(x=0, y=0, height=4, width=0)

    def show_timeout_message(self):
        """Show session-expired message after auto-logout."""
        self.status.show_warning(
            "Session expired due to inactivity. Please insert your card again."
        )

    def _on_insert_card(self):
        """Validate card number and proceed to PIN screen."""
        card = self.card_entry.get().strip()
        
        # Basic validation
        from security.utils import validate_card_number
        valid, error = validate_card_number(card)
        if not valid:
            self.status.show_error(error)
            return

        # Check account exists
        account = self.app.db.get_account(card)
        if account is None:
            self.status.show_error("Card not recognized. Please try again.")
            return

        # Animate card slot then proceed
        self._animate_slot(card)

    def _animate_slot(self, card: str, step: int = 0):
        """Simple card-slot insertion animation."""
        max_width = self.slot_frame.winfo_width()
        if max_width <= 1:
            max_width = 400  # Fallback
        
        current_width = int((step / 20) * max_width)
        self.slot_indicator.place(x=0, y=0, height=4, width=current_width)
        
        if step < 20:
            self.after(25, self._animate_slot, card, step + 1)
        else:
            # Animation complete — go to PIN screen
            self.app.show_screen("pin", card_number=card)

    def _on_admin_login(self):
        """Navigate to admin screen."""
        self.app.show_screen("admin")
