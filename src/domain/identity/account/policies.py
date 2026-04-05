"""Политики доступа для Account."""

from src.domain.errors import AccessDeniedError


class AccountPolicy:
    """Проверки прав доступа для операций с аккаунтом."""

    @staticmethod
    def ensure_admin(actor_roles: set[str]) -> None:
        """Проверяет, что у актора есть роль admin."""

        if "admin" not in actor_roles:
            raise AccessDeniedError("Операция доступна только администратору.")

    @staticmethod
    def ensure_self_or_admin(actor_id: str, target_user_id: str, actor_roles: set[str]) -> None:
        """Проверяет, что операция выполняется владельцем или админом."""

        if actor_id == target_user_id or "admin" in actor_roles:
            return
        raise AccessDeniedError("Недостаточно прав для операции над профилем.")
