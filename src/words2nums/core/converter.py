from enum import StrEnum
from typing import Dict, Type, TYPE_CHECKING, NoReturn

from words2nums.core.exceptions import (
    LocaleNotInstalledError,
    LocaleNotSupportedError,
)
from words2nums.core.types import ReturnValue


if TYPE_CHECKING:
    from words2nums.core.handler import Handler


class Locale(StrEnum):
    ENGLISH = "en"


class Format(StrEnum):
    CARDINAL = "cardinal"
    ORDINAL = "ordinal"


class _Locale:
    _registry: Dict[Locale, Type["Handler"]] = {}

    def __get__(self, instance, owner):
        return getattr(instance, "_locale")

    def __set__(self, instance, value: Locale):
        if not isinstance(value, Locale):
            raise LocaleNotSupportedError(value)

        instance._locale = value

        if value not in self._registry:
            self._load_handler(value)

        handler_class = self._registry[value]
        instance._handler = handler_class.create_default()

    # TODO (hrimov): refactor to dispatch dict instead
    def _load_handler(self, locale: Locale) -> NoReturn | None:
        if locale == Locale.ENGLISH:
            from words2nums.locales.english import EnglishHandler
            self._registry[locale] = EnglishHandler
            return None

        raise LocaleNotInstalledError(locale)


class Converter:
    __slots__ = ("_locale", "_handler",)

    locale = _Locale()

    def __init__(
            self,
            locale: Locale = Locale.ENGLISH,
    ) -> None:
        # noinspection PyUnresolvedReferences,PyDunderSlots
        self.locale = locale
        self._handler: "Handler"

    def convert(self, text: str) -> ReturnValue:
        handler = self._handler
        return handler.convert(text)
