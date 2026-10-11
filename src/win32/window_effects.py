import ctypes
from ctypes import wintypes
import logging

logger = logging.getLogger(__name__)

# Constantes da Win32 API
GWL_EXSTYLE = -20

WS_EX_TRANSPARENT = 0x00000020  # Cliques do mouse passam direto pela janela
WS_EX_LAYERED     = 0x00080000  # Janela com suporte a camadas/transparência
WS_EX_TOOLWINDOW  = 0x00000080  # Oculta da barra de tarefas e do Alt+Tab
WS_EX_TOPMOST     = 0x00000008  # Sempre no topo

user32 = ctypes.windll.user32

# Suporte adequado a 64-bit e 32-bit para GetWindowLongPtr / SetWindowLongPtr
if hasattr(user32, "GetWindowLongPtrW"):
    _GetWindowLongPtr = user32.GetWindowLongPtrW
    _SetWindowLongPtr = user32.SetWindowLongPtrW
    _GetWindowLongPtr.argtypes = [wintypes.HWND, ctypes.c_int]
    _GetWindowLongPtr.restype = ctypes.c_ssize_t
    _SetWindowLongPtr.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_ssize_t]
    _SetWindowLongPtr.restype = ctypes.c_ssize_t
else:
    _GetWindowLongPtr = user32.GetWindowLongW
    _SetWindowLongPtr = user32.SetWindowLongW
    _GetWindowLongPtr.argtypes = [wintypes.HWND, ctypes.c_int]
    _GetWindowLongPtr.restype = wintypes.LONG
    _SetWindowLongPtr.argtypes = [wintypes.HWND, ctypes.c_int, wintypes.LONG]
    _SetWindowLongPtr.restype = wintypes.LONG

def get_window_extended_style(hwnd: int) -> int:
    """Recupera os estilos estendidos (GWL_EXSTYLE) de uma janela Windows."""
    if not hwnd:
        return 0
    try:
        return int(_GetWindowLongPtr(hwnd, GWL_EXSTYLE))
    except Exception as e:
        logger.error(f"Erro ao obter estilos da janela {hwnd}: {e}")
        return 0

def set_window_extended_style(hwnd: int, style: int) -> bool:
    """Aplica novos estilos estendidos (GWL_EXSTYLE) a uma janela Windows."""
    if not hwnd:
        return False
    try:
        res = _SetWindowLongPtr(hwnd, GWL_EXSTYLE, style)
        return True
    except Exception as e:
        logger.error(f"Erro ao definir estilos da janela {hwnd}: {e}")
        return False

def set_click_through(hwnd: int, enable: bool) -> bool:
    """
    Ativa ou desativa o modo Click-Through (cliques passam direto para o jogo).
    Quando enable=True, adiciona WS_EX_TRANSPARENT e WS_EX_LAYERED.
    Quando enable=False, remove WS_EX_TRANSPARENT.
    """
    if not hwnd:
        return False

    current_style = get_window_extended_style(hwnd)
    if enable:
        new_style = current_style | WS_EX_TRANSPARENT | WS_EX_LAYERED
    else:
        new_style = (current_style & ~WS_EX_TRANSPARENT) | WS_EX_LAYERED

    return set_window_extended_style(hwnd, new_style)

def set_tool_window(hwnd: int) -> bool:
    """Garante que a janela tenha WS_EX_TOOLWINDOW (fora do Alt+Tab e da barra de tarefas)."""
    if not hwnd:
        return False
    current_style = get_window_extended_style(hwnd)
    return set_window_extended_style(hwnd, current_style | WS_EX_TOOLWINDOW | WS_EX_TOPMOST)
