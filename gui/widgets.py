"""
gui/widgets.py — Reusable custom Tkinter widgets for the ATM GUI.

Provides styled, consistent UI components:
  - ATMButton:     Hover-animated button with configurable style
  - ATMKeypad:     3x4 numeric keypad with Clear/Enter buttons
  - MaskedEntry:   PIN entry that shows bullet characters
  - StatusLabel:   Color-coded message display (success/error/info)
  - CardFrame:     Rounded-look panel with border styling
"""

import tkinter as tk
from gui.theme import Colors, Fonts, Sizing


class ATMButton(tk.Button):
    """
    Styled button with hover color animation.
    
    Variants:
        'primary'   - Teal background, dark text
        'secondary' - Dark blue background, light text
        'danger'    - Red background, white text
        'keypad'    - Dark panel background, for numeric keys
        'menu'      - Wider button for main menu options
    """

    # Map variant names to (bg, fg, hover_bg) colors
    VARIANTS = {
        "primary": (Colors.BTN_PRIMARY_BG, Colors.BTN_PRIMARY_FG, Colors.ACCENT_HOVER),
        "secondary": (Colors.BTN_SECONDARY_BG, Colors.BTN_SECONDARY_FG, "#2a4a6f"),
        "danger": (Colors.BTN_DANGER_BG, Colors.BTN_DANGER_FG, "#ff6b7a"),
        "keypad": (Colors.BTN_KEYPAD_BG, Colors.BTN_KEYPAD_FG, Colors.BTN_KEYPAD_HOVER),
        "menu": (Colors.BG_INPUT, Colors.TEXT_PRIMARY, Colors.BTN_SECONDARY_BG),
    }

    def __init__(self, parent, text="", variant="primary", command=None,
                 width=None, height=None, font=None, **kwargs):
        bg, fg, hover_bg = self.VARIANTS.get(variant, self.VARIANTS["primary"])
        
        # Default sizes
        if width is None:
            width = Sizing.KEYPAD_BTN_WIDTH if variant == "keypad" else Sizing.BTN_WIDTH
        if height is None:
            height = Sizing.KEYPAD_BTN_HEIGHT if variant == "keypad" else Sizing.BTN_HEIGHT
        if font is None:
            font = Fonts.KEYPAD if variant == "keypad" else Fonts.BUTTON

        super().__init__(
            parent,
            text=text,
            font=font,
            bg=bg,
            fg=fg,
            activebackground=hover_bg,
            activeforeground=fg,
            width=width,
            height=height,
            bd=0,
            relief="flat",
            cursor="hand2",
            command=command,
            **kwargs,
        )

        self._bg = bg
        self._hover_bg = hover_bg
        self._fg = fg

        # Hover effects
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)

    def _on_enter(self, event):
        """Mouse enter — highlight."""
        self.config(bg=self._hover_bg)

    def _on_leave(self, event):
        """Mouse leave — restore."""
        self.config(bg=self._bg)


class ATMKeypad(tk.Frame):
    """
    3x4 numeric keypad with Clear and Enter buttons.
    
    Layout:
        [1] [2] [3]
        [4] [5] [6]
        [7] [8] [9]
        [C] [0] [<-]
        [  Enter  ]
    
    Args:
        parent:       Parent widget.
        on_key:       Callback for digit presses — on_key(digit: str)
        on_clear:     Callback for Clear button.
        on_backspace: Callback for Backspace button.
        on_enter:     Callback for Enter button.
    """

    def __init__(self, parent, on_key=None, on_clear=None,
                 on_backspace=None, on_enter=None, **kwargs):
        super().__init__(parent, bg=Colors.BG_DARK, **kwargs)
        
        self.on_key = on_key
        self.on_clear = on_clear
        self.on_backspace = on_backspace
        self.on_enter = on_enter
        
        self._build_keypad()

    def _build_keypad(self):
        """Construct the keypad grid."""
        pad = Sizing.PAD_XS
        
        # Digit buttons (1-9)
        digits = [
            ["1", "2", "3"],
            ["4", "5", "6"],
            ["7", "8", "9"],
        ]
        
        for row_idx, row in enumerate(digits):
            for col_idx, digit in enumerate(row):
                btn = ATMButton(
                    self, text=digit, variant="keypad",
                    command=lambda d=digit: self._digit_pressed(d),
                )
                btn.grid(row=row_idx, column=col_idx, padx=pad, pady=pad)
        
        # Bottom row: Clear, 0, Backspace
        btn_clear = ATMButton(
            self, text="C", variant="danger",
            width=Sizing.KEYPAD_BTN_WIDTH,
            height=Sizing.KEYPAD_BTN_HEIGHT,
            font=Fonts.KEYPAD,
            command=self._clear_pressed,
        )
        btn_clear.grid(row=3, column=0, padx=pad, pady=pad)
        
        btn_zero = ATMButton(
            self, text="0", variant="keypad",
            command=lambda: self._digit_pressed("0"),
        )
        btn_zero.grid(row=3, column=1, padx=pad, pady=pad)
        
        btn_back = ATMButton(
            self, text="<<", variant="secondary",
            width=Sizing.KEYPAD_BTN_WIDTH,
            height=Sizing.KEYPAD_BTN_HEIGHT,
            font=Fonts.KEYPAD,
            command=self._backspace_pressed,
        )
        btn_back.grid(row=3, column=2, padx=pad, pady=pad)
        
        # Enter button (spans full width)
        btn_enter = ATMButton(
            self, text="ENTER", variant="primary",
            width=20, height=2,
            font=Fonts.BUTTON,
            command=self._enter_pressed,
        )
        btn_enter.grid(row=4, column=0, columnspan=3,
                       padx=pad, pady=(pad + 4, pad), sticky="ew")

    def _digit_pressed(self, digit: str):
        if self.on_key:
            self.on_key(digit)

    def _clear_pressed(self):
        if self.on_clear:
            self.on_clear()

    def _backspace_pressed(self):
        if self.on_backspace:
            self.on_backspace()

    def _enter_pressed(self):
        if self.on_enter:
            self.on_enter()


class StatusLabel(tk.Label):
    """
    Color-coded message label for showing success/error/info messages.
    
    Usage:
        status = StatusLabel(parent)
        status.show_success("Transaction complete!")
        status.show_error("Insufficient funds.")
        status.clear()
    """

    def __init__(self, parent, **kwargs):
        super().__init__(
            parent,
            text="",
            font=Fonts.BODY_MD,
            bg=Colors.BG_DARK,
            fg=Colors.TEXT_SECONDARY,
            wraplength=400,
            justify="center",
            **kwargs,
        )

    def show_success(self, message: str):
        self.config(text=message, fg=Colors.SUCCESS)

    def show_error(self, message: str):
        self.config(text=message, fg=Colors.ERROR)

    def show_warning(self, message: str):
        self.config(text=message, fg=Colors.WARNING)

    def show_info(self, message: str):
        self.config(text=message, fg=Colors.INFO)

    def clear(self):
        self.config(text="", fg=Colors.TEXT_SECONDARY)


class CardFrame(tk.Frame):
    """
    Styled panel frame with border, used to group related content.
    Mimics a card/panel with subtle border styling.
    """

    def __init__(self, parent, **kwargs):
        # Outer border frame
        super().__init__(
            parent,
            bg=Colors.BORDER,
            bd=0,
            highlightthickness=1,
            highlightbackground=Colors.BORDER,
            **kwargs,
        )
        
        # Inner content frame
        self.inner = tk.Frame(self, bg=Colors.BG_CARD)
        self.inner.pack(fill="both", expand=True, padx=1, pady=1)

    def get_inner(self) -> tk.Frame:
        """Return the inner frame to place widgets in."""
        return self.inner


class HeaderBar(tk.Frame):
    """
    Top header bar with title and optional subtitle.
    Used at the top of each screen.
    """

    def __init__(self, parent, title: str, subtitle: str = "", **kwargs):
        super().__init__(parent, bg=Colors.BG_HEADER, **kwargs)
        
        # Title
        self.title_label = tk.Label(
            self, text=title, font=Fonts.TITLE_LG,
            bg=Colors.BG_HEADER, fg=Colors.ACCENT,
        )
        self.title_label.pack(pady=(Sizing.PAD_MD, 0))
        
        # Subtitle
        if subtitle:
            self.subtitle_label = tk.Label(
                self, text=subtitle, font=Fonts.BODY_MD,
                bg=Colors.BG_HEADER, fg=Colors.TEXT_SECONDARY,
            )
            self.subtitle_label.pack(pady=(2, Sizing.PAD_SM))
        
        # Divider line
        divider = tk.Frame(self, bg=Colors.ACCENT, height=2)
        divider.pack(fill="x", padx=Sizing.PAD_XL)


class TimerBar(tk.Label):
    """
    Session timeout countdown display.
    Shows remaining seconds and changes color when low.
    """

    def __init__(self, parent, **kwargs):
        super().__init__(
            parent, text="",
            font=Fonts.BODY_SM,
            bg=Colors.BG_DARK,
            fg=Colors.TEXT_SECONDARY,
            anchor="e",
            **kwargs,
        )

    def update_time(self, seconds: int):
        """Update the displayed countdown."""
        if seconds <= 0:
            self.config(text="Session expired", fg=Colors.ERROR)
        elif seconds <= 15:
            self.config(
                text=f"Session timeout: {seconds}s",
                fg=Colors.WARNING,
            )
        else:
            self.config(
                text=f"Session timeout: {seconds}s",
                fg=Colors.TEXT_SECONDARY,
            )
