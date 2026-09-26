import re


REGISTRATION_PATTERN = re.compile(r"^[A-Z0-9][A-Z0-9 -]{2,11}$")
PHONE_PATTERN = re.compile(r"^(?:\+254|0)7\d{8}$")


def clean_text(value: str, max_length=100) -> str:
    return " ".join(value.strip().split())[:max_length]


def valid_registration(value: str) -> bool:
    value = value.strip().upper()
    return bool(REGISTRATION_PATTERN.fullmatch(value))


def valid_phone(value: str) -> bool:
    value = value.strip().replace(" ", "")
    return bool(PHONE_PATTERN.fullmatch(value))


def valid_name(value: str) -> bool:
    value = clean_text(value, 80)
    return 2 <= len(value) <= 80 and any(ch.isalpha() for ch in value)


def valid_username(value: str) -> bool:
    return bool(re.fullmatch(r"[A-Za-z0-9_.-]{3,30}", value.strip()))


def valid_password(value: str) -> bool:
    return len(value) >= 8 and len(value) <= 128


def normalize_registration(value: str) -> str:
    return " ".join(value.strip().upper().split())
