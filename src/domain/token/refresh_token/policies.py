"""Политики доступа для refresh token."""

from src.domain.errors import AccessDeniedError


class RefreshTokenPolicy:
    """Проверки прав для операций с refresh token."""

    @staticmethod
    def ensure_owner_or_admin(actor_account_id: str, token_account_id: str, actor_roles: set[str]) -> None:
        """Разрешает действие владельцу токена или администратору."""

        if actor_account_id == token_account_id or "admin" in actor_roles:
            return
        raise AccessDeniedError("Недостаточно прав для управления refresh token.")
