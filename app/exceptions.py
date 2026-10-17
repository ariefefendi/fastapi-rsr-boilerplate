"""Exception domain. Dilempar oleh service, diterjemahkan ke HTTP di main.py."""


class NotFoundError(Exception):
    def __init__(self, message: str = "Data tidak ditemukan"):
        self.message = message
        super().__init__(message)


class UniqueViolationError(Exception):
    def __init__(self, field: str):
        self.field = field
        self.message = f"The {field} has already been taken."
        super().__init__(self.message)
