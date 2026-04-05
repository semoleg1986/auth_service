"""Политики доступа для сессий."""

from src.domain.errors import AccessDeniedError


class SessionPolicy:
    """Проверки прав для операций с сессией."""

    @staticmethod
    def ensure_owner_or_admin(actor_account_id: str, session_account_id: str, actor_roles: set[str]) -> None:
        """Разрешает операцию владельцу сессии или администратору."""

        if actor_account_id == session_account_id or "admin" in actor_roles:
            return
        raise AccessDeniedError("Недостаточно прав для управления сессией.")
