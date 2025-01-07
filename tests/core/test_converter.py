import pytest
from unittest.mock import patch

from words2nums.core.converter import Converter, Locale
from words2nums.core.exceptions import LocaleNotSupportedError, LocaleNotInstalledError


def test_unsupported_locale():
    """Test that setting an unsupported locale raises LocaleNotSupportedError"""
    converter = Converter()
    with pytest.raises(LocaleNotSupportedError):
        converter.locale = "invalid"


def test_uninstalled_locale():
    """Test that loading an uninstalled locale raises LocaleNotInstalledError"""
    converter = Converter()
    with patch("words2nums.core.converter.isinstance", lambda x, y: True):
        with pytest.raises(LocaleNotInstalledError):
            converter.locale = "test"


def test_default_locale():
    """Test that default locale is English"""
    converter = Converter()
    assert converter.locale == Locale.ENGLISH


def test_convert_english():
    """Test basic conversion with English locale"""
    converter = Converter(locale=Locale.ENGLISH)
    assert converter.convert("one") == 1
    assert converter.convert("twenty one") == 21
    assert converter.convert("one hundred") == 100 