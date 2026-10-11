import pytest
from PyQt6.QtWidgets import QApplication
from src.ui.overlay_window import GamerHudWindow
from src.hardware.collector import HardwareMetrics

# Garante uma única instância do QApplication para os testes
@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app

def test_gamer_hud_window_initialization(qapp):
    win = GamerHudWindow(x=200, y=150, locked=True)
    assert win.locked is True
    assert win.x() == 200
    assert win.y() == 150

    # Teste toggle
    new_state = win.toggle_lock()
    assert new_state is False
    assert win.locked is False

    # Teste de atualização de métricas
    metrics = HardwareMetrics(
        cpu_usage=45.0,
        cpu_temp=62.0,
        gpu_usage=85.0,
        gpu_temp=71.0,
        ram_usage=55.0,
        ram_used_gb=16.0,
        ram_total_gb=32.0,
        vram_used_gb=6.0,
        vram_total_gb=8.0,
    )
    win.update_metrics(metrics)
    assert "45% 62°C" in win.lbl_cpu_val.text()
    assert "85% 71°C" in win.lbl_gpu_val.text()
    assert "55%" in win.lbl_ram_val.text()
    win.close()
