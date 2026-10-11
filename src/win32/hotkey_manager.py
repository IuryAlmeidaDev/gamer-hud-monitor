import ctypes
from ctypes import wintypes
import logging
from PyQt6.QtCore import QThread, pyqtSignal

logger = logging.getLogger(__name__)

user32 = ctypes.windll.user32

WM_HOTKEY = 0x0312
HOTKEY_ID = 1001

# Virtual-Key codes comuns
VK_MAPPING = {
    "F1": 0x70, "F2": 0x71, "F3": 0x72, "F4": 0x73,
    "F5": 0x74, "F6": 0x75, "F7": 0x76, "F8": 0x77,
    "F9": 0x78, "F10": 0x79, "F11": 0x7A, "F12": 0x7B,
}

class GlobalHotkeyListener(QThread):
    """
    Escuta atalhos de teclado globais no Windows usando RegisterHotKey da Win32 API.
    Funciona perfeitamente mesmo quando o usuário está dentro de qualquer jogo.
    """
    hotkey_triggered = pyqtSignal()

    def __init__(self, key_name: str = "F9"):
        super().__init__()
        self.key_name = key_name.upper()
        self.vk_code = VK_MAPPING.get(self.key_name, 0x78)  # Padrão F9
        self.running = True
        self.registered = False

    def run(self) -> None:
        # Modificadores: 0 = sem modificador (apenas a tecla F9 direta)
        # MOD_NOREPEAT = 0x4000 (evita disparos repetidos se segurar a tecla)
        fs_modifiers = 0x4000

        res = user32.RegisterHotKey(None, HOTKEY_ID, fs_modifiers, self.vk_code)
        if not res:
            # Tenta sem MOD_NOREPEAT em sistemas legados
            res = user32.RegisterHotKey(None, HOTKEY_ID, 0, self.vk_code)

        if res:
            self.registered = True
            logger.info(f"Atalho global registrado com sucesso: {self.key_name}")
        else:
            logger.warning(f"Falha ao registrar atalho global {self.key_name}")

        msg = wintypes.MSG()
        while self.running:
            # PeekMessageW não-bloqueante com timeout curto para poder responder a stop()
            has_msg = user32.PeekMessageW(
                ctypes.byref(msg),
                None,
                0,
                0,
                0x0001 # PM_REMOVE
            )

            if has_msg:
                if msg.message == WM_HOTKEY and msg.wParam == HOTKEY_ID:
                    self.hotkey_triggered.emit()
                user32.TranslateMessage(ctypes.byref(msg))
                user32.DispatchMessageW(ctypes.byref(msg))
            else:
                self.msleep(30)

        if self.registered:
            user32.UnregisterHotKey(None, HOTKEY_ID)
            self.registered = False

    def stop(self) -> None:
        self.running = False
        self.wait(1000)
