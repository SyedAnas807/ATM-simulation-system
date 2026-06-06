"""
gui/theme.py — Visual theme constants for the ATM GUI.

Defines the color palette, font families, sizing, and style
dictionaries used across all screens and widgets.
Dark navy + teal accent creates a premium ATM feel.
"""


# ──────────────────────────────────────────────
# Color Palette
# ──────────────────────────────────────────────

class Colors:
    """Centralized color constants for the entire UI."""
    
    # Backgrounds
    BG_DARK = "#0a1628"           # Main background (deep navy)
    BG_CARD = "#111d35"           # Card/panel background
    BG_INPUT = "#162240"          # Input field background
    BG_HEADER = "#0d1f3c"        # Header bar background
    
    # Accent colors
    ACCENT = "#00d4aa"            # Primary accent (teal)
    ACCENT_HOVER = "#00f0c0"     # Accent hover state
    ACCENT_DARK = "#009977"      # Accent pressed state
    ACCENT_SUBTLE = "#0a3d35"    # Subtle accent background
    
    # Status colors
    SUCCESS = "#00d4aa"           # Success green (same as accent)
    ERROR = "#ff4757"             # Error red
    WARNING = "#ffa726"           # Warning orange
    INFO = "#42a5f5"              # Info blue
    
    # Text colors
    TEXT_PRIMARY = "#e8eaf6"      # Primary text (light)
    TEXT_SECONDARY = "#8892b0"    # Secondary text (muted)
    TEXT_DARK = "#0a1628"         # Dark text (on light backgrounds)
    TEXT_ACCENT = "#00d4aa"       # Accent-colored text
    
    # Borders & Dividers
    BORDER = "#1e3a5f"            # Subtle border
    BORDER_ACTIVE = "#00d4aa"     # Active/focused border
    DIVIDER = "#1a2744"           # Section divider
    
    # Button variants
    BTN_PRIMARY_BG = "#00d4aa"
    BTN_PRIMARY_FG = "#0a1628"
    BTN_SECONDARY_BG = "#1e3a5f"
    BTN_SECONDARY_FG = "#e8eaf6"
    BTN_DANGER_BG = "#ff4757"
    BTN_DANGER_FG = "#ffffff"
    BTN_KEYPAD_BG = "#162240"
    BTN_KEYPAD_FG = "#e8eaf6"
    BTN_KEYPAD_HOVER = "#1e3a5f"


# ──────────────────────────────────────────────
# Fonts
# ──────────────────────────────────────────────

class Fonts:
    """Font family and size constants."""
    
    # Font family — Segoe UI on Windows, falls back gracefully
    FAMILY = "Segoe UI"
    FAMILY_MONO = "Consolas"
    
    # Title fonts
    TITLE_XL = (FAMILY, 28, "bold")
    TITLE_LG = (FAMILY, 22, "bold")
    TITLE_MD = (FAMILY, 18, "bold")
    TITLE_SM = (FAMILY, 15, "bold")
    
    # Body fonts
    BODY_LG = (FAMILY, 14)
    BODY_MD = (FAMILY, 12)
    BODY_SM = (FAMILY, 10)
    
    # Special
    KEYPAD = (FAMILY, 20, "bold")
    BALANCE = (FAMILY_MONO, 32, "bold")
    PIN_DISPLAY = (FAMILY_MONO, 28)
    RECEIPT = (FAMILY_MONO, 11)
    BANNER = (FAMILY_MONO, 10)
    BUTTON = (FAMILY, 13, "bold")
    MENU_BUTTON = (FAMILY, 14, "bold")


# ──────────────────────────────────────────────
# Sizing & Spacing
# ──────────────────────────────────────────────

class Sizing:
    """Consistent spacing and dimension constants."""
    
    # Padding
    PAD_XS = 4
    PAD_SM = 8
    PAD_MD = 16
    PAD_LG = 24
    PAD_XL = 32
    
    # Margins
    MARGIN_SM = 8
    MARGIN_MD = 16
    MARGIN_LG = 24
    
    # Widget dimensions
    BTN_WIDTH = 18           # Standard button width (chars)
    BTN_HEIGHT = 2           # Standard button height
    KEYPAD_BTN_WIDTH = 6     # Keypad button width
    KEYPAD_BTN_HEIGHT = 2    # Keypad button height
    ENTRY_WIDTH = 30         # Standard entry width
    
    # Card dimensions
    CARD_PAD_X = 30
    CARD_PAD_Y = 20
    
    # Border
    BORDER_WIDTH = 1
    BORDER_RADIUS = 8        # Note: Tkinter doesn't support border-radius natively


# ──────────────────────────────────────────────
# ASCII Art Banner
# ──────────────────────────────────────────────

ATM_BANNER = r"""
     _   _____ __  __   ____  _                 _       _   _             
    / \ |_   _|  \/  | / ___|(_)_ __ ___  _   _| | __ _| |_(_) ___  _ __  
   / _ \  | | | |\/| | \___ \| | '_ ` _ \| | | | |/ _` | __| |/ _ \| '_ \ 
  / ___ \ | | | |  | |  ___) | | | | | | | |_| | | (_| | |_| | (_) | | | |
 /_/   \_\|_| |_|  |_| |____/|_|_| |_| |_|\__,_|_|\__,_|\__|_|\___/|_| |_|
"""

ATM_BANNER_SMALL = """
  =============================================
  |         ATM  SIMULATION  SYSTEM           |
  |         Secure Banking Terminal            |
  =============================================
"""
