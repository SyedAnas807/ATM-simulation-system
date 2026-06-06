# ATM Simulation System

A comprehensive ATM Simulation System built with Python, featuring a modern
Tkinter GUI, SQLite database persistence, and full security compliance.
Developed as an end-of-semester software engineering project.

---

## Features

### Core Features
- **User Authentication**: Card number + PIN login with masked input
- **Account Types**: Savings (interest-bearing, minimum balance) and Current/Checking
- **Check Balance**: View current available balance with receipt
- **Withdraw Cash**: Denomination selection, daily limits, ATM cash tracking
- **Deposit Cash**: Add funds with confirmation and receipt
- **Fund Transfer**: Transfer between accounts with recipient validation
- **Mini Statement**: Last 10 transactions with full details
- **Change PIN**: 3-step secure PIN change flow

### Security
- PIN hashed with **SHA-256** (never stored as plain text)
- Constant-time PIN comparison (prevents timing attacks)
- **3-attempt lockout** — account auto-locks after 3 wrong PINs
- **60-second session timeout** with auto-logout
- Input sanitization and parameterized SQL queries (prevents injection)
- No sensitive data displayed in console or logs

### Data Persistence
- **SQLite** database (`atm.db`) — survives program restarts
- Full transaction logging with timestamps
- Automatic table creation on first run

### Admin Module (+10% Bonus)
- Separate admin login (username + password)
- View all accounts and balances
- Lock / Unlock any account
- Reset user PINs
- Set daily withdrawal limits per account
- Filter transaction logs by date, card number, and type
- Add new accounts / remove accounts

---

## Technology Stack

| Component | Technology |
|-----------|-----------|
| Language | Python 3.8+ |
| GUI | Tkinter (standard library) |
| Database | SQLite3 (standard library) |
| Hashing | hashlib SHA-256 (standard library) |
| Architecture | OOP with MVC pattern |

> **Zero external dependencies** — runs on any machine with Python 3.8+ installed.
> No `pip install` required.

---

## Setup & Running

### Prerequisites
- Python 3.8 or higher
- tkinter (included with standard Python installation)

### Installation

```bash
# 1. Navigate to the project directory
cd "ATM simulation system"

# 2. Run the application
python main.py
```

The database is automatically created and seeded with demo accounts on first run.

### Reset Database
To reset all data to the initial state:
```bash
# Delete the database file and re-run
del atm.db
python main.py
```

---

## Demo Credentials

### User Accounts

| Name | Card Number | PIN | Balance | Type | Status |
|------|-------------|-----|---------|------|--------|
| Ali Hassan | 1234567890 | 1111 | Rs.25,000 | Savings | Active |
| Sara Khan | 9876543210 | 2222 | Rs.75,000 | Current | Active |
| Usman Ahmed | 1111222233 | 3333 | Rs.5,000 | Savings | Locked |

### Admin Access

| Username | Password |
|----------|----------|
| admin | admin123 |

---

## Project Structure

```
ATM simulation system/
|-- main.py                     # Entry point
|-- config.py                   # Configuration constants
|-- seed_data.py                # Database seeder with demo data
|-- atm.db                     # SQLite database (auto-created)
|-- models/
|   |-- account.py             # Account, SavingsAccount, CurrentAccount
|   |-- transaction.py         # Transaction model with receipt formatting
|-- database/
|   |-- db_manager.py          # SQLite CRUD operations
|-- auth/
|   |-- auth_manager.py        # Login, lockout, session management
|-- core/
|   |-- atm.py                 # ATM controller (all transaction logic)
|-- admin/
|   |-- admin_manager.py       # Admin operations (bonus module)
|-- security/
|   |-- utils.py               # PIN hashing, input validation
|-- gui/
|   |-- app.py                 # Main Tk application & screen manager
|   |-- theme.py               # Colors, fonts, styling constants
|   |-- widgets.py             # Reusable custom widgets
|   |-- screens/
|       |-- welcome_screen.py  # Card insertion with animation
|       |-- pin_screen.py      # Keypad PIN entry
|       |-- main_menu_screen.py# 6-option transaction menu
|       |-- balance_screen.py  # Balance display
|       |-- withdraw_screen.py # Cash withdrawal
|       |-- deposit_screen.py  # Cash deposit
|       |-- transfer_screen.py # Fund transfer
|       |-- statement_screen.py# Mini statement table
|       |-- change_pin_screen.py# PIN change flow
|       |-- receipt_screen.py  # Transaction receipt
|       |-- admin_screen.py    # Admin panel (bonus)
|-- docs/
    |-- README.md              # This file
    |-- project_report.md      # Design report
```

---

## Architecture

The system follows an **OOP Model-View-Controller (MVC)** pattern:

- **Models** (`models/`): Data classes for Account and Transaction
- **Controllers** (`auth/`, `core/`, `admin/`): Business logic
- **Views** (`gui/`): Tkinter GUI screens and widgets
- **Data Access** (`database/`): SQLite persistence layer

### Class Hierarchy
```
Account (base)
  |-- SavingsAccount (min balance, interest rate)
  |-- CurrentAccount (no restrictions)

Transaction (immutable record)

ATMController -> DatabaseManager -> SQLite
AuthManager   -> DatabaseManager -> SQLite
AdminManager  -> DatabaseManager -> SQLite
```

---

## Author
End-of-semester Software Engineering Project
