from dataclasses import dataclass


@dataclass(eq=False)
class LocaleNotSupportedError(Exception):
    locale: str

    @property
    def title(self) -> str:
        return f"Locale '{self.locale}' is not supported"


@dataclass(eq=False)
class LocaleNotInstalledError(Exception):
    locale: str

    @property
    def title(self) -> str:
        return f"Locale '{self.locale}' is not installed"


@dataclass(eq=False)
class ParsingError(Exception):
    description: str

    @property
    def title(self) -> str:
        return f"{self.description}"


@dataclass(eq=False)
class EvaluationError(Exception):
    description: str

    @property
    def title(self) -> str:
        return self.description
