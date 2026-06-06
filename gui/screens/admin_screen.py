"""
gui/screens/admin_screen.py — Admin Panel screen.

Provides a tabbed interface for admin operations:
  - Login / Logout
  - View all accounts
  - Lock / Unlock accounts
  - Reset PIN
  - Set daily limits
  - View transaction logs with filters
  - Add / Remove accounts
"""

import tkinter as tk
from gui.theme import Colors, Fonts, Sizing
from gui.widgets import ATMButton, StatusLabel, CardFrame, HeaderBar
from security.utils import mask_card_number


class AdminScreen(tk.Frame):
    """Admin panel with login and management tabs."""

    def __init__(self, parent, app, **kwargs):
        super().__init__(parent, bg=Colors.BG_DARK, **kwargs)
        self.app = app
        self._build_ui()

    def _build_ui(self):
        # Header
        header = HeaderBar(self, title="Admin Panel", subtitle="Bank Management System")
        header.pack(fill="x", pady=(15, 10))

        # ── Login Section ─────────────────────
        self.login_frame = tk.Frame(self, bg=Colors.BG_DARK)

        tk.Label(
            self.login_frame, text="Admin Authentication",
            font=Fonts.TITLE_SM, bg=Colors.BG_DARK, fg=Colors.TEXT_PRIMARY,
        ).pack(pady=(20, 15))

        login_card = CardFrame(self.login_frame)
        login_card.pack(padx=200)
        login_inner = login_card.get_inner()

        tk.Label(
            login_inner, text="Username",
            font=Fonts.BODY_MD, bg=Colors.BG_CARD, fg=Colors.TEXT_SECONDARY,
        ).pack(pady=(Sizing.PAD_LG, Sizing.PAD_XS))

        self.username_entry = tk.Entry(
            login_inner, font=Fonts.BODY_LG,
            bg=Colors.BG_INPUT, fg=Colors.TEXT_PRIMARY,
            insertbackground=Colors.ACCENT, bd=0, width=25,
            highlightthickness=2, highlightcolor=Colors.ACCENT,
            highlightbackground=Colors.BORDER,
        )
        self.username_entry.pack(ipady=6, pady=Sizing.PAD_XS)

        tk.Label(
            login_inner, text="Password",
            font=Fonts.BODY_MD, bg=Colors.BG_CARD, fg=Colors.TEXT_SECONDARY,
        ).pack(pady=(Sizing.PAD_MD, Sizing.PAD_XS))

        self.password_entry = tk.Entry(
            login_inner, font=Fonts.BODY_LG, show="*",
            bg=Colors.BG_INPUT, fg=Colors.TEXT_PRIMARY,
            insertbackground=Colors.ACCENT, bd=0, width=25,
            highlightthickness=2, highlightcolor=Colors.ACCENT,
            highlightbackground=Colors.BORDER,
        )
        self.password_entry.pack(ipady=6, pady=Sizing.PAD_XS)
        self.password_entry.bind("<Return>", lambda e: self._do_login())

        ATMButton(
            login_inner, text="LOGIN",
            variant="primary", width=20,
            command=self._do_login,
        ).pack(pady=(Sizing.PAD_LG, Sizing.PAD_XL))

        self.login_status = StatusLabel(self.login_frame)
        self.login_status.pack(pady=Sizing.PAD_SM)

        ATMButton(
            self.login_frame, text="BACK",
            variant="secondary", width=12,
            command=lambda: self.app.show_screen("welcome"),
        ).pack(pady=Sizing.PAD_MD)

        # ── Dashboard Section ─────────────────
        self.dashboard_frame = tk.Frame(self, bg=Colors.BG_DARK)

        # Tab buttons
        tab_frame = tk.Frame(self.dashboard_frame, bg=Colors.BG_DARK)
        tab_frame.pack(fill="x", padx=20, pady=(5, 5))

        tabs = [
            ("Accounts", self._show_accounts_tab),
            ("Transactions", self._show_txn_tab),
            ("Add Account", self._show_add_tab),
            ("Settings", self._show_settings_tab),
        ]

        for text, command in tabs:
            ATMButton(
                tab_frame, text=text,
                variant="secondary", width=14, height=1,
                font=Fonts.BODY_MD, command=command,
            ).pack(side="left", padx=4)

        ATMButton(
            tab_frame, text="Logout",
            variant="danger", width=10, height=1,
            font=Fonts.BODY_MD, command=self._do_admin_logout,
        ).pack(side="right", padx=4)

        # Tab content area
        self.tab_content = tk.Frame(self.dashboard_frame, bg=Colors.BG_DARK)
        self.tab_content.pack(fill="both", expand=True, padx=20, pady=5)

        # Status
        self.dash_status = StatusLabel(self.dashboard_frame)
        self.dash_status.pack(pady=Sizing.PAD_XS)

    def on_show(self, **kwargs):
        """Show login or dashboard based on admin auth state."""
        self.login_status.clear()
        self.username_entry.delete(0, tk.END)
        self.password_entry.delete(0, tk.END)

        if self.app.admin_mgr.is_logged_in:
            self.login_frame.pack_forget()
            self.dashboard_frame.pack(fill="both", expand=True)
            self._show_accounts_tab()
        else:
            self.dashboard_frame.pack_forget()
            self.login_frame.pack(fill="both", expand=True)
            self.username_entry.focus_set()

    def _do_login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        success, message = self.app.admin_mgr.login(username, password)
        if success:
            self.login_status.show_success(message)
            self.after(500, self.on_show)
        else:
            self.login_status.show_error(message)

    def _do_admin_logout(self):
        self.app.admin_mgr.logout()
        self.app.show_screen("welcome")

    def _clear_tab(self):
        for widget in self.tab_content.winfo_children():
            widget.destroy()
        self.dash_status.clear()

    # ── Accounts Tab ─────────────────────────

    def _show_accounts_tab(self):
        self._clear_tab()

        tk.Label(
            self.tab_content, text="All Accounts",
            font=Fonts.TITLE_SM, bg=Colors.BG_DARK, fg=Colors.ACCENT,
        ).pack(anchor="w", pady=(5, 8))

        # Table header
        hdr = tk.Frame(self.tab_content, bg=Colors.BG_HEADER)
        hdr.pack(fill="x")
        cols = [("Name", 16), ("Card", 14), ("Balance", 12),
                ("Type", 10), ("Status", 8), ("Action", 14)]
        for text, w in cols:
            tk.Label(
                hdr, text=text, font=Fonts.BODY_SM,
                bg=Colors.BG_HEADER, fg=Colors.ACCENT, width=w, anchor="w",
            ).pack(side="left", padx=3, pady=4)

        # Scrollable list
        canvas = tk.Canvas(self.tab_content, bg=Colors.BG_DARK, highlightthickness=0, height=330)
        scrollbar = tk.Scrollbar(self.tab_content, orient="vertical", command=canvas.yview)
        scrollable = tk.Frame(canvas, bg=Colors.BG_DARK)
        scrollable.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        accounts = self.app.admin_mgr.get_all_accounts()
        for idx, acct in enumerate(accounts):
            bg = Colors.BG_CARD if idx % 2 == 0 else Colors.BG_DARK
            row = tk.Frame(scrollable, bg=bg)
            row.pack(fill="x")

            tk.Label(row, text=acct.holder_name, font=Fonts.BODY_SM, bg=bg, fg=Colors.TEXT_PRIMARY, width=16, anchor="w").pack(side="left", padx=3, pady=3)
            tk.Label(row, text=mask_card_number(acct.card_number), font=Fonts.BODY_SM, bg=bg, fg=Colors.TEXT_PRIMARY, width=14, anchor="w").pack(side="left", padx=3, pady=3)
            tk.Label(row, text=f"Rs.{acct.balance:,.0f}", font=Fonts.BODY_SM, bg=bg, fg=Colors.TEXT_PRIMARY, width=12, anchor="w").pack(side="left", padx=3, pady=3)
            tk.Label(row, text=acct.account_type.title(), font=Fonts.BODY_SM, bg=bg, fg=Colors.TEXT_PRIMARY, width=10, anchor="w").pack(side="left", padx=3, pady=3)

            status_color = Colors.SUCCESS if acct.is_active() else Colors.ERROR
            tk.Label(row, text=acct.status.title(), font=Fonts.BODY_SM, bg=bg, fg=status_color, width=8, anchor="w").pack(side="left", padx=3, pady=3)

            # Action buttons
            action_frame = tk.Frame(row, bg=bg)
            action_frame.pack(side="left", padx=3)

            if acct.is_active():
                tk.Button(
                    action_frame, text="Lock", font=("Segoe UI", 9),
                    bg=Colors.ERROR, fg="white", bd=0, width=5, cursor="hand2",
                    command=lambda c=acct.card_number: self._lock_acct(c),
                ).pack(side="left", padx=2)
            else:
                tk.Button(
                    action_frame, text="Unlock", font=("Segoe UI", 9),
                    bg=Colors.SUCCESS, fg=Colors.TEXT_DARK, bd=0, width=5, cursor="hand2",
                    command=lambda c=acct.card_number: self._unlock_acct(c),
                ).pack(side="left", padx=2)

            tk.Button(
                action_frame, text="Del", font=("Segoe UI", 9),
                bg=Colors.BTN_DANGER_BG, fg="white", bd=0, width=4, cursor="hand2",
                command=lambda c=acct.card_number: self._delete_acct(c),
            ).pack(side="left", padx=2)

    def _lock_acct(self, card):
        success, msg = self.app.admin_mgr.lock_account(card)
        self.dash_status.show_success(msg) if success else self.dash_status.show_error(msg)
        self._show_accounts_tab()

    def _unlock_acct(self, card):
        success, msg = self.app.admin_mgr.unlock_account(card)
        self.dash_status.show_success(msg) if success else self.dash_status.show_error(msg)
        self._show_accounts_tab()

    def _delete_acct(self, card):
        success, msg = self.app.admin_mgr.remove_account(card)
        self.dash_status.show_success(msg) if success else self.dash_status.show_error(msg)
        self._show_accounts_tab()

    # ── Transactions Tab ─────────────────────

    def _show_txn_tab(self):
        self._clear_tab()

        tk.Label(
            self.tab_content, text="Transaction Log",
            font=Fonts.TITLE_SM, bg=Colors.BG_DARK, fg=Colors.ACCENT,
        ).pack(anchor="w", pady=(5, 8))

        # Filters
        filter_frame = tk.Frame(self.tab_content, bg=Colors.BG_DARK)
        filter_frame.pack(fill="x", pady=(0, 8))

        tk.Label(filter_frame, text="Card:", font=Fonts.BODY_SM, bg=Colors.BG_DARK, fg=Colors.TEXT_SECONDARY).pack(side="left", padx=4)
        self.txn_card_filter = tk.Entry(filter_frame, font=Fonts.BODY_SM, bg=Colors.BG_INPUT, fg=Colors.TEXT_PRIMARY, bd=0, width=14, insertbackground=Colors.ACCENT)
        self.txn_card_filter.pack(side="left", padx=4, ipady=3)

        tk.Label(filter_frame, text="Type:", font=Fonts.BODY_SM, bg=Colors.BG_DARK, fg=Colors.TEXT_SECONDARY).pack(side="left", padx=4)
        self.txn_type_filter = tk.Entry(filter_frame, font=Fonts.BODY_SM, bg=Colors.BG_INPUT, fg=Colors.TEXT_PRIMARY, bd=0, width=12, insertbackground=Colors.ACCENT)
        self.txn_type_filter.pack(side="left", padx=4, ipady=3)

        tk.Label(filter_frame, text="From:", font=Fonts.BODY_SM, bg=Colors.BG_DARK, fg=Colors.TEXT_SECONDARY).pack(side="left", padx=4)
        self.txn_date_from = tk.Entry(filter_frame, font=Fonts.BODY_SM, bg=Colors.BG_INPUT, fg=Colors.TEXT_PRIMARY, bd=0, width=10, insertbackground=Colors.ACCENT)
        self.txn_date_from.pack(side="left", padx=4, ipady=3)

        tk.Label(filter_frame, text="To:", font=Fonts.BODY_SM, bg=Colors.BG_DARK, fg=Colors.TEXT_SECONDARY).pack(side="left", padx=4)
        self.txn_date_to = tk.Entry(filter_frame, font=Fonts.BODY_SM, bg=Colors.BG_INPUT, fg=Colors.TEXT_PRIMARY, bd=0, width=10, insertbackground=Colors.ACCENT)
        self.txn_date_to.pack(side="left", padx=4, ipady=3)

        ATMButton(
            filter_frame, text="Search",
            variant="primary", width=8, height=1,
            font=Fonts.BODY_SM,
            command=self._search_txns,
        ).pack(side="left", padx=8)

        # Table header
        hdr = tk.Frame(self.tab_content, bg=Colors.BG_HEADER)
        hdr.pack(fill="x")
        cols = [("Date", 16), ("Card", 12), ("Type", 12), ("Amount", 10), ("Balance", 10), ("Status", 7)]
        for text, w in cols:
            tk.Label(hdr, text=text, font=Fonts.BODY_SM, bg=Colors.BG_HEADER, fg=Colors.ACCENT, width=w, anchor="w").pack(side="left", padx=3, pady=4)

        # Results
        self.txn_canvas = tk.Canvas(self.tab_content, bg=Colors.BG_DARK, highlightthickness=0, height=280)
        txn_scrollbar = tk.Scrollbar(self.tab_content, orient="vertical", command=self.txn_canvas.yview)
        self.txn_scrollable = tk.Frame(self.txn_canvas, bg=Colors.BG_DARK)
        self.txn_scrollable.bind("<Configure>", lambda e: self.txn_canvas.configure(scrollregion=self.txn_canvas.bbox("all")))
        self.txn_canvas.create_window((0, 0), window=self.txn_scrollable, anchor="nw")
        self.txn_canvas.configure(yscrollcommand=txn_scrollbar.set)
        self.txn_canvas.pack(side="left", fill="both", expand=True)
        txn_scrollbar.pack(side="right", fill="y")

        # Load all transactions by default
        self._search_txns()

    def _search_txns(self):
        for w in self.txn_scrollable.winfo_children():
            w.destroy()

        card = self.txn_card_filter.get().strip() or None
        txn_type = self.txn_type_filter.get().strip() or None
        date_from = self.txn_date_from.get().strip() or None
        date_to = self.txn_date_to.get().strip() or None

        transactions = self.app.admin_mgr.get_transaction_log(
            card_number=card, txn_type=txn_type,
            date_from=date_from, date_to=date_to,
        )

        if not transactions:
            tk.Label(
                self.txn_scrollable, text="No transactions found.",
                font=Fonts.BODY_MD, bg=Colors.BG_DARK, fg=Colors.TEXT_SECONDARY,
            ).pack(pady=20)
            return

        for idx, txn in enumerate(transactions):
            bg = Colors.BG_CARD if idx % 2 == 0 else Colors.BG_DARK
            row = tk.Frame(self.txn_scrollable, bg=bg)
            row.pack(fill="x")

            tk.Label(row, text=txn.timestamp, font=Fonts.BODY_SM, bg=bg, fg=Colors.TEXT_PRIMARY, width=16, anchor="w").pack(side="left", padx=3, pady=2)
            tk.Label(row, text=f"***{txn.card_number[-4:]}", font=Fonts.BODY_SM, bg=bg, fg=Colors.TEXT_PRIMARY, width=12, anchor="w").pack(side="left", padx=3, pady=2)
            tk.Label(row, text=txn.txn_type.replace("_", " ").title(), font=Fonts.BODY_SM, bg=bg, fg=Colors.TEXT_PRIMARY, width=12, anchor="w").pack(side="left", padx=3, pady=2)
            tk.Label(row, text=f"Rs.{txn.amount:,.0f}", font=Fonts.BODY_SM, bg=bg, fg=Colors.TEXT_PRIMARY, width=10, anchor="w").pack(side="left", padx=3, pady=2)
            tk.Label(row, text=f"Rs.{txn.balance_after:,.0f}", font=Fonts.BODY_SM, bg=bg, fg=Colors.TEXT_PRIMARY, width=10, anchor="w").pack(side="left", padx=3, pady=2)
            sc = Colors.SUCCESS if txn.status == "success" else Colors.ERROR
            tk.Label(row, text=txn.status.title(), font=Fonts.BODY_SM, bg=bg, fg=sc, width=7, anchor="w").pack(side="left", padx=3, pady=2)

    # ── Add Account Tab ──────────────────────

    def _show_add_tab(self):
        self._clear_tab()

        tk.Label(
            self.tab_content, text="Add New Account",
            font=Fonts.TITLE_SM, bg=Colors.BG_DARK, fg=Colors.ACCENT,
        ).pack(anchor="w", pady=(5, 8))

        form = CardFrame(self.tab_content)
        form.pack(padx=100, fill="x")
        inner = form.get_inner()

        fields = {}
        for label_text in ["Holder Name", "Card Number", "PIN", "Balance"]:
            row = tk.Frame(inner, bg=Colors.BG_CARD)
            row.pack(fill="x", padx=Sizing.PAD_LG, pady=4)
            tk.Label(row, text=label_text + ":", font=Fonts.BODY_MD, bg=Colors.BG_CARD, fg=Colors.TEXT_SECONDARY, width=14, anchor="w").pack(side="left")
            entry = tk.Entry(row, font=Fonts.BODY_MD, bg=Colors.BG_INPUT, fg=Colors.TEXT_PRIMARY, bd=0, width=25, insertbackground=Colors.ACCENT)
            if label_text == "PIN":
                entry.config(show="*")
            entry.pack(side="left", padx=5, ipady=4)
            fields[label_text] = entry

        # Account type dropdown
        type_row = tk.Frame(inner, bg=Colors.BG_CARD)
        type_row.pack(fill="x", padx=Sizing.PAD_LG, pady=4)
        tk.Label(type_row, text="Account Type:", font=Fonts.BODY_MD, bg=Colors.BG_CARD, fg=Colors.TEXT_SECONDARY, width=14, anchor="w").pack(side="left")

        self.acct_type_var = tk.StringVar(value="savings")
        for val in ["savings", "current"]:
            tk.Radiobutton(
                type_row, text=val.title(), variable=self.acct_type_var, value=val,
                font=Fonts.BODY_MD, bg=Colors.BG_CARD, fg=Colors.TEXT_PRIMARY,
                selectcolor=Colors.BG_INPUT, activebackground=Colors.BG_CARD,
                activeforeground=Colors.TEXT_PRIMARY,
            ).pack(side="left", padx=10)

        ATMButton(
            inner, text="CREATE ACCOUNT",
            variant="primary", width=20,
            command=lambda: self._create_account(fields),
        ).pack(pady=(Sizing.PAD_LG, Sizing.PAD_XL))

    def _create_account(self, fields):
        name = fields["Holder Name"].get().strip()
        card = fields["Card Number"].get().strip()
        pin = fields["PIN"].get().strip()
        balance_str = fields["Balance"].get().strip()

        try:
            balance = float(balance_str) if balance_str else 0.0
        except ValueError:
            self.dash_status.show_error("Invalid balance amount.")
            return

        success, msg = self.app.admin_mgr.add_account(
            holder_name=name, card_number=card, pin=pin,
            balance=balance, account_type=self.acct_type_var.get(),
        )
        if success:
            self.dash_status.show_success(msg)
            # Clear fields
            for entry in fields.values():
                entry.delete(0, tk.END)
        else:
            self.dash_status.show_error(msg)

    # ── Settings Tab ─────────────────────────

    def _show_settings_tab(self):
        self._clear_tab()

        tk.Label(
            self.tab_content, text="Account Settings",
            font=Fonts.TITLE_SM, bg=Colors.BG_DARK, fg=Colors.ACCENT,
        ).pack(anchor="w", pady=(5, 8))

        settings_card = CardFrame(self.tab_content)
        settings_card.pack(padx=100, fill="x")
        inner = settings_card.get_inner()

        # Reset PIN section
        tk.Label(
            inner, text="Reset User PIN",
            font=Fonts.TITLE_SM, bg=Colors.BG_CARD, fg=Colors.TEXT_PRIMARY,
        ).pack(pady=(Sizing.PAD_LG, Sizing.PAD_SM))

        pin_row = tk.Frame(inner, bg=Colors.BG_CARD)
        pin_row.pack(pady=4)
        tk.Label(pin_row, text="Card:", font=Fonts.BODY_MD, bg=Colors.BG_CARD, fg=Colors.TEXT_SECONDARY).pack(side="left", padx=4)
        self.reset_card = tk.Entry(pin_row, font=Fonts.BODY_MD, bg=Colors.BG_INPUT, fg=Colors.TEXT_PRIMARY, bd=0, width=16, insertbackground=Colors.ACCENT)
        self.reset_card.pack(side="left", padx=4, ipady=4)
        tk.Label(pin_row, text="New PIN:", font=Fonts.BODY_MD, bg=Colors.BG_CARD, fg=Colors.TEXT_SECONDARY).pack(side="left", padx=4)
        self.reset_pin = tk.Entry(pin_row, font=Fonts.BODY_MD, bg=Colors.BG_INPUT, fg=Colors.TEXT_PRIMARY, bd=0, width=8, show="*", insertbackground=Colors.ACCENT)
        self.reset_pin.pack(side="left", padx=4, ipady=4)
        ATMButton(pin_row, text="Reset", variant="primary", width=8, height=1, font=Fonts.BODY_SM, command=self._reset_pin).pack(side="left", padx=8)

        # Divider
        tk.Frame(inner, bg=Colors.DIVIDER, height=1).pack(fill="x", padx=Sizing.PAD_LG, pady=Sizing.PAD_MD)

        # Daily limit section
        tk.Label(
            inner, text="Set Daily Withdrawal Limit",
            font=Fonts.TITLE_SM, bg=Colors.BG_CARD, fg=Colors.TEXT_PRIMARY,
        ).pack(pady=(Sizing.PAD_SM, Sizing.PAD_SM))

        limit_row = tk.Frame(inner, bg=Colors.BG_CARD)
        limit_row.pack(pady=(4, Sizing.PAD_XL))
        tk.Label(limit_row, text="Card:", font=Fonts.BODY_MD, bg=Colors.BG_CARD, fg=Colors.TEXT_SECONDARY).pack(side="left", padx=4)
        self.limit_card = tk.Entry(limit_row, font=Fonts.BODY_MD, bg=Colors.BG_INPUT, fg=Colors.TEXT_PRIMARY, bd=0, width=16, insertbackground=Colors.ACCENT)
        self.limit_card.pack(side="left", padx=4, ipady=4)
        tk.Label(limit_row, text="Limit:", font=Fonts.BODY_MD, bg=Colors.BG_CARD, fg=Colors.TEXT_SECONDARY).pack(side="left", padx=4)
        self.limit_amount = tk.Entry(limit_row, font=Fonts.BODY_MD, bg=Colors.BG_INPUT, fg=Colors.TEXT_PRIMARY, bd=0, width=10, insertbackground=Colors.ACCENT)
        self.limit_amount.pack(side="left", padx=4, ipady=4)
        ATMButton(limit_row, text="Set", variant="primary", width=8, height=1, font=Fonts.BODY_SM, command=self._set_limit).pack(side="left", padx=8)

    def _reset_pin(self):
        card = self.reset_card.get().strip()
        pin = self.reset_pin.get().strip()
        success, msg = self.app.admin_mgr.reset_pin(card, pin)
        self.dash_status.show_success(msg) if success else self.dash_status.show_error(msg)

    def _set_limit(self):
        card = self.limit_card.get().strip()
        try:
            limit = float(self.limit_amount.get().strip())
        except ValueError:
            self.dash_status.show_error("Invalid limit amount.")
            return
        success, msg = self.app.admin_mgr.set_daily_limit(card, limit)
        self.dash_status.show_success(msg) if success else self.dash_status.show_error(msg)
