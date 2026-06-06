# ATM Simulation System — Project Report

## 1. Introduction

This project implements a fully functional ATM (Automated Teller Machine) Simulation
System using Python 3 with a graphical user interface built on Tkinter. The system
replicates real-world ATM operations including user authentication, multiple transaction
types, data persistence, and administrative controls.

The project was developed following Object-Oriented Programming (OOP) principles
with a clean Model-View-Controller (MVC) architecture. All data is persisted in an
SQLite database, and security measures include SHA-256 PIN hashing, input validation,
and parameterized SQL queries.

---

## 2. Design Decisions

### 2.1 Technology Stack
**Python 3** was chosen for its rich standard library, enabling the entire project
to run with zero external dependencies. Key standard library modules used:
- `tkinter` — GUI framework (no installation needed)
- `sqlite3` — Relational database persistence
- `hashlib` — SHA-256 cryptographic hashing
- `hmac` — Constant-time comparison for PIN verification
- `datetime` — Timestamp generation for transaction logging

### 2.2 GUI vs Console
A **Tkinter GUI** was implemented instead of a console interface because:
1. It provides a more realistic ATM simulation experience
2. The virtual keypad mirrors real ATM hardware
3. Screen-based navigation naturally separates transaction flows
4. It demonstrates stronger software engineering skills

### 2.3 Database Choice
**SQLite** was selected over flat files (JSON/CSV) for several reasons:
- ACID-compliant transactions ensure data integrity
- SQL queries enable efficient filtering (e.g., transaction log searches)
- Parameterized queries prevent SQL injection attacks
- Scales better than file-based approaches
- Still uses zero external dependencies (sqlite3 is in Python's stdlib)

### 2.4 Architecture
The project follows a layered MVC architecture:
- **Models** define data structures (Account, Transaction)
- **Controllers** implement business logic (ATM, Auth, Admin)
- **Views** handle user interface (GUI screens and widgets)
- **Data Access** abstracts database operations (DatabaseManager)

This separation ensures each module can be tested, modified, or replaced
independently. For example, the GUI could be swapped for a web interface
without changing any business logic.

### 2.5 Security
- PINs are hashed with SHA-256 before storage — the plain text is never saved
- PIN verification uses `hmac.compare_digest()` for constant-time comparison,
  preventing timing-based side-channel attacks
- All SQL queries use parameterized statements (`?` placeholders) to prevent injection
- User input is sanitized to remove dangerous characters
- Account lockout after 3 failed attempts deters brute-force attacks
- Session auto-logout after 60 seconds of inactivity protects unattended terminals

---

## 3. Challenges Faced

### 3.1 Unicode on Windows Console
Windows' default console encoding (cp1252) does not support Unicode characters
like checkmarks and box-drawing symbols. The solution was to use ASCII-safe
alternatives for all console output during startup and seeding.

### 3.2 Session Timeout in GUI
Implementing a reliable inactivity timer in Tkinter required careful use of
the `after()` method to create a non-blocking polling loop. The timer resets
on any keyboard, mouse, or motion event via global event bindings.

### 3.3 Screen Navigation
Managing multiple screens in Tkinter required a frame-stacking approach where
all screens are pre-created and layered using `grid()`. The active screen is
raised to the front with `tkraise()`, and each screen's `on_show()` method
refreshes its content to reflect the latest data.

### 3.4 Atomic Transfers
Fund transfers between accounts must update two balances atomically.
The DatabaseManager handles this by performing both updates within
the same database connection before committing.

---

## 4. Future Improvements

1. **Biometric Authentication**: Add fingerprint or face recognition for PIN-less login
2. **Network Integration**: Connect to a real banking API for live transactions
3. **Multi-language Support**: Add Urdu, Arabic, and other language options
4. **Receipt Printing**: Interface with a thermal printer for physical receipts
5. **Mobile App**: Create a companion mobile application with QR-code login
6. **Two-Factor Authentication**: Send OTP via SMS for high-value transactions
7. **Interest Calculation**: Automatic monthly interest accrual for savings accounts
8. **Audit Logging**: Track admin actions with who-did-what-when records
9. **Currency Denomination Tracking**: Track individual note counts (e.g., 50 x Rs.1000)
10. **Web Dashboard**: Admin panel as a web application for remote management

---

## 5. Conclusion

This ATM Simulation System successfully implements all required features including
user authentication with lockout, multiple account types, six transaction operations,
full data persistence, comprehensive security measures, and a bonus admin module.
The project demonstrates strong software engineering practices including OOP design,
clean architecture, thorough error handling, and user-friendly interface design.
