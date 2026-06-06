"""
gui/app.py — Main ATM application window and screen manager.

Creates the Tk root window, initializes all managers (DB, Auth, ATM, Admin),
and handles screen navigation with transitions. Monitors session timeout
and triggers auto-logout.
"""

import tkinter as tk
from config import APP_TITLE, WINDOW_WIDTH, WINDOW_HEIGHT
from database.db_manager import DatabaseManager
from auth.auth_manager import AuthManager
from core.atm import ATMController
from admin.admin_manager import AdminManager
from gui.theme import Colors, Fonts


class ATMApp(tk.Tk):
    """
    Root application window and screen controller.
    
    Manages:
        - Screen navigation (show_screen)
        - Session timeout monitoring
        - Inactivity detection
        - Global event binding
    
    Attributes:
        db           (DatabaseManager): Shared database instance.
        auth         (AuthManager):     Authentication manager.
        atm          (ATMController):   Transaction controller.
        admin_mgr    (AdminManager):    Admin operations.
        screens      (dict):            Screen name → frame mapping.
        current      (str):             Currently visible screen name.
    """

    def __init__(self):
        super().__init__()

        # ── Window Configuration ──────────────
        self.title(APP_TITLE)
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.resizable(False, False)
        self.configure(bg=Colors.BG_DARK)
        
        # Center on screen
        self.update_idletasks()
        x = (self.winfo_screenwidth() - WINDOW_WIDTH) // 2
        y = (self.winfo_screenheight() - WINDOW_HEIGHT) // 2
        self.geometry(f"+{x}+{y}")

        # ── Initialize Backend Managers ───────
        self.db = DatabaseManager()
        self.auth = AuthManager(self.db)
        self.atm = ATMController(self.db)
        self.admin_mgr = AdminManager(self.db)

        # ── Screen Container ──────────────────
        self.container = tk.Frame(self, bg=Colors.BG_DARK)
        self.container.pack(fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        # ── Screen Registry ───────────────────
        self.screens = {}
        self.current = None
        self._timeout_job = None

        # ── Register All Screens (lazy import to avoid circular deps) ──
        self._register_screens()

        # ── Inactivity Detection ──────────────
        self.bind_all("<Key>", self._on_activity)
        self.bind_all("<Button>", self._on_activity)
        self.bind_all("<Motion>", self._on_activity)

        # ── Start with Welcome Screen ─────────
        self.show_screen("welcome")

    def _register_screens(self):
        """Import and register all screen classes."""
        from gui.screens.welcome_screen import WelcomeScreen
        from gui.screens.pin_screen import PinScreen
        from gui.screens.main_menu_screen import MainMenuScreen
        from gui.screens.balance_screen import BalanceScreen
        from gui.screens.withdraw_screen import WithdrawScreen
        from gui.screens.deposit_screen import DepositScreen
        from gui.screens.transfer_screen import TransferScreen
        from gui.screens.statement_screen import StatementScreen
        from gui.screens.change_pin_screen import ChangePinScreen
        from gui.screens.receipt_screen import ReceiptScreen
        from gui.screens.admin_screen import AdminScreen

        screen_classes = {
            "welcome": WelcomeScreen,
            "pin": PinScreen,
            "main_menu": MainMenuScreen,
            "balance": BalanceScreen,
            "withdraw": WithdrawScreen,
            "deposit": DepositScreen,
            "transfer": TransferScreen,
            "statement": StatementScreen,
            "change_pin": ChangePinScreen,
            "receipt": ReceiptScreen,
            "admin": AdminScreen,
        }

        for name, cls in screen_classes.items():
            screen = cls(parent=self.container, app=self)
            screen.grid(row=0, column=0, sticky="nsew")
            self.screens[name] = screen

    def show_screen(self, name: str, **kwargs):
        """
        Navigate to a screen by name.
        
        Calls the screen's `on_show(**kwargs)` method if it exists,
        allowing screens to refresh their content.
        
        Args:
            name:   Registered screen name.
            **kwargs: Data to pass to the screen's on_show method.
        """
        if name not in self.screens:
            print(f"Warning: Screen '{name}' not found.")
            return

        screen = self.screens[name]
        
        # Call on_show if the screen implements it
        if hasattr(screen, "on_show"):
            screen.on_show(**kwargs)
        
        # Raise the screen to the front
        screen.tkraise()
        self.current = name

        # Manage session timeout
        if name in ("welcome", "pin", "admin"):
            self._stop_timeout_timer()
        elif self.auth.is_logged_in():
            self._start_timeout_timer()

    # ──────────────────────────────────────────
    # Session Timeout Management
    # ──────────────────────────────────────────

    def _on_activity(self, event=None):
        """Reset session timer on any user input."""
        if self.auth.current_account is not None:
            self.auth.refresh_session()

    def _start_timeout_timer(self):
        """Start the periodic session-timeout check."""
        self._stop_timeout_timer()
        self._check_timeout()

    def _stop_timeout_timer(self):
        """Cancel the session-timeout check."""
        if self._timeout_job is not None:
            self.after_cancel(self._timeout_job)
            self._timeout_job = None

    def _check_timeout(self):
        """
        Periodic check (every 1s) for session expiration.
        If expired, force logout and return to welcome screen.
        """
        if self.auth.current_account is None:
            return

        if self.auth.is_session_expired():
            self.session_expired_logout()
            return

        # Update timer bar on current screen
        remaining = self.auth.get_remaining_time()
        current_screen = self.screens.get(self.current)
        if current_screen and hasattr(current_screen, "update_timer"):
            current_screen.update_timer(remaining)

        # Check again in 1 second
        self._timeout_job = self.after(1000, self._check_timeout)

    def session_expired_logout(self):
        """Handle session expiration — notify and redirect."""
        self._stop_timeout_timer()
        self.auth.logout()
        self.show_screen("welcome")
        # Show timeout message on welcome screen
        welcome = self.screens.get("welcome")
        if welcome and hasattr(welcome, "show_timeout_message"):
            welcome.show_timeout_message()

    def logout(self):
        """Manual logout — clear session and return to welcome."""
        self._stop_timeout_timer()
        self.auth.logout()
        self.show_screen("welcome")

    def get_account(self):
        """Get the currently logged-in account (refreshed from DB)."""
        self.auth.refresh_account()
        return self.auth.current_account
