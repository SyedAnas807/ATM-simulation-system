"""
generate_diagrams.py — Generate UML diagrams as text files.

Creates login flow and transaction flow diagrams using
ASCII art format (no external dependencies needed).
"""

import os

DOCS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "docs", "diagrams")
os.makedirs(DOCS_DIR, exist_ok=True)


def generate_login_flow():
    """Generate the login/authentication flow diagram."""
    diagram = """
    ============================================
         ATM LOGIN FLOW DIAGRAM
    ============================================

    +------------------+
    |   ATM Welcome    |
    |   Screen         |
    +--------+---------+
             |
             v
    +------------------+
    | Enter Card       |
    | Number           |
    +--------+---------+
             |
             v
    +------------------+     NO      +------------------+
    | Valid Format?    |------------>| Show Error:      |
    | (8-16 digits)    |             | Invalid format   |
    +--------+---------+             +--------+---------+
             | YES                            |
             v                                | (retry)
    +------------------+     NO      +--------+---------+
    | Account Exists?  |------------>| Show Error:      |
    |                  |             | Card not found   |
    +--------+---------+             +------------------+
             | YES
             v
    +------------------+     YES     +------------------+
    | Account Locked?  |------------>| Show Error:      |
    |                  |             | Account locked   |
    +--------+---------+             +------------------+
             | NO
             v
    +------------------+
    | Enter PIN        |
    | (Keypad Screen)  |
    +--------+---------+
             |
             v
    +------------------+     NO      +------------------+
    | PIN Correct?     |------------>| Increment Failed |
    | (SHA-256 verify) |             | Attempts Counter |
    +--------+---------+             +--------+---------+
             | YES                            |
             |                                v
             |                       +------------------+
             |                       | Attempts >= 3?   |---YES--->  LOCK ACCOUNT
             |                       +--------+---------+
             |                                | NO
             |                                v
             |                       +------------------+
             |                       | Show Error:      |
             |                       | X attempts left  |
             |                       +------------------+
             v
    +------------------+
    | Reset Failed     |
    | Attempts to 0    |
    +--------+---------+
             |
             v
    +------------------+
    | Start Session    |
    | (60s timeout)    |
    +--------+---------+
             |
             v
    +------------------+
    | Main Menu        |
    | (6 operations)   |
    +------------------+

    ============================================
         SESSION TIMEOUT FLOW
    ============================================

    +------------------+
    | User Active?     |<--- Check every 1 second
    +--------+---------+
             |
        YES  |  NO (60s elapsed)
             |       |
             v       v
    +----------+  +------------------+
    | Reset    |  | Auto-Logout      |
    | Timer    |  | Return to Welcome|
    +----------+  +------------------+
"""
    filepath = os.path.join(DOCS_DIR, "login_flow.txt")
    with open(filepath, "w") as f:
        f.write(diagram)
    print(f"  Generated: {filepath}")


def generate_transaction_flow():
    """Generate the transaction operations flow diagram."""
    diagram = """
    ============================================
         ATM TRANSACTION FLOW DIAGRAM
    ============================================

    +------------------+
    | Main Menu        |
    | 1-6 + Logout     |
    +--------+---------+
             |
      +------+------+------+------+------+------+
      |      |      |      |      |      |      |
      v      v      v      v      v      v      v
    [BAL]  [WDR]  [DEP]  [TRF]  [STM]  [PIN]  [OUT]


    === 1. CHECK BALANCE ===========================

    Main Menu --> Query DB --> Display Balance
                            --> Log: balance_inquiry
                            --> [Print Receipt?]
                            --> Return to Menu


    === 2. WITHDRAW CASH ============================

    Main Menu --> Select Amount (preset/custom)
             |
             v
    +------------------+
    | Validate Amount  |
    +--------+---------+
             |
             v
    +-------------------+  FAIL   +------------------+
    | Check: Balance    |-------->| Show Error       |
    | Check: Daily Limit|         | Log: failed txn  |
    | Check: ATM Cash   |         +------------------+
    | Check: Min Balance|
    | Check: Denomination|
    +--------+----------+
             | PASS
             v
    +------------------+
    | Confirm Withdraw?|
    +--YES---+---------+
             |
             v
    +------------------+
    | Deduct Balance   |
    | Deduct ATM Cash  |
    | Update Daily Total|
    | Log: withdrawal  |
    +--------+---------+
             |
             v
    +------------------+
    | Show Receipt     |
    +------------------+


    === 3. DEPOSIT CASH =============================

    Main Menu --> Enter Amount --> Validate
             --> Confirm? --> Add to Balance
             --> Add to ATM Cash --> Log: deposit
             --> Show Receipt


    === 4. FUND TRANSFER ============================

    Main Menu --> Enter Recipient Card
             --> Validate Recipient (exists, active)
             --> Enter Amount
             --> Validate (balance, min balance)
             --> Confirm Transfer?
             --> Debit Sender
             --> Credit Recipient
             --> Log: transfer_out (sender)
             --> Log: transfer_in (recipient)
             --> Show Receipt


    === 5. MINI STATEMENT ===========================

    Main Menu --> Query last 10 transactions
             --> Display table:
                 | Date | Type | Amount | Balance | Status |
             --> Return to Menu


    === 6. CHANGE PIN ===============================

    Main Menu --> Step 1: Enter Current PIN
             --> Verify against hash
             --> Step 2: Enter New PIN
             --> Validate format (4-6 digits)
             --> Step 3: Confirm New PIN
             --> Check match
             --> Hash & store new PIN
             --> Log: pin_change
             --> Return to Menu


    ============================================
         CLASS DIAGRAM
    ============================================

    +-------------------+       +-------------------+
    |     Account       |       |   Transaction     |
    +-------------------+       +-------------------+
    | - holder_name     |       | - id              |
    | - card_number     |       | - card_number     |
    | - pin_hash        |       | - timestamp       |
    | - balance         |       | - txn_type        |
    | - account_type    |       | - amount          |
    | - status          |       | - balance_after   |
    | - daily_limit     |       | - recipient_card  |
    | - withdrawn_today |       | - status          |
    | - failed_attempts |       | - description     |
    +-------------------+       +-------------------+
    | + can_withdraw()  |       | + format_receipt()|
    | + is_active()     |       | + from_db_row()   |
    | + from_db_row()   |       +-------------------+
    +--------+----------+
             |
      +------+------+
      |             |
    +-v---------+ +-v-----------+
    | Savings   | | Current     |
    | Account   | | Account     |
    +-----------+ +-------------+
    | - interest| | (no min bal)|
    | - min_bal | +-------------+
    +-----------+

    +-------------------+       +-------------------+
    | DatabaseManager   |       |  ATMController    |
    +-------------------+       +-------------------+
    | + get_account()   |       | + check_balance() |
    | + update_balance()|       | + withdraw()      |
    | + add_transaction()|      | + deposit()       |
    | + get_all_accounts|       | + transfer()      |
    | + lock_account()  |       | + change_pin()    |
    +-------------------+       | + get_statement() |
                                +-------------------+

    +-------------------+       +-------------------+
    |  AuthManager      |       |  AdminManager     |
    +-------------------+       +-------------------+
    | + authenticate()  |       | + login()         |
    | + refresh_session()|      | + lock_account()  |
    | + is_expired()    |       | + reset_pin()     |
    | + logout()        |       | + set_limit()     |
    +-------------------+       | + add_account()   |
                                +-------------------+
"""
    filepath = os.path.join(DOCS_DIR, "transaction_flow.txt")
    with open(filepath, "w") as f:
        f.write(diagram)
    print(f"  Generated: {filepath}")


if __name__ == "__main__":
    print("\nGenerating UML diagrams...\n")
    generate_login_flow()
    generate_transaction_flow()
    print("\nDone! Diagrams saved to docs/diagrams/")
