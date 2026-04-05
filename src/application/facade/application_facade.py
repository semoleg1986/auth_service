"""Единая точка входа в application слой auth_service."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any


Handler = Callable[[Any], Any]


@dataclass(slots=True)
class ApplicationFacade:
    """Фасад use case уровня приложения.

    Фасад скрывает реализацию handlers от interface-слоя и предоставляет
    единый контракт выполнения команд и запросов.
    """

    command_handlers: dict[type[Any], Handler] = field(default_factory=dict)
    query_handlers: dict[type[Any], Handler] = field(default_factory=dict)

    def execute(self, command: Any) -> Any:
        """Выполняет команду через зарегистрированный handler.

        :param command: Экземпляр command DTO.
        :type command: Any
        :return: Результат команды.
        :rtype: Any
        :raises KeyError: Если обработчик команды не зарегистрирован.
        """

        handler = self.command_handlers[type(command)]
        return handler(command)

    def query(self, query: Any) -> Any:
        """Выполняет query через зарегистрированный handler.

        :param query: Экземпляр query DTO.
        :type query: Any
        :return: Результат запроса.
        :rtype: Any
        :raises KeyError: Если обработчик query не зарегистрирован.
        """

        handler = self.query_handlers[type(query)]
        return handler(query)

    def register_command_handler(self, command_type: type[Any], handler: Handler) -> None:
        """Регистрирует обработчик команды."""

        self.command_handlers[command_type] = handler

    def register_query_handler(self, query_type: type[Any], handler: Handler) -> None:
        """Регистрирует обработчик запроса."""

        self.query_handlers[query_type] = handler
