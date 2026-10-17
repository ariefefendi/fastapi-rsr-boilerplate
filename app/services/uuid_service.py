import uuid


class UuidService:
    def generate(self) -> str:
        return str(uuid.uuid4())
