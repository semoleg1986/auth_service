"""Генератор UUID идентификаторов."""

import uuid


class UuidGenerator:
    """Генерирует строковые UUID4."""

    def new(self) -> str:
        return str(uuid.uuid4())
