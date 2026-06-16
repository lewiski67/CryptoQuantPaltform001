"""Notification port."""

from typing import Protocol


class NotifierPort(Protocol):
    def notify(self, message: str) -> None: ...
