"""
security/utils.py — Cryptographic and validation utilities.

Provides PIN hashing (SHA-256), constant-time verification,
and input validation helpers used throughout the system.
"""

import hashlib
import hmac
import re
from config import (
    CARD_MIN_LENGTH, CARD_MAX_LENGTH,
    PIN_MIN_LENGTH, PIN_MAX_LENGTH,
)


# ──────────────────────────────────────────────
# PIN Hashing
# ──────────────────────────────────────────────

def hash_pin(pin: str) -> str:
    """
    Hash a PIN string using SHA-256.
    
    Args:
        pin: The plain-text PIN to hash.
        
    Returns:
        Hexadecimal digest string.
    """
    return hashlib.sha256(pin.encode("utf-8")).hexdigest()


def verify_pin(plain_pin: str, stored_hash: str) -> bool:
    """
    Verify a plain-text PIN against a stored SHA-256 hash.
    Uses constant-time comparison to prevent timing attacks.
    
    Args:
        plain_pin:   The PIN entered by the user.
        stored_hash: The hash stored in the database.
        
    Returns:
        True if the PIN matches, False otherwise.
    """
    candidate = hash_pin(plain_pin)
    return hmac.compare_digest(candidate, stored_hash)


# ──────────────────────────────────────────────
# Input Validation
# ──────────────────────────────────────────────

def validate_card_number(card: str) -> tuple:
    """
    Validate that a card number is 8–16 digits.
    
    Returns:
        (is_valid: bool, error_message: str)
    """
    card = card.strip()
    if not card:
        return False, "Card number cannot be empty."
    if not card.isdigit():
        return False, "Card number must contain only digits."
    if len(card) < CARD_MIN_LENGTH or len(card) > CARD_MAX_LENGTH:
        return False, f"Card number must be {CARD_MIN_LENGTH}–{CARD_MAX_LENGTH} digits."
    return True, ""


def validate_pin_format(pin: str) -> tuple:
    """
    Validate that a PIN is 4–6 digits.
    
    Returns:
        (is_valid: bool, error_message: str)
    """
    pin = pin.strip()
    if not pin:
        return False, "PIN cannot be empty."
    if not pin.isdigit():
        return False, "PIN must contain only digits."
    if len(pin) < PIN_MIN_LENGTH or len(pin) > PIN_MAX_LENGTH:
        return False, f"PIN must be {PIN_MIN_LENGTH}–{PIN_MAX_LENGTH} digits."
    return True, ""


def validate_amount(amount_str: str) -> tuple:
    """
    Validate and parse a monetary amount string.
    
    Returns:
        (is_valid: bool, amount_or_error: float | str)
    """
    amount_str = amount_str.strip()
    if not amount_str:
        return False, "Amount cannot be empty."
    
    # Allow digits and a single decimal point
    if not re.match(r"^\d+(\.\d{1,2})?$", amount_str):
        return False, "Invalid amount. Enter a positive number (e.g. 5000 or 1500.50)."
    
    amount = float(amount_str)
    if amount <= 0:
        return False, "Amount must be greater than zero."
    
    return True, amount


def sanitize_input(text: str) -> str:
    """
    Strip potentially dangerous characters from user input.
    Prevents basic SQL injection if parameterized queries are bypassed.
    
    Args:
        text: Raw user input string.
        
    Returns:
        Sanitized string with harmful characters removed.
    """
    # Remove characters that could be used in SQL injection
    dangerous = ["'", '"', ";", "--", "/*", "*/", "\\", "\x00"]
    cleaned = text.strip()
    for char in dangerous:
        cleaned = cleaned.replace(char, "")
    return cleaned


def mask_card_number(card: str) -> str:
    """
    Mask a card number for display, showing only the last 4 digits.
    Example: '1234567890' → '******7890'
    
    Args:
        card: Full card number string.
        
    Returns:
        Masked string.
    """
    if len(card) <= 4:
        return card
    return "*" * (len(card) - 4) + card[-4:]
