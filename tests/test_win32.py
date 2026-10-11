import pytest
from src.win32.window_effects import (
    get_window_extended_style,
    set_click_through,
    WS_EX_TRANSPARENT,
    WS_EX_LAYERED,
)

def test_get_window_extended_style_invalid_hwnd():
    # Deve retornar 0 ou int sem estourar exceção para hwnd 0
    style = get_window_extended_style(0)
    assert isinstance(style, int)

def test_set_click_through_safe_execution():
    # Chamar para hwnd 0 não deve quebrar
    success = set_click_through(0, enable=True)
    assert isinstance(success, bool)
