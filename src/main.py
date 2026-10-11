import sys
import os
from pathlib import Path

# Adiciona o diretório raiz ao PYTHONPATH
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QCoreApplication

from src.config import ConfigManager
from src.hardware.collector import HardwareCollector
from src.win32.hotkey_manager import GlobalHotkeyListener
from src.ui.overlay_window import GamerHudWindow
from src.ui.tray_icon import TrayIconManager

def main():
    # Inicializa aplicação Qt
    app = QApplication(sys.argv)
    app.setApplicationName("Gamer HUD Monitor")
    app.setQuitOnLastWindowClosed(False)

    # Carrega configurações do disco
    config_path = ROOT_DIR / "config.json"
    cfg = ConfigManager(str(config_path))
    x = cfg.get("x", 100)
    y = cfg.get("y", 100)
    locked = cfg.get("locked", True)
    hotkey = cfg.get("hotkey", "F9")
    interval_ms = cfg.get("update_interval_ms", 1000)

    # Cria janela HUD
    window = GamerHudWindow(x=x, y=y, locked=locked)

    # Cria ícone na bandeja do sistema
    tray = TrayIconManager()
    tray.update_lock_state(locked)

    # Cria listener para atalho global de teclado
    hotkey_listener = GlobalHotkeyListener(key_name=hotkey)

    # Cria coletor de métricas de hardware
    collector = HardwareCollector(interval_ms=interval_ms)

    # Conexões de sinais
    collector.metrics_ready.connect(window.update_metrics)

    def on_toggle_lock():
        new_locked = window.toggle_lock()
        cfg.set("locked", new_locked)
        cfg.save()

    hotkey_listener.hotkey_triggered.connect(on_toggle_lock)
    tray.toggle_lock_requested.connect(on_toggle_lock)

    def on_position_changed(new_x: int, new_y: int):
        cfg.set("x", new_x)
        cfg.set("y", new_y)
        cfg.save()

    window.position_changed.connect(on_position_changed)
    window.lock_state_changed.connect(tray.update_lock_state)

    def on_reset_position():
        window.move(100, 100)
        on_position_changed(100, 100)

    tray.reset_position_requested.connect(on_reset_position)

    def cleanup():
        collector.stop()
        hotkey_listener.stop()
        cfg.set("x", window.x())
        cfg.set("y", window.y())
        cfg.set("locked", window.locked)
        cfg.save()

    tray.quit_requested.connect(app.quit)
    app.aboutToQuit.connect(cleanup)

    # Exibe janela e inicia threads de background
    window.show()
    collector.start()
    hotkey_listener.start()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
