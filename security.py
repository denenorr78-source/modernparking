import hashlib
import hmac
import secrets
import time


PBKDF2_ITERATIONS = 310_000
MAX_LOGIN_ATTEMPTS = 3
LOCKOUT_SECONDS = 5


def hash_password(password: str) -> str:
    """Create a salted PBKDF2-SHA256 password hash."""
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        PBKDF2_ITERATIONS,
    )
    return f"pbkdf2_sha256${PBKDF2_ITERATIONS}${salt.hex()}${digest.hex()}"


def verify_password(password: str, stored_hash: str) -> bool:
    """Verify a password against a stored PBKDF2 hash."""
    try:
        algorithm, iterations, salt_hex, digest_hex = stored_hash.split("$")
        if algorithm != "pbkdf2_sha256":
            return False

        salt = bytes.fromhex(salt_hex)
        expected = bytes.fromhex(digest_hex)

        actual = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt,
            int(iterations),
        )

        return hmac.compare_digest(actual, expected)
    except (ValueError, TypeError):
        return False


class LoginLimiter:
    """Simple in-memory protection against repeated failed logins."""

    def __init__(self):
        self.failures = {}
        self.locked_until = {}

    def is_locked(self, username: str):
        until = self.locked_until.get(username, 0)
        remaining = int(until - time.time())

        if remaining > 0:
            return True, remaining

        self.locked_until.pop(username, None)
        self.failures.pop(username, None)
        return False, 0

    def failed(self, username: str):
        count = self.failures.get(username, 0) + 1
        self.failures[username] = count

        if count >= MAX_LOGIN_ATTEMPTS:
            self.locked_until[username] = time.time() + LOCKOUT_SECONDS
            self.failures[username] = 0

    def success(self, username: str):
        self.failures.pop(username, None)
        self.locked_until.pop(username, None)
