"""
gui/screens/change_pin_screen.py — Change PIN screen.

Three-step flow: enter current PIN → enter new PIN → confirm new PIN.
"""

import tkinter as tk
from gui.theme import Colors, Fonts, Sizing
from gui.widgets import ATMButton, ATMKeypad, StatusLabel, CardFrame, HeaderBar, TimerBar


class ChangePinScreen(tk.Frame):
    """
    Change PIN screen with a three-step keypad flow.
    
    Steps:
        1. Enter current PIN
        2. Enter new PIN
        3. Confirm new PIN
    """

    def __init__(self, parent, app, **kwargs):
        super().__init__(parent, bg=Colors.BG_DARK, **kwargs)
        self.app = app
        self.step = 1          # 1=old, 2=new, 3=confirm
        self.old_pin = ""
        self.new_pin = ""
        self.confirm_pin = ""
        self.current_input = ""
        self._build_ui()

    def _build_ui(self):
        # Timer
        self.timer = TimerBar(self)
        self.timer.pack(anchor="ne", padx=Sizing.PAD_LG, pady=(Sizing.PAD_SM, 0))

        # Header
        header = HeaderBar(self, title="Change PIN", subtitle="")
        header.pack(fill="x", pady=(10, 10))

        # Step indicator
        self.step_label = tk.Label(
            self, text="Step 1/3: Enter Current PIN",
            font=Fonts.TITLE_SM,
            bg=Colors.BG_DARK, fg=Colors.TEXT_PRIMARY,
        )
        self.step_label.pack(pady=(5, 10))

        # PIN display
        pin_card = CardFrame(self)
        pin_card.pack(pady=5, padx=220)
        inner = pin_card.get_inner()

        self.pin_display = tk.Label(
            inner, text="",
            font=Fonts.PIN_DISPLAY,
            bg=Colors.BG_CARD, fg=Colors.ACCENT,
            width=12, anchor="center",
        )
        self.pin_display.pack(pady=Sizing.PAD_LG, padx=Sizing.PAD_XL)

        # Keypad
        self.keypad = ATMKeypad(
            self,
            on_key=self._on_digit,
            on_clear=self._on_clear,
            on_backspace=self._on_backspace,
            on_enter=self._on_enter,
        )
        self.keypad.pack(pady=5)

        # Status
        self.status = StatusLabel(self)
        self.status.pack(pady=Sizing.PAD_SM)

        # Cancel
        ATMButton(
            self, text="CANCEL",
            variant="secondary", width=14,
            command=lambda: self.app.show_screen("main_menu"),
        ).pack(pady=(5, 10))

    def on_show(self, **kwargs):
        self.step = 1
        self.old_pin = ""
        self.new_pin = ""
        self.confirm_pin = ""
        self.current_input = ""
        self._update_step()
        self.status.clear()

    def update_timer(self, seconds: int):
        self.timer.update_time(seconds)

    def _on_digit(self, digit: str):
        if len(self.current_input) < 6:
            self.current_input += digit
            self._update_display()

    def _on_clear(self):
        self.current_input = ""
        self._update_display()

    def _on_backspace(self):
        if self.current_input:
            self.current_input = self.current_input[:-1]
            self._update_display()

    def _on_enter(self):
        if len(self.current_input) < 4:
            self.status.show_error("PIN must be at least 4 digits.")
            return

        if self.step == 1:
            self.old_pin = self.current_input
            self.current_input = ""
            self.step = 2
            self._update_step()
            self.status.clear()

        elif self.step == 2:
            self.new_pin = self.current_input
            self.current_input = ""
            self.step = 3
            self._update_step()
            self.status.clear()

        elif self.step == 3:
            self.confirm_pin = self.current_input
            self._submit_pin_change()

    def _update_step(self):
        steps = {
            1: "Step 1/3: Enter Current PIN",
            2: "Step 2/3: Enter New PIN",
            3: "Step 3/3: Confirm New PIN",
        }
        self.step_label.config(text=steps.get(self.step, ""))
        self._update_display()

    def _update_display(self):
        dots = " ".join(["*"] * len(self.current_input))
        needed = 4 - len(self.current_input)
        if needed > 0:
            placeholders = " ".join(["_"] * needed)
            self.pin_display.config(text=f"{dots} {placeholders}" if dots else placeholders)
        else:
            self.pin_display.config(text=dots)

    def _submit_pin_change(self):
        account = self.app.get_account()
        if not account:
            self.status.show_error("Session error.")
            return

        success, message = self.app.atm.change_pin(
            account, self.old_pin, self.new_pin, self.confirm_pin
        )

        if success:
            self.status.show_success(message)
            self.after(2000, lambda: self.app.show_screen("main_menu"))
        else:
            self.status.show_error(message)
            # Reset to step 1
            self.step = 1
            self.old_pin = ""
            self.new_pin = ""
            self.confirm_pin = ""
            self.current_input = ""
            self._update_step()
