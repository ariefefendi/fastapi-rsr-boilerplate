import secrets
import string

_ALPHABET = string.ascii_uppercase + string.digits


class ShortIdService:
    def generate(self, prefix: str = "", length: int = 5) -> str:
        suffix = "".join(secrets.choice(_ALPHABET) for _ in range(length))
        return f"{prefix}{suffix}"
